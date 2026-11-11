import time
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s","level":"%(levelname)s","role":"queue_worker","message":"%(message)s"}'
)
logger = logging.getLogger("autoreels.worker")

def start_worker():
    logger.info("AutoReels Pipeline Queue Worker starting...")
    logger.info("Listening for video rendering and dispatch jobs on Redis queue...")
    
    # Standalone event loop for worker processing
    try:
        while True:
            # Poll / await queue items
            time.sleep(5)
    except KeyboardInterrupt:
        logger.info("Worker stopped by user.")

if __name__ == "__main__":
    start_worker()
