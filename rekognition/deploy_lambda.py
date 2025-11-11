import boto3
import zipfile
import os

lambda_client = boto3.client('lambda', region_name='us-east-2')
role_arn = 'arn:aws:iam::094092120892:role/lambda-role-FaceProcessor'

def deploy_lambda():
    # Check if lambda-func.py exists
    lambda_file = 'lambda-func.py'
    if not os.path.exists(lambda_file):
        print(f"Error: {lambda_file} not found in current directory.")
        print(f"Current directory: {os.getcwd()}")
        return False
    
    # Zip the lambda function
    zip_file = 'lambda.zip'
    try:
        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as z:
            z.write(lambda_file, 'lambda_function.py')  # Write as lambda_function.py in zip
        
        with open(zip_file, 'rb') as f:
            zipped_code = f.read()
        
        # Create or update Lambda
        try:
            lambda_client.create_function(
                FunctionName='FaceProcessor',
                Runtime='python3.9',
                Role=role_arn,
                Handler='lambda_function.lambda_handler',
                Code={'ZipFile': zipped_code},
                Timeout=30,  # Increased timeout for Rekognition processing
                MemorySize=256,  # Increased memory for better performance
                Environment={
                    'Variables': {
                        'DYNAMO_TABLE': 'FaceMetadata',
                        'SNS_TOPIC_ARN': 'arn:aws:sns:us-east-2:094092120892:FaceDetectedTopic',
                        'REKOGNITION_COLLECTION': 'employeeFaces'
                    }
                }
            )
            print("Lambda function created successfully.")
        except lambda_client.exceptions.ResourceConflictException:
            # Function already exists, update the code and configuration
            lambda_client.update_function_code(
                FunctionName='FaceProcessor',
                ZipFile=zipped_code
            )
            # Update environment variables and configuration
            lambda_client.update_function_configuration(
                FunctionName='FaceProcessor',
                Timeout=30,
                MemorySize=256,
                Environment={
                    'Variables': {
                        'DYNAMO_TABLE': 'FaceMetadata',
                        'SNS_TOPIC_ARN': 'arn:aws:sns:us-east-2:094092120892:FaceDetectedTopic',
                        'REKOGNITION_COLLECTION': 'employeeFaces'
                    }
                }
            )
            print("Lambda function code and configuration updated successfully.")
        except Exception as e:
            print(f"Error deploying Lambda function: {str(e)}")
            return False
        
        return True
    except Exception as e:
        print(f"Error creating Lambda package: {str(e)}")
        return False
    finally:
        # Clean up zip file
        if os.path.exists(zip_file):
            os.remove(zip_file)
            print("Cleanup: Removed lambda.zip")

if __name__ == "__main__":
    deploy_lambda()