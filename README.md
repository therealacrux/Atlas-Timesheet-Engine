# Atlas Timesheet Engine

**Goal**: Convert raw OneNote notes into clean, client‑facing timesheet entries in a consistent “Cobaltix tone” (confident, concise, lightly witty), then auto‑publish the results to OneNote at 7 PM PT via Power Automate.

## Outcomes
- Polished, consistent entries across clients (e.g., TCG, NR, KOBOLD)
- Minimal manual rewriting time
- Local CLI + Cloud automation

## Components
- **Prompt**: `/prompt/timesheet_engine_prompt.md`
- **Flow guide**: `/flow/power_automate_instructions.md`
- **CLI**: `/cli/timesheet_rewriter.py`
- **Examples**: `/examples/*`
- **Cursor Agent Mode**: Auto‑rewrite on paste using `/ .cursor/prompts/*`

## Setup

```bash
# Optional: enable model-powered rewriting and clipboard support
pip install -r requirements.txt
# Set your key if using model mode
# PowerShell
$env:OPENAI_API_KEY = "sk-..."
# or mac/linux
export OPENAI_API_KEY="sk-..."
```

## Usage

### A) Zero-typing clipboard workflow
- Copy your raw bullets (one per line) to the clipboard
- Run and get rewritten entries back into the clipboard:
```bash
python cli/timesheet_rewriter.py --from-clipboard --to-clipboard --default-client KOBOLD
```
Paste directly into OneNote.

### B) File or stdin → stdout (local heuristics)
```bash
python cli/timesheet_rewriter.py examples/raw.txt
# or
type examples\raw.txt | python cli\timesheet_rewriter.py
```

### C) LLM mode (prompt + model) with fallback to local
```bash
python cli/timesheet_rewriter.py --from-clipboard --to-clipboard \
  --model gpt-4o-mini --prompt prompt/timesheet_engine_prompt.md --default-client KOBOLD
```
- If the API call fails or no key is set, it automatically falls back to the local heuristics.

### D) Power Automate (7 PM daily)
Follow `/flow/power_automate_instructions.md` to build:
Recurrence → Get OneNote → HTML→Text → HTTP→OpenAI → Create OneNote page.

### E) Cursor Agent Mode (auto on paste)
- When Cursor detects a block of raw bullets in any text file, it will suggest a rewrite using the Timesheet Engine prompt.
- You control acceptance. The rules live in `/.cursor/prompts/`.

## Guardrails
- No invented work; keep to provided facts.
- Action → result → confirmation; 1–3 sentences per entry.
- End each entry with client suffix (e.g., `– TCG`, `– NR`, `– KOBOLD`).
- Avoid passive “resolved issue”; be concrete and human.

## Notes on client codes
- Auto-detection supports: `TCG`, `NR`, `KOBOLD`, `KB`.
- Use `--default-client <CODE>` to append a client code when not present in a line.

## Roadmap
- Tag extraction (PRINTER/ONBOARDING/EMAIL TRACE)
- Per‑client expansions (add tone and templates per client)
- Unit tests for the CLI heuristics