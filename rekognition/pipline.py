import create_s3
import create_rekognition_collection
import create_dynamodb
import create_sns

def run_pipeline():
    create_s3.create_bucket()
    create_rekognition_collection.create_collection()
    create_dynamodb.create_table()
    create_sns.create_topic()
    print("Pipeline setup complete.")

if __name__ == "__main__":
    run_pipeline()