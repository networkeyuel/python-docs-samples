# Copyright 2020 Google LLC
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
import sys

from django.db import migrations
import google.auth
from google.cloud import secretmanager_v1


def createsuperuser(apps, schema_editor):
    """
    Dynamically create an admin user as part of a migration
    Password is pulled from Secret Manger (previously created as part of tutorial)
    """
    if os.getenv('TRAMPOLINE_CI', None):
        admin_password = "test"
    else:
        client = secretmanager_v1.SecretManagerServiceClient()

        # Get project value for identifying current context
        _, project = google.auth.default()

        # Retrieve the previously stored admin password
        PASSWORD_NAME = os.environ.get("PASSWORD_NAME", "superuser_password")
        name = f"projects/{project}/secrets/{PASSWORD_NAME}/versions/latest"
        admin_password = client.access_secret_version(name=name).payload.data.decode(
            "UTF-8"
        )
    
    # Create a new user using acquired password
    from django.contrib.auth.models import User

    User.objects.create_superuser("admin", password=admin_password)


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [migrations.RunPython(createsuperuser)]
