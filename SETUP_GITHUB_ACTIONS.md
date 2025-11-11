# GitHub Actions Setup Guide

This guide will help you set up GitHub Actions to deploy your AWS infrastructure pipeline.

## Quick Start

### 1. Add AWS Credentials to GitHub Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add these two secrets:

   **Secret 1:**
   - Name: `AWS_ACCESS_KEY_ID`
   - Value: Your AWS Access Key ID

   **Secret 2:**
   - Name: `AWS_SECRET_ACCESS_KEY`
   - Value: Your AWS Secret Access Key

### 2. Trigger the Workflow

#### Option A: Manual Trigger (Recommended for testing)
1. Go to the **Actions** tab in your GitHub repository
2. Select **"Deploy AWS Infrastructure"** workflow from the left sidebar
3. Click **"Run workflow"** button
4. Select your branch (usually `main`)
5. Click **"Run workflow"** to start

#### Option B: Automatic Trigger
The workflow will automatically run when you push changes to:
- Files in the `rekognition/` directory
- The workflow file itself (`.github/workflows/deploy-infrastructure.yml`)

## What the Workflow Does

1. ✅ Checks out your code
2. ✅ Sets up Python 3.9 environment
3. ✅ Installs required dependencies (boto3)
4. ✅ Configures AWS credentials
5. ✅ Runs the infrastructure pipeline:
   - Creates S3 bucket
   - Creates Rekognition collection
   - Creates DynamoDB table
   - Creates SNS topic
   - Deploys Lambda function
   - Configures S3 event notifications

## Required AWS Permissions

Your AWS IAM user needs the following permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:CreateBucket",
        "s3:PutBucketNotification",
        "s3:GetBucketNotification",
        "s3:HeadBucket",
        "s3:ListBucket"
      ],
      "Resource": "arn:aws:s3:::rekognition-upload-bucket1"
    },
    {
      "Effect": "Allow",
      "Action": [
        "lambda:CreateFunction",
        "lambda:UpdateFunctionCode",
        "lambda:UpdateFunctionConfiguration",
        "lambda:GetFunction",
        "lambda:AddPermission",
        "lambda:GetPolicy"
      ],
      "Resource": "arn:aws:lambda:us-east-2:*:function:FaceProcessor"
    },
    {
      "Effect": "Allow",
      "Action": [
        "rekognition:CreateCollection",
        "rekognition:DescribeCollection"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:CreateTable",
        "dynamodb:DescribeTable"
      ],
      "Resource": "arn:aws:dynamodb:us-east-2:*:table/FaceMetadata"
    },
    {
      "Effect": "Allow",
      "Action": [
        "sns:CreateTopic",
        "sns:ListTopics",
        "sns:GetTopicAttributes"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "iam:PassRole"
      ],
      "Resource": "arn:aws:iam::094092120892:role/lambda-role-FaceProcessor"
    }
  ]
}
```

## Troubleshooting

### Error: "AWS_ACCESS_KEY_ID not found"
- Make sure you've added the secrets in GitHub repository settings
- Check that the secret names are exactly: `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`

### Error: "Access Denied"
- Verify your AWS credentials have the required permissions
- Check that the AWS region is correct (us-east-2)
- Ensure the IAM role for Lambda exists: `lambda-role-FaceProcessor`

### Error: "Bucket already exists"
- This is normal! The pipeline is idempotent
- Existing resources will be skipped
- Check the workflow logs for details

### Workflow fails at Lambda deployment
- Verify the IAM role ARN in `rekognition/deploy_lambda.py` matches your AWS account
- Check that the role has trust relationship with Lambda service
- Ensure the role has permissions for Rekognition, DynamoDB, and SNS

## Security Best Practices

1. **Never commit AWS credentials** to the repository
2. **Use GitHub Secrets** for all sensitive information
3. **Rotate access keys** regularly (every 90 days recommended)
4. **Use least privilege** - only grant necessary permissions
5. **Monitor workflow runs** for unauthorized access

## Files Created

- `.github/workflows/deploy-infrastructure.yml` - Main workflow file
- `requirements.txt` - Python dependencies
- `SETUP_GITHUB_ACTIONS.md` - This setup guide

## Next Steps

1. Add AWS credentials to GitHub Secrets
2. Test the workflow with a manual trigger
3. Monitor the workflow execution in the Actions tab
4. Verify resources are created in AWS Console
5. Set up SNS email subscriptions for notifications

## Support

If you encounter issues:
1. Check the workflow logs in the Actions tab
2. Verify AWS credentials and permissions
3. Ensure all required AWS resources (like IAM roles) exist
4. Check that the AWS region matches (us-east-2)

