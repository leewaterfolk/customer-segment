@echo off
REM 수민 AI Agency — Daily Scheduler (Windows Task Scheduler용)
REM Task Scheduler 등록: 작업 스케줄러 → 기본 작업 만들기 → 매일 07:00 → 이 bat 파일 실행

cd /d "%~dp0"
python scheduler.py >> logs\daily_%date:~0,4%%date:~5,2%%date:~8,2%.log 2>&1
