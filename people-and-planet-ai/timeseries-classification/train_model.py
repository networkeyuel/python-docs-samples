# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from google.cloud import aiplatform


def run(
    project: str,
    region: str,
    train_data_dir: str,
    eval_data_dir: str,
    output_dir: str,
    image: str,
    train_steps: int,
    eval_steps: int,
):
    client = aiplatform.gapic.JobServiceClient(
        client_options={"api_endpoint": "us-central1-aiplatform.googleapis.com"}
    )
    response = client.create_custom_job(
        parent=f"projects/{project}/locations/{region}",
        custom_job={
            "display_name": "global-fishing-watch",
            "job_spec": {
                # https://cloud.google.com/vertex-ai/docs/reference/rest/v1/CustomJobSpec
                "base_output_directory": {
                    "output_uri_prefix": output_dir,
                },
                # https://cloud.google.com/vertex-ai/docs/training/distributed-training
                "worker_pool_specs": [
                    {
                        # Scheduler
                        "machine_spec": {"machine_type": "e2-highcpu-4"},
                        "replica_count": 1,
                        "container_spec": {
                            "image_uri": image,
                            "command": ["python"],
                            "args": [
                                "trainer.py",
                                f"--train-data-dir={train_data_dir}",
                                f"--eval-data-dir={eval_data_dir}",
                                f"--train-steps={train_steps}",
                                f"--eval-steps={eval_steps}",
                            ],
                        },
                    },
                ],
            },
        },
    )
    logging.info("Vertex AI job response:")
    logging.info(response)
    return response.name.split("/")[-1]
