# Problem 2: Sizing up the handbook

The vendor desk agent sends `data/shop_handbook.md` to gpt-6-luna on **every** call, so its size sets a floor on what every call costs. This file estimates that floor before we run anything. Problem 4 checks the estimate against real token counts from the API.

---

## 1. Token count

| Method | Result |
|---|---|
| **`tiktoken` `o200k_base` encoding (headline estimate)** | **10,058 tokens** |
| `tiktoken` `cl100k_base` encoding (older GPT-4 tokenizer, for comparison) | 10,184 tokens |
| Rule of thumb: characters ÷ 4 (28,903 ÷ 4) | ~7,226 tokens |
| Rule of thumb: words × 4/3 (6,127 × 1.33) | ~8,169 tokens |

**Headline estimate: about 10,058 tokens.** This matches the assignment's "about 10,000 tokens".

### How it was calculated

```python
import tiktoken
text = open("data/shop_handbook.md", encoding="utf-8").read()
enc = tiktoken.get_encoding("o200k_base")
print(len(enc.encode(text)))   # 10058
```

- `tiktoken` (v0.14.0) has no built-in mapping for `gpt-6-luna`; `encoding_for_model("gpt-6-luna")` raises an error. I used `o200k_base`, the tokenizer of OpenAI's current model families, as the closest stand-in. The real count gets checked against the API's `usage.prompt_tokens` in Problem 4.
- The two rules of thumb come in **low** (7.2k to 8.2k). The handbook is mostly Markdown tables full of `|`, `$`, SKU codes like `CC-HD-001`, and decimal prices. These split into many short tokens, so the handbook has fewer characters per token than ordinary prose.
- When the handbook is sent as a system message, the chat format adds a few tokens of wrapper (role markers). The agent's own instructions and the vendor document go on top of that. Those belong to the full prompt, not the handbook, and Problem 4 measures them.

### Where the tokens are

| Section | Tokens (`o200k_base`) | Share |
|---|---:|---:|
| §9 Product catalogue (177 SKU rows) | 6,920 | 68.8% |
| §10 Recent purchase orders (40 rows) | 1,462 | 14.5% |
| §5 Approved vendors | 417 | 4.1% |
| §4 Purchasing rules | 269 | 2.7% |
| All other sections (§1–3, §6–8, §11–13, title) | 990 | 9.8% |
| **Total** | **10,058** | **100%** |

Most of the handbook is the product catalogue. The purchasing rules that actually decide recommend or do_not_recommend take under 3% of the tokens.

---

## 2. Prices (`data/prices.json`, gpt-6-luna, per 1M tokens)

| Token type | Price per 1M | Price per token |
|---|---:|---:|
| Input (uncached) | $0.10 | $0.0000001 |
| Cached input (cache read) | $0.01 | $0.00000001 |
| Cache write | $0.125 | $0.000000125 |
| Output | $0.50 | $0.0000005 |

The handbook is **input** only. Output tokens depend on the agent's answer, not on the handbook, so they aren't part of this estimate.

---

## 3. What the handbook alone costs

Formula: **cost = tokens × (price per 1M) ÷ 1,000,000**, with T = 10,058 tokens.

### One call

| Scenario | Math | Cost |
|---|---|---:|
| Uncached (normal input) | 10,058 × $0.10 ÷ 1,000,000 | **$0.0010058** (≈ 0.10¢) |
| Cache write (first call that stores the handbook in the cache) | 10,058 × $0.125 ÷ 1,000,000 | **$0.0012573** (≈ 0.13¢) |
| Cache read (later call that reuses the cache) | 10,058 × $0.01 ÷ 1,000,000 | **$0.0001006** (≈ 0.01¢) |

### Many calls

Without caching, every call pays the full input price.
With caching, the first call pays the cache-write price and every later call pays the cache-read price, assuming the cache stays warm.

| Calls | Without caching: N × $0.0010058 | With caching: $0.0012573 + (N − 1) × $0.0001006 | Saved |
|---:|---:|---:|---:|
| 1 | $0.0010058 | $0.0012573 | −$0.0002515 (caching costs more) |
| 1,000 | **$1.0058** | $0.0012573 + 999 × $0.0001006 = **$0.1017** | $0.9041 (89.9%) |
| 10,000 | $10.058 | $0.0012573 + 9,999 × $0.0001006 = **$1.0070** | $9.051 (90.0%) |
| 100,000 | $100.58 | $0.0012573 + 99,999 × $0.0001006 = **$10.059** | $90.52 (90.0%) |

### Break-even

- A cache write costs **$0.0002515 more** than an uncached call: 10,058 × ($0.125 − $0.10) ÷ 1,000,000.
- Each cache read saves **$0.0009052**: 10,058 × ($0.10 − $0.01) ÷ 1,000,000.
- So caching pays for itself on the **2nd call**. One read saves about 3.6× the write premium.
- As N grows, the saving approaches **90%**, because the cached rate is one tenth of the input rate.

---

## 4. Real-world adjustments (things Problem 4 should check)

1. **Cache expiry.** Prompt caches expire after a few minutes of inactivity. Suppose 1,000 calls arrive in 10 separate bursts. That's 10 cache writes instead of 1: 10 × $0.0012573 + 990 × $0.0001006 = **$0.1121**. That's still 89% cheaper than no caching.
2. **Cache granularity.** OpenAI-style caching usually matches the first 1,024 tokens and then extends in 128-token steps. If gpt-6-luna works that way, only 1,024 + 128 × ⌊(10,058 − 1,024) ÷ 128⌋ = **9,984** handbook tokens are cacheable. The last 74 tokens are always billed at the full input rate.
   - Cached call: 9,984 × $0.01/1M + 74 × $0.10/1M = **$0.0001072**
   - 1,000 calls: $0.0012554 + 999 × $0.0001072 ≈ **$0.1084** (vs. $0.1017 above)

   In practice the system prompt and handbook come first, so the cached prefix will extend past the handbook into the fixed instructions. This 74-token tail is a worst case.
3. **Prefix order matters.** The cache only matches when the start of the prompt is identical from call to call. The handbook (and any fixed instructions) must come **before** the vendor document. If the document comes first, nothing gets cached.
4. **Tokenizer uncertainty.** If gpt-6-luna uses a different tokenizer, the count could shift by a few percent. `cl100k_base` gives 10,184 tokens, +1.3%. Every dollar figure above scales linearly with the token count.

---

## 5. Summary

| | Value |
|---|---:|
| Handbook size | **≈ 10,058 tokens** |
| One call, uncached | $0.0010058 |
| One call, cache read | $0.0001006 |
| 1,000 calls, uncached | **$1.01** |
| 1,000 calls, cached (1 write + 999 reads) | **$0.10** |
| Saving from caching at scale | **≈ 90%** |
