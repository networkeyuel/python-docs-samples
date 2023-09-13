# Copyright 2023 Google LLC

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import backoff
from google.api_core.exceptions import RetryError
from google.api_core.exceptions import ServiceUnavailable
from google.cloud.storage import Bucket

import event_driven_gcs_transfer


@backoff.on_exception(
    backoff.expo,
    (
            RetryError,
            ServiceUnavailable,
    ),
    max_time=60,
)
def test_event_driven_gcs_transfer(
        capsys,
        project_id: str,
        job_description_unique: str,
        source_bucket: Bucket,
        destination_bucket: Bucket,
        pubsub_id: str,
):
    event_driven_gcs_transfer.create_event_driven_gcs_transfer(
        project_id=project_id,
        description=job_description_unique,
        source_bucket=source_bucket.name,
        sink_bucket=destination_bucket.name,
        pubsub_id=pubsub_id,
    )

    out, _ = capsys.readouterr()

    # Ensure the transferJob has been created
    assert "Created transferJob:" in out

