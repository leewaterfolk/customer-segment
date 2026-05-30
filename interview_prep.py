#!/usr/bin/env python3
"""
interview_prep.py - Step 04: Turn AI into the hiring manager
                    A real interview, the hardest questions in your field,
                    every answer scored out of 10.
Usage:
  python interview_prep.py                        # uses cv_master.txt, no JD
  python interview_prep.py --cv path/to/cv.txt
  python interview_prep.py --jd "job desc text"
  python interview_prep.py --jd-file jd.txt
  python interview_prep.py --rounds 5            # number of questions (default: 6)
"""

import argparse
import os
import sys

import anthropic

CV_DEFAULT = "cv_master.txt"
DEFAULT_ROUNDS = 6

SYSTEM_PROMPT = """\
You are a demanding but fair senior hiring manager conducting a real job interview.
You have read the candidate's CV and (if provided) the job description thoroughly.

Your interview style:
- Ask ONE question at a time. Never stack multiple questions.
- Start with a moderately tough behavioural question, then escalate to hard technical
  or situational questions as the interview progresses.
- After each answer, do TWO things:
  1. Score the answer out of 10, with a brief (2-3 line) rationale.
     Format: SCORE: X/10 — [rationale]
  2. Give one specific coaching tip to make the answer stronger.
     Format: TIP: [coaching note]
  Then ask the next question immediately.
- Use the STAR method (Situation, Task, Action, Result) as the benchmark for behavioural
  answers.
- Be specific to the candidate's background and the target role. No generic questions.
- If the candidate gives a vague or weak answer, probe once before scoring.

After all rounds are complete, produce a final summary:
## INTERVIEW SUMMARY
- Overall score: [average]/10
- Strongest answer: [question topic] — [why]
- Weakest answer: [question topic] — [why]
- Top 3 coaching priorities before the real interview

Stay in character as the hiring manager throughout. Do not break character.
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
        text = sys.stdin.read()
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(0)
    return text.strip()


def run_interview(cv_text: str, job_description: str, rounds: int) -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    context = f"## Candidate CV\n\n{cv_text}"
    if job_description:
        context += f"\n\n---\n\n## Target Role\n\n{job_description}"
    context += f"\n\n---\n\nConduct a {rounds}-question interview. Start with the first question now."

    messages = [{"role": "user", "content": context}]

    print("\n" + "=" * 60)
    print("INTERVIEW SIMULATION")
    if job_description:
        print("(targeted to provided job description)")
    print(f"{rounds} questions — every answer scored /10")
    print("=" * 60)
    print("\nType your answer after each question. Press Enter twice when done.")
    print("Type 'quit' to end early.\n")

    question_count = 0

    while question_count < rounds:
        print(f"\n{'─' * 60}")
        print(f"Question {question_count + 1} of {rounds}")
        print(f"{'─' * 60}\n")

        full_response = ""
        try:
            with client.messages.stream(
                model="claude-opus-4-6",
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                messages=messages,
            ) as stream:
                for text in stream.text_stream:
                    print(text, end="", flush=True)
                    full_response += text

            messages.append({"role": "assistant", "content": full_response})

        except anthropic.APIStatusError as e:
            print(f"\nAPI error ({e.status_code}): {e.message}", file=sys.stderr)
            sys.exit(1)
        except (anthropic.AuthenticationError, anthropic.RateLimitError, anthropic.APIConnectionError) as e:
            print(f"\nError: {e}", file=sys.stderr)
            sys.exit(1)

        question_count += 1

        if question_count >= rounds:
            break

        print("\n\nYour answer: ", end="", flush=True)
        answer_lines = []
        try:
            while True:
                line = input()
                if line.lower() == "quit":
                    print("\nEnding interview early...")
                    break
                if line == "" and answer_lines and answer_lines[-1] == "":
                    break
                answer_lines.append(line)
        except (EOFError, KeyboardInterrupt):
            print()
            break

        answer = "\n".join(answer_lines).strip()
        if not answer or answer.lower() == "quit":
            break

        messages.append({"role": "user", "content": answer})

    print(f"\n\n{'─' * 60}")
    print("Generating final summary...\n")

    messages.append({
        "role": "user",
        "content": "The interview is now complete. Please provide the final INTERVIEW SUMMARY.",
    })

    try:
        with client.messages.stream(
            model="claude-opus-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=messages,
        ) as stream:
            for text in stream.text_stream:
                print(text, end="", flush=True)

        final = stream.get_final_message()
        print(f"\n\n{'─' * 60}")
        print(f"Tokens used — input: {final.usage.input_tokens}, output: {final.usage.output_tokens}")

    except anthropic.APIStatusError as e:
        print(f"\nAPI error ({e.status_code}): {e.message}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Step 04 — Prep: AI hiring manager interview with scoring"
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
        help="Job description to target questions (optional)",
    )
    parser.add_argument(
        "--jd-file",
        metavar="FILE",
        help="Path to a file containing the job description (optional)",
    )
    parser.add_argument(
        "--no-jd",
        action="store_true",
        help="Skip job description prompt and run a generic interview",
    )
    parser.add_argument(
        "--rounds",
        type=int,
        default=DEFAULT_ROUNDS,
        metavar="N",
        help=f"Number of interview questions (default: {DEFAULT_ROUNDS})",
    )
    args = parser.parse_args()

    if args.rounds < 1 or args.rounds > 20:
        print("Error: --rounds must be between 1 and 20.", file=sys.stderr)
        sys.exit(1)

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

    run_interview(cv_text, job_description, args.rounds)


if __name__ == "__main__":
    main()
