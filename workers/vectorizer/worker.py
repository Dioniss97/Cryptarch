import os
import sys
import time

import redis


def main():
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    try:
        r = redis.from_url(redis_url)
        r.ping()
        print("Worker ready — connected to Redis", flush=True)
    except redis.ConnectionError:
        print("Worker ready — Redis not yet available, will retry", flush=True)

    while True:
        time.sleep(5)


if __name__ == "__main__":
    main()
