"""
Copyright 2021 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import random
import time

from flask import Flask

from prometheus_client import (
    Counter,
    generate_latest,
    Histogram,
    REGISTRY,
)


app = Flask(__name__)
PYTHON_REQUESTS_COUNTER = Counter("python_requests", "total requests")
PYTHON_FAILED_REQUESTS_COUNTER = Counter("python_failed_requests", "failed requests")
PYTHON_LATENCIES_HISTOGRAM = Histogram(
    "python_request_latency", "request latency by path"
)


@app.route("/")
@PYTHON_LATENCIES_HISTOGRAM.time()
def homePage():
    # count request
    PYTHON_REQUESTS_COUNTER.inc()
    # fail 10% of the time
    if random.randint(0, 100) > 90:
        PYTHON_FAILED_REQUESTS_COUNTER.inc()
        return ("error!", 500)
    else:
        random_delay = random.randint(0, 5000) / 1000
        # delay for a bit to vary latency measurement
        time.sleep(random_delay)
        return "home page"


@app.route("/metrics", methods=["GET"])
def stats():
    return generate_latest(REGISTRY), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
