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

from google.cloud import kms


# [START kms_create_key_asymmetric_sign]
def create_key_asymmetric_sign(
    project_id: str, location_id: str, key_ring_id: str, key_id: str
) -> kms.CryptoKey:
    """
    Creates a new asymmetric signing key in Cloud KMS.

    Args:
        project_id (string): Google Cloud project ID (e.g. 'my-project').
        location_id (string): Cloud KMS location (e.g. 'us-east1').
        key_ring_id (string): ID of the Cloud KMS key ring (e.g. 'my-key-ring').
        key_id (string): ID of the key to create (e.g. 'my-asymmetric-signing-key').

    Returns:
        CryptoKey: Cloud KMS key.

    """

    # Import the client library.
    from google.cloud import kms
    from google.protobuf import duration_pb2  # type: ignore
    import datetime

    # Create the client.
    client = kms.KeyManagementServiceClient()

    # Build the parent key ring name.
    key_ring_name = client.key_ring_path(project_id, location_id, key_ring_id)

    # Build the key.
    purpose = kms.CryptoKey.CryptoKeyPurpose.ASYMMETRIC_SIGN
    algorithm = (
        kms.CryptoKeyVersion.CryptoKeyVersionAlgorithm.RSA_SIGN_PKCS1_2048_SHA256
    )
    key = {
        "purpose": purpose,
        "version_template": {
            "algorithm": algorithm,
        },
        # Optional: customize how long key versions should be kept before
        # destroying.
        "destroy_scheduled_duration": duration_pb2.Duration().FromTimedelta(
            datetime.timedelta(days=1)
        ),
    }

    # Call the API.
    created_key = client.create_crypto_key(
        request={"parent": key_ring_name, "crypto_key_id": key_id, "crypto_key": key}
    )
    print(f"Created asymmetric signing key: {created_key.name}")
    return created_key


# [END kms_create_key_asymmetric_sign]
