from redis import Redis
from rq import Worker, SimpleWorker, Queue, Connection
from app.config import REDIS_URL
import logging
import os
import signal
import sys

# Ensure logging is set up
logging.basicConfig(level=logging.INFO)

listen = ['default']

# Define a custom worker for Windows that bypasses Unix-specific signal handlers
class WindowsDeathPenalty:
    def __init__(self, timeout, exception, job_id=None):
        pass
    def __enter__(self):
        pass
    def __exit__(self, type, value, traceback):
        pass

class WindowsWorker(SimpleWorker):
    death_penalty_class = WindowsDeathPenalty

def handle_shutdown(signum, frame):
    print(f"Received signal {signum}. Exiting...")
    sys.exit(0)

def start_worker():
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    conn = Redis.from_url(REDIS_URL)
    with Connection(conn):
        # Detect Operating System
        if os.name == 'nt':
            print("Detected Windows OS. Using WindowsWorker (SimpleWorker).")
            worker_class = WindowsWorker
        else:
            print("Detected Unix/Linux/Mac OS. Using standard Worker.")
            worker_class = Worker
            
        try:
            worker = worker_class(list(map(Queue, listen)))
            worker.work()
        except KeyboardInterrupt:
            print("Worker stopped by user via KeyboardInterrupt.")
            sys.exit(0)

if __name__ == '__main__':
    print(f"Starting worker listening on {listen}...")
    start_worker()
