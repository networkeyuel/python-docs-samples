# Copyright 2019 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
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
"""
Tests for hmac.py. Requires GOOGLE_CLOUD_PROJECT (valid project) and
HMAC_KEY_TEST_SERVICE_ACCOUNT (valid service account email) env variables to be
set in order to run.
"""


import os

from google.cloud import storage
import pytest

import hmac


PROJECT_ID = os.environ['GOOGLE_CLOUD_PROJECT']
SERVICE_ACCOUNT_EMAIL = os.environ['HMAC_KEY_TEST_SERVICE_ACCOUNT']


@pytest.fixture()
def new_hmac_key():
    """
    Fixture to create a new HMAC key, and to guarantee all keys are deleted at
    the end of each test.
    """
    hmac_key = hmac.create_key(PROJECT_ID, SERVICE_ACCOUNT_EMAIL)
    yield hmac_key
    storage_client = storage.Client(project=PROJECT_ID)
    hmac_key = storage_client.get_hmac_key_metadata(hmac_key.access_id,
                                                    project_id=PROJECT_ID)
    if hmac_key.state == 'DELETED':
        return
    if not hmac_key.state == 'INACTIVE':
        hmac_key.state = 'INACTIVE'
        hmac_key.update()
    hmac_key.delete()


def test_list_keys(capsys, new_hmac_key):
    hmac_keys = hmac.list_keys(PROJECT_ID)
    assert 'HMAC Keys:' in capsys.readouterr().out
    assert hmac_keys.num_results >= 1


def test_create_key(capsys, new_hmac_key):
    assert 'Key ID:' in capsys.readouterr().out
    assert new_hmac_key.access_id
    assert new_hmac_key.state == 'ACTIVE'


def test_get_key(capsys, new_hmac_key):
    hmac_key = hmac.get_key(new_hmac_key.access_id, PROJECT_ID)
    assert 'HMAC key metadata' in capsys.readouterr().out
    assert hmac_key.access_id == new_hmac_key.access_id


def test_activate_key(capsys, new_hmac_key):
    new_hmac_key.state = 'INACTIVE'
    new_hmac_key.update()
    hmac_key = hmac.activate_key(new_hmac_key.access_id, PROJECT_ID)
    assert 'State: ACTIVE' in capsys.readouterr().out
    assert hmac_key.state == 'ACTIVE'


def test_deactivate_key(capsys, new_hmac_key):
    hmac_key = hmac.deactivate_key(new_hmac_key.access_id, PROJECT_ID)
    assert 'State: INACTIVE' in capsys.readouterr().out
    assert hmac_key.state == 'INACTIVE'


def test_delete_key(capsys, new_hmac_key):
    new_hmac_key.state = 'INACTIVE'
    new_hmac_key.update()
    hmac.delete_key(new_hmac_key.access_id, PROJECT_ID)
    assert 'The key is deleted' in capsys.readouterr().out
