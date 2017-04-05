# Copyright 2016 Google Inc. All Rights Reserved.
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

import os

import mock
import pytest
import requests

PROJECT = os.environ['GCLOUD_PROJECT']
BUCKET = os.environ['CLOUD_STORAGE_BUCKET']


def get_resource_path(resource, local_path):
    local_resource_path = os.path.join(local_path, 'resources', *resource)

    if os.path.exists(local_resource_path):
        return local_resource_path
    else:
        raise EnvironmentError('Resource {} not found.'.format(
            os.path.join(*resource)))


def fetch_gcs_resource(resource, tmpdir, _chunk_size=1024):
    resp = requests.get(resource, stream=True)
    dest_file = str(tmpdir.join(os.path.basename(resource)))
    with open(dest_file, 'wb') as f:
        for chunk in resp.iter_content(_chunk_size):
            f.write(chunk)

    return dest_file


@pytest.fixture(scope='module')
def remote_resource():
    """Provides a function that downloads the given resource from Cloud
    Storage, returning the path to the downloaded resource."""
    remote_uri = 'http://storage.googleapis.com/{}/'.format(
        BUCKET)

    return lambda path, tmpdir: fetch_gcs_resource(
        remote_uri + path.strip('/'), tmpdir)


@pytest.fixture
def api_client_inject_project_id():
    """Patches all googleapiclient requests to replace 'YOUR_PROJECT_ID' with
    the project ID."""
    import googleapiclient.http

    old_execute = googleapiclient.http.HttpRequest.execute

    def new_execute(self, http=None, num_retries=0):
        self.uri = self.uri.replace('YOUR_PROJECT_ID', PROJECT)
        return old_execute(self, http=http, num_retries=num_retries)

    with mock.patch(
            'googleapiclient.http.HttpRequest.execute',
            new=new_execute):
        yield
