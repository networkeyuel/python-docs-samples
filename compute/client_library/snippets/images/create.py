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
# flake8: noqa


# This file is automatically generated. Please do not modify it directly.
# Find the relevant recipe file in the samples/recipes or samples/ingredients
# directory and apply your changes there.


# [START compute_windows_image_create]
# [START compute_images_create]
from __future__ import annotations

import sys
from typing import Any
import warnings

from google.api_core.extended_operation import ExtendedOperation
from google.cloud import compute_v1


def wait_for_extended_operation(
    operation: ExtendedOperation, verbose_name: str = "operation", timeout: int = 300
) -> Any:
    """
    Waits for the extended (long-running) operation to complete.

    If the operation is successful, it will return its result.
    If the operation ends with an error, an exception will be raised.
    If there were any warnings during the execution of the operation
    they will be printed to sys.stderr.

    Args:
        operation: a long-running operation you want to wait on.
        verbose_name: (optional) a more verbose name of the operation,
            used only during error and warning reporting.
        timeout: how long (in seconds) to wait for operation to finish.
            If None, wait indefinitely.

    Returns:
        Whatever the operation.result() returns.

    Raises:
        This method will raise the exception received from `operation.exception()`
        or RuntimeError if there is no exception set, but there is an `error_code`
        set for the `operation`.

        In case of an operation taking longer than `timeout` seconds to complete,
        a `concurrent.futures.TimeoutError` will be raised.
    """
    result = operation.result(timeout=timeout)

    if operation.error_code:
        print(
            f"Error during {verbose_name}: [Code: {operation.error_code}]: {operation.error_message}",
            file=sys.stderr,
            flush=True,
        )
        print(f"Operation ID: {operation.name}", file=sys.stderr, flush=True)
        raise operation.exception() or RuntimeError(operation.error_message)

    if operation.warnings:
        print(f"Warnings during {verbose_name}:\n", file=sys.stderr, flush=True)
        for warning in operation.warnings:
            print(f" - {warning.code}: {warning.message}", file=sys.stderr, flush=True)

    return result


STOPPED_MACHINE_STATUS = (
    compute_v1.Instance.Status.TERMINATED.name,
    compute_v1.Instance.Status.STOPPED.name,
)


def create_image_from_disk(
    project_id: str,
    zone: str,
    source_disk_name: str,
    image_name: str,
    storage_location: str | None = None,
    force_create: bool = False,
) -> compute_v1.Image:
    """
    Creates a new disk image.

    Args:
        project_id: project ID or project number of the Cloud project you use.
        zone: zone of the disk you copy from.
        source_disk_name: name of the source disk you copy from.
        image_name: name of the image you want to create.
        storage_location: storage location for the image. If the value is undefined,
            function will store the image in the multi-region closest to your image's
            source location.
        force_create: create the image even if the source disk is attached to a
            running instance.

    Returns:
        An Image object.
    """
    image_client = compute_v1.ImagesClient()
    disk_client = compute_v1.DisksClient()
    instance_client = compute_v1.InstancesClient()

    # Get source disk
    disk = disk_client.get(project=project_id, zone=zone, disk=source_disk_name)

    for disk_user in disk.users:
        instance = instance_client.get(
            project=project_id, zone=zone, instance=disk_user
        )
        if instance.status in STOPPED_MACHINE_STATUS:
            continue
        if not force_create:
            raise RuntimeError(
                f"Instance {disk_user} should be stopped. For Windows instances please "
                f"stop the instance using `GCESysprep` command. For Linux instances just "
                f"shut it down normally. You can supress this error and create an image of"
                f"the disk by setting `force_create` parameter to true (not recommended). \n"
                f"More information here: \n"
                f" * https://cloud.google.com/compute/docs/instances/windows/creating-windows-os-image#api \n"
                f" * https://cloud.google.com/compute/docs/images/create-delete-deprecate-private-images#prepare_instance_for_image"
            )
        else:
            warnings.warn(
                f"Warning: The `force_create` option may compromise the integrity of your image. "
                f"Stop the {disk_user} instance before you create the image if possible."
            )

    # Create image
    image = compute_v1.Image()
    image.source_disk = disk.self_link
    image.name = image_name
    if storage_location:
        image.storage_locations = [storage_location]

    operation = image_client.insert(project=project_id, image_resource=image)

    wait_for_extended_operation(operation, "image creation from disk")

    return image_client.get(project=project_id, image=image_name)


# [END compute_images_create]
# [END compute_windows_image_create]
