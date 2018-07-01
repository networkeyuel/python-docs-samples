# Copyright 2016 Google Inc.
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

import os
import random


from tableadmin import run_table_operations
from tableadmin import delete_table
from _pytest.capture import capsys

PROJECT = os.environ['GCLOUD_PROJECT']
BIGTABLE_CLUSTER = os.environ['BIGTABLE_CLUSTER']
TABLE_NAME_FORMAT = 'hello-bigtable-system-tests-{}'
TABLE_NAME_RANGE = 10000


def test_run_table_operations(capsys):
    table_name = TABLE_NAME_FORMAT.format(
        random.randrange(TABLE_NAME_RANGE))

    run_table_operations(PROJECT, BIGTABLE_CLUSTER, table_name)
    out, _ = capsys.readouterr()
    assert 'Creating the {} table.'.format(table_name) in out
    assert not 'Table {} already exists.'.format(table_name) in out
    assert 'Listing tables in current project.' in out
    assert not 'Error creating table {}.'.format(table_name) in out
    assert 'Creating column family cf1 with with MaxAge GC Rule' in out
    assert 'Created MaxAge GC rule.' in out
    assert not 'Error creating MaxAge GC Rule.' in out
    assert 'Created column family cf1 with MaxAge GC Rule.' in out
    assert not 'Error creating column family with MaxAge GC Rule.' in out
    assert 'Created Max Versions GC Rule.' in out
    assert not 'Error creating Max Versions GC Rule.' in out
    assert 'Created column family cf2 with Max Versions GC Rule.' in out
    assert not 'Error creating column family with Max Versions GC Rule.' in out
    assert 'Created Union GC Rule.' in out
    assert not 'Error creating Union GC Rule.' in out
    assert 'Created column family cf3 with Union GC rule' in out
    assert not 'Error creating column family with Union GC rule' in out
    assert 'Created Intersection GC Rule.' in out
    assert not 'Error creating Intersection GC Rule.' in out
    assert 'Created column family cf4 with Intersection GC rule.' in out
    assert not 'Error creating column family with Intersection GC rule.' in out
    assert 'Created Nested GC Rule.' in out
    assert not 'Error creating Nested GC Rule.' in out
    assert 'Created column family cf5 with a Nested GC rule.' in out
    assert not 'Error creating column family with a Nested GC rule.' in out
    assert 'Printing Column Family and GC Rule for all column families.' in out
    assert not 'Error Column Family and GC Rule.' in out
    
    delete_table(PROJECT, BIGTABLE_CLUSTER, table_name)
    out, _ = capsys.readouterr()
    assert 'Table {} exists.'.format(table_name) in out
    assert 'Deleting {} table.'.format(table_name) in out
    assert 'Deleted {} table.'.format(table_name) in out
    assert not 'Table {} does not exists.'.format(table_name) in out
    
    
    
    
    
    
    
    
    