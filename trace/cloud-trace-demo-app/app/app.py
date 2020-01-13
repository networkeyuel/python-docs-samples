# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
A sample app demonstrating Stackdriver Trace
"""

import google.auth
from flask import Flask, render_template, request
from opencensus.trace import execution_context
from opencensus.trace.propagation import google_cloud_format
from opencensus.trace.samplers import AlwaysOnSampler
from opencensus.ext.stackdriver.trace_exporter import StackdriverExporter
from opencensus.ext.flask.flask_middleware import FlaskMiddleware

import requests
import argparse
import time,random

app = Flask(__name__)

propagator = google_cloud_format.GoogleCloudFormatPropagator()

def createMiddleWare(exporter, sampler):
  # Configure Tracing
  middleware = FlaskMiddleware(
      app,
      exporter=exporter,
      propagator=propagator,
      sampler=sampler)
  return middleware

@app.route('/')
def template_test():
  # Sleep for a random time to create various spans.
  time.sleep(random.uniform(0,0.5))
  # Keyword that gets passed in will be concatenated to the final output string.
  output_string = app.config['keyword']
  # If there is no endpoint, return the output string.
  if app.config['endpoint'] == "":
    return output_string, 200
  # Endpoint is the next service to send string to.
  url = app.config['endpoint']
  data = {'body': output_string}
  trace_context_header = propagator.to_header(execution_context.get_opencensus_tracer().span_context)
  response = requests.get(
      url,
      params = data,
      headers={
        'X-Cloud-Trace-Context' : trace_context_header}
  )
  return response.text + app.config['keyword']

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--keyword",  default="", help="name of the service.")
  parser.add_argument("--endpoint", default="", help="endpoint to dispatch appended string, simply respond if not set")
  args = parser.parse_args()
  app.config['keyword'] = args.keyword
  app.config['endpoint'] = args.endpoint
  createMiddleWare(StackdriverExporter(), AlwaysOnSampler())
  app.run(debug=True, host='0.0.0.0', port=8080)
