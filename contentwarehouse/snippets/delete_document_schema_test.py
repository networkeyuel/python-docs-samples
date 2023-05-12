# # Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os

from contentwarehouse.snippets import delete_document_schema_sample
from contentwarehouse.snippets import test_utilities

import pytest

project_id = os.environ["GOOGLE_CLOUD_PROJECT"]
location = "us"
document_schema_id = "78jim5u8cvrrg"


def test_delete_document_schema(capsys: pytest.CaptureFixture) -> None:
    project_number = test_utilities.get_project_number(project_id)

    delete_document_schema_sample.sample_delete_document_schema(
        project_number=project_number,
        location=location,
        document_schema_id=document_schema_id)

    out, _ = capsys.readouterr()

    assert "Document Schema Deleted" in out
