# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# [START functions_log_cloudevent]
# CloudEvent function to be triggered by an Eventarc Cloud Audit Logging trigger
# Note: this is NOT designed for second-party (Cloud Audit Logs -> Pub/Sub) triggers!
def hello_auditlog(cloudevent):
    # Print out details from the CloudEvent itself
    print(f"Event type: {cloudevent['type']}")

    # Print out the CloudEvent's `subject` property
    # See https://github.com/cloudevents/spec/blob/v1.0.1/spec.md#subject
    print(f"Subject: {cloudevent['subject']}")

    # Print out details from the `protoPayload`
    # This field encapsulates a Cloud Audit Logging entry
    # See https://cloud.google.com/logging/docs/audit#audit_log_entry_structure

    payload = cloudevent.data.get("protoPayload")
    if payload:
        print(f"API method: {payload['methodName']}")
        print(f"Resource name: {payload['resourceName']}")
        print(f"Principal: {payload['authenticationInfo']['principalEmail']}")


# [END functions_log_cloudevent]
