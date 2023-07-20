# Copyright 2023 Google LLC
#
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

import os
import re
from uuid import uuid4

from flaky import flaky
from google.cloud import storage
from google.cloud.speech_v2.types import cloud_speech

import pytest

import transcribe_batch_multiple_files_v2


_TEST_AUDIO_FILE_PATH = "gs://cloud-samples-data/speech/audio.flac"
_GCS_BUCKET_OBJECT_RE = r"gs://([^/]+)/(.*)"


def create_gcs_bucket() -> str:
    client = storage.Client()
    bucket = client.bucket("speech-samples-" + str(uuid4()))
    new_bucket = client.create_bucket(bucket, location="us")
    return new_bucket.name


def delete_gcs_bucket(bucket_name: str) -> None:
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    bucket.delete(force=True)


def get_gcs_object(gcs_path: str) -> cloud_speech.BatchRecognizeResults:
    client = storage.Client()
    bucket_name, object_name = re.match(_GCS_BUCKET_OBJECT_RE, gcs_path).group(1, 2)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(object_name)
    results_bytes = blob.download_as_bytes()
    return cloud_speech.BatchRecognizeResults.from_json(
        results_bytes, ignore_unknown_fields=True
    )


@flaky(max_runs=10, min_passes=1)
def test_transcribe_batch_multiple_files_v2(capsys: pytest.CaptureFixture) -> None:
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")

    bucket_name = create_gcs_bucket()

    response = transcribe_batch_multiple_files_v2.transcribe_batch_multiple_files_v2(
        project_id, [_TEST_AUDIO_FILE_PATH], f"gs://{bucket_name}"
    )

    results = get_gcs_object(response.results[_TEST_AUDIO_FILE_PATH].uri)

    assert re.search(
        r"how old is the Brooklyn Bridge",
        results.results[0].alternatives[0].transcript,
        re.DOTALL | re.I,
    )

    delete_gcs_bucket(bucket_name)
