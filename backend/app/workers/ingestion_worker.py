import asyncio
import logging
import sys
import os

# Add backend dir to path if running directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.db import AsyncSessionLocal as async_session_maker
from app.services.ingestion_orchestrator import IngestionOrchestrator
from app.services.storage import LocalStorageProvider

logger = logging.getLogger(__name__)

async def claim_next_job(session: AsyncSession):
    """
    Claims the next available graph build job using FOR UPDATE SKIP LOCKED.
    """
    stmt = text('''
        UPDATE graph_build_jobs
        SET status = 'PARSING', started_at = NOW(), updated_at = NOW()
        WHERE id = (
            SELECT id FROM graph_build_jobs
            WHERE status = 'QUEUED'
            ORDER BY created_at ASC
            FOR UPDATE SKIP LOCKED
            LIMIT 1
        )
        RETURNING id;
    ''')
    result = await session.execute(stmt)
    await session.commit()
    row = result.fetchone()
    return row[0] if row else None


async def worker_loop():
    logger.info("Starting Ingestion Worker Loop...")
    storage_provider = LocalStorageProvider()
    orchestrator = IngestionOrchestrator(storage_provider=storage_provider)
    
    while True:
        try:
            async with async_session_maker() as session:
                job_id = await claim_next_job(session)
                
                if job_id:
                    logger.info(f"Claimed job {job_id}. Processing...")
                    success = await orchestrator.process_job(job_id, session)
                    if not success:
                        logger.error(f"Failed processing job {job_id}")
                else:
                    # No job found, sleep before polling again
                    await asyncio.sleep(5)
        except Exception as e:
            logger.error(f"Worker loop error: {str(e)}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(worker_loop())
