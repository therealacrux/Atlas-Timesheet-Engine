# Atlas Timesheet Engine

**Goal**: Convert raw OneNote notes into clean, client‑facing timesheet entries in a consistent “Cobaltix tone” (confident, concise, lightly witty), then auto‑publish the results to OneNote at 7 PM PT via Power Automate.

## Outcomes
- Polished, consistent entries across clients (e.g., TCG, NR)
- Minimal manual rewriting time
- Local CLI + Cloud automation

## Components
- **Prompt**: `/prompt/timesheet_engine_prompt.md`
- **Flow guide**: `/flow/power_automate_instructions.md`
- **CLI**: `/cli/timesheet_rewriter.py`
- **Examples**: `/examples/*`
- **Cursor Agent Mode**: Auto‑rewrite on paste using `/ .cursor/prompts/*`

## Usage

### A) Local CLI (offline)
1. Put your bullets in `examples/raw.txt` (one per line).
2. Run:
   ```bash
   python cli/timesheet_rewriter.py examples/raw.txt examples/output.txt
   ```

### B) Power Automate (7 PM daily)
Follow `/flow/power_automate_instructions.md` to build:
Recurrence → Get OneNote → HTML→Text → HTTP→OpenAI → Create OneNote page.

### C) Cursor Agent Mode (auto on paste)
- When Cursor detects a block of raw bullets in any text file, it will suggest a rewrite using the Timesheet Engine prompt.
- You control acceptance. The rules live in `/.cursor/prompts/`.

## Guardrails
- No invented work; keep to provided facts.
- Action → result → confirmation; 1–3 sentences per entry.
- End each entry with client suffix (e.g., `– TCG`, `– NR`).
- Avoid passive “resolved issue”; be concrete and human.

## Roadmap
- Tag extraction (PRINTER/ONBOARDING/EMAIL TRACE)
- Per‑client expansions
- Unit tests for the CLI heuristics