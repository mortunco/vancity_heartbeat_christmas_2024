# %%
import boto3
import pandas as pd

# AWS Session and S3 client
profile = "tunc_personal"
region = "us-west-2"
session = boto3.Session(profile_name=profile, region_name=region)
s3_client = session.client("s3")

# Configuration
bucket_name = "tunc-evo-athena"
key = "attempt1/51cb1441-c067-4703-99fc-26468c4497f6.csv"
local_file_path = "/Users/mortunco/Desktop/Tunc_Sukru/evo_project/athena_output/trips_jan3rd.csv"  # Local file name for the downloaded CSV

# Download the file from S3
s3_client.download_file(bucket_name, key, local_file_path)

# Read the file into Pandas
df = pd.read_csv(local_file_path)
print("Data downloaded and loaded successfully!")
print(df)
