import boto3
from botocore.exceptions import ClientError

rekognition = boto3.client('rekognition', region_name='us-east-2')
collection_id = 'employeeFaces'

def create_collection():
    try:
        rekognition.create_collection(CollectionId=collection_id)
        print(f"Rekognition collection '{collection_id}' created successfully.")
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ResourceAlreadyExistsException':
            print(f"Rekognition collection '{collection_id}' already exists.")
            return True
        else:
            print(f"Error creating Rekognition collection: {e}")
            return False

if __name__ == "__main__":
    create_collection()