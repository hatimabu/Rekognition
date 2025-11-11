import boto3

s3 = boto3.client('s3', region_name='us-east-2')
bucket_name = 'rekognition-upload-bucket1'

def create_bucket():
    s3.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={'LocationConstraint': 'us-east-2'}
    )
    print(f"S3 bucket '{bucket_name}' created.")

if __name__ == "__main__":
    create_bucket()