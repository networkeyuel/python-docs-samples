#!/usr/bin/env python

# Copyright 2016 Google, Inc.
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

"""This application demonstrates how to upload and download encrypted blobs
(objects) in Google Cloud Storage.

Use `generate-encryption-key` to generate an example key:

    python encryption.py generate-encryption-key

Then use the key to upload and download files encrypted with a custom key.

For more information, see the README.md under /storage and the documentation
at https://cloud.google.com/storage/docs/encryption.
"""

import argparse
import base64
import os

from gcloud import storage


def generate_encryption_key():
    """Generates a 256 bit (32 byte) AES encryption key and prints the
    base64 representation.

    This is included for demonstration purposes. You should generate your own
    key. Please remember that encryption keys should be handled with a
    comprehensive security policy.
    """
    key = os.urandom(32)
    encoded_key = base64.b64encode(key).decode('utf-8')
    print('Base 64 encoded encryption key: {}'.format(encoded_key))


def upload_encrypted_blob(bucket_name, source_file_name,
                          destination_blob_name, base64_encryption_key):
    """Uploads a file to a Google Cloud Storage bucket using a custom
    encryption key.

    The file will be encrypted by Google Cloud Storage and only
    retrievable using the provided encryption key.
    """
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    # Encryption key must be an AES256 key represented as a bytestring with
    # 32 bytes. Since it's passed in as a base64 encoded string, it needs
    # to be decoded.
    encryption_key = base64.b64decode(base64_encryption_key)

    blob.upload_from_filename(
        source_file_name, encryption_key=encryption_key)

    print('File {} uploaded to {}.'.format(
        source_file_name,
        destination_blob_name))


def download_encrypted_blob(bucket_name, source_blob_name,
                            destination_file_name, base64_encryption_key):
    """Downloads a previously-encrypted blob from Google Cloud Storage.

    The encryption key provided must be the same key provided when uploading
    the blob.
    """
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    # Encryption key must be an AES256 key represented as a bytestring with
    # 32 bytes. Since it's passed in as a base64 encoded string, it needs
    # to be decoded.
    encryption_key = base64.b64decode(base64_encryption_key)

    blob.download_to_filename(
        destination_file_name, encryption_key=encryption_key)

    print('Blob {} downloaded to {}.'.format(
        source_blob_name,
        destination_file_name))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest='command')

    subparsers.add_parser(
        'generate-encryption-key', help=generate_encryption_key.__doc__)

    upload_parser = subparsers.add_parser(
        'upload', help=upload_encrypted_blob.__doc__)
    upload_parser.add_argument(
        'bucket_name', help='Your cloud storage bucket.')
    upload_parser.add_argument('source_file_name')
    upload_parser.add_argument('destination_blob_name')
    upload_parser.add_argument('base64_encryption_key')

    download_parser = subparsers.add_parser(
        'download', help=download_encrypted_blob.__doc__)
    download_parser.add_argument(
        'bucket_name', help='Your cloud storage bucket.')
    download_parser.add_argument('source_blob_name')
    download_parser.add_argument('destination_file_name')
    download_parser.add_argument('base64_encryption_key')

    args = parser.parse_args()

    if args.command == 'generate-encryption-key':
        generate_encryption_key()
    elif args.command == 'upload':
        upload_encrypted_blob(
            args.bucket_name,
            args.source_file_name,
            args.destination_blob_name,
            args.base64_encryption_key)
    elif args.command == 'download':
        download_encrypted_blob(
            args.bucket_name,
            args.source_blob_name,
            args.destination_file_name,
            args.base64_encryption_key)
