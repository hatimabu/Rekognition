
This project analyzes images uploaded to S3 with Amazon Rekognition, and if faces are detected, records the results in DynamoDB and notifies users via SNS.
 
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

### 💰 *pricing*
S3 Standard - General purpose storage for any type of data, typically used for frequently accessed data	
First 50 TB / Month	$0.023 per GB

##### Requests & data retrievals 
- PUT, COPY, POST, LIST requests $0.005/per 1,000 requests
- GET, SELECT, and all other request $0.0004/per 1,000 requests
###### TOTAL
 Storage: ~4.883 GB × $0.023 ≈ $0.1123
 Requests: $0.0027
 Total ≈ $0.1150 / month

---

## 🧮 Processing (Lambda + Rekognition)

+ Lambda function is invoked when the new object (image) is created in S3.

### 💰 *pricing*
 The Lambda free tier includes 1M free requests per month and 400,000 GB-seconds of compute time per month.

+ Inside the Lambda function, you call Amazon Rekognition.

+ Rekognition analyzes the uploaded image and checks whether it contains faces.

---

## Decision Making

+ If no face is detected → nothing happens (or you can log it).

+ If a face is detected:

 + The Lambda function writes the metadata (image name, S3 path, number of faces, confidence score, etc.) into a DynamoDB table.
 + The Lambda function also triggers Amazon SNS (Simple Notification Service) to send an email notification (or SMS/push, depending on configuration).

---

## Notification

+ SNS publishes the message to all subscribers.

For example, if you configured email, the subscriber receives an email saying something like:

"A face has been detected in the uploaded image: [filename]."