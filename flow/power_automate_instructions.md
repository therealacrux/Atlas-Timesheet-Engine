# Power Automate — HTTP → OpenAI (7 PM PT)

## Prereqs
- Environment variable: `OPENAI_API_KEY` (stores your key securely).
- Scratchpad OneNote Page ID: `1-1401c2e5-ca97-41f7-bfc6-55c1bf00853d`.

## Steps
1) **Recurrence**
   - Every day, 7:00 PM
   - Time zone: America/Los_Angeles

2) **OneNote (Business) → Get page content**
   - Page Id: `1-1401c2e5-ca97-41f7-bfc6-55c1bf00853d`

3) **Content Conversion → HTML to text**
   - Content: `@{body('Get_page_content')}`
   - Output: `Html_to_text`

4) **Compose → Timesheet_Engine_Prompt**
   - Paste the contents of `/prompt/timesheet_engine_prompt.md`.

5) **Compose → Prompt_plus_RAW**
   ```
   @{concat(outputs('Timesheet_Engine_Prompt'), '\n\nRAW:\n', outputs('Html_to_text'))}
   ```

6) **HTTP (Premium) → POST** `https://api.openai.com/v1/chat/completions`
   - Headers:
     - `Authorization`: `Bearer @{variables('OPENAI_API_KEY')}`
     - `Content-Type`: `application/json`
   - Body:
   ```json
   {
     "model": "gpt-4o-mini",
     "temperature": 0.2,
     "messages": [
       { "role": "system", "content": "You are the Atlas Timesheet Engine. Follow the style and templates exactly. Do not add timestamps." },
       { "role": "user", "content": "@{outputs('Prompt_plus_RAW')}" }
     ]
   }
   ```

7) **Compose → Final_Text**
   Expression:
   ```
   @{body('HTTP')?['choices']?[0]?['message']?['content']}
   ```

8) **Compose → Page_Title**
   ```
   @{concat('Timesheet ', formatDateTime(utcNow(), 'yyyy-MM-dd'))}
   ```

9) **OneNote (Business) → Create page**
   - Notebook: `Timesheets`
   - Section: `Daily Entries`
   - Title: `@{outputs('Page_Title')}`
   - Content: If OneNote requires HTML, wrap it:
   ```
   @{concat('<html><body><pre style="font-family:Consolas,monospace;white-space:pre-wrap;">', 
   replace(outputs('Final_Text'), '&','&amp;'),
   '</pre></body></html>')}
   ```

## Notes
- If the HTTP response needs parsing, insert **Parse JSON** (use a sample response).
- Model can be swapped; `gpt-4o-mini` is cost‑efficient and sharp.
- To append to an existing page instead, use the **Append content** action.