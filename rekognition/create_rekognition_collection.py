import boto3

rekognition = boto3.client('rekognition', region_name='us-east-2')
collection_id = 'employeeFaces'

def create_collection():
    rekognition.create_collection(CollectionId=collection_id)
    print(f"Rekognition collection '{collection_id}' created.")

if __name__ == "__main__":
    create_collection()