#!/usr/bin/env python

# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Sample command-line program for interacting with the Cloud Tasks API.

See README.md for instructions on setting up your development environment
and running the scripts.
"""

import argparse
import base64

from googleapiclient import discovery


def list_queues(project_id, location_id):
    """List the queues in the location."""
    DISCOVERY_URL = (
        'https://cloudtasks.googleapis.com/$discovery/rest?version=v2beta2')
    client = discovery.build('cloudtasks', 'v2beta2',
                             discoveryServiceUrl=discovery_url)
    parent = 'projects/{}/locations/{}'.format(project_id, location_id)
    queues = []
    next_page_token = None

    while True:
        queues_api = client.projects().locations().queues()
        response = queues_api.list(
            parent=parent, pageToken=next_page_token).execute()
        queues += response['queues']
        if next_page_token is None:
            break

    print('Listing queues for location {}'.format(location_id))

    for queue in response['queues']:
        print queue['name']
    return response


def create_task(queue_name):
    """Create a task for a given queue with an arbitrary payload."""
    DISCOVERY_URL = (
        'https://cloudtasks.googleapis.com/$discovery/rest?version=v2beta2')
    client = discovery.build('cloudtasks', 'v2beta2',
                             discoveryServiceUrl=discovery_url)
    payload = 'a message for the recipient'
    task = {
        'task': {
            'pull_task_target': {
                'payload': base64.b64encode(payload)
            }
        }
    }
    response = client.projects().locations().queues().tasks().create(
        parent=queue_name, body=task).execute()
    print('Created task {}'.format(response['name']))
    return response


def pull_task(queue_name):
    """Pull a single task from a given queue and lease it for 10 minutes."""
    DISCOVERY_URL = (
        'https://cloudtasks.googleapis.com/$discovery/rest?version=v2beta2')
    client = discovery.build('cloudtasks', 'v2beta2',
                             discoveryServiceUrl=discovery_url)
    duration_seconds = '600s'
    pull_options = {
        'max_tasks': 1,
        'leaseDuration': duration_seconds,
        'responseView': 'FULL'
    }
    response = client.projects().locations().queues().tasks().pull(
        name=queue_name, body=pull_options).execute()
    print('Pulled task {}'.format(response))
    return response['tasks'][0]


def acknowledge_task(task):
    """Acknowledge a given task."""
    DISCOVERY_URL = (
        'https://cloudtasks.googleapis.com/$discovery/rest?version=v2beta2')
    client = discovery.build('cloudtasks', 'v2beta2',
                             discoveryServiceUrl=discovery_url)
    body = {'scheduleTime': task['scheduleTime']}
    client.projects().locations().queues().tasks().acknowledge(
        name=task['name'], body=body).execute()
    print('Acknowledged task {}'.format(task['name']))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    subparsers = parser.add_subparsers(dest='command')

    list_queues_parser = subparsers.add_parser(
        'list-queues',
        help=list_queues.__doc__)

    list_queues_parser.add_argument(
        '--project_id',
        help='Project ID you want to access.',
        required=True)
    list_queues_parser.add_argument(
        '--location_id',
        help='Location of the queues.',
        required=True)

    create_task_parser = subparsers.add_parser(
        'create-task',
        help=create_task.__doc__)
    create_task_parser.add_argument(
        '--queue_name',
        help='Fully qualified name of the queue to add the task to.')

    pull_and_ack_parser = subparsers.add_parser(
        'pull-and-ack-task',
        help=create_task.__doc__)
    pull_and_ack_parser.add_argument(
        '--queue_name',
        help='Fully qualified name of the queue to add the task to.')

    args = parser.parse_args()

    if args.command == 'list-queues':
        list_queues(args.project_id, args.location_id)
    if args.command == 'create-task':
        create_task(args.queue_name)
    if args.command == 'pull-and-ack-task':
        task = pull_task(args.queue_name)
        acknowledge_task(task)
