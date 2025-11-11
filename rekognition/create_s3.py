import boto3
from botocore.exceptions import ClientError

s3 = boto3.client('s3', region_name='us-east-2')
bucket_name = 'rekognition-upload-bucket1'

def create_bucket():
    try:
        # Check if bucket already exists
        try:
            s3.head_bucket(Bucket=bucket_name)
            print(f"S3 bucket '{bucket_name}' already exists.")
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                # Bucket doesn't exist, proceed to create it
                pass
            elif error_code == '403':
                # Bucket exists but we don't have permission (or it's in another region)
                print(f"S3 bucket '{bucket_name}' may already exist (access denied).")
                return True
            else:
                print(f"Error checking bucket: {error_code}")
                return False
        
        # Create the bucket
        try:
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': 'us-east-2'}
            )
            print(f"S3 bucket '{bucket_name}' created successfully.")
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'BucketAlreadyOwnedByYou':
                print(f"S3 bucket '{bucket_name}' already exists and is owned by you.")
                return True
            elif error_code == 'BucketAlreadyExists':
                print(f"S3 bucket '{bucket_name}' already exists (may be owned by another account).")
                return True
            else:
                print(f"Error creating S3 bucket: {e}")
                return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    create_bucket()