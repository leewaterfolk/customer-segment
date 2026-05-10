# 수민 AI 에이전시 팀 구성

## 팀장 (Orchestrator)
모든 요청의 진입점. 역할 분배 + 최종 취합.
복잡한 요청 → 여러 에이전트 동시 호출.

## 에이전트 목록
- `meta_ads` : 메타광고 카피 + 전략 (Facebook/Instagram)
- `naver_ads` : 네이버광고 + 블로그 SEO
- `insta` : 인스타 캡션 + 릴스 + 콘텐츠 캘린더
- `korea_market` : 한국시장 진입 전략 (Fiverr 핵심)
- `investment` : 포트폴리오 + 시장 모니터링
- `secretary` : 이메일 + 일정 정리
- `newsbot` : AI · 마케팅 · 투자 · 싱가포르 뉴스 큐레이션

## Slack 채널 매핑
| 에이전트 | Slack 채널 |
|---|---|
| meta_ads | #meta-ads |
| naver_ads | #naver-ads |
| insta | #insta |
| korea_market | #korea-market |
| investment | #investment |
| secretary | #summary |
| newsbot | #daily-alerts |
| orchestrator (summary) | #summary |
| fiverr inbox | #inbox-fiverr |

## 모드
- **MODE A (협업)** : 큰 프로젝트 → 팀장이 여러 에이전트 병렬 실행 → #summary 통합
- **MODE B (독립+태그)** : Fiverr 문의 → Make.com → 분류 → 담당 채널 자동 전송

## 실행
```bash
# 멀티에이전트 협업 요청
python orchestrator.py "인스타 캠페인이랑 메타광고 같이 짜줘. 제품: XXX, 타겟: 2030 여성"

# 매일 자동 알림 (스케줄러)
python scheduler.py
```

## 파일 구조
```
sumin-ai-agency/
├── CLAUDE.md
├── orchestrator.py      ← 멀티에이전트 메인
├── scheduler.py         ← 매일 자동 실행
├── run_daily.bat        ← Windows Task Scheduler용
├── .env                 ← API 키 (git에 올리지 말 것)
├── .env.example         ← 키 템플릿
├── agents/
│   ├── orchestrator.txt
│   ├── meta_ads.txt
│   ├── naver_ads.txt
│   ├── insta.txt
│   ├── korea_market.txt
│   ├── investment.txt
│   ├── secretary.txt
│   └── newsbot.txt
└── logs/
```
