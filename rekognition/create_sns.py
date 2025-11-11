import boto3
from botocore.exceptions import ClientError

sns = boto3.client('sns', region_name='us-east-2')
topic_name = 'FaceDetectedTopic'

def create_topic():
    try:
        # SNS create_topic is idempotent - it returns the existing topic ARN if it exists
        response = sns.create_topic(Name=topic_name)
        topic_arn = response['TopicArn']
        print(f"SNS topic '{topic_name}' is ready. ARN: {topic_arn}")
        return True
    except ClientError as e:
        print(f"Error creating SNS topic: {e}")
        return False

if __name__ == "__main__":
    create_topic()
