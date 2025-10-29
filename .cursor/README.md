# Cursor Agent Mode (C)

- Cursor should load `.cursor/prompts/timesheet_engine.system.md` as the default system context for timesheet files.
- When a file name matches `timesheet_*.txt` or the selected text starts with bullets, Cursor should suggest a rewrite using `timesheet_engine.user.md` with `{{raw}}` = the selected text.
- You approve the suggestion (no silent edits).
- To opt-out in a file, add `# TIMESHEET_ENGINE: OFF` at top.