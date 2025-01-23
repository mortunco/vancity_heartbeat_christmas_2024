import pandas as pd
import requests
from datetime import datetime
import pytz
import os
import boto3

def upload_to_s3(file_path):
    try:
        bucket_name = "tunc-evo"
        s3_key = f"raw/{os.path.basename(file_path)}"  # Adjust key as needed
        s3 = boto3.client('s3')
        s3.upload_file(file_path, bucket_name, s3_key)
        print(f"File uploaded to S3: s3://{bucket_name}/{s3_key}")
        return {"statusCode": 200, "body": f"File uploaded to S3: s3://{bucket_name}/{s3_key}"}
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        return {"statusCode": 500, "body": str(e)}
    
def test_libraries():
    try:
        # Test pandas
        data = {'Name': ['Alice', 'Bob'], 'Age': [25, 30]}
        df = pd.DataFrame(data)
        print("Pandas Test Passed: DataFrame created successfully")
        
        # Test requests
        response = requests.get("https://jsonplaceholder.typicode.com/posts/1")
        if response.status_code == 200:
            print("Requests Test Passed: Successfully fetched data from API")
        else:
            print(f"Requests Test Failed: Status code {response.status_code}")
        
        # Test pytz
        tz = pytz.timezone('America/Los_Angeles')
        print("Pytz Test Passed: Timezone 'US/Eastern' loaded successfully")
        
        return {"statusCode": 200, "body": "All libraries are working fine."}
    except Exception as e:
        print(f"Test Failed: {e}")
        return {"statusCode": 500, "body": str(e)}

def run_main_logic():
    # Your main script logic goes here
    
    # Contact the authentication API to get a token
    oauth_url = 'https://java-us01.vulog.com/auth/realms/BCAA-CAYVR/protocol/openid-connect/token/'
    data = {
        'grant_type': 'client_credentials',
        'scope': '',
        'client_id': 'BCAA-CAYVR_anon',
        'client_secret': 'dbe490f4-2f4a-4bef-8c0b-52c0ecedb6c8'
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept-Encoding': 'gzip'
    }

    response = requests.post(oauth_url, data=data, headers=headers)
    response = response.json()
    access_token = response['access_token']
    refresh_token = response['refresh_token']

    # Contact the data API using the token from above to access the evo location data
    data_url = 'https://java-us01.vulog.com/apiv5/availableVehicles/fc256982-77d1-455c-8ab0-7862c170db6a'

    headers1 = {
        'user-lat': '49.273351',
        'user-lon': '-123.102684',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Connection': 'close',
        'Authorization': 'bearer ' + str(access_token),
        'X-API-Key': 'f52e5e56-c7db-4af0-acf5-0d8b13ac4bfc',
        'Host': 'java-us01.vulog.com',
        'Accept-Encoding': 'gzip',
        'User-Agent': 'okhttp/3.12.8'
    }

    response = requests.get(data_url, headers=headers1)
    response = response.json()

    # Assign the JSON data to a pandas DataFrame
    df = pd.DataFrame(response)

    # Extract the data from the nested dataframes
    df_status = pd.DataFrame(df['status'].to_dict()).transpose()
    df_description = pd.DataFrame(df['description'].to_dict()).transpose()
    df_location = pd.DataFrame(df['location'].to_dict()).transpose()

    # Merge the extracted data back into one DataFrame 
    evo_data = pd.merge(df_status, df_description, left_index=True, right_index=True)
    evo_data = pd.merge(evo_data, df_location, left_index=True, right_index=True)

    # Split the location variable into lat and lon variables
    evo_data_coor = pd.DataFrame(evo_data['position'].to_dict()).transpose()
    evo_data = pd.merge(evo_data, evo_data_coor, left_index=True, right_index=True)

    # Set timezone to PST
    pst_timezone = pytz.timezone('America/Los_Angeles')
    current_time_pst = datetime.now(pst_timezone)

    # Add retrieved date and timestamp in PST
    evo_data['retrieved_datestamp'] = current_time_pst.strftime('%Y/%m/%d')
    evo_data['retrieved_timestamp'] = current_time_pst.strftime('%H:%M:%S')

    # Extract the variables of interest
    evo_data = evo_data[['id', 'plate', 'lat', 'lon', 'energyLevel', 'retrieved_datestamp', 'retrieved_timestamp']]

    # Ensure the directory exists before saving
    output_dir = "/tmp/"
    os.makedirs(output_dir, exist_ok=True)

    # Define the filename based on the current PST date and time (down to the minute)
    filename = f"evo_{current_time_pst.strftime('%Y_%m_%d_%H_%M')}.csv"

    #upload_to_s3(filename)
    evo_data.to_csv(f"/tmp/{filename}", mode='w', index=False, header=True)
    upload_to_s3(f"/tmp/{filename}")
    
    print('Done!')

    return {"statusCode": 200, "body": "Main logic executed successfully."}

# Lambda handler
def lambda_handler(event, context):
    return run_main_logic()
