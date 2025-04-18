from contextlib import asynccontextmanager

from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore

from loguru import logger

# Create a FastAPI app instance
jobstores = {
    'default': MemoryJobStore()
}

# Initialize an AsyncIOScheduler with the jobstore
scheduler = AsyncIOScheduler(jobstores=jobstores, timezone='America/Chicago')

# Job running every 10 seconds
@scheduler.scheduled_job('interval', seconds=2, id="test_job")
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
    scheduler.pause_job(job_id="test_job")

@app.post("/start")
async def start_jobj():
    scheduler.resume_job(job_id="test_job")