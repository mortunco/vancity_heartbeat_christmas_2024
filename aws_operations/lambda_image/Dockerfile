# Use Amazon Linux base image compatible with AWS Lambda
FROM public.ecr.aws/lambda/python:3.13

# Install the required packages
RUN pip install pandas --no-deps --no-cache-dir
RUN pip install numpy requests pytz --no-cache-dir

# Copy your Lambda function code into the container
COPY "get_evo_status.py" ${LAMBDA_TASK_ROOT}

# Set the CMD to your Lambda function handler
CMD ["get_evo_status.lambda_handler"]
