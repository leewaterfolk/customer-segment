#!/usr/bin/env python3
"""
job_tracker.py - CSV-based job application tracker
Usage:
  python job_tracker.py add
  python job_tracker.py list [--status STATUS]
  python job_tracker.py update <id> --status STATUS [--follow-up DATE] [--notes NOTES]
  python job_tracker.py followups
"""

import argparse
import csv
import os
import sys
from datetime import date, datetime

CSV_FILE = "applications.csv"
FIELDS = ["id", "company", "role", "date_applied", "url", "status", "follow_up_date", "notes"]
VALID_STATUSES = ["applied", "interview", "offer", "rejected"]


def load_applications():
    if not os.path.exists(CSV_FILE):
        return []
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_applications(apps):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(apps)


def next_id(apps):
    if not apps:
        return 1
    return max(int(a["id"]) for a in apps) + 1


def prompt(label, required=True, default=None):
    hint = f" [{default}]" if default else ""
    while True:
        value = input(f"{label}{hint}: ").strip()
        if not value and default is not None:
            return default
        if value or not required:
            return value
        print("  This field is required.")


def cmd_add(args):
    apps = load_applications()
    print("=== Add new application ===")
    company = prompt("Company")
    role = prompt("Role")
    date_applied = prompt("Date applied (YYYY-MM-DD)", default=str(date.today()))
    url = prompt("Job URL", required=False)
    status = ""
    while status not in VALID_STATUSES:
        status = prompt(f"Status ({'/'.join(VALID_STATUSES)})", default="applied")
    follow_up = prompt("Follow-up date (YYYY-MM-DD, optional)", required=False)
    notes = prompt("Notes (optional)", required=False)

    app = {
        "id": next_id(apps),
        "company": company,
        "role": role,
        "date_applied": date_applied,
        "url": url,
        "status": status,
        "follow_up_date": follow_up,
        "notes": notes,
    }
    apps.append(app)
    save_applications(apps)
    print(f"\n[+] Added application #{app['id']} — {company} / {role}")


def cmd_list(args):
    apps = load_applications()
    if args.status:
        apps = [a for a in apps if a["status"].lower() == args.status.lower()]

    if not apps:
        print("No applications found.")
        return

    col_widths = [4, 20, 25, 12, 10, 12, 30]
    headers = ["ID", "Company", "Role", "Date", "Status", "Follow-up", "Notes"]
    fmt = "  ".join(f"{{:<{w}}}" for w in col_widths)

    print(fmt.format(*headers))
    print("  ".join("-" * w for w in col_widths))
    for a in apps:
        print(fmt.format(
            a["id"],
            a["company"][:20],
            a["role"][:25],
            a["date_applied"],
            a["status"],
            a["follow_up_date"] or "",
            a["notes"][:30] if a["notes"] else "",
        ))
    print(f"\n{len(apps)} application(s) listed.")


def cmd_update(args):
    apps = load_applications()
    target = next((a for a in apps if str(a["id"]) == str(args.id)), None)
    if not target:
        print(f"No application with id {args.id}")
        sys.exit(1)

    if args.status:
        if args.status not in VALID_STATUSES:
            print(f"Invalid status. Choose from: {', '.join(VALID_STATUSES)}")
            sys.exit(1)
        target["status"] = args.status
    if args.follow_up:
        target["follow_up_date"] = args.follow_up
    if args.notes:
        target["notes"] = args.notes

    save_applications(apps)
    print(f"[+] Updated application #{args.id}")


def cmd_followups(args):
    apps = load_applications()
    today = str(date.today())
    due = [a for a in apps if a["follow_up_date"] and a["follow_up_date"] <= today
           and a["status"] not in ("offer", "rejected")]
    if not due:
        print("No follow-ups due today.")
        return
    print(f"=== Follow-ups due (as of {today}) ===")
    for a in due:
        print(f"  #{a['id']}  {a['company']} / {a['role']}  — follow-up: {a['follow_up_date']}  [{a['status']}]")


def main():
    parser = argparse.ArgumentParser(description="Job Application Tracker")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("add", help="Add a new application")

    p_list = sub.add_parser("list", help="List applications")
    p_list.add_argument("--status", choices=VALID_STATUSES, help="Filter by status")

    p_update = sub.add_parser("update", help="Update an application")
    p_update.add_argument("id", help="Application ID")
    p_update.add_argument("--status", choices=VALID_STATUSES)
    p_update.add_argument("--follow-up", metavar="DATE")
    p_update.add_argument("--notes")

    sub.add_parser("followups", help="Show follow-ups due today or earlier")

    args = parser.parse_args()

    commands = {
        "add": cmd_add,
        "list": cmd_list,
        "update": cmd_update,
        "followups": cmd_followups,
    }

    if args.command not in commands:
        parser.print_help()
        sys.exit(1)

    commands[args.command](args)


if __name__ == "__main__":
    main()
