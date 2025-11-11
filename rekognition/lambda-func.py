import boto3
import json
import os
from decimal import Decimal

rekognition = boto3.client('rekognition', region_name='us-east-2')
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
sns = boto3.client('sns', region_name='us-east-2')

# Get configuration from environment variables (set during Lambda deployment)
DYNAMO_TABLE = os.environ.get('DYNAMO_TABLE', 'FaceMetadata')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN', 'arn:aws:sns:us-east-2:094092120892:FaceDetectedTopic')
REKOGNITION_COLLECTION = os.environ.get('REKOGNITION_COLLECTION', 'employeeFaces')

def lambda_handler(event, context):
    # Extract bucket and key early for error handling
    bucket = 'Unknown'
    key = 'Unknown'
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
        
        # Handle case when no face is detected
        if not face_details:
            print("No face detected in image.")
            # Send notification even when no face is detected
            message = f"""Image Processing Result

Image: {key}
Bucket: {bucket}
Status: No face detected

The uploaded image does not contain any detectable faces.
Access should be denied."""
            
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Message=message,
                Subject="🚫 Face Recognition Alert - No Face Detected"
            )
            print("SNS notification sent for no face detected.")
            return {'statusCode': 200, 'body': 'No face detected. Notification sent.'}

        # Face detected - process it
        face = face_details[0]
        print("Face detected. Processing...")

        # Step 2: Search for face match in collection
        match_response = rekognition.search_faces_by_image(
            CollectionId=REKOGNITION_COLLECTION,
            Image={'S3Object': {'Bucket': bucket, 'Name': key}},
            MaxFaces=1,
            FaceMatchThreshold=90
        )

        matches = match_response.get('FaceMatches', [])
        is_matched = len(matches) > 0
        match_info = matches[0]['Face']['ExternalImageId'] if is_matched else 'No match found'
        match_confidence = matches[0]['Similarity'] if is_matched else 0
        
        print(f"Match result: {match_info} (Matched: {is_matched})")

        # Step 3: Write to DynamoDB with match status
        table = dynamodb.Table(DYNAMO_TABLE)
        table.put_item(Item={
            'FaceId': key,
            'ImageKey': key,
            'Bucket': bucket,
            'MatchStatus': 'MATCHED' if is_matched else 'UNMATCHED',
            'MatchedEmployee': match_info if is_matched else 'N/A',
            'MatchConfidence': Decimal(str(match_confidence)) if is_matched else Decimal('0'),
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
            ],
            'ProcessedAt': context.aws_request_id if context else 'unknown'
        })
        print("Data written to DynamoDB.")

        # Step 4: Publish to SNS with detailed information
        if is_matched:
            # Matched employee - authorized access
            message = f"""✅ AUTHORIZED ACCESS - Employee Recognized

Image: {key}
Bucket: {bucket}
Employee ID: {match_info}
Match Confidence: {match_confidence:.2f}%
Status: MATCHED

Face Details:
- Age Range: {face['AgeRange']['Low']}-{face['AgeRange']['High']} years
- Gender: {face['Gender']['Value']} (Confidence: {face['Gender']['Confidence']:.2f}%)

Action: Door should be UNLOCKED. Employee is authorized to enter."""
            
            subject = "✅ Face Recognition - Authorized Access"
        else:
            # Unmatched face - unauthorized access
            message = f"""🚫 UNAUTHORIZED ACCESS - Unknown Person

Image: {key}
Bucket: {bucket}
Status: UNMATCHED
Match Result: No matching employee found in database

Face Details:
- Age Range: {face['AgeRange']['Low']}-{face['AgeRange']['High']} years
- Gender: {face['Gender']['Value']} (Confidence: {face['Gender']['Confidence']:.2f}%)

Action: Door should remain LOCKED. Unauthorized access attempt detected.
Security should be notified immediately."""
            
            subject = "🚫 Face Recognition - Unauthorized Access Attempt"
        
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=message,
            Subject=subject
        )
        print(f"SNS notification sent. Status: {'MATCHED' if is_matched else 'UNMATCHED'}")

        return {
            'statusCode': 200,
            'body': json.dumps({
                'status': 'processed',
                'matched': is_matched,
                'employee': match_info,
                'confidence': match_confidence if is_matched else 0
            })
        }

    except Exception as e:
        error_message = str(e)
        print(f"Error: {error_message}")
        
        # Send error notification via SNS
        try:
            error_notification = f"""❌ ERROR - Face Recognition Processing Failed

Image: {key}
Bucket: {bucket}
Error: {error_message}

The face recognition pipeline encountered an error while processing the image.
Please check the Lambda logs for more details."""
            
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Message=error_notification,
                Subject="❌ Face Recognition - Processing Error"
            )
            print("Error notification sent via SNS.")
        except Exception as sns_error:
            print(f"Failed to send error notification: {str(sns_error)}")
        
        return {'statusCode': 500, 'body': f'Error: {error_message}'}