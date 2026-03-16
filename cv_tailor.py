#!/usr/bin/env python3
"""
cv_tailor.py - Tailor your CV to a job description using Claude
Usage:
  python cv_tailor.py                        # interactive: paste job description
  python cv_tailor.py --jd "job desc text"   # inline job description
  python cv_tailor.py --jd-file path.txt     # job description from file
  python cv_tailor.py --cv path/to/cv.txt    # specify CV file (default: cv_master.txt)
"""

import argparse
import os
import sys

import anthropic

CV_DEFAULT = "cv_master.txt"

SYSTEM_PROMPT = """\
You are an expert career coach and resume writer. You help job seekers tailor their CVs
to specific job descriptions to maximise their chances of getting an interview.

When given a CV and a job description, you produce a concise, actionable analysis with
two clearly separated sections:

1. **Tailored Bullet Points to Emphasise**
   - List 5-8 existing achievements or skills from the CV that best match this role.
   - Rewrite each as a punchy, metric-driven bullet point optimised for ATS systems.
   - Format: "• [Original context] → [Tailored version]"

2. **Missing Keywords & Gaps**
   - List keywords, tools, certifications, or skills that appear in the job description
     but are absent (or under-represented) in the CV.
   - For each gap, suggest a brief strategy: add a project, get a cert, or simply surface
     an implied skill.
   - Format: "• [Keyword/skill] — [Suggestion]"

Keep the tone professional and direct. No fluff.
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
    print("Paste the job description below.")
    print("When done, press Enter then Ctrl+D (Linux/Mac) or Ctrl+Z then Enter (Windows):")
    print("-" * 60)
    try:
        lines = sys.stdin.read()
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(0)
    return lines.strip()


def tailor_cv(cv_text: str, job_description: str) -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set.", file=sys.stderr)
        print("Set it with: export ANTHROPIC_API_KEY=your_key_here", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    user_message = f"""\
## My CV

{cv_text}

---

## Job Description

{job_description}

---

Please provide:
1. Tailored bullet points to emphasise from my CV for this specific role.
2. Missing keywords and gaps I should address.
"""

    print("\n" + "=" * 60)
    print("CV TAILORING ANALYSIS")
    print("=" * 60 + "\n")

    try:
        with client.messages.stream(
            model="claude-opus-4-6",
            max_tokens=2048,
            thinking={"type": "adaptive"},
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        ) as stream:
            in_thinking = False
            for event in stream:
                if event.type == "content_block_start":
                    if event.content_block.type == "thinking":
                        in_thinking = True
                        print("[Analysing…]", flush=True)
                    elif event.content_block.type == "text":
                        if in_thinking:
                            print()  # blank line after thinking indicator
                        in_thinking = False
                elif event.type == "content_block_delta":
                    if event.delta.type == "text_delta":
                        print(event.delta.text, end="", flush=True)

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
        print("Error: Could not connect to the Anthropic API. Check your internet connection.", file=sys.stderr)
        sys.exit(1)
    except anthropic.APIStatusError as e:
        print(f"API error ({e.status_code}): {e.message}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Tailor your CV to a job description using Claude AI"
    )
    parser.add_argument(
        "--cv",
        default=CV_DEFAULT,
        metavar="FILE",
        help=f"Path to your master CV text file (default: {CV_DEFAULT})",
    )
    parser.add_argument(
        "--jd",
        metavar="TEXT",
        help="Job description as a string",
    )
    parser.add_argument(
        "--jd-file",
        metavar="FILE",
        help="Path to a file containing the job description",
    )

    args = parser.parse_args()

    # Load CV
    cv_text = read_file(args.cv)
    if not cv_text:
        print(f"Error: CV file '{args.cv}' is empty.", file=sys.stderr)
        sys.exit(1)

    # Load job description
    if args.jd:
        job_description = args.jd.strip()
    elif args.jd_file:
        job_description = read_file(args.jd_file)
    else:
        job_description = read_job_description_interactively()

    if not job_description:
        print("Error: job description is empty.", file=sys.stderr)
        sys.exit(1)

    tailor_cv(cv_text, job_description)


if __name__ == "__main__":
    main()
