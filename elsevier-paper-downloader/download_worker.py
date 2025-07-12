import os
import sys
import time
import random
import aiohttp
import asyncio
from redis import Redis
import logging

API_KEY = "your own API KEY"  # replace with your Elsevier API key
OUTPUT_DIR = "papers"
REQUEST_TIMEOUT = 60
MAX_RETRIES = 3
RETRY_DELAY = 5
LOG_FILE = "download_worker.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def get_script_dir():
    return os.path.dirname(os.path.abspath(__file__))


def ensure_output_dir():
    script_dir = get_script_dir()
    output_path = os.path.join(script_dir, OUTPUT_DIR)
    os.makedirs(output_path, exist_ok=True)
    return output_path

def connect_redis():
    return Redis(host='localhost', port=6379, db=0)

async def download_article(session, doi):
    tdm_url = f"https://api.elsevier.com/content/article/doi/{doi}?apiKey={API_KEY}"

    try:
        async with session.get(
                tdm_url,
                headers={"Accept": "application/pdf"},
                timeout=REQUEST_TIMEOUT
        ) as response:

            if response.status == 200:
                content = await response.read()
                output_dir = ensure_output_dir()
                filename = doi.replace('/', '_') + ".pdf"
                filepath = os.path.join(output_dir, filename)

                with open(filepath, "wb") as f:
                    f.write(content)

                logging.info(f"downlaod successful: {doi}")
                return True
            else:
                error_msg = f"download failed {doi}: HTTP {response.status}"
                logging.warning(error_msg)
                return False
    except asyncio.TimeoutError:
        logging.warning(f"request timeout: {doi}")
    except Exception as e:
        logging.error(f"download error {doi}: {str(e)}")

    return False

async def process_queue():
    redis_conn = connect_redis()
    output_dir = ensure_output_dir()

    connector = aiohttp.TCPConnector(limit_per_host=3)
    async with aiohttp.ClientSession(connector=connector) as session:
        while True:
            doi = redis_conn.rpop('doi_queue')
            if doi is None:
                logging.info("queue is empty,worker process exiting")
                break

            doi = doi.decode('utf-8')
            logging.info(f"start: {doi}")

            success = False
            for attempt in range(MAX_RETRIES):
                if attempt > 0:
                    delay = RETRY_DELAY * (2 ** attempt) + random.uniform(0, 1)
                    logging.info(f"retry #{attempt} after {delay:.1f}second")
                    await asyncio.sleep(delay)

                success = await download_article(session, doi)
                if success:
                    break

            if not success:
                logging.error(f"multiple attempts yielded no success: {doi}")

            await asyncio.sleep(random.uniform(0.1, 0.5))


def main():
    pid = os.getpid()
    logging.info(f"launch the download worker process (PID: {pid})")

    asyncio.run(process_queue())

    logging.info("worker process exited normally")

if __name__ == "__main__":
    main()