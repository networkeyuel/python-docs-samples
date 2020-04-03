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

# [START job_search_list_companies]

from google.cloud import talent_v4beta1
import six


def sample_list_companies(project_id, tenant_id):
    """List Companies"""

    client = talent_v4beta1.CompanyServiceClient()

    # project_id = 'Your Google Cloud Project ID'
    # tenant_id = 'Your Tenant ID (using tenancy is optional)'

    if isinstance(project_id, six.binary_type):
        project_id = project_id.decode("utf-8")
    if isinstance(tenant_id, six.binary_type):
        tenant_id = tenant_id.decode("utf-8")
    parent = client.tenant_path(project_id, tenant_id)

    # Iterate over all results
    for response_item in client.list_companies(parent):
        print("Company Name: {}".format(response_item.name))
        print("Display Name: {}".format(response_item.display_name))
        print("External ID: {}".format(response_item.external_id))


# [END job_search_list_companies]
