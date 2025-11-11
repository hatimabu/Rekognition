import create_s3
import create_rekognition_collection
import create_dynamodb
import create_sns
import deploy_lambda
import configure_s3_event

def run_pipeline():
    print("=" * 50)
    print("Starting AWS Infrastructure Setup Pipeline")
    print("=" * 50)
    
    # Step 1: Create S3 bucket
    print("\n[1/6] Creating S3 bucket...")
    create_s3.create_bucket()
    
    # Step 2: Create Rekognition collection
    print("\n[2/6] Creating Rekognition collection...")
    create_rekognition_collection.create_collection()
    
    # Step 3: Create DynamoDB table
    print("\n[3/6] Creating DynamoDB table...")
    create_dynamodb.create_table()
    
    # Step 4: Create SNS topic
    print("\n[4/6] Creating SNS topic...")
    create_sns.create_topic()
    
    # Step 5: Deploy Lambda function
    print("\n[5/6] Deploying Lambda function...")
    deploy_lambda.deploy_lambda()
    
    # Step 6: Configure S3 event notification
    print("\n[6/6] Configuring S3 event notification...")
    configure_s3_event.configure_s3_lambda_trigger()
    
    print("\n" + "=" * 50)
    print("Pipeline setup complete!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Upload employee face images to the Rekognition collection")
    print("2. Subscribe to the SNS topic to receive notifications")
    print("3. Test by uploading an image to the S3 bucket")

if __name__ == "__main__":
    run_pipeline()