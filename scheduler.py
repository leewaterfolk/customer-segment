"""
수민 AI Agency — Daily Scheduler
매일 오전 7시 자동 실행: 뉴스봇 + Investment 브리핑 + 6개 언어 단어

Usage:
  python scheduler.py           # 즉시 1회 실행
  python scheduler.py --watch   # 매일 07:00 자동 실행 (백그라운드)
"""

import asyncio
import os
import sys
import urllib.request
import json
from datetime import datetime
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

SLACK_DAILY   = os.environ.get("SLACK_WEBHOOK_DAILY", "")
SLACK_INVEST  = os.environ.get("SLACK_WEBHOOK_INVEST", "")
SLACK_SUMMARY = os.environ.get("SLACK_WEBHOOK_SUMMARY", "")

NEWSBOT_PROMPT     = Path("agents/newsbot.txt").read_text(encoding="utf-8")
INVESTMENT_PROMPT  = Path("agents/investment.txt").read_text(encoding="utf-8")

WORD_LANGUAGES = ["한국어", "영어", "프랑스어", "일본어", "스페인어", "중국어(간체)"]


async def send_slack(webhook: str, text: str):
    if not webhook:
        return
    payload = json.dumps({"text": text}).encode("utf-8")
    req = urllib.request.Request(
        webhook,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, lambda: urllib.request.urlopen(req))


def ask_claude(system: str, user: str, max_tokens: int = 2048) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return response.content[0].text


async def run_newsbot():
    today = datetime.now().strftime("%Y년 %m월 %d일")
    result = await asyncio.get_event_loop().run_in_executor(
        None,
        lambda: ask_claude(
            NEWSBOT_PROMPT,
            f"오늘({today}) 일일 브리핑 작성해줘. 최신 뉴스 기반으로.",
        ),
    )
    print(f"📰 뉴스봇 완료\n{result}\n{'─'*60}\n")
    await send_slack(SLACK_DAILY, f"*📰 DAILY NEWS BRIEF — {today}*\n\n{result}")


async def run_investment():
    today = datetime.now().strftime("%Y년 %m월 %d일")
    result = await asyncio.get_event_loop().run_in_executor(
        None,
        lambda: ask_claude(
            INVESTMENT_PROMPT,
            f"오늘({today}) 시장 브리핑 작성해줘.",
        ),
    )
    print(f"💰 Investment 완료\n{result}\n{'─'*60}\n")
    await send_slack(SLACK_INVEST, f"*📊 DAILY MARKET BRIEF — {today}*\n\n{result}")


async def run_daily_words():
    today = datetime.now().strftime("%Y년 %m월 %d일")
    langs = ", ".join(WORD_LANGUAGES)
    prompt = (
        f"오늘의 단어 학습 카드를 만들어줘.\n"
        f"언어별로 단어 2개씩: {langs}\n"
        f"형식: [언어] 단어 — 뜻 — 예문(한 줄)\n"
        f"실생활에서 유용한 단어로 선택해줘."
    )
    result = await asyncio.get_event_loop().run_in_executor(
        None,
        lambda: ask_claude("당신은 언어 학습 도우미입니다.", prompt, max_tokens=1000),
    )
    print(f"📚 단어 완료\n{result}\n{'─'*60}\n")
    await send_slack(SLACK_DAILY, f"*📚 오늘의 단어 — {today}*\n\n{result}")


async def run_daily():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"\n🌅 일일 자동 알림 시작 — {now}\n{'═'*60}\n")
    await asyncio.gather(run_newsbot(), run_investment(), run_daily_words())
    print(f"\n✅ 모든 일일 알림 전송 완료 — {now}")


def watch_loop():
    """Run every day at 07:00."""
    import time
    print("⏰ 스케줄러 시작 — 매일 07:00 자동 실행")
    while True:
        now = datetime.now()
        if now.hour == 7 and now.minute == 0:
            asyncio.run(run_daily())
            time.sleep(61)  # skip duplicate triggers within same minute
        time.sleep(30)


if __name__ == "__main__":
    if "--watch" in sys.argv:
        watch_loop()
    else:
        asyncio.run(run_daily())
