import boto3

sns = boto3.client('sns', region_name='us-east-2')
topic_name = 'FaceDetectedTopic'

def create_topic():
    response = sns.create_topic(Name=topic_name)
    print(f"SNS topic '{topic_name}' created. ARN: {response['TopicArn']}")

if __name__ == "__main__":
    create_topic()
