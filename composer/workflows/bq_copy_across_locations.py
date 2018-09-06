# Copyright 2018 Google LLC
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

"""Example Airflow DAG that performs an export from BQ tables listed in
config file to GCS, copies GCS objects across locations (e.g., from US to
EU) then imports from GCS to BQ. The DAG imports the gcs_to_gcs operator
from plugins and dynamically builds the tasks based on the list of tables.
Lastly, the DAG defines a specific application logger to generate logs.

This DAG relies on three Airflow variables
(https://airflow.apache.org/concepts.html#variables):
* table_list_file_path - CSV file listing source and target tables, including
Datasets.
* gcs_source_bucket - Google Cloud Storage bucket to use for exporting
BigQuery tables in source.
* gcs_dest_bucket - Google Cloud Storage bucket to use for importing
BigQuery tables in destination.
See https://cloud.google.com/storage/docs/creating-buckets for creating a
bucket.
"""

# --------------------------------------------------------------------------------
# Load The Dependencies
# --------------------------------------------------------------------------------

import csv
from datetime import datetime
from datetime import timedelta
import logging

from airflow import models
from airflow.contrib.operators import bigquery_to_gcs
from airflow.contrib.operators import gcs_to_bq
from airflow.operators import dummy_operator
# Import operator from plugins
from gcs_plugin.operators import gcs_to_gcs


# --------------------------------------------------------------------------------
# Set default arguments
# --------------------------------------------------------------------------------

default_args = {
    'owner': 'airflow',
    'start_date': datetime.today(),
    'depends_on_past': False,
    'email': [''],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# --------------------------------------------------------------------------------
# Set variables
# --------------------------------------------------------------------------------

# 'table_list_file_path': This variable will contain the location of the master
# file.
table_list_file_path = models.Variable.get('table_list_file_path')

# Source Bucket
source_bucket = models.Variable.get('gcs_source_bucket')

# Destination Bucket
dest_bucket = models.Variable.get('gcs_dest_bucket')

# --------------------------------------------------------------------------------
# Set GCP logging
# --------------------------------------------------------------------------------

logger = logging.getLogger('bq_copy_us_to_eu_01')

# --------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------


def read_table_list(table_list_file):
    """
    Reads the master CSV file that will help in creating Airflow tasks in
    the DAG dynamically.
    :param table_list_file: (String) The file location of the master file,
    e.g. '/home/airflow/framework/master.csv'
    :return master_record_all: (List) List of Python dictionaries containing
    the information for a single row in master CSV file.
    """
    master_record_all = []
    logger.info('Reading table_list_file from : %s' % str(table_list_file))
    try:
        with open(table_list_file, 'rb') as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)  # skip the headers
            for row in csv_reader:
                logger.info(row)
                master_record = {
                    'table_source': row[0],
                    'table_dest': row[1]
                }
                master_record_all.append(master_record)
            return master_record_all
    except IOError as e:
        logger.error('Error opening table_list_file %s: ' % str(
            table_list_file), e)


# --------------------------------------------------------------------------------
# Main DAG
# --------------------------------------------------------------------------------

# Define a DAG (directed acyclic graph) of tasks.
# Any task you create within the context manager is automatically added to the
# DAG object.
with models.DAG('bq_copy_us_to_eu_01',
                default_args=default_args,
                schedule_interval=None) as dag:
    start = dummy_operator.DummyOperator(
        task_id='start',
        trigger_rule='all_success'
    )

    end = dummy_operator.DummyOperator(
        task_id='end',

        trigger_rule='all_success'
    )

    # Get the table list from master file
    all_records = read_table_list(table_list_file_path)

    # Loop over each record in the 'all_records' python list to build up
    # Airflow tasks
    for record in all_records:
        logger.info('Generating tasks to transfer table: {}'.format(record))

        table_source = record['table_source']
        table_dest = record['table_dest']

        BQ_to_GCS = bigquery_to_gcs.BigQueryToCloudStorageOperator(
            # Replace ":" with valid character for Airflow task
            task_id='{}_BQ_to_GCS'.format(table_source.replace(":", "_")),
            source_project_dataset_table=table_source,
            destination_cloud_storage_uris=['{}-*.avro'.format(
                'gs://' + source_bucket + '/' + table_source)],
            export_format='AVRO'
        )

        GCS_to_GCS = gcs_to_gcs.GoogleCloudStorageToGoogleCloudStorageOperator(
            # Replace ":" with valid character for Airflow task
            task_id='{}_GCS_to_GCS'.format(table_source.replace(":", "_")),
            source_bucket=source_bucket,
            source_object='{}-*.avro'.format(table_source),
            destination_bucket=dest_bucket,
            # destination_object='{}-*.avro'.format(table_dest)
        )

        GCS_to_BQ = gcs_to_bq.GoogleCloudStorageToBigQueryOperator(
            # Replace ":" with valid character for Airflow task
            task_id='{}_GCS_to_BQ'.format(table_dest.replace(":", "_")),
            bucket=dest_bucket,
            source_objects=['{}-*.avro'.format(table_source)],
            destination_project_dataset_table=table_dest,
            source_format='AVRO',
            write_disposition='WRITE_TRUNCATE'
        )

        start >> BQ_to_GCS >> GCS_to_GCS >> GCS_to_BQ >> end
