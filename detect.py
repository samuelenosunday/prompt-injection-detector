"""
Prompt Injection Detector
=========================
Rule-based detection of common prompt injection patterns.

Author: Samuel Eno Sunday
License: MIT
"""

import sys
import re
from pathlib import Path


# ---------------------------------------------------------
# PATTERN DEFINITIONS
# ---------------------------------------------------------

PATTERNS = {
    "Instruction Override": [
        r"ignore\s+(all\s+)?(previous|prior|above|earlier)\s+(instructions?|prompts?|rules?)",
        r"disregard\s+(all\s+)?(previous|prior|above)\s+(instructions?|rules?)",
        r"forget\s+(everything|all|your)\s+(above|before|previous|instructions?)",
        r"override\s+(your\s+)?(instructions?|programming|safety)",
    ],
    "System Prompt Extraction": [
        r"(repeat|show|print|reveal|output|tell\s+me)\s+(your|the)\s+(system\s+)?(prompt|instructions?|rules?)",
        r"what\s+(were|are)\s+you\s+(told|instructed)",
        r"what\s+is\s+your\s+(system\s+)?prompt",
        r"print\s+the\s+first\s+instruction",
    ],
    "Role-Play Jailbreak": [
        r"pretend\s+(you\s+are|to\s+be)",
        r"you\s+are\s+now\s+(an?\s+)?(unrestricted|unfiltered|jailbroken|DAN)",
        r"act\s+as\s+(an?\s+)?(unrestricted|unfiltered|evil)",
        r"jailbreak\s+mode",
        r"do\s+anything\s+now",
    ],
    "Delimiter Attack": [
        r"<\|?\s*endoftext\s*\|?>",
        r"<\|?\s*system\s*\|?>",
        r"###\s*SYSTEM\s*###",
        r"---\s*END\s+OF\s+(PROMPT|SYSTEM)\s*---",
        r"\[/INST\]",
        r"<<SYS>>",
    ],
    "Encoded Payload": [
        r"<script[^>]*>",
        r"\\u0000",
        r"(?:[A-Za-z0-9+/]{40,}={0,2})",
        r"(?:0x)?[0-9a-fA-F]{32,}",
    ],
}


# ---------------------------------------------------------
# DETECTION LOGIC
# ---------------------------------------------------------

def scan_prompt(prompt):
    """
    Scan a prompt for injection patterns.
    Returns a dict with: score, risk_level, matches.
    """
    matches = []

    for category, patterns in PATTERNS.items():
        for pattern in patterns:
            m = re.search(pattern, prompt, re.IGNORECASE)
            if m:
                matches.append({
                    "category": category,
                    "matched_text": m.group(0),
                })
                break

    score = min(len(matches) * 20, 100)

    if score == 0:
        risk = "LOW RISK"
    elif score < 50:
        risk = "MEDIUM RISK"
    else:
        risk = "HIGH RISK"

    return {
        "score": score,
        "risk_level": risk,
        "matches": matches,
    }


# ---------------------------------------------------------
# REPORTING
# ---------------------------------------------------------

def print_scan(prompt, result):
    print("=" * 50)
    print("PROMPT INJECTION SCAN")
    print("=" * 50)
    print(f'Prompt: "{prompt}"\n')
    print(f"Risk score: {result['score']}/100  {result['risk_level']}\n")

    if result["matches"]:
        print("Detected categories:")
        for m in result["matches"]:
            print(f"  - {m['category']}  (matched: \"{m['matched_text']}\")")
    else:
        print("No injection patterns detected.")

    print()


# ---------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------

def main():
    if len(sys.argv) > 1:
        filepath = Path(sys.argv[1])
        if not filepath.exists():
            print(f"Error: File not found -> {filepath}")
            sys.exit(1)

        prompts = [
            line.strip()
            for line in filepath.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        print(f"Scanning {len(prompts)} prompt(s) from {filepath}\n")
        for p in prompts:
            print_scan(p, scan_prompt(p))
        return

    print("Prompt Injection Detector (type 'exit' to quit)\n")
    while True:
        try:
            prompt = input("Enter a prompt to scan:\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
        if prompt.lower() in {"exit", "quit"}:
            print("Exiting.")
            break
        if not prompt:
            continue
        print_scan(prompt, scan_prompt(prompt))


if __name__ == "__main__":
    main()
