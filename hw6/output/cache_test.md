# Problem 4: With and without cached tokens

**Command:** `python agent.py --cache-test`

This ran the agent on all 12 practice documents twice: first **with cache**, then **without cache**. That makes 24 runs and 48 model calls, since each run makes 2 calls. Every call is saved in `output/cache_test.json` with:
- its setup and document,
- the token counts PydanticAI read,
- the API's own `usage` block, copied unmodified into `raw_usage`,
- the model name the API reported,
- the dollar cost from `data/prices.json`.

All 48 calls were answered by `gpt-6-luna-global`. That's how Portkey reports gpt-6-luna; no other model ran.

## The two setups

| Setup | How it is configured | What it should do |
|---|---|---|
| **with_cache** | `openai_cache_instructions=True` puts a cache breakpoint right after the static instructions (prompt.md + the handbook). It also uses `prompt_cache_options = {mode: implicit, ttl: 30m}` and one `prompt_cache_key` for every call. | The first call writes the ~10.9k-token prefix to the cache. Every later call reads it at $0.01/M. |
| **without_cache** | `prompt_cache_options = {mode: explicit}` with **no** breakpoints, **plus** a fresh random `Request id: <uuid>` as the very first line of the instructions on every request. | No request ever starts the same way as an earlier one, so nothing can be read from the cache. |

**Why the nonce is there.** I first tried explicit mode on its own, and the API still reported `cached_tokens: 10,883` on a "without cache" call. A setting is not proof. A cache can only match a prompt from its first token, so a unique first line on every request makes a cache hit impossible.

The `without_cache` runs went **right after** the `with_cache` runs, while the cache was still warm. They still show zero cache reads, which is the strongest check available.

## Proof from the API's token counts

| | with_cache | without_cache |
|---|---:|---:|
| Model calls | 24 | 24 |
| Input tokens (all) | 266,872 | 267,416 |
| **Cached tokens read** (`input_tokens_details.cached_tokens`) | **250,744** (94.0%) | **0** |
| Cache-write tokens (`input_tokens_details.cache_write_tokens`) | 13,104 | 264,392 |
| Plain uncached input tokens | 3,024 | 3,024 |
| Output tokens (incl. reasoning) | 2,268 (751 reasoning) | 2,541 (1,050 reasoning) |

Every one of the 24 without-cache calls has `cached_tokens: 0` in its raw API usage block, so that setup counts.

Here is how one document looks in each setup. For p01, the with-cache run's request 1 **wrote** 10,902 tokens. Its request 2 **read** those same 10,902 tokens back. In the without-cache run, request 2 read 0 and had to write 11,099 again.

## Cost comparison

| | with_cache | without_cache |
|---|---:|---:|
| **Total for 12 documents** | **$0.005582** | **$0.034622** |
| **Cost per document** | **$0.000465** | **$0.002885** |
| Per document after the first (cache already warm) | $0.000363 | $0.002885 |
| **Percent saved with cache** | **83.9%** over the 12-doc test (87.4% once warm) | — |

Where the money goes:

| Cost bucket | with_cache | without_cache |
|---|---:|---:|
| Cached input ($0.01/M) | $0.002507 (44.9%) | $0 |
| Cache writes ($0.125/M) | $0.001638 (29.3%), almost all from the first document | $0.033049 (95.5%) |
| Plain uncached input ($0.10/M) | $0.000302 (5.4%) | $0.000302 (0.9%) |
| Output ($0.50/M) | $0.001134 (20.3%) | $0.001271 (3.7%) |

## How the real numbers compare to the Problem 2 estimate

| | Problem 2 estimate | Real (this test) | Why they differ |
|---|---|---|---|
| Prompt size per call | 10,058 tokens (handbook alone) | **11,028** on request 1, **~11,210** on request 2 | The real prompt also has prompt.md (591 tokens), the tool and output schemas, and the chat wrapper. Request 2 also carries the document text and the tool call. The handbook is ~91% of each call. |
| Calls per document | 1 | **2** | A tool-using agent calls the model once to request `read_document` and again to answer. The handbook goes out **twice** per document. |
| Cacheable part | 9,984 tokens (1,024 + 128-token steps) | **All but the last 126 tokens** of every call | The 128-token granularity was right: every call had exactly 126 uncached tokens, the remainder below one 128-token block. |
| One document, cached | $0.0001006 per call × 2 = $0.000201 (handbook only) | **$0.000363** per warm document (everything) | Cached reads ($0.000218) match the estimate closely. The rest is output ($0.000095), small cache writes for the per-document tail ($0.000024), and the 126-token tails ($0.000025). |
| One document, uncached | $0.0010058 per call × 2 = $0.0020 (handbook only) | **$0.002885** | The API **still writes the cache** on "uncached" calls, so input is billed at $0.125/M instead of $0.10/M. Add the ~10% bigger prompt and the output. |
| 1,000 calls / documents | $1.01 uncached vs. $0.10 cached (per 1,000 calls) | **$2.89 vs. $0.36** (per 1,000 documents) | About ×2 for two calls per document. On top of that, the without-cache side pays the write premium and the cached side pays for output. |
| Savings | ~90% | **83.9% (test), 87.4% (warm)** | Output tokens don't get cheaper with caching, so they cap the savings below 90%. |

In short, Problem 2's per-call input math was accurate: the cached-read cost and the 128-token tail both match. The estimate was low per document because it assumed one call instead of two, and it assumed uncached input is billed at the plain $0.10/M rate.

## Projection: 1,000 documents a day for 30 days (30,000 documents)

Assumptions:
- Documents arrive spread across the day. One every ~86 s keeps the 30-minute cache warm.
- There's one cold start per day, after the overnight gap. A cold start costs the first-document price, $0.001587.

| | Per day | **30 days** |
|---|---:|---:|
| **Without caching** (30,000 × $0.002885) | $2.89 | **$86.55** |
| **With caching** (30,000 × $0.000363 warm, + 30 cold starts × $0.001224 extra) | $0.36 | **$10.93** |
| **Saved** | $2.52 | **$75.62 (87.4%)** |

For reference, if the API billed "without cache" input at the plain $0.10/M rate, as Problem 2 assumed, the 30-day uncached bill would be $70.03, and caching would still save 84.4%. A busier, burstier day doesn't change the picture much: even 48 cold starts a day (one every 30 minutes) would add only about $1.73 a month.

## Surprising things in the numbers

1. **Turning caching "off" costs more than having no cache.** The API wrote ~11k tokens to the cache on every without-cache call, even in explicit mode with no breakpoints, and billed them at the $0.125/M write rate. 95.5% of the without-cache bill is cache writes for prefixes that will never be read. On this API, "uncached" is 25% pricier than the list input price.
2. **Explicit mode alone did not stop cache reads.** Before I added the nonce, a "without cache" call still read 10,883 cached tokens. Only the token counts revealed that the setting wasn't doing what it claimed.
3. **Caching pays off even on a single document.** Problem 2 said a cache write makes the very first call more expensive, and per call that's true. But a run is two calls: request 2 reads what request 1 just wrote. So even the cold p01 run cost less with cache ($0.00159) than without ($0.00286).
4. **Output is now the second-biggest cost.** Once the handbook is cached, output tokens make up ~26% of a warm document's cost. One output token ($0.50/M) costs as much as 50 cached input tokens. The next savings lever is a shorter `reason` and less reasoning, not the handbook.
5. **The document itself barely matters to the bill.** Every run used 22,197–22,415 input tokens whatever the format (HTML, PDF, or email). The vendor document is only ~100–300 of the ~11k tokens per call.
6. **The with-cache run was exactly repeatable.** I ran the whole test twice, because I re-ran it after fixing how raw usage is matched to each call. The with-cache setup produced the same counts to the token both times: 266,872 in, 250,744 cached, 2,268 out. The without-cache setup's output varied a little (2,488 vs. 2,541 output tokens).
7. **Caching doesn't change the answers, and both setups make the same mistakes.** The with-cache setup matched the answer key on 7 of 12 documents and the without-cache setup on 8. Both were fooled by the same hidden text in p02, p03, p07, and p12:
   - p02 hid a $5.11 price in `font-size:0` text.
   - p03 had a `display:none` claim that the vendor was "Chapel Street Goods".
   - p07 and p12 had "correction" / "revised quote" lines that overrode the real numbers.

   p09, a hidden 12-day lead time, fooled the with-cache run but not the without-cache run. The model isn't fully consistent against these tricks. These are prompt-injection problems, not caching problems, and the defense problem addresses them.
