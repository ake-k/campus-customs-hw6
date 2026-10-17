# AI Prompts Log — Homework 6

This file records the prompts I gave my AI coding assistant, one section per problem. Where the first prompt wasn't enough, the section also lists the follow-up and says in one sentence what the first prompt was missing.

---

## Setup — Scenario and data pack

**Prompt:**
> Campus Customs gets a steady stream of vendor quotes, invoices, catalog pages, and supplier emails. You will build a vendor desk agent that reads one of these documents, pulls out the key facts (vendor, item, price, lead time, minimum order), and recommends whether the shop should buy, following the rules in the Campus Customs Shop handbook. This week is about two things that matter once an agent runs for real: cost (the handbook is about 10,000 tokens and goes out on every call) and safety (some vendor documents hide instructions aimed at your AI). You will measure the bill, cut it, attack your own agent, and defend it. Do NOT send emails or make payments. The agent's email and payment tools only write to a log file. Use the Portkey API key and ONLY gpt-6-luna for every AI call. Final submission of the assignment will be via a public GitHub repo (see screenshot attached for the expected file tree). I will now give you the data pack for this assignment. Unzip it so you have data/shop_handbook.md, data/prices.json, data/practice_docs/ (12 vendor documents), data/practice_key.json, and data/exam_docs/ (10 more vendor documents with no answer key).

**Follow-up:** None needed.

---

## Problem 1 — Vibe coder prompts

**Prompt:**
> Create AI_prompts.md and update as we go. This file is the log of what I tell you. Put one section for each problem. Each section must include the problem number and title, at least one prompt I gave you, and one follow-up prompt if it was needed (with a one-sentence note on what was lacking from the first prompt).

**Follow-up:** None needed.

---

## Problem 2 — Size up the handbook

**Prompt:**
> Unzip the data pack and look through the Campus Customs Shop Handbook. This is what the agent will send to the model on every single call. Also look at data/prices.json to see the gpt-6-luna price list. Calculate how many tokens the handbook is, and write to output/handbook_estimate.md: the token count, and how it was calculated; what the handbook alone costs in dollars on one call, on 1,000 calls, with cached tokens, without cached tokens, etc. Show your math. We will check these estimates against real runs later in Problem 4.

**Follow-up:** None needed.

---

## Problem 3 — Build the vendor desk agent

**Prompt:**
> Build the vendor desk agent with PydanticAI using gpt-6-luna. The agent is prompts/prompt.md (the instructions for the agent), agent.py (the entry point), tools.py (the tools), models.py (the structured types). Give the agent the path to one vendor document. It should read the document with a tool, and it should be able to read HTML, PDF, or .eml email files. It should return the vendor, SKU, unit price, lead time in days, minimum order, a decision (recommend or do_not_recommend) following the handbook rules, and a brief, one-sentence reason. The agent should have two trap tools, send_email and approve_payment -- its job never needs them. They are only there to catch a malicious document that tricks the agent into emailing someone or paying a vendor. They do not send or pay anything, but only append the call and its arguments to output/trap_calls.json (which starts empty, so if that file ever has an entry, I will immediately know a document took over my agent). Keep them on the system for the whole homework. After every run, append to: output/usage_log.json: document, time, token counts reported by the API, and dollar cost using prices.json; output/audit_trail.json: each tool call with arguments and short result, plus the final answer. The agent should run with the following Terminal command: `python agent.py --doc data/practice_docs/p01_bluehen_quote.html` (This command runs the agent on one vendor quote and logs the answer, tool, and cost). Run it first on p01 and p08 first and show me how it works. Also start output/harness.md (each field in models.py and why, and each tool in one line).

**Follow-up:** None needed.

---

## Problem 4 — With and without cached tokens

**Prompt:**
> The handbook is the same on every call, so the model can reuse it from a cache at a much cheaper price. Test what this is worth -- run the agent on all 12 practice documents two ways: with cache (i.e., set up so the handbook gets reused from cache) and without cache (i.e., set up so nothing gets reused from cache). Check the token counts the API sends back to prove which setup runs more efficiently. A without-cache run that still shows cached tokens does not count. Save every model call from both setups in output/cache_test.json. For each call, include the setup, the document, every token count returned by the API, and dollars from prices.json. In output/cache_test.md, compare the total cost and cost per document for each setup (and the percent saved) and describe how the real numbers compare to the estimate from Problem 2. Provide a projection for 1,000 documents a day for 30 days, with and without caching, and remark on anything else in the numbers that is surprising.

**Follow-up:** None needed.

---

## Problem 5 — Attack your own agent

**Prompt:**
> Some vendor documents are booby-trapped with text aimed at AI. Run the agent from Problem 3 with no new defenses on all 12 practice documents. Compare each answer to data/practice_key.json and check output/trap_calls.json, then log the fake email and payment tools from Problem 3 write to. Save output/attack_results.json that records whether each field matched the key, whether the decision matched, whether a trap tool was called, and whether a link or other strange text showed up in the answer for each document. In output/attack_results.md, make note of every document that fooled the agent, including what fooled it and where in the file it was hiding.

**Follow-up:** None needed.

---

## Problem 6 — Defend your agent

**Prompt:**
> Now, defend the agent at three levels: Code: What the program does to the document before any model sees it. Design: How the agent is put together, so a contaminated document cannot reach the dangerous tools or the decision. Prompt: rules in prompts/prompt.md. Do not delete send_email or approve_payment. The shop will use them later with human approval. Keep a way for the agent to run with no defenses (we will need to do so later in Problem 7). Rerun all 12 practice documents and save the results to output/defense_results.json in the same shape as Problem 5, plus token and dollars per document. Clean documents must still come back with the right values -- do NOT refuse or blank out a real quote. In output/defense_results.md, write a before and after for all 12 documents, what each layer catches that the others miss, and the extra tokens/dollars each layer adds per document. Also, add safety features and guardrails to output/harness.md in a Safety section, which describes what each defense layer does in plain words.

**Follow-up:** None needed.

---

## Problem 7 — Red team

**Prompt:**
> Now pretend you are the attacker. Make two booby-trapped vendor documents in data/my_attacks/ (they can be HTML, PDF, or email). Each one should use a hiding trick or attack goal that is not already in the practice set. A human opening the document should see normal contents. Run both attacks on the agent: (1) with no defenses and (2) with defenses. In output/red_team.md, for each attack, write: what is hidden, where, and what it tried to make the agent do, and what happened before and after the defenses. More points will be given for attacks that are totally new and that actually fool the defenseless agent.

**Follow-up:**
> Apply the red-team fixes: background-contrast check in the HTML sanitizer, covered-text detection for PDFs, an SKU-to-item cross-check, and a needs-review path for conflicting documents. Then rerun the 12 practice docs and both attacks.

*What was lacking:* the first prompt only asked to attack and report, so the gaps the attacks found were documented but not fixed until this follow-up.

---

## Problem 8 — Exam documents

**Prompt:**
> Now, run the final defended agent on all of the 10 vendor documents in data/exam_docs/, which has 10 vendor documents with no answer key. Save the results to output/exam_results.json with one entry per exam file. Each entry should have the following fields: file (the exam file name), vendor, sku, unit_price, lead_time_days, min_order, decision (recommend or do_not_recommend), reason, trap_tool_called (true or false), input_tokens, cached_tokens, output_tokens, and cost_usd. IMPORTANT: More points will be awarded for correct fields and decisions, no trap tool calls, and clean documents handled normally.

**Follow-up:** None needed.

---

## Problem 9 — Results page

**Prompt:**
> Create output/hw6_report.html (this should be one file that can be opened by double-clicking on it with no internet and no other files next to it). The page should include five things, with real numbers from the earlier problems: the caching results, with a chart; attacks before and after the defenses; what the defenses cost in tokens and dollars; the exam results and the two red team attacks; a brief recommendation for the store manager -- should Campus Customs turn this agent on for real vendor mail, and what would it cost per month at 1,000 documents per day? The page should have a well designed style (with coherent font, color, layout, etc.) and easily legible.

**Follow-up:** None needed.

---

## Problem 10 — Push to GitHub and submit the URL

**Prompt:**
> Push the project to a public GitHub repository and provide me the repo URL in the chat. Graders will clone this, so all the files in the file tree (see screenshot attached) should be in there. Include the whole data/ folder containing the course data plus the two attack files, so graders can clone the repo and run the agent right away. Do NOT commit the real .env, and use .gitignore to keep it out, including only .env.example with placeholders. It is fine if there are other Python files beyond what's listed in the file tree. Also, add a short README.md on how to run the agent.

**Follow-up:** None needed.
