import boto3
import zipfile
import os

lambda_client = boto3.client('lambda', region_name='us-east-2')
role_arn = 'arn:aws:iam::094092120892:role/lambda-role-FaceProcessor'

def deploy_lambda():
    # Zip the lambda function
    with zipfile.ZipFile('lambda.zip', 'w') as z:
        z.write('lambda_function.py')

    with open('lambda.zip', 'rb') as f:
        zipped_code = f.read()

    # Create or update Lambda
    try:
        lambda_client.create_function(
            FunctionName='FaceProcessor',
            Runtime='python3.9',
            Role=role_arn,
            Handler='lambda_function.lambda_handler',
            Code={'ZipFile': zipped_code},
            Timeout=10,
            MemorySize=128
        )
        print("Lambda function created.")
    except lambda_client.exceptions.ResourceConflictException:
        lambda_client.update_function_code(
            FunctionName='FaceProcessor',
            ZipFile=zipped_code
        )
        print("Lambda function updated.")

if __name__ == "__main__":
    deploy_lambda()