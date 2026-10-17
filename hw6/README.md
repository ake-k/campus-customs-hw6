# Campus Customs vendor desk agent: MGT 409 Homework 6

This is a PydanticAI agent that reads **one vendor document** (an HTML quote, a PDF quote, or an `.eml` email). It pulls out the vendor, SKU, unit price, lead time, and minimum order, then decides **recommend** or **do_not_recommend** using the rules in `data/shop_handbook.md`.

Every AI call uses **`gpt-6-luna` through Portkey**. The agent has two trap tools, `send_email` and `approve_payment`. They never send or pay anything; they only write to `output/trap_calls.json`.

## Setup (Python 3.12+)

```bash
cd hw6
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then put your PORTKEY_API_KEY in .env
```

The agent also finds a `.env` in a parent folder, so a course-wide `.env` works too. The real `.env` is never committed.

## Run the agent on one document

```bash
python agent.py --doc data/practice_docs/p01_bluehen_quote.html
```

This prints the tool calls, the answer, the token counts, and the cost. Each run appends to `output/usage_log.json` (tokens and dollars) and `output/audit_trail.json` (tool calls, anything the defenses removed or blocked, and the final answer).

| Option | What it does |
|---|---|
| `--defense all` (default) | All three defense layers: code (removes hidden text), design (decision made in code, trap tools need human approval), prompt (security rules) |
| `--defense none` | The undefended Problem 3 agent |
| `--defense code,prompt` | Any combination of `code`, `design`, `prompt` |
| `--cache off` | Turns off prompt caching (the default is on) |

## Reproduce each problem's results

| Command | Problem | Writes |
|---|---|---|
| `python agent.py --cache-test` | 4: with vs. without cache, 12 practice docs | `output/cache_test.json` |
| `python agent.py --attack-test` | 5: the undefended agent vs. the answer key | `output/attack_results.json` |
| `python agent.py --defense-test` | 6: no defenses, each layer alone, all three | `output/defense_results.json` |
| `python agent.py --doc data/my_attacks/a1_elmcity_quote.html --defense none` | 7: red-team attack 1 (also try `a2_eastrock_quote.pdf`, and `--defense all`) | logs only |
| `python agent.py --exam` | 8: the defended agent on the 10 exam docs | `output/exam_results.json` |
| `python build_report.py` | 9: rebuild the results page from the JSON outputs | `output/hw6_report.html` |

The batch commands make 24–60 model calls, costing well under $0.05 at `data/prices.json` rates. They overwrite their own result file and append to the logs.

## What's where

- `agent.py`: entry point and CLI, run logging, and the test and exam batches
- `tools.py`: `read_document`, the two trap tools, the document sanitizers (code layer), and the decision checks (design layer)
- `models.py`: structured types for the answer and the log entries
- `prompts/prompt.md`: agent instructions; the security-rules block is used only with the prompt layer
- `data/`: the handbook, prices, practice docs and key, exam docs, and `my_attacks/` (the two red-team documents)
- `output/`: every write-up and result. Start with [`output/hw6_report.html`](output/hw6_report.html) (open it in a browser) and [`output/harness.md`](output/harness.md).
- `AI_prompts.md`: the prompts used to build this, one section per problem
