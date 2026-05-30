#!/usr/bin/env python3
"""
cv_rewrite.py - Step 03: Rebuild every bullet on the XYZ formula
               Accomplished [X], as measured by [Y], by doing [Z].
Usage:
  python cv_rewrite.py                        # uses default cv_master.txt, interactive
  python cv_rewrite.py --cv path/to/cv.txt
  python cv_rewrite.py --jd "job desc text"   # target rewrites to a specific role
  python cv_rewrite.py --jd-file jd.txt
"""

import argparse
import os
import sys

import anthropic

CV_DEFAULT = "cv_master.txt"

SYSTEM_PROMPT = """\
You are an expert résumé writer who specialises in the XYZ bullet formula:
"Accomplished [X], as measured by [Y], by doing [Z]."

This formula forces every bullet to have:
- X: the outcome or result
- Y: a quantified metric that proves the result
- Z: the method or action taken

Your task: take every experience bullet from the provided CV and rewrite it in XYZ format.

Rules:
1. Keep the content truthful — do NOT invent metrics. If a metric is missing, write it as
   [METRIC NEEDED: e.g. "% improvement", "$ saved", "N users"] so the candidate knows what
   to fill in.
2. Use strong, specific action verbs. No "responsible for" or "helped with".
3. If a job description is provided, prioritise rewrites that surface the most relevant
   skills for that role.
4. Output format for each bullet:
   ORIGINAL: <original bullet text>
   REWRITTEN: <XYZ rewrite>
   (blank line between entries)
5. After all bullets, add a short section "## METRIC GAPS" listing any bullets where you
   inserted a placeholder, so the candidate knows exactly what data to hunt down.

Do not rewrite non-bullet content (headers, dates, education degrees, etc.).
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


def read_job_description_interactively() -> str:
    print("Paste the job description below (optional — press Ctrl+D to skip).")
    print("When done, press Enter then Ctrl+D (Linux/Mac) or Ctrl+Z then Enter (Windows):")
    print("-" * 60)
    try:
        lines = sys.stdin.read()
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(0)
    return lines.strip()


def rewrite(cv_text: str, job_description: str = "") -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    user_message = f"## CV\n\n{cv_text}"
    if job_description:
        user_message += f"\n\n---\n\n## Target Job Description\n\n{job_description}"
    user_message += "\n\n---\n\nPlease rewrite every experience bullet using the XYZ formula."

    print("\n" + "=" * 60)
    print("XYZ BULLET REWRITE")
    print("=" * 60 + "\n")

    try:
        with client.messages.stream(
            model="claude-opus-4-6",
            max_tokens=4096,
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
        description="Step 03 — Rewrite: Rebuild every bullet on the XYZ formula"
    )
    parser.add_argument(
        "--cv",
        default=CV_DEFAULT,
        metavar="FILE",
        help=f"Path to your CV text file (default: {CV_DEFAULT})",
    )
    parser.add_argument(
        "--jd",
        metavar="TEXT",
        help="Job description to target rewrites (optional)",
    )
    parser.add_argument(
        "--jd-file",
        metavar="FILE",
        help="Path to a file containing the job description (optional)",
    )
    parser.add_argument(
        "--no-jd",
        action="store_true",
        help="Skip job description prompt and rewrite generically",
    )
    args = parser.parse_args()

    cv_text = read_file(args.cv)
    if not cv_text:
        print(f"Error: CV file '{args.cv}' is empty.", file=sys.stderr)
        sys.exit(1)

    job_description = ""
    if args.jd:
        job_description = args.jd.strip()
    elif args.jd_file:
        job_description = read_file(args.jd_file)
    elif not args.no_jd:
        job_description = read_job_description_interactively()

    rewrite(cv_text, job_description)


if __name__ == "__main__":
    main()
