from contextlib import asynccontextmanager

from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.job import Job

from loguru import logger

TEST_JOB = "test_job"

# Create a FastAPI app instance
jobstores = {
    'default': MemoryJobStore()
}

# Initialize an AsyncIOScheduler with the jobstore
scheduler = AsyncIOScheduler(jobstores=jobstores, timezone='America/Chicago')

# Job running every 10 seconds
@scheduler.scheduled_job('interval', seconds=2, id=TEST_JOB)
def scheduled_job_1():
    logger.info("scheduled_job_1")

@asynccontextmanager
async def lifespan(app: FastAPI):
	# start the scheduler
	scheduler.start()
	yield
	# shutdown the scheduler
	scheduler.shutdown()
	app = FastAPI(lifespan=lifespan)

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def read_root():
    return {"message": "up"}

@app.post("/pause")
async def pause_job():
    job: Job = scheduler.get_job(job_id=TEST_JOB)
    if job.next_run_time is None:
        return {"state": "job is already paused"}
    else:
        scheduler.pause_job(job_id=TEST_JOB)
        if job.next_run_time is None:
            return {"state": "successfully paused job"}

@app.post("/start")
async def start_jobj():
    job: Job = scheduler.get_job(job_id=TEST_JOB)
    if job.next_run_time is None:
        scheduler.resume_job(job_id=TEST_JOB)
        return {"state": "successfully started up job"}
    else:
        return {"state": "Job is already running"}

@app.get("/view_jobs")
async def view_jobs():
	jobs: list[Job] = scheduler.get_jobs()
	jobs = [job.name for job in jobs]
	return {"jobs": jobs}