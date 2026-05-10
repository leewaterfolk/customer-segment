"""
수민 AI Agency — Multi-Agent Orchestrator (MODE A)
Usage: python orchestrator.py "인스타 캠페인이랑 메타광고 같이 짜줘. 제품: XXX"
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime

import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

SLACK_WEBHOOKS = {
    "summary":      os.environ.get("SLACK_WEBHOOK_SUMMARY", ""),
    "meta_ads":     os.environ.get("SLACK_WEBHOOK_META", ""),
    "naver_ads":    os.environ.get("SLACK_WEBHOOK_NAVER", ""),
    "insta":        os.environ.get("SLACK_WEBHOOK_INSTA", ""),
    "korea_market": os.environ.get("SLACK_WEBHOOK_KOREA", ""),
    "investment":   os.environ.get("SLACK_WEBHOOK_INVEST", ""),
    "daily":        os.environ.get("SLACK_WEBHOOK_DAILY", ""),
}

AGENTS = {
    "meta_ads":     "agents/meta_ads.txt",
    "naver_ads":    "agents/naver_ads.txt",
    "insta":        "agents/insta.txt",
    "korea_market": "agents/korea_market.txt",
    "investment":   "agents/investment.txt",
    "secretary":    "agents/secretary.txt",
    "newsbot":      "agents/newsbot.txt",
}

ORCHESTRATOR_PROMPT = Path("agents/orchestrator.txt").read_text(encoding="utf-8")


def load_agent_prompt(agent_name: str) -> str:
    path = AGENTS.get(agent_name)
    if not path:
        return ""
    return Path(path).read_text(encoding="utf-8")


def select_agents(request: str) -> list[str]:
    """Ask the orchestrator which agents are needed for this request."""
    selection_prompt = f"""{ORCHESTRATOR_PROMPT}

---
요청: {request}

위 요청에 필요한 에이전트 목록을 JSON 배열로만 반환하세요.
사용 가능한 에이전트: meta_ads, naver_ads, insta, korea_market, investment, secretary, newsbot
예시 형식: ["meta_ads", "insta"]
JSON 배열 외 다른 텍스트 없이 반환하세요."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=200,
        messages=[{"role": "user", "content": selection_prompt}],
    )
    raw = response.content[0].text.strip()
    import json
    try:
        agents = json.loads(raw)
        return [a for a in agents if a in AGENTS]
    except json.JSONDecodeError:
        # Fallback: pick agents mentioned in raw text
        return [a for a in AGENTS if a in raw]


async def run_agent(agent_name: str, request: str) -> tuple[str, str]:
    """Run a single agent asynchronously and return (agent_name, result)."""
    system_prompt = load_agent_prompt(agent_name)
    loop = asyncio.get_event_loop()

    def call_api():
        return client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=system_prompt,
            messages=[{"role": "user", "content": request}],
        )

    response = await loop.run_in_executor(None, call_api)
    return agent_name, response.content[0].text


async def send_to_slack(webhook_url: str, text: str):
    """Send message to Slack via webhook."""
    if not webhook_url:
        return
    import urllib.request
    import json
    payload = json.dumps({"text": text}).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, lambda: urllib.request.urlopen(req))


def synthesize_results(request: str, results: dict[str, str]) -> str:
    """Have the orchestrator synthesize all agent results into a final summary."""
    agent_outputs = "\n\n".join(
        f"[{name} 결과]\n{output}" for name, output in results.items()
    )
    synthesis_prompt = f"""{ORCHESTRATOR_PROMPT}

---
원래 요청: {request}

각 에이전트 결과물:
{agent_outputs}

위 결과물들을 하나의 통합 결과물로 취합해주세요. Slack #summary 채널용 포맷으로."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=3000,
        messages=[{"role": "user", "content": synthesis_prompt}],
    )
    return response.content[0].text


async def orchestrate(request: str):
    print(f"\n🧠 요청 분석 중: {request}\n")

    # Step 1: Select agents
    selected = select_agents(request)
    if not selected:
        print("⚠️  적절한 에이전트를 찾지 못했습니다.")
        return
    print(f"📋 투입 에이전트: {', '.join(selected)}\n")

    # Step 2: Run agents in parallel
    print("⚡ 에이전트 병렬 실행 중...\n")
    tasks = [run_agent(agent, request) for agent in selected]
    agent_results_list = await asyncio.gather(*tasks)
    agent_results = dict(agent_results_list)

    # Step 3: Print and send each result to its Slack channel
    slack_tasks = []
    for agent_name, result in agent_results.items():
        print(f"✅ [{agent_name}] 완료\n{result}\n{'─'*60}\n")
        webhook = SLACK_WEBHOOKS.get(agent_name, "")
        if webhook:
            header = f"*[{agent_name.upper()}]* — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            slack_tasks.append(send_to_slack(webhook, header + result))

    if slack_tasks:
        await asyncio.gather(*slack_tasks)

    # Step 4: Synthesize into final summary
    print("🔗 최종 통합 결과물 생성 중...\n")
    summary = synthesize_results(request, agent_results)
    print(f"💬 최종 요약:\n{summary}\n")

    # Step 5: Send summary to #summary
    if SLACK_WEBHOOKS["summary"]:
        header = f"*[SUMMARY]* — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n요청: {request}\n\n"
        await send_to_slack(SLACK_WEBHOOKS["summary"], header + summary)
        print("📨 #summary 채널로 전송 완료 ✅")
    else:
        print("ℹ️  SLACK_WEBHOOK_SUMMARY 미설정 — Slack 전송 생략")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python orchestrator.py \"요청 내용\"")
        sys.exit(1)
    request_text = " ".join(sys.argv[1:])
    asyncio.run(orchestrate(request_text))
