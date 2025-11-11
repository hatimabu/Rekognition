This project implements a facial recognition pipeline for a building's security system. It analyzes images captured by a front-door camera, processing up to 500 employee scans daily. Using Amazon Rekognition, the system detects faces in images uploaded to S3. If a face is recognized, the results are stored in DynamoDB, and a notification is sent via SNS to authorize security to unlock the door, allowing employees to enter the building and begin work.
 
 ---

![alt text](image.png)
source:https://tutorialsdojo.com/5-best-cloud-projects-for-beginners/

---

# Services:

- Amazon S3
- AWS Lambda
- Amazon Rekognition
- Amazon DynamoDB
- Amazon SNS

# zone 

US East (N.Virginia)

---

# Architecture Workflow

## ✳️ Image Upload (S3)

+ A user uploads an image from their computer into an Amazon S3 bucket.

+ The bucket is configured with event notifications so that whenever a new image is uploaded, it automatically triggers the AWS Lambda function.

### 💰 *S3 pricing*
S3 Standard - General purpose storage for any type of data, typically used for frequently accessed data	
First 50 TB / Month	$0.023 per GB

##### Requests & data retrievals 
- PUT, COPY, POST, LIST requests $0.005/per 1,000 requests
- GET, SELECT, and all other request $0.0004/per 1,000 requests
###### TOTAL
- 1️⃣ S3 Storage

15,000 images × 0.5 MB = 7,500 MB = 7.5 GB stored per month.
Pricing (S3 Standard): $0.023 per GB
Cost: 7.5 × $0.023 = $0.1725 ≈ $0.18 per month

- 2️⃣ S3 Requests

PUT (uploads) = 15,000 / 1,000 × $0.005 = $0.075
GET (retrieval by Rekognition) = 15,000 / 1,000 × $0.0004 = $0.006
Total = $0.081 ≈ $0.08 per month

---

## 🧮 Processing (Lambda + Rekognition)

+ Lambda function is invoked when the new object (image) is created in S3.

```hcl
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
```

### 💰 *lambda pricing*
 The Lambda free tier includes 1M free requests per month and 400,000 GB-seconds of compute time per month.

+ Inside the Lambda function, you call Amazon Rekognition.

+ Rekognition analyzes the uploaded image and checks whether it contains faces.

### 💰 *Rekognition pricing*
Group 1 AssociateFaces First 1 million images $0.001
- workload: 500/day × 30 days = 15,000 images/month.
- 15,000 × $0.001 = $15.00/month (ignoring any free-tier credits).

---

## Decision Making

+ If no face is detected → nothing happens (or you can log it).

+ If a face is detected:

 + The Lambda function writes the metadata (image name, S3 path, number of faces, confidence score, etc.) into a DynamoDB table.
 + The Lambda function also triggers Amazon SNS (Simple Notification Service) to send an email notification (or SMS/push, depending on configuration).
 
### 💰 *DynamoDB pricing* 
DynamoDB Standard table class > On-Demand Throughput Type
DynamoDB Monthly Cost Estimate
500 uploads/day × 30 days = 15,000 writes/month
- Writes = ~$0.02
- Reads = ~$0.003 (depends on usage)
- Storage = ~$0.004
- Total ≈ $0.03/month
---

## Notification

+ SNS publishes the message to all subscribers.

For example, if you configured email, the subscriber receives an email saying something like:

"A face has been detected in the uploaded image: [filename]."

### 💰 *sns pricing*
--- 
![alt text](image-1.png)
--- 
$2 per 100,000 emails → your 15,000/month is only $0.30/month.

# TOTAL PROJECT WILL COST AROUND $15.56 per month

---

# 🔍 Monitoring 
## Amazon CloudWatch (Core Monitoring)

Tracks metrics for:
- Lambda: invocations, duration, errors
- S3: object count, storage size
- DynamoDB: read/write capacity, throttling
- SNS: messages published/delivered/failed
