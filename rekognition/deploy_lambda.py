import boto3
import zipfile
import os
from botocore.exceptions import ClientError

lambda_client = boto3.client('lambda', region_name='us-east-2')
iam = boto3.client('iam')
sts = boto3.client('sts')
role_name = 'lambda-role-FaceProcessor'

def get_role_arn():
    """Get the IAM role ARN for Lambda function"""
    try:
        # Try to get the role
        response = iam.get_role(RoleName=role_name)
        return response['Role']['Arn']
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchEntity':
            # Role doesn't exist, get account ID and construct ARN
            try:
                account_id = sts.get_caller_identity()['Account']
                return f'arn:aws:iam::{account_id}:role/{role_name}'
            except Exception:
                # Fallback to default account ID
                return f'arn:aws:iam::094092120892:role/{role_name}'
        else:
            # Other error, try to construct ARN
            try:
                account_id = sts.get_caller_identity()['Account']
                return f'arn:aws:iam::{account_id}:role/{role_name}'
            except Exception:
                return f'arn:aws:iam::094092120892:role/{role_name}'

def deploy_lambda():
    # Get the role ARN
    role_arn = get_role_arn()
    print(f"Using IAM Role ARN: {role_arn}")
    
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
        except lambda_client.exceptions.InvalidParameterValueException as e:
            error_msg = str(e)
            if "cannot be assumed by Lambda" in error_msg or "The role defined for the function cannot be assumed" in error_msg:
                print(f"\n❌ Error: IAM role cannot be assumed by Lambda.")
                print(f"   Role ARN: {role_arn}")
                print(f"\n💡 Solution: Create the IAM role first by running:")
                print(f"   python create_iam_role.py")
                print(f"\n   Or run the full pipeline:")
                print(f"   python pipline.py")
            else:
                print(f"Error deploying Lambda function: {error_msg}")
            return False
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