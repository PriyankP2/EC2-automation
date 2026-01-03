# Automated Instance Management Using AWS Lambda and Boto3

## 📋 Project Overview

This project demonstrates automated EC2 instance management using AWS Lambda and Boto3. The Lambda function automatically stops instances tagged with `Auto-Stop` and starts instances tagged with `Auto-Start`.

## 🎯 Objectives

- Automate EC2 instance lifecycle management based on tags
- Utilize AWS Lambda for serverless automation
- Implement Boto3 SDK for AWS resource interaction
- Practice Infrastructure as Code principles

## 🏗️ Architecture

```
EC2 Instances (Tagged) → Lambda Function (Boto3) → EC2 API
                              ↓
                        CloudWatch Logs
```

## 📦 Prerequisites

- AWS Account
- Basic understanding of AWS EC2
- Python 3.x knowledge
- AWS IAM permissions to create resources

## 🚀 Features

- **Tag-based automation**: Uses EC2 tags to determine actions
- **Intelligent state detection**: Only acts on instances in appropriate states
- **Comprehensive logging**: CloudWatch logs for audit trail
- **Error handling**: Robust exception handling with detailed error messages
- **Flexible**: Easy to extend for additional automation rules

## 📁 Repository Structure

```
EC2-automation/
├── README.md                          # This file
├── lambda_function.py                 # Lambda function code
├── documentation.md                   # Detailed step-by-step guide
└── screenshots/                       # Project screenshots
    ├── 01-ec2-instances-created.png
    ├── 02-instance-tags.png
    ├── 03-iam-role-created.png
    ├── 04-lambda-function-created.png
    ├── 05-lambda-code-deployed.png
    ├── 06-test-execution-results.png
    ├── 07-cloudwatch-logs.png
    └── 08-ec2-final-state.png
```

## 🔧 Setup Instructions

### Step 1: Create EC2 Instances

1. Launch two t2.micro EC2 instances
2. Tag first instance: `Action = Auto-Stop`
3. Tag second instance: `Action = Auto-Start`
4. Ensure first instance is running, second is stopped

### Step 2: Create IAM Role

1. Create IAM role: `Lambda-EC2-Management-Role`
2. Attach policy: `AmazonEC2FullAccess`
3. Trust entity: Lambda service

### Step 3: Create Lambda Function

1. Function name: `EC2-Auto-Management`
2. Runtime: Python 3.12
3. Execution role: `Lambda-EC2-Management-Role`
4. Deploy the code from `lambda_function.py`

### Step 4: Test

1. Create test event in Lambda
2. Execute the function
3. Verify instance state changes in EC2 console

## 💻 Lambda Function Code

The Lambda function performs the following operations:

1. Initializes Boto3 EC2 client
2. Filters instances with `Action` tag
3. Identifies instances to stop (running + Auto-Stop tag)
4. Identifies instances to start (stopped + Auto-Start tag)
5. Executes stop/start operations
6. Logs all actions to CloudWatch

See `lambda_function.py` for complete implementation.

## 📊 Expected Results

- ✅ Instance with `Auto-Stop` tag changes to **stopped** state
- ✅ Instance with `Auto-Start` tag changes to **running** state
- ✅ CloudWatch logs show affected instance IDs
- ✅ Lambda returns HTTP 200 status code
- ✅ No errors in execution

## 📸 Screenshots

All screenshots documenting the implementation process are available in the `screenshots/` directory.

## 🔍 Testing

### Manual Testing

```bash
# Test event (use Lambda console)
{}
```

### Expected Output

```json
{
  "statusCode": 200,
  "body": "{\"message\": \"EC2 instance management completed successfully\", \"stopped_instances\": [\"i-xxxxx\"], \"started_instances\": [\"i-yyyyy\"]}"
}
```

## 📝 CloudWatch Logs Sample

```
Stopping instances: ['i-0123456789abcdef0']
Successfully stopped instances: ['i-0123456789abcdef0']
Starting instances: ['i-0123456789abcdef1']
Successfully started instances: ['i-0123456789abcdef1']
```

## 🔐 Security Considerations

### Current Implementation
- Uses `AmazonEC2FullAccess` for simplicity

### Production Recommendations
- Use least privilege IAM policies
- Restrict to specific EC2 actions: `ec2:DescribeInstances`, `ec2:StopInstances`, `ec2:StartInstances`
- Add resource-level permissions for specific instances
- Enable CloudTrail for compliance

### Recommended IAM Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ec2:StopInstances",
        "ec2:StartInstances"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "ec2:ResourceTag/Action": ["Auto-Stop", "Auto-Start"]
        }
      }
    }
  ]
}
```

## 🎓 Learning Outcomes

- Understanding of AWS Lambda event-driven architecture
- Practical Boto3 SDK usage
- EC2 instance lifecycle management
- IAM role and policy configuration
- CloudWatch logging and monitoring
- Tag-based resource management

## 🔄 Future Enhancements

- [ ] Schedule Lambda with EventBridge for automated execution
- [ ] Add SNS notifications for state changes
- [ ] Support multiple tag patterns
- [ ] Implement dry-run mode
- [ ] Add DynamoDB logging for audit history
- [ ] Create CloudFormation template for infrastructure

## 🧹 Cleanup

To avoid unnecessary AWS charges:

```bash
# Stop/terminate EC2 instances
# Delete Lambda function
# Delete IAM role
# Remove CloudWatch log groups
```

## 📚 References

- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [Boto3 EC2 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html)
- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)

## 👤 Author

Priyank Pandey
- GitHub: [@PriyankP2](https://github.com/PriyankP2)

## 📄 License

This project is created for educational purposes as part of AWS Lambda automation.

## 🤝 Contributing

Suggestions and improvements are welcome! Feel free to open an issue or submit a pull request.

---

**Note**: This project is part of AWS Lambda and Boto3 automation. For detailed implementation steps, refer to `documentation.md`.
