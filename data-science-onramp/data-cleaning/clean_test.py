import os
import re
import uuid

from google.cloud import bigquery
from google.cloud import dataproc_v1 as dataproc
from google.cloud import storage
import pandas as pd
import pytest

# GCP project
PROJECT_ID = os.environ["GOOGLE_CLOUD_PROJECT"]
TEST_ID = uuid.uuid4()

# Google Cloud Storage constants
BUCKET_NAME = f"clean-test-code-{TEST_ID}"
BUCKET_BLOB = "clean.py"

# Big Query constants
BQ_DATASET = f"{PROJECT_ID}.clean_test_{str(TEST_ID).replace('-', '_')}"
BQ_TABLE = f"{BQ_DATASET}.dirty_data"
CSV_FILE = "testing_data/raw_data.csv"

# Dataproc constants
DATAPROC_CLUSTER = f"clean-test-{TEST_ID}"
CLUSTER_REGION = "us-central1"
CLUSTER_IMAGE = "1.5.4-debian10"
CLUSTER_CONFIG = {  # Dataproc cluster configuration
    "project_id": PROJECT_ID,
    "cluster_name": DATAPROC_CLUSTER,
    "config": {
        "gce_cluster_config": {
            "zone_uri": "",
            "metadata": {"PIP_PACKAGES": "google-cloud-storage"},
        },
        "master_config": {"num_instances": 1, "machine_type_uri": "n1-standard-8"},
        "worker_config": {"num_instances": 6, "machine_type_uri": "n1-standard-8"},
        "software_config": {
            "image_version": CLUSTER_IMAGE,
            "optional_components": ["ANACONDA"],
        },
    },
}
DATAPROC_JOB = {    # Dataproc job configuration
    "placement": {"cluster_name": DATAPROC_CLUSTER},
    "pyspark_job": {
        "main_python_file_uri": f"gs://{BUCKET_NAME}/{BUCKET_BLOB}",
        "args": [BQ_TABLE, BUCKET_NAME, "--dry-run"],
        "jar_file_uris": ["gs://spark-lib/bigquery/spark-bigquery-latest_2.12.jar"],
    },
}


@pytest.fixture(autouse=True)
def setup_and_teardown_table():
    bq_client = bigquery.Client()

    # Create dataset and load table
    dataset = bigquery.Dataset(BQ_DATASET)
    dataset = bq_client.create_dataset(dataset)

    # Load table from dataframe
    df = pd.read_csv(CSV_FILE)
    job_config = bigquery.LoadJobConfig(
        autodetect=True,
        write_disposition="WRITE_TRUNCATE"
    )
    operation = bq_client.load_table_from_dataframe(
        df, BQ_TABLE, job_config=job_config
    )

    # Wait for job to complete
    operation.result()

    yield

    # Delete dataset
    bq_client.delete_dataset(BQ_DATASET, delete_contents=True)


@pytest.fixture(autouse=True)
def setup_and_teardown_cluster():
    # Create Dataproc cluster using cluster client
    cluster_client = dataproc.ClusterControllerClient(
        client_options={"api_endpoint": f"{CLUSTER_REGION}-dataproc.googleapis.com:443"}
    )
    operation = cluster_client.create_cluster(
        project_id=PROJECT_ID, region=CLUSTER_REGION, cluster=CLUSTER_CONFIG
    )

    # Wait for cluster to provision
    operation.result()

    yield

    # Delete cluster
    operation = cluster_client.delete_cluster(
        project_id=PROJECT_ID,
        region=CLUSTER_REGION,
        cluster_name=DATAPROC_CLUSTER,
        timeout=300
    )
    operation.result()


@pytest.fixture(autouse=True)
def setup_and_teardown_bucket():
    # Create GCS bucket
    storage_client = storage.Client()
    bucket = storage_client.create_bucket(BUCKET_NAME)

    # Upload file
    blob = bucket.blob(BUCKET_BLOB)
    blob.upload_from_filename("clean.py")

    yield

    # Delete GCS bucket
    bucket = storage_client.get_bucket(BUCKET_NAME)
    bucket.delete(force=True)


def is_in_table(value, out):
    return re.search(f"\\| *{value} *\\|", out)


def get_blob_from_path(path):
    bucket_name = re.search("dataproc.+?/", path).group(0)[0:-1]
    bucket = storage.Client().get_bucket(bucket_name)
    output_location = re.search("google-cloud-dataproc.+", path).group(0)
    return bucket.blob(output_location)


def test_clean():
    """Tests clean.py by submitting it to a Dataproc cluster"""
    # Submit job to Dataproc cluster
    job_client = dataproc.JobControllerClient(
        client_options={"api_endpoint": f"{CLUSTER_REGION}-dataproc.googleapis.com:443"}
    )
    operation = job_client.submit_job_as_operation(
        project_id=PROJECT_ID, region=CLUSTER_REGION, job=DATAPROC_JOB
    )

    # Wait for job to complete
    result = operation.result()

    # Get job output
    output_location = result.driver_output_resource_uri + ".000000000"
    blob = get_blob_from_path(output_location)
    out = blob.download_as_string().decode("utf-8")

    # trip duration
    assert not is_in_table(r"\d*.\d* s", out)
    assert not is_in_table(r"\d*.\d* min", out)
    assert not is_in_table(r"\d*.\d* h", out)

    # station latitude & longitude
    assert not is_in_table(r"\d+" + "\u00B0" + r"\d+\'\d+\"", out)

    assert is_in_table(r"\d*.\d*", out)

    # gender
    assert not is_in_table("M", out)
    assert not is_in_table("m", out)
    assert not is_in_table("male", out)
    assert not is_in_table("MALE", out)
    assert not is_in_table("F", out)
    assert not is_in_table("f", out)
    assert not is_in_table("female", out)
    assert not is_in_table("FEMALE", out)
    assert not is_in_table("U", out)
    assert not is_in_table("u", out)
    assert not is_in_table("unknown", out)
    assert not is_in_table("UNKNOWN", out)

    assert is_in_table("Male", out)
    assert is_in_table("Female", out)

    # customer plan
    assert not is_in_table("subscriber", out)
    assert not is_in_table("SUBSCRIBER", out)
    assert not is_in_table("sub", out)
    assert not is_in_table("customer", out)
    assert not is_in_table("CUSTOMER", out)
    assert not is_in_table("cust", out)

    assert is_in_table("Subscriber", out)
    assert is_in_table("Customer", out)
