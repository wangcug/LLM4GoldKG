import json
import subprocess
import os
import sys
import time
from redis import Redis


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    doi_file = os.path.join(script_dir, 'doi_list.json')

    if not os.path.exists(doi_file):
        print(f"error:  {doi_file} no exist！")
        print("run fetch_dois.py first.")
        return

    try:
        with open(doi_file) as f:
            data = json.load(f)
            dois = data['dois']
            print(f"from {doi_file} load {len(dois)} DOI")
    except Exception as e:
        print(f"failed to load the list: {str(e)}")
        return

    try:
        redis_conn = Redis(host='localhost', port=6379, db=0)
        redis_conn.ping()
        print("successfully connected to the Redis server")
    except Exception as e:
        print(f"cannot connect to Redis server: {str(e)}")
        print("please ensure the Redis server is running")
        return

    redis_conn.delete('doi_queue')

    for doi in dois:
        redis_conn.lpush('doi_queue', doi)

    print(f" {len(dois)} tasks have been added to the queue")

    num_workers = 8  # scales based on CPU core count

    workers = []
    for i in range(num_workers):
        python_path = sys.executable

        worker_script = os.path.join(script_dir, 'download_worker.py')
        cmd = [python_path, worker_script]

        worker = subprocess.Popen(cmd)
        workers.append(worker)
        print(f"#{i + 1} (PID: {worker.pid})")
        time.sleep(0.5)

    print(f"all {num_workers} worker processes strated successfully,awaiting task completion...")

    for worker in workers:
        worker.wait()

    print("all worker processes have completed")

if __name__ == "__main__":
    main()