# Campus Customs vendor desk agent: MGT 409 Homework 6

Everything is in **[`hw6/`](hw6/)**: a PydanticAI agent (`gpt-6-luna` via Portkey) that reads vendor quotes, invoices, catalog pages, and emails and recommends whether Campus Customs should buy. The homework measures its token cost with and without prompt caching, attacks it with booby-trapped documents, and defends it at three layers (code, design, prompt).

- How to set up and run: [`hw6/README.md`](hw6/README.md)
- Results page (open in a browser, works offline): [`hw6/output/hw6_report.html`](hw6/output/hw6_report.html)
- How it works, including the Safety section: [`hw6/output/harness.md`](hw6/output/harness.md)

The whole `hw6/data/` folder is included: the course data pack plus the two red-team attack files in `hw6/data/my_attacks/`. The real `.env` is not. Copy `hw6/.env.example` to `hw6/.env` and add your key.
