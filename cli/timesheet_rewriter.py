import os, re, sys, argparse
from typing import List, Optional

try:
	# Optional dependency; only needed if using --model
	from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover
	OpenAI = None  # type: ignore

try:
	import pyperclip  # type: ignore
except Exception:  # pragma: no cover
	pyperclip = None  # type: ignore

CLIENT_CODES = {"TCG": "TCG", "NR": "NR", "KOBOLD": "KOBOLD", "KB": "KOBOLD"}

def guess_client(text):
	for code in CLIENT_CODES:
		if re.search(rf"\b{code}\b", text, re.I):
			return CLIENT_CODES[code]
	return ""

def rewrite_line(line):
	raw = line.strip("-• ").strip()
	if not raw:
		return ""
	client = guess_client(raw)
	body = re.sub(r"\s*[-–—]\s*(TCG|NR|KOBOLD|KB)\s*$", "", raw, flags=re.I)
	lower = body.lower()

	if "printer" in lower or "toner" in lower:
		detail = "found a toner spill" if "spill" in lower or "magenta" in lower else "identified a device fault"
		action = "Contained the mess and scheduled vendor service" if "vendor" in lower else "Performed remediation and confirmed functionality"
		return f"Responded to a printer issue; {detail}. {action}.{' – ' + client if client else ''}"

	if "onboard" in lower or "orientation" in lower:
		who = re.findall(r"(?:for|with)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", body)
		who = who[0] if who else "the new hire"
		return f"Completed new-hire onboarding for {who}. Configured workstation, core apps (Zoom/Slack/Outlook/Adobe), and MFA; confirmed readiness.{' – ' + client if client else ''}"

	if "slack" in lower and ("invite" in lower or "re-invit" in lower or "reinv" in lower):
		who = re.findall(r"(?:for|with)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", body)
		who = who[0] if who else "the user"
		return f"Reinstated {who} in Slack. Confirmed access and restored collaboration.{' – ' + client if client else ''}"

	if "trace" in lower or ("email" in lower and ("search" in lower or "delivery" in lower or "delivered" in lower)):
		who = re.findall(r"for\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", body)
		who = who[0] if who else "the user"
		return f"Verified delivery of the referenced email for {who} and guided broader search across mailbox folders.{' – ' + client if client else ''}"

	if "backup" in lower or "cloudally" in lower or "restore" in lower:
		who = re.findall(r"for\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", body)
		who = who[0] if who else "the user"
		platform = "CloudAlly" if "cloudally" in lower else "backup platform"
		return f"Recovered the requested file via {platform} and restored {who}'s access; verified integrity.{' – ' + client if client else ''}"

	if "webcam" in lower or "ordered" in lower or "procured" in lower or "purchased" in lower:
		item = "webcams"
		vendor = "Amazon" if "amazon" in lower else "vendor"
		purpose = "video conferencing"
		return f"Procured {item} via {vendor} to support {purpose}.{' – ' + client if client else ''}"

	if "received" in lower and ("laptop" in lower or "device" in lower or "equipment" in lower or "updated the spreadsheet" in lower):
		who = re.findall(r"for\s+([A-Z][a-z]+.*)", body)
		who = who[0] if who else "incoming devices"
		who = re.sub(r"and updated.*", "", who).strip(", ")
		return f"Received and logged equipment for {who}. Updated inventory records for accurate tracking.{' – ' + client if client else ''}"

	if "bluetooth" in lower or "keyboard" in lower or "mouse" in lower:
		who = re.findall(r"help(?:ed)?\s+([A-Z][a-z]+)", body)
		who = who[0] if who else "the user"
		return f"Assisted {who} with keyboard/mouse connectivity. Re-enabled Bluetooth, re-paired devices, and rebooted to confirm stability.{' – ' + client if client else ''}"

	body = body.rstrip(".")
	return f"{body}.{' – ' + client if client else ''}"


def read_text_from_file(path: str) -> str:
	with open(path, "r", encoding="utf-8") as f:
		return f.read()


def write_text_to_file(path: str, text: str) -> None:
	with open(path, "w", encoding="utf-8") as f:
		f.write(text)


def split_lines(raw_text: str) -> List[str]:
	return [l for l in raw_text.splitlines() if l.strip()]


def rewrite_locally(raw_text: str) -> str:
	lines = split_lines(raw_text)
	outputs = [rewrite_line(l) for l in lines]
	outputs = [o for o in outputs if o]
	return "\n".join(outputs) + ("\n" if outputs else "")


def load_prompt(prompt_path: str) -> str:
	try:
		return read_text_from_file(prompt_path)
	except FileNotFoundError:
		return ""


def rewrite_with_openai(raw_text: str, prompt_text: str, model: str, temperature: float = 0.2) -> str:
	if OpenAI is None:
		raise RuntimeError("openai package not installed. Install and set OPENAI_API_KEY, or omit --model.")
	api_key = os.getenv("OPENAI_API_KEY")
	if not api_key:
		raise RuntimeError("OPENAI_API_KEY is not set. Set it in your environment or .env file.")

	client = OpenAI(api_key=api_key)
	system_msg = "You are the Atlas Timesheet Engine. Follow the style and templates exactly. Do not add timestamps."
	user_msg = f"{prompt_text}\n\nRAW:\n{raw_text}"
	resp = client.chat.completions.create(
		model=model,
		temperature=temperature,
		messages=[
			{"role": "system", "content": system_msg},
			{"role": "user", "content": user_msg},
		],
	)
	content = resp.choices[0].message.content if resp and resp.choices else ""
	return (content or "").strip() + ("\n" if content else "")


def get_clipboard_text() -> str:
	if pyperclip is None:
		raise RuntimeError("pyperclip is not installed. Install it or omit --from-clipboard.")
	return pyperclip.paste() or ""


def set_clipboard_text(text: str) -> None:
	if pyperclip is None:
		raise RuntimeError("pyperclip is not installed. Install it or omit --to-clipboard.")
	pyperclip.copy(text)


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
	p = argparse.ArgumentParser(description="Atlas Timesheet Engine: rewrite raw bullets into client-facing entries")
	src = p.add_mutually_exclusive_group(required=False)
	src.add_argument("input", nargs="?", help="Path to raw.txt (default: read from stdin if not provided)")
	src.add_argument("--from-clipboard", action="store_true", dest="from_clipboard", help="Read raw text from clipboard")

	p.add_argument("--out", dest="out", default=None, help="Write output to file path")
	p.add_argument("--to-clipboard", action="store_true", dest="to_clipboard", help="Copy output to clipboard")
	p.add_argument("--model", dest="model", default=None, help="OpenAI model name (e.g., gpt-4o-mini). If omitted, use local heuristics.")
	p.add_argument("--prompt", dest="prompt", default="prompt/timesheet_engine_prompt.md", help="Path to prompt md file for LLM mode")
	p.add_argument("--temperature", type=float, default=0.2, help="Temperature for model mode")
	p.add_argument("--default-client", dest="default_client", default=None, help="Default client code to append when not detected (e.g., TCG, NR, KOBOLD)")

	return p.parse_args(argv)


def apply_default_client(text: str, default_client: Optional[str]) -> str:
	if not default_client:
		return text
	code = CLIENT_CODES.get(default_client.upper())
	if not code:
		return text
	lines = split_lines(text)
	finalized: List[str] = []
	for l in lines:
		if re.search(r"\s[-–—]\s([A-Z]{2,})\s$", l):
			finalized.append(l)
		else:
			finalized.append(f"{l} – {code}")
	return "\n".join(finalized) + ("\n" if finalized else "")


def main(argv: Optional[List[str]] = None) -> None:
	args = parse_args(argv)

	# Acquire input text
	if args.from_clipboard:
		raw_text = get_clipboard_text()
	elif args.input:
		raw_text = read_text_from_file(args.input)
	else:
		raw_text = sys.stdin.read()

	raw_text = raw_text.strip("\ufeff")  # strip BOM if present

	# Produce output
	if args.model:
		prompt_text = load_prompt(args.prompt)
		try:
			out_text = rewrite_with_openai(raw_text, prompt_text, model=args.model, temperature=args.temperature)
		except Exception:
			# Fallback to local if LLM fails
			out_text = rewrite_locally(raw_text)
	else:
		out_text = rewrite_locally(raw_text)

	if args.default_client:
		out_text = apply_default_client(out_text, args.default_client)

	# Emit output
	if args.out:
		write_text_to_file(args.out, out_text)
	if args.to_clipboard:
		set_clipboard_text(out_text)

	# Always print to stdout for chaining
	sys.stdout.write(out_text)

if __name__ == "__main__":
	main()