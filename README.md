
## AWS Section Setup

### S3 Setup
We need to create a S3 bucket for this operation. If you take a look at get_evo_status.py you will see that it will upload csv files to `s3://tunc-evo/raw` so make sure you create them.

#### Lambda Setup
```
cd aws_operations/lambda_image
docker build --platform linux/amd64 -t my-lambda-function . ### lambda is default x86_64. I have a mac and docker was created with ARM. This is the fix for that.
### ACCOUNTNUMBER is AWS account number. I removed it for privacy
### DUMMYNAME is the name of the image. I removed it for privacy
docker tag my-lambda-function:latest ACCOUNTNUMBER.dkr.ecr.us-west-2.amazonaws.com/DUMMYNAME:latest
docker push 870145404826.dkr.ecr.us-west-2.amazonaws.com/DUMMYNAME:latest
```

#### Set Time threshold for Lambda Function
```
aws lambda update-function-code --function-name evo_get_loc_2 \
    --image-uri ACCOUNTNUMBER.dkr.ecr.us-west-2.amazonaws.com/DUMMYNAME:latest
    --timeout 60
```

#### Make it run every 5 minutes
Create a trigger using AWS event bridge
```
aws events put-rule \
    --name "InvokeEvoGetLoc2Every5Minutes" \
    --schedule-expression "rate(5 minutes)" 

### Assign it to lambda function
aws events put-targets \
    --rule "InvokeEvoGetLoc2Every5Minutes" \
    --targets "Id"="1","Arn"=$(aws lambda get-function \
        --function-name evo_get_loc_2 \
        --query "Configuration.FunctionArn" \
        --output text ) \

### Add permission
aws lambda add-permission \
    --function-name evo_get_loc_2 \
    --statement-id "AllowEventBridgeTrigger" \
    --action "lambda:InvokeFunction" \
    --principal "events.amazonaws.com" \
    --source-arn $(aws events list-rules \
        --name-prefix "InvokeEvoGetLoc2Every5Minutes" \
        --query "Rules[0].Arn" \
        --output text ) \
```
## Athena Setup.
(I dont know how to share this but these are my Athena queries to create my trips table.)

Following code reads all the CSVs and merges them into a giant table. (This section could be improved)
```
CREATE EXTERNAL TABLE `evo_car.evo_car_locations_1`(
  `id` string, 
  `plate` string, 
  `lat` float, 
  `lon` float, 
  `energylevel` int, 
  `retrieved_datestamp` string, 
  `retrieved_timestamp` string)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ',' 
STORED AS TEXTFILE
LOCATION
  's3://tunc-evo/raw'
TBLPROPERTIES (
  'skip.header.line.count'='1',
  'classification'='csv'
);
```
Following code, creates the table that i used in this experiment. I also shared this table in the athena_output so feel free to use that one if you dont have access to Athena. This section is mainly for me to remember this in the future.
```
CREATE TABLE "evo_car"."trips_jan3" WITH (format = 'parquet') AS WITH grouped_data AS (
  SELECT plate,
    lat,
    lon,
    MAX(
      CAST(
        CONCAT(
          REGEXP_REPLACE(retrieved_datestamp, '/', '-'),
          ' ',
          retrieved_timestamp
        ) AS TIMESTAMP
      )
    ) AS last_time
  FROM evo_car.evo_car_locations_1
  GROUP BY plate,
    lat,
    lon
),
ordered_data AS (
  SELECT plate,
    lat,
    lon,
    last_time,
    ROW_NUMBER() OVER (
      PARTITION BY plate
      ORDER BY last_time
    ) AS row_num
  FROM grouped_data
)
SELECT a.plate,
  a.lat AS lat1,
  a.lon AS long1,
  b.lat AS lat2,
  b.lon AS long2,
  a.last_time AS time1,
  b.last_time AS time2
FROM ordered_data a
  JOIN ordered_data b ON a.plate = b.plate
  AND a.row_num = b.row_num - 1
ORDER BY a.plate,
  time1;
```

## Visualisation
I used Foursquare Studio to visualise this data. You can see my workspace here. Feel free to play with it. I wanted to stress on the drop on Christmas Day, therefore made the dot plot in Vancouver Harbour in a dirty way. There is definetely room for improvement here to use more moduler options.

There is also an easter egg here. If you zoom out you will actually see all of the EVOs in BC which includes Nanaimo and Victoria.

https://studio.foursquare.com/map/public/91cd2435-77eb-4c29-84c1-dd34e33971e2/embed
