# %%
import boto3
import pandas as pd
import time

# AWS profile and region
profile = "tunc_personal"  # Specify if you're using named profiles
region = "us-west-2"

# Create Athena client
session = boto3.Session(profile_name=profile, region_name=region)
athena_client = session.client("athena")
credentials = session.get_credentials().get_frozen_credentials()

# Configuration
DATABASE = "evo_car"
OUTPUT_LOCATION = "s3://tunc-evo-athena/attempt1"  # S3 bucket for query results

# Athena Query
QUERY = "SELECT * FROM evo_car.trips_jan3;"

def run_athena_query(client, query, database, output_location):
    response = client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={"Database": database},
        ResultConfiguration={"OutputLocation": output_location},
    )
    return response["QueryExecutionId"]

# Run query
query_id = run_athena_query(athena_client, QUERY, DATABASE, OUTPUT_LOCATION)

# Wait for query to complete
while True:
    status = athena_client.get_query_execution(QueryExecutionId=query_id)["QueryExecution"]["Status"]["State"]
    if status in ["SUCCEEDED", "FAILED", "CANCELLED"]:
        break
    time.sleep(2)

# Check if query succeeded
if status == "SUCCEEDED":
    print("Query succeeded!")
    result_location = f"{OUTPUT_LOCATION}/{query_id}.csv"
    print(f"Result file: {result_location}")
else:
    print(f"Query failed with status: {status}")

# Load results into Pandas
results = pd.read_csv(result_location, storage_options={
    'key': credentials.access_key,
    'secret': credentials.secret_key
})
print(results)

# %%
