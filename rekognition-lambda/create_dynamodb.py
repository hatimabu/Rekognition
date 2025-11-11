import boto3

dynamodb = boto3.client('dynamodb', region_name='us-east-2')
table_name = 'FaceMetadata'

def create_table():
    dynamodb.create_table(
        TableName=table_name,
        KeySchema=[{'AttributeName': 'FaceId', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'FaceId', 'AttributeType': 'S'}],
        BillingMode='PAY_PER_REQUEST'
    )
    print(f"DynamoDB table '{table_name}' created.")

if __name__ == "__main__":
    create_table()
