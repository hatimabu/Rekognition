import boto3
import json

s3_client = boto3.client('s3', region_name='us-east-2')
lambda_client = boto3.client('lambda', region_name='us-east-2')

BUCKET_NAME = 'rekognition-upload-bucket1'
LAMBDA_FUNCTION_NAME = 'FaceProcessor'

def get_lambda_function_arn():
    """Get the ARN of the Lambda function"""
    try:
        response = lambda_client.get_function(FunctionName=LAMBDA_FUNCTION_NAME)
        return response['Configuration']['FunctionArn']
    except lambda_client.exceptions.ResourceNotFoundException:
        print(f"Error: Lambda function '{LAMBDA_FUNCTION_NAME}' not found.")
        print("Please deploy the Lambda function first using deploy_lambda.py")
        return None

def add_lambda_permission():
    """Add permission for S3 to invoke Lambda function"""
    lambda_arn = get_lambda_function_arn()
    if not lambda_arn:
        return False
    
    try:
        # Check if permission already exists by getting the policy
        try:
            policy_response = lambda_client.get_policy(FunctionName=LAMBDA_FUNCTION_NAME)
            policy = json.loads(policy_response['Policy'])
            # Check if our statement already exists
            statement_id = 's3-trigger-permission'
            existing_statements = policy.get('Statement', [])
            if any(stmt.get('Sid') == statement_id for stmt in existing_statements):
                print("Lambda permission already exists.")
                return True
        except lambda_client.exceptions.ResourceNotFoundException:
            # Policy doesn't exist, we'll create it
            pass
        
        # Add permission for S3 to invoke Lambda
        try:
            lambda_client.add_permission(
                FunctionName=LAMBDA_FUNCTION_NAME,
                StatementId='s3-trigger-permission',
                Action='lambda:InvokeFunction',
                Principal='s3.amazonaws.com',
                SourceArn=f'arn:aws:s3:::{BUCKET_NAME}'
            )
            print(f"Added permission for S3 bucket '{BUCKET_NAME}' to invoke Lambda function.")
            return True
        except lambda_client.exceptions.ResourceConflictException:
            print("Lambda permission already exists.")
            return True
    except Exception as e:
        print(f"Error adding Lambda permission: {str(e)}")
        return False

def configure_s3_event_notification():
    """Configure S3 bucket to trigger Lambda on object creation"""
    lambda_arn = get_lambda_function_arn()
    if not lambda_arn:
        return False
    
    # Check if bucket exists
    try:
        s3_client.head_bucket(Bucket=BUCKET_NAME)
    except s3_client.exceptions.ClientError:
        print(f"Error: S3 bucket '{BUCKET_NAME}' not found.")
        print("Please create the bucket first using create_s3.py")
        return False
    
    # Get current notification configuration
    try:
        current_config = s3_client.get_bucket_notification_configuration(Bucket=BUCKET_NAME)
    except Exception as e:
        print(f"Error getting bucket notification configuration: {str(e)}")
        return False
    
    # Prepare Lambda configuration
    lambda_config = {
        'LambdaFunctionArn': lambda_arn,
        'Events': ['s3:ObjectCreated:*']  # Trigger on all object creation events
    }
    
    # Merge with existing Lambda configurations if any
    lambda_configurations = current_config.get('LambdaFunctionConfigurations', [])
    
    # Check if configuration already exists
    existing_config = next(
        (cfg for cfg in lambda_configurations if cfg['LambdaFunctionArn'] == lambda_arn),
        None
    )
    
    if existing_config:
        print("S3 event notification already configured.")
        return True
    
    # Add new Lambda configuration
    lambda_configurations.append(lambda_config)
    
    # Prepare notification configuration
    notification_config = {
        'LambdaFunctionConfigurations': lambda_configurations
    }
    
    # Preserve other notification types if they exist
    if 'TopicConfigurations' in current_config:
        notification_config['TopicConfigurations'] = current_config['TopicConfigurations']
    if 'QueueConfigurations' in current_config:
        notification_config['QueueConfigurations'] = current_config['QueueConfigurations']
    if 'EventBridgeConfiguration' in current_config:
        notification_config['EventBridgeConfiguration'] = current_config['EventBridgeConfiguration']
    
    try:
        # Configure bucket notification
        s3_client.put_bucket_notification_configuration(
            Bucket=BUCKET_NAME,
            NotificationConfiguration=notification_config
        )
        print(f"S3 event notification configured successfully.")
        print(f"Bucket '{BUCKET_NAME}' will now trigger Lambda '{LAMBDA_FUNCTION_NAME}' on object creation.")
        return True
    except Exception as e:
        print(f"Error configuring S3 event notification: {str(e)}")
        return False

def configure_s3_lambda_trigger():
    """Main function to configure S3 to trigger Lambda"""
    print(f"Configuring S3 bucket '{BUCKET_NAME}' to trigger Lambda '{LAMBDA_FUNCTION_NAME}'...")
    
    # Step 1: Add Lambda permission
    if not add_lambda_permission():
        return False
    
    # Step 2: Configure S3 event notification
    if not configure_s3_event_notification():
        return False
    
    print("S3 event configuration complete!")
    return True

if __name__ == "__main__":
    configure_s3_lambda_trigger()

