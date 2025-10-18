import boto3
import json

rekognition = boto3.client('rekognition', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
sns = boto3.client('sns', region_name='us-east-1')

# Replace with your actual table name and SNS topic ARN
DYNAMO_TABLE = 'FaceMetadata'
SNS_TOPIC_ARN = 'arn:aws:sns: us-east-2:094092120892:FaceDetectedTopic'

def lambda_handler(event, context):
    # Extract bucket and image key from the S3 event
    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']

    # Call Rekognition to detect faces
    response = rekognition.detect_faces(
        Image={'S3Object': {'Bucket': bucket, 'Name': key}},
        Attributes=['ALL']
    )

    face_details = response.get('FaceDetails', [])
    if not face_details:
        return {'statusCode': 200, 'body': 'No face detected.'}

    # Use the first detected face
    face = face_details[0]
    table = dynamodb.Table(DYNAMO_TABLE)

    # Store metadata in DynamoDB
    table.put_item(Item={
        'FaceId': key,
        'AgeRange': face['AgeRange'],
        'Gender': face['Gender'],
        'Emotions': face['Emotions']
    })

    # Send notification via SNS
    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Message=f"Face detected in image: {key}",
        Subject="Face Recognition Alert"
    )

    return {'statusCode': 200, 'body': 'Face processed and metadata stored.'}