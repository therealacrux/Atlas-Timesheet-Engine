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

## Approval Mode (Review before Sending)
- By default, both the CLI and the scheduler script pause for your approval before delivering or clearing `examples/raw.txt`.
- You’ll see the proposed Markdown output in your terminal; approve or reject interactively.
- To skip approval (auto-send), add `--no-approval` to the CLI or `-Approval:$false` to the PowerShell script.

**Examples:**
```powershell
powershell -ExecutionPolicy Bypass -NoProfile -File scripts\schedule_timesheet.ps1 -UseOneNoteCom -SectionId "..."
# You’ll be asked: Approve and send these entries? [y/n]:

# To skip approval:
powershell -ExecutionPolicy Bypass -NoProfile -File scripts\schedule_timesheet.ps1 -UseOneNoteCom -SectionId "..." -Approval:$false
```

For ad-hoc/manual review with the CLI itself:
```bash
python cli/timesheet_rewriter.py examples/raw.txt --approval
# Output shown for approval. If approved, saves output; if not, nothing is sent/cleared.
```

---

## No‑cost Windows automation (recommended)
Avoids Power Automate premium HTTP connector. Two delivery options:

1) OneNote COM (no email; recommended if Email to OneNote is blocked)
- Uses the desktop OneNote COM API to create a page directly in your section.
- You need your Section ID. Example from this repo: `1401C2E5-CA97-41F7-BFC6-55C1BF00853D`.
- Test now:
```powershell
# Put bullets in examples\raw.txt first
powershell -ExecutionPolicy Bypass -NoProfile -File scripts\schedule_timesheet.ps1 `
  -UseOneNoteCom:$true -SectionId "1401C2E5-CA97-41F7-BFC6-55C1BF00853D"
```
- Register daily task at 7 PM (still works with COM):
```powershell
powershell -ExecutionPolicy Bypass -NoProfile -File scripts\register_timesheet_task.ps1
# Then edit the registered task action to add: -UseOneNoteCom:$true -SectionId "<YOUR_SECTION_ID>"
```

2) Email to OneNote (if available in your tenant)
- Configure destination at the OneNote Email Settings page if reachable.
- One-liner task registration (default):
```powershell
powershell -ExecutionPolicy Bypass -NoProfile -File scripts\register_timesheet_task.ps1 `
  -TaskName "AtlasTimesheetDaily" -RunTime "19:00" -OneNoteRecipient "me@onenote.com"
```

What the scheduled script does
- Reads raw bullets from `examples/raw.txt`
- Runs the CLI to rewrite entries (local heuristics by default)
- Delivers either via OneNote COM (SectionId) or email to OneNote
- Clears `examples/raw.txt` after a successful send

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