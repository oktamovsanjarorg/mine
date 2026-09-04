import structlog
from typing import Optional, Any, Callable, List
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.base import BaseTrigger

logger = structlog.get_logger()

scheduler: Optional[AsyncIOScheduler] = None

def init_scheduler() -> AsyncIOScheduler:
    """Initialize and start the background scheduler."""
    global scheduler
    if not scheduler:
        scheduler = AsyncIOScheduler()
        scheduler.start()
        logger.info("Scheduler initialized and started")
    return scheduler

def shutdown_scheduler() -> None:
    """Shutdown the background scheduler."""
    global scheduler
    if scheduler:
        scheduler.shutdown()
        scheduler = None
        logger.info("Scheduler shutdown")

def add_job(func: Callable[..., Any], trigger: BaseTrigger, **kwargs: Any) -> str:
    """Add a job to the scheduler."""
    if not scheduler:
        raise RuntimeError("Scheduler not initialized")
    job = scheduler.add_job(func, trigger=trigger, **kwargs)
    logger.info("Job added", job_id=job.id)
    return job.id

def remove_job(job_id: str) -> None:
    """Remove a job from the scheduler."""
    if not scheduler:
        raise RuntimeError("Scheduler not initialized")
    scheduler.remove_job(job_id)
    logger.info("Job removed", job_id=job_id)

def reschedule_job(job_id: str, trigger: BaseTrigger) -> None:
    """Reschedule an existing job."""
    if not scheduler:
        raise RuntimeError("Scheduler not initialized")
    scheduler.reschedule_job(job_id, trigger=trigger)
    logger.info("Job rescheduled", job_id=job_id)

def get_job(job_id: str) -> Any:
    """Get a job by its ID."""
    if not scheduler:
        raise RuntimeError("Scheduler not initialized")
    return scheduler.get_job(job_id)

def list_jobs() -> List[Any]:
    """List all scheduled jobs."""
    if not scheduler:
        raise RuntimeError("Scheduler not initialized")
    return scheduler.get_jobs()
