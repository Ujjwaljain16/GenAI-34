"""
Ingestion Worker — Resilient polling loop with exponential-backoff retry.

Scheduling:
  - Polls for QUEUED jobs every POLL_INTERVAL_S seconds.
  - On job failure, increments retry_count and schedules next_retry_at with
    exponential backoff (capped at MAX_BACKOFF_S). After MAX_RETRIES the job
    stays FAILED and is not retried automatically.

Run:
  python app/workers/ingestion_worker.py
"""
from __future__ import annotations

import asyncio
import logging
import math
import os
import sys
from datetime import datetime, timezone, timedelta

# Add backend dir to path if running directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import AsyncSessionLocal as async_session_maker
from app.services.ingestion_orchestrator import IngestionOrchestrator
from app.services.storage import LocalStorageProvider

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# Config
# ──────────────────────────────────────────────
POLL_INTERVAL_S = 5       # idle sleep between polls
MAX_RETRIES = 3           # max automatic retries per job
BASE_BACKOFF_S = 30       # initial backoff delay in seconds
MAX_BACKOFF_S = 600       # cap: 10 minutes


def _backoff_seconds(retry_count: int) -> int:
    """Exponential backoff with cap: 30s → 60s → 120s → … → 600s"""
    return min(int(BASE_BACKOFF_S * (2 ** retry_count)), MAX_BACKOFF_S)


async def claim_next_job(session: AsyncSession) -> str | None:
    """
    Claim the next QUEUED job using FOR UPDATE SKIP LOCKED.
    Also picks up FAILED jobs that are eligible for retry (retry_count < MAX_RETRIES
    and next_retry_at <= NOW()).
    """
    stmt = text("""
        UPDATE graph_build_jobs
        SET status = 'PARSING',
            started_at = COALESCE(started_at, NOW()),
            updated_at = NOW()
        WHERE id = (
            SELECT id FROM graph_build_jobs
            WHERE
                (status = 'QUEUED')
                OR (
                    status = 'FAILED'
                    AND retry_count < :max_retries
                    AND (next_retry_at IS NULL OR next_retry_at <= NOW())
                )
            ORDER BY created_at ASC
            FOR UPDATE SKIP LOCKED
            LIMIT 1
        )
        RETURNING id, retry_count
    """)
    result = await session.execute(stmt, {"max_retries": MAX_RETRIES})
    await session.commit()
    row = result.fetchone()
    return (str(row[0]), int(row[1])) if row else (None, 0)


async def mark_for_retry(job_id: str, retry_count: int, error: str, session: AsyncSession) -> None:
    """Schedule a failed job for retry with exponential backoff."""
    new_retry = retry_count + 1
    if new_retry >= MAX_RETRIES:
        logger.error(f"Job {job_id} exhausted {MAX_RETRIES} retries. Marking permanently FAILED.")
        await session.execute(
            text("""
                UPDATE graph_build_jobs
                SET status = 'FAILED', last_error = :err, retry_count = :rc, updated_at = NOW()
                WHERE id = :jid
            """),
            {"err": error, "rc": new_retry, "jid": job_id},
        )
    else:
        delay = _backoff_seconds(new_retry)
        retry_at = datetime.now(timezone.utc) + timedelta(seconds=delay)
        logger.warning(
            f"Job {job_id} failed (attempt {new_retry}/{MAX_RETRIES}). "
            f"Retrying in {delay}s at {retry_at.isoformat()}"
        )
        await session.execute(
            text("""
                UPDATE graph_build_jobs
                SET status = 'FAILED', last_error = :err, retry_count = :rc,
                    next_retry_at = :rat, updated_at = NOW()
                WHERE id = :jid
            """),
            {"err": error, "rc": new_retry, "rat": retry_at, "jid": job_id},
        )
    await session.commit()


async def worker_loop() -> None:
    logger.info("Starting Ingestion Worker Loop…")
    storage_provider = LocalStorageProvider()
    orchestrator = IngestionOrchestrator(storage_provider=storage_provider)

    while True:
        try:
            async with async_session_maker() as session:
                job_id, retry_count = await claim_next_job(session)

                if job_id:
                    logger.info(f"Claimed job {job_id} (retry #{retry_count}). Processing…")
                    success = await orchestrator.process_job(job_id, session)
                    if not success:
                        async with async_session_maker() as retry_session:
                            await mark_for_retry(job_id, retry_count, "See job error_message", retry_session)
                else:
                    # No job found — idle sleep before next poll
                    await asyncio.sleep(POLL_INTERVAL_S)

        except Exception as exc:
            logger.error(f"Worker loop error: {exc}", exc_info=True)
            await asyncio.sleep(POLL_INTERVAL_S)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(worker_loop())
