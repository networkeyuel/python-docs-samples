# Lint as: python3

# Copyright 2020 Google Inc. All Rights Reserved.
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

"""Tests for quickstartv2."""

import os
import uuid

from googleapiclient import errors
import pytest
from retrying import retry

import quickstartv2
import service_accounts

# Setting up variables for testing
GCLOUD_PROJECT = os.environ["GCLOUD_PROJECT"]


def retry_if_conflict(exception):
    return (isinstance(exception, errors.HttpError)
            and 'There were concurrent policy changes' in str(exception))


@pytest.fixture(scope="module")
def test_member():
    # section to create service account to test policy updates.
    # we use the first portion of uuid4 because full version is too long.
    name = "python-test-" + str(uuid.uuid4()).split('-')[0]
    email = name + "@" + GCLOUD_PROJECT + ".iam.gserviceaccount.com"
    member = "serviceAccount:" + email
    service_accounts.create_service_account(
        GCLOUD_PROJECT, name, "Py Test Account"
    )

    yield member

    # deleting the service account created above
    service_accounts.delete_service_account(email)


def test_quickstartv2(test_member, capsys):
    @retry(wait_exponential_multiplier=1000, wait_exponential_max=10000,
           stop_max_attempt_number=5, retry_on_exception=retry_if_conflict)
    def test_call():
        """Test follows the structure of quickstartv2 quickstart()"""

        project_id = GCLOUD_PROJECT
        role = "roles/logging.logWriter"

        """Initializes service."""
        crm_service = quickstartv2.initialize_service()

        """Grants your member the 'Log Writer' role for the project."""
        quickstartv2.modify_policy_add_role(
            crm_service, project_id, role, test_member)

        """Gets the project's policy and prints all members with the 'Log Writer' role."""
        policy = quickstartv2.get_policy(crm_service, project_id)
        binding = next(b for b in policy["bindings"] if b["role"] == role)
        print("Role: " + binding["role"])
        print("Members: ")
        for m in binding["members"]:
            print("[" + m + "] ")

        out, _ = capsys.readouterr()
        assert test_member in out

        """Removes the member from the 'Log Writer' role"""
        quickstartv2.modify_policy_remove_member(
            crm_service, project_id, role, test_member)
    test_call()
