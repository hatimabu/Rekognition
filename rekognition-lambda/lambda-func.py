import boto3
import json
from decimal import Decimal

rekognition = boto3.client('rekognition', region_name='us-east-2')
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
sns = boto3.client('sns', region_name='us-east-2')

DYNAMO_TABLE = 'FaceMetadata'
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-2:094092120892:FaceDetectedTopic'
REKOGNITION_COLLECTION = 'employeeFaces'

def lambda_handler(event, context):
    try:
        record = event['Records'][0]
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        print(f"Processing image: {key} from bucket: {bucket}")

        # Step 1: Detect faces
        response = rekognition.detect_faces(
            Image={'S3Object': {'Bucket': bucket, 'Name': key}},
            Attributes=['ALL']
        )

        face_details = response.get('FaceDetails', [])
        if not face_details:
            print("No face detected.")
            return {'statusCode': 200, 'body': 'No face detected.'}

        face = face_details[0]
        print("Face detected. Writing to DynamoDB...")

        # Step 2: Write to DynamoDB
        table = dynamodb.Table(DYNAMO_TABLE)
        table.put_item(Item={
            'FaceId': key,
            'AgeRange': {
                'Low': Decimal(str(face['AgeRange']['Low'])),
                'High': Decimal(str(face['AgeRange']['High']))
            },
            'Gender': {
                'Value': face['Gender']['Value'],
                'Confidence': Decimal(str(face['Gender']['Confidence']))
            },
            'Emotions': [
                {
                    'Type': e['Type'],
                    'Confidence': Decimal(str(e['Confidence']))
                } for e in face['Emotions']
            ]
        })

        # Step 3: Search for face match
        match_response = rekognition.search_faces_by_image(
            CollectionId=REKOGNITION_COLLECTION,
            Image={'S3Object': {'Bucket': bucket, 'Name': key}},
            MaxFaces=1,
            FaceMatchThreshold=90
        )

        matches = match_response.get('FaceMatches', [])
        match_info = matches[0]['Face']['ExternalImageId'] if matches else 'No match found'
        print(f"Match result: {match_info}")

        # Step 4: Publish to SNS
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=f"Face detected in image: {key}\nMatch result: {match_info}",
            Subject="Face Recognition Alert"
        )
        print("SNS notification sent.")

        return {'statusCode': 200, 'body': f'Face processed. Match result: {match_info}'}

    except Exception as e:
        print(f"Error: {str(e)}")
        return {'statusCode': 500, 'body': f'Error: {str(e)}'}