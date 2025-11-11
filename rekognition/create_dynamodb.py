import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.client('dynamodb', region_name='us-east-2')
table_name = 'FaceMetadata'

def create_table():
    try:
        # Check if table already exists
        try:
            response = dynamodb.describe_table(TableName=table_name)
            print(f"DynamoDB table '{table_name}' already exists.")
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code != 'ResourceNotFoundException':
                print(f"Error checking table: {error_code}")
                return False
        
        # Create the table
        dynamodb.create_table(
            TableName=table_name,
            KeySchema=[{'AttributeName': 'FaceId', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'FaceId', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        print(f"DynamoDB table '{table_name}' created successfully.")
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ResourceInUseException':
            print(f"DynamoDB table '{table_name}' already exists.")
            return True
        else:
            print(f"Error creating DynamoDB table: {e}")
            return False

if __name__ == "__main__":
    create_table()
