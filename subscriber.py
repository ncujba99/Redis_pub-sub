import redis
import json
import config
import threading
import time

pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
redis_con = redis.Redis(connection_pool=pool)
pub_sub = redis_con.pubsub()
pub_sub.subscribe("file_tasks")


def process_file_thread(file_path):
    # any file processing from new thread here
    print(file_path)


for task in pub_sub.listen():
    try:
        task = json.loads(task["data"].decode("utf-8"))

        if config.active_threads < config.max_threads:
            threading.Thread(target=process_file_thread, args=[task]).start()
        else:
            while config.active_threads >= config.max_threads:
                time.sleep(0.1)
                print("max threads number reached ")
    except Exception as eee:
        print(eee)
