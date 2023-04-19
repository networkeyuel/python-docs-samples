#  Copyright 2022 Google LLC
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

TEST_CONFIG_OVERRIDE = {
    # Tests in test_default_values.py require separate projects to not interfere with each other.
    # "gcloud_project_env": "GOOGLE_CLOUD_PROJECT",
    "gcloud_project_env": "BUILD_SPECIFIC_GCLOUD_PROJECT",
}
