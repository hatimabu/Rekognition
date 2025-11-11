# GitHub Actions Workflow Setup

This workflow allows you to deploy your AWS infrastructure pipeline from GitHub Actions.

## Prerequisites

1. AWS Account with appropriate permissions
2. GitHub Repository with Actions enabled
3. AWS Access Keys (or IAM Role for GitHub OIDC - advanced)

## Setup Instructions

### Step 1: Create AWS Access Keys

1. Log in to AWS Console
2. Go to IAM → Users → Your User → Security Credentials
3. Create a new Access Key
4. Save the Access Key ID and Secret Access Key securely

### Step 2: Configure GitHub Secrets

1. Go to your GitHub repository
2. Navigate to Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add the following secrets:

   - **Name**: `AWS_ACCESS_KEY_ID`
     - **Value**: Your AWS Access Key ID

   - **Name**: `AWS_SECRET_ACCESS_KEY`
     - **Value**: Your AWS Secret Access Key

### Step 3: Required AWS Permissions

Your AWS user/role needs the following permissions:

- S3: CreateBucket, PutBucketNotification, GetBucketNotification
- Lambda: CreateFunction, UpdateFunctionCode, UpdateFunctionConfiguration, AddPermission, GetFunction, GetPolicy
- Rekognition: CreateCollection
- DynamoDB: CreateTable, DescribeTable
- SNS: CreateTopic, ListTopics
- IAM: (for Lambda execution role - should already exist)

### Step 4: Trigger the Workflow

#### Manual Trigger (Recommended)
1. Go to Actions tab in your GitHub repository
2. Select "Deploy AWS Infrastructure" workflow
3. Click "Run workflow"
4. Select the branch (usually `main`)
5. Click "Run workflow" button

#### Automatic Trigger
The workflow will also run automatically when you push changes to:
- `rekognition/**` files
- `.github/workflows/deploy-infrastructure.yml`

## Workflow Features

- ✅ Manual trigger via GitHub Actions UI
- ✅ Automatic trigger on code changes
- ✅ Python 3.9 environment setup
- ✅ Dependency installation
- ✅ AWS credential configuration
- ✅ Full pipeline execution
- ✅ Detailed logging and error handling

## Troubleshooting

### Workflow fails with "Access Denied"
- Check that your AWS credentials have the required permissions
- Verify the AWS region is correct (us-east-2)
- Check that the IAM role for Lambda exists

### Workflow fails with "Bucket already exists"
- This is normal if resources already exist
- The pipeline is idempotent and will skip existing resources
- Check the logs for specific error messages

### Lambda deployment fails
- Verify the IAM role ARN in `deploy_lambda.py` is correct
- Check that the role has permissions for Lambda, Rekognition, DynamoDB, and SNS
- Ensure the role trusts the Lambda service

## Security Best Practices

1. **Never commit AWS credentials to the repository**
2. **Use GitHub Secrets for all sensitive data**
3. **Rotate access keys regularly**
4. **Use IAM roles with least privilege principle**
5. **Consider using AWS IAM Roles for GitHub OIDC** (more secure, but requires additional setup)

## Advanced: Using OIDC (Optional)

For better security, you can use AWS IAM Roles with GitHub OIDC instead of access keys. This requires:
1. Configuring OIDC in AWS IAM
2. Updating the workflow to use `aws-actions/configure-aws-credentials@v4` with OIDC
3. Removing the access key secrets

See AWS documentation for GitHub OIDC setup.

