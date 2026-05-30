#!/usr/bin/env python3
"""
cv_diagnose.py - Step 01: See your résumé the way an ATS parses it
Usage:
  python cv_diagnose.py                    # uses default cv_master.txt
  python cv_diagnose.py --cv path/to/cv.txt
"""

import argparse
import os
import sys

import anthropic

CV_DEFAULT = "cv_master.txt"

SYSTEM_PROMPT = """\
You are an ATS (Applicant Tracking System) expert and career strategist. Your job is to \
analyse a résumé exactly as a modern ATS would — then translate that into actionable feedback.

Produce a structured diagnostic report with these sections:

## ATS PARSE SCORE  /100
Give an overall ATS compatibility score. Brief justification (2-3 lines).

## AUTO-REJECT TRIGGERS
List any elements that commonly cause instant rejection:
- Unreadable formatting (tables, text boxes, headers/footers, columns)
- Missing contact info or unparseable email/phone
- Non-standard section headings the ATS won't recognise
- Date format inconsistencies
- Graphics, icons, or photos
- File-type issues (assume .txt input but flag if you see signs of PDF artefacts)
Format each as: "⚠ [Issue] — [Why it matters]"
If none, write "✓ No auto-reject triggers detected."

## KEYWORD DENSITY
List the top 10 keywords/phrases present in the CV, with approximate frequency.
Then flag 3-5 generic filler phrases that dilute keyword signal (e.g. "team player", \
"results-oriented").

## STRUCTURE & SECTIONS
Score each standard section (Present / Missing / Weak):
- Contact Info
- Summary / Objective
- Work Experience
- Education
- Skills
- Certifications / Awards (optional)
Briefly note what's weak and why.

## TOP 5 QUICK WINS
Concrete, specific changes that would raise the ATS score most — ordered by impact.
Format: "1. [Action] → [Expected gain]"

Keep the tone direct and diagnostic. No filler.
"""


def read_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"Error reading {path}: {e}", file=sys.stderr)
        sys.exit(1)


def diagnose(cv_text: str) -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    user_message = f"Please run a full ATS diagnostic on this résumé:\n\n{cv_text}"

    print("\n" + "=" * 60)
    print("ATS DIAGNOSTIC REPORT")
    print("=" * 60 + "\n")

    try:
        with client.messages.stream(
            model="claude-opus-4-6",
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        ) as stream:
            for text in stream.text_stream:
                print(text, end="", flush=True)

        final = stream.get_final_message()
        print(f"\n\n{'─' * 60}")
        print(f"Tokens used — input: {final.usage.input_tokens}, output: {final.usage.output_tokens}")

    except anthropic.AuthenticationError:
        print("Error: Invalid API key.", file=sys.stderr)
        sys.exit(1)
    except anthropic.RateLimitError:
        print("Error: Rate limit hit. Please wait a moment and try again.", file=sys.stderr)
        sys.exit(1)
    except anthropic.APIConnectionError:
        print("Error: Could not connect to the Anthropic API.", file=sys.stderr)
        sys.exit(1)
    except anthropic.APIStatusError as e:
        print(f"API error ({e.status_code}): {e.message}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Step 01 — Diagnose: See your résumé the way an ATS parses it"
    )
    parser.add_argument(
        "--cv",
        default=CV_DEFAULT,
        metavar="FILE",
        help=f"Path to your CV text file (default: {CV_DEFAULT})",
    )
    args = parser.parse_args()

    cv_text = read_file(args.cv)
    if not cv_text:
        print(f"Error: CV file '{args.cv}' is empty.", file=sys.stderr)
        sys.exit(1)

    diagnose(cv_text)


if __name__ == "__main__":
    main()
