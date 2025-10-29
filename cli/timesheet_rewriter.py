import os, re, sys

CLIENT_CODES = {"TCG": "TCG", "NR": "NR"}

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
    body = re.sub(r"\s*[-–—]\s*(TCG|NR)\s*$", "", raw, flags=re.I)
    lower = body.lower()

    if "printer" in lower or "toner" in lower:
        detail = "found a toner spill" if "spill" in lower or "magenta" in lower else "identified a device fault"
        action = "Contained the mess and scheduled vendor service" if "vendor" in lower else "Performed remediation and confirmed functionality"
        return f"Responded to a printer issue; {detail}. {action}.{' – ' + client if client else ''}"

    if "onboard" in lower or "orientation" in lower:
        who = re.findall(r"(?:for|with)\\s+([A-Z][a-z]+(?:\\s+[A-Z][a-z]+)*)", body)
        who = who[0] if who else "the new hire"
        return f"Completed new-hire onboarding for {who}. Configured workstation, core apps (Zoom/Slack/Outlook/Adobe), and MFA; confirmed readiness.{' – ' + client if client else ''}"

    if "slack" in lower and ("invite" in lower or "re-invit" in lower or "reinv" in lower):
        who = re.findall(r"(?:for|with)\\s+([A-Z][a-z]+(?:\\s+[A-Z][a-z]+)*)", body)
        who = who[0] if who else "the user"
        return f"Reinstated {who} in Slack. Confirmed access and restored collaboration.{' – ' + client if client else ''}"

    if "trace" in lower or ("email" in lower and ("search" in lower or "delivery" in lower or "delivered" in lower)):
        who = re.findall(r"for\\s+([A-Z][a-z]+(?:\\s+[A-Z][a-z]+)*)", body)
        who = who[0] if who else "the user"
        return f"Verified delivery of the referenced email for {who} and guided broader search across mailbox folders.{' – ' + client if client else ''}"

    if "backup" in lower or "cloudally" in lower or "restore" in lower:
        who = re.findall(r"for\\s+([A-Z][a-z]+(?:\\s+[A-Z][a-z]+)*)", body)
        who = who[0] if who else "the user"
        platform = "CloudAlly" if "cloudally" in lower else "backup platform"
        return f"Recovered the requested file via {platform} and restored {who}'s access; verified integrity.{' – ' + client if client else ''}"

    if "webcam" in lower or "ordered" in lower or "procured" in lower or "purchased" in lower:
        item = "webcams"
        vendor = "Amazon" if "amazon" in lower else "vendor"
        purpose = "video conferencing"
        return f"Procured {item} via {vendor} to support {purpose}.{' – ' + client if client else ''}"

    if "received" in lower and ("laptop" in lower or "device" in lower or "equipment" in lower or "updated the spreadsheet" in lower):
        who = re.findall(r"for\\s+([A-Z][a-z]+.*)", body)
        who = who[0] if who else "incoming devices"
        who = re.sub(r"and updated.*", "", who).strip(", ")
        return f"Received and logged equipment for {who}. Updated inventory records for accurate tracking.{' – ' + client if client else ''}"

    if "bluetooth" in lower or "keyboard" in lower or "mouse" in lower:
        who = re.findall(r"help(?:ed)?\\s+([A-Z][a-z]+)", body)
        who = who[0] if who else "the user"
        return f"Assisted {who} with keyboard/mouse connectivity. Re-enabled Bluetooth, re-paired devices, and rebooted to confirm stability.{' – ' + client if client else ''}"

    body = body.rstrip(".")
    return f"{body}.{' – ' + client if client else ''}"

def main():
    if len(sys.argv) < 2:
        print("Usage: python cli/timesheet_rewriter.py <raw.txt> [out.txt]")
        raise SystemExit(1)
    inp = sys.argv[1]
    outp = sys.argv[2] if len(sys.argv) > 2 else "examples/output.txt"
    with open(inp, "r", encoding="utf-8") as f:
        lines = [l for l in f.read().splitlines() if l.strip()]
    outputs = [rewrite_line(l) for l in lines]
    outputs = [o for o in outputs if o]
    text = "\\n".join(outputs) + "\\n"
    with open(outp, "w", encoding="utf-8") as f:
        f.write(text)
    print(text)

if __name__ == "__main__":
    main()