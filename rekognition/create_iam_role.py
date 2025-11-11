import boto3
import json
from botocore.exceptions import ClientError

iam = boto3.client('iam')
sts = boto3.client('sts')
role_name = 'lambda-role-FaceProcessor'

def get_account_id():
    """Get the current AWS account ID"""
    try:
        response = sts.get_caller_identity()
        return response['Account']
    except Exception as e:
        print(f"Warning: Could not get account ID automatically: {e}")
        print("Using default account ID: 094092120892")
        return '094092120892'  # Fallback to default

def create_lambda_role():
    """Create IAM role for Lambda function with necessary permissions"""
    
    # Get AWS account ID
    account_id = get_account_id()
    print(f"Using AWS Account ID: {account_id}")
    
    # Trust policy that allows Lambda service to assume the role
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    # Policy document with permissions needed for the Lambda function
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": "arn:aws:logs:*:*:*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "rekognition:DetectFaces",
                    "rekognition:SearchFacesByImage",
                    "rekognition:DescribeCollection"
                ],
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "dynamodb:PutItem",
                    "dynamodb:GetItem",
                    "dynamodb:UpdateItem",
                    "dynamodb:DescribeTable"
                ],
                "Resource": f"arn:aws:dynamodb:us-east-2:{account_id}:table/FaceMetadata"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "sns:Publish"
                ],
                "Resource": f"arn:aws:sns:us-east-2:{account_id}:FaceDetectedTopic"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject"
                ],
                "Resource": f"arn:aws:s3:::rekognition-upload-bucket1/*"
            }
        ]
    }
    
    try:
        # Check if role already exists
        try:
            response = iam.get_role(RoleName=role_name)
            print(f"IAM role '{role_name}' already exists.")
            role_arn = response['Role']['Arn']
            
            # Update trust policy if needed
            try:
                iam.update_assume_role_policy(
                    RoleName=role_name,
                    PolicyDocument=json.dumps(trust_policy)
                )
                print("Trust policy updated.")
            except Exception as e:
                print(f"Note: Could not update trust policy: {e}")
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchEntity':
                # Role doesn't exist, create it
                print(f"Creating IAM role '{role_name}'...")
                response = iam.create_role(
                    RoleName=role_name,
                    AssumeRolePolicyDocument=json.dumps(trust_policy),
                    Description='IAM role for Face Recognition Lambda function'
                )
                role_arn = response['Role']['Arn']
                print(f"IAM role '{role_name}' created successfully.")
            else:
                print(f"Error checking role: {e}")
                return False
        
        # Attach inline policy to the role
        policy_name = f'{role_name}-policy'
        try:
            # Try to get existing policy
            iam.get_role_policy(RoleName=role_name, PolicyName=policy_name)
            print(f"Policy '{policy_name}' already exists. Updating...")
            # Delete old policy and create new one
            iam.delete_role_policy(RoleName=role_name, PolicyName=policy_name)
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchEntity':
                print(f"Creating policy '{policy_name}'...")
            else:
                print(f"Error checking policy: {e}")
        
        # Put the policy
        iam.put_role_policy(
            RoleName=role_name,
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_document)
        )
        print(f"Policy '{policy_name}' attached to role.")
        
        # Attach AWS managed policy for basic Lambda execution (CloudWatch Logs)
        try:
            iam.attach_role_policy(
                RoleName=role_name,
                PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
            )
            print("AWS managed policy 'AWSLambdaBasicExecutionRole' attached.")
        except ClientError as e:
            if e.response['Error']['Code'] == 'EntityAlreadyExists':
                print("AWS managed policy already attached.")
            else:
                print(f"Note: Could not attach managed policy: {e}")
        
        print(f"\n✅ IAM role setup complete!")
        print(f"Role ARN: {role_arn}")
        print(f"\nYou can now deploy the Lambda function using: python deploy_lambda.py")
        return True
        
    except Exception as e:
        print(f"Error creating IAM role: {e}")
        return False

if __name__ == "__main__":
    create_lambda_role()

