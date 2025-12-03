from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from zoneinfo import ZoneInfo

from app.core.database import SessionLocal
from app.services.match_service import create_daily_match_results_by_best_score

# 한국 시간 기준으로 돌리고 싶으면 timezone 설정
scheduler = AsyncIOScheduler(timezone=ZoneInfo("Asia/Seoul"))


def run_daily_match_job():
    """
    매일 0시에 실행될 실제 작업 함수.
    DB 세션을 직접 열어서 match_service 호출.
    """
    db = SessionLocal()
    try:
        created_matches = create_daily_match_results_by_best_score(db)
        print(
            f"[{datetime.now()}] daily match job 실행. "
            f"생성된 매칭 수 = {len(created_matches)}"
        )
    finally:
        db.close()


def start_scheduler():
    """
    앱 시작 시 호출할 함수.
    - 매일 0시(한국 시간)에 run_daily_match_job 실행
    """
    # 이미 등록된 job 있으면 중복 방지
    if not scheduler.get_jobs():
        scheduler.add_job(
            run_daily_match_job,
            CronTrigger(hour=0, minute=0),  # 매일 00:00
            id="daily_match_job",
            replace_existing=True,
        )
    scheduler.start()
    print("APScheduler started.")


def shutdown_scheduler():
    """
    앱 종료 시 호출할 함수.
    """
    scheduler.shutdown()
    print("APScheduler shutdown.")
