# -*- coding: utf-8 -*-
# Copyright 2020 Google LLC
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
# Generated code. DO NOT EDIT!
#
# Snippet for ExportInsightsData
# NOTE: This snippet has been automatically generated for illustrative purposes only.
# It may require modifications to work in your environment.

# To install the latest published package dependency, execute the following:
#   python3 -m pip install google-cloud-contact-center-insights


# [START contactcenterinsights_generated_contact_center_insights_v1_ContactCenterInsights_ExportInsightsData_sync]
from google.cloud import contact_center_insights_v1


def sample_export_insights_data():
    # Create a client
    client = contact_center_insights_v1.ContactCenterInsightsClient()

    # Initialize request argument(s)
    big_query_destination = contact_center_insights_v1.BigQueryDestination()
    big_query_destination.dataset = "dataset_value"

    request = contact_center_insights_v1.ExportInsightsDataRequest(
        big_query_destination=big_query_destination,
        parent="parent_value",
    )

    # Make the request
    operation = client.export_insights_data(request=request)

    print("Waiting for operation to complete...")

    response = operation.result()

    # Handle the response
    print(response)

# [END contactcenterinsights_generated_contact_center_insights_v1_ContactCenterInsights_ExportInsightsData_sync]
