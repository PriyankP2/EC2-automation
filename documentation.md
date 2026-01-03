# Automated Instance Management - Complete Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [Architecture Overview](#architecture-overview)
3. [Prerequisites](#prerequisites)
4. [Step-by-Step Implementation](#step-by-step-implementation)
5. [Code Explanation](#code-explanation)
6. [Testing and Verification](#testing-and-verification)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

---

## Introduction

### Project Goal
Automate the management of EC2 instances using AWS Lambda and Boto3. The solution automatically stops instances tagged with `Auto-Stop` and starts instances tagged with `Auto-Start`.

### Use Cases
- Cost optimization by stopping development instances after hours
- Automatic instance recovery and restart
- Scheduled maintenance workflows
- Resource management automation

### Technologies Used
- **AWS Lambda**: Serverless compute service
- **AWS EC2**: Virtual machine instances
- **Boto3**: AWS SDK for Python
- **AWS IAM**: Identity and Access Management
- **CloudWatch Logs**: Logging and monitoring

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                     AWS Cloud                           │
│                                                         │
│  ┌──────────────┐                                       │
│  │   EC2        │                                       │
│  │  Instance 1  │  Tag: Action=Auto-Stop                │
│  │  (Running)   │                                       │
│  └──────────────┘                                       │
│         ↓                                               │
│  ┌──────────────────────────────────────┐               │
│  │      Lambda Function                  │              │
│  │  - Scans tagged instances             │              │
│  │  - Stops Auto-Stop instances          │              │
│  │  - Starts Auto-Start instances        │              │
│  │  - Logs all actions                   │              │
│  └──────────────────────────────────────┘               │
│         ↓                                               │
│  ┌──────────────┐                                       │
│  │   EC2        │                                       │
│  │  Instance 2  │  Tag: Action=Auto-Start               │
│  │  (Stopped)   │                                       │
│  └──────────────┘                                       │
│                                                         │
│         ↓                                               │
│  ┌──────────────┐                                       │
│  │ CloudWatch   │                                       │
│  │    Logs      │                                       │
│  └──────────────┘                                       │
└─────────────────────────────────────────────────────────┘
```

**Workflow:**
1. EC2 instances are tagged with Action=Auto-Stop or Action=Auto-Start
2. Lambda function is invoked (manually or scheduled)
3. Function queries EC2 for instances with specific tags
4. Function stops instances with Auto-Stop tag (if running)
5. Function starts instances with Auto-Start tag (if stopped)
6. All actions are logged to CloudWatch

---

## Prerequisites

### AWS Account Requirements
- Active AWS account with console access
- Access to create the following resources:
  - EC2 instances (t2.micro free tier eligible)
  - Lambda functions
  - IAM roles and policies

### Knowledge Requirements
- Basic AWS console navigation
- Understanding of EC2 instances and their lifecycle
- Basic Python programming
- Familiarity with AWS IAM concepts

### Required Permissions
Your AWS user should have permissions to:
- Launch and manage EC2 instances
- Create Lambda functions
- Create IAM roles and attach policies
- View CloudWatch logs

---

## Step-by-Step Implementation

### Step 1: Create EC2 Instances

#### 1.1 Navigate to EC2 Service

1. Log in to [AWS Management Console](https://console.aws.amazon.com)
2. In the search bar at the top, type **"EC2"**
3. Click on **"EC2"** under Services
4. You should now be on the EC2 Dashboard

#### 1.2 Launch First Instance (Auto-Stop)

1. Click the **"Launch Instance"** button (orange button on the right side)

2. **Configure Instance Details:**

   **Name and tags:**
   - **Name**: `Instance-Auto-Stop`

   **Application and OS Images (Amazon Machine Image):**
   - Select **"Quick Start"** tab
   - Choose **"Amazon Linux"**
   - Select **"Amazon Linux 2023 AMI"** (Free tier eligible)

   **Instance type:**
   - Select **"t2.micro"** (Free tier eligible)

   **Key pair (login):**
   - If you have an existing key pair, select it
   - If not, click **"Create new key pair"**:
     - Key pair name: `my-ec2-key`
     - Key pair type: **RSA**
     - Private key file format: **.pem**
     - Click **"Create key pair"**
     - Save the downloaded .pem file securely

   **Network settings:**
   - Keep all default settings
   - Default VPC and subnet are fine

   **Configure storage:**
   - Keep default: **8 GiB gp3**

   **Advanced details:**
   - Leave as default

3. Review your configuration

4. Click **"Launch instance"** button

5. Wait for the success message: "Successfully initiated launch of instance"

6. Click on the **instance ID link** (starts with i-) to view your instance

#### 1.3 Launch Second Instance (Auto-Start)

1. Click **"Launch Instance"** button again

2. Configure with the **same settings** as the first instance:
   - **Name**: `Instance-Auto-Start`
   - Same AMI: Amazon Linux 2023
   - Same instance type: t2.micro
   - Same key pair

3. Click **"Launch instance"**

4. Wait for success message

#### 1.4 Add Tags to First Instance

1. Navigate to **EC2 Dashboard** → **Instances** (left sidebar)

2. You should see both instances listed

3. **Select** the **Instance-Auto-Stop** instance (click the checkbox)

4. Click on the **"Tags"** tab in the bottom panel

5. Click **"Manage tags"** button

6. Click **"Add tag"** button

7. Enter the tag:
   - **Key**: `Action`
   - **Value**: `Auto-Stop`

8. Click **"Save"** button

9. Verify the tag appears in the Tags tab

#### 1.5 Add Tags to Second Instance

1. **Select** the **Instance-Auto-Start** instance

2. Click on **"Tags"** tab

3. Click **"Manage tags"** button

4. Click **"Add tag"** button

5. Enter the tag:
   - **Key**: `Action`
   - **Value**: `Auto-Start`

6. Click **"Save"** button

#### 1.6 Set Initial Instance States

We need to ensure the instances are in the correct initial states for testing.

**For Instance-Auto-Stop (should be running):**
1. Select the **Instance-Auto-Stop** instance
2. Check the **Instance state** column
3. If it shows "running", you're good
4. If it shows "stopped", select it and click:
   - **Instance state** → **Start instance**
   - Wait until state becomes "running"

**For Instance-Auto-Start (should be stopped):**
1. Select the **Instance-Auto-Start** instance
2. Check the **Instance state** column
3. If it shows "stopped", you're good
4. If it shows "running", select it and click:
   - **Instance state** → **Stop instance**
   - In the confirmation dialog, click **"Stop"**
   - Wait until state becomes "stopped" (may take 30-60 seconds)

**EC2 Instances list showing:
- Instance-Auto-Stop: running
- Instance-Auto-Start: stopped

**✅ Checkpoint**: You should now have:
- ✓ Two EC2 instances created
- ✓ Instance 1 tagged with `Action=Auto-Stop` and in **running** state
- ✓ Instance 2 tagged with `Action=Auto-Start` and in **stopped** state

---

### Step 2: Create IAM Role for Lambda

#### 2.1 Navigate to IAM Service

1. In the AWS Console search bar (top), type **"IAM"**
2. Click on **"IAM"** under Services
3. You should now be on the IAM Dashboard

#### 2.2 Access Roles Section

1. In the left sidebar, click **"Roles"**
2. You'll see a list of existing roles (if any)

#### 2.3 Create New Role

1. Click the **"Create role"** button (orange/blue button)

#### 2.4 Select Trusted Entity Type

1. **Select trusted entity** page will open

2. **Trusted entity type**: 
   - Select **"AWS service"** (should be selected by default)

3. **Use case**:
   - Under "Common use cases", you'll see several services
   - Scroll down or look for **"Lambda"**
   - Select **"Lambda"**
   - This allows Lambda functions to assume this role

4. Click **"Next"** button at the bottom


#### 2.5 Add Permissions Policy

1. You're now on the **"Add permissions"** page

2. In the search box, type: `AmazonEC2FullAccess` & `AWSLambdaBasicExecutionRole` (Select these roles one after the another)

3. In the results, find **"AmazonEC2FullAccess"** & **"AWSLambdaBasicExecutionRole"**

4. **Check the checkbox** next to it

5. You should see "2 policy selected" at the top

6. Click **"Next"** button

**Important Note**: In production environments, you should use more restrictive policies following the principle of least privilege. For learning purposes, we're using the full access policy.

#### 2.6 Name and Create the Role

1. You're now on the **"Name, review, and create"** page

2. **Role details**:
   - **Role name**: `Lambda-EC2-Management-Role`
   - **Description**: `Allows Lambda function to manage EC2 instances based on tags`

3. **Review the configuration**:
   - Trusted entities: lambda.amazonaws.com
   - Permissions: AmazonEC2FullAccess , AWSLambdaBasicExecutionRole

4. Click **"Create role"** button

5. You should see a success message: "Role Lambda-EC2-Management-Role created"


#### 2.7 Verify Role Creation

1. In the Roles list, use the search box to find your role

2. Type: `Lambda-EC2-Management-Role`

3. Click on the role name to open its details

4. **Verify the following tabs**:
   
   **Permissions tab**:
   - Should show: AmazonEC2FullAccess policy & AWSLambdaBasicExecutionRole

   **Trust relationships tab**:
   - Click on it
   - Should show lambda.amazonaws.com as the trusted entity


**✅ Checkpoint**: 
- ✓ IAM role created: Lambda-EC2-Management-Role
- ✓ Policy attached: AmazonEC2FullAccess , AWSLambdaBasicExecutionRole
- ✓ Trust relationship configured for Lambda

---

### Step 3: Create Lambda Function

#### 3.1 Navigate to Lambda Service

1. In the AWS Console search bar, type **"Lambda"**
2. Click on **"Lambda"** under Services
3. You should see the Lambda Dashboard


#### 3.2 Start Creating Function

1. Click the **"Create function"** button (orange button)

2. You'll see three options:
   - Author from scratch
   - Use a blueprint
   - Container image

3. Select **"Author from scratch"** (should be selected by default)


#### 3.3 Configure Basic Function Information

Fill in the following details:

**Basic information:**

1. **Function name**: `EC2-Auto-Management`
   - This will be the name of your Lambda function

2. **Runtime**: 
   - Click the dropdown
   - Select **"Python 3.12"** (or the latest Python 3.x version available)

3. **Architecture**: 
   - Select **"x86_64"** (default)

#### 3.4 Configure Execution Role

1. **Expand** the section **"Change default execution role"**

2. You'll see four options. Select:
   - **"Use an existing role"**

3. **Existing role** dropdown will appear:
   - Click the dropdown
   - Search for and select: **"Lambda-EC2-Management-Role"**
   - This is the role we created in Step 2

#### 3.5 Advanced Settings (Optional)

Leave all other settings as default:
- Enable function URL: Not checked
- VPC: No VPC

#### 3.6 Create the Function

1. Review all your settings:
   - Function name: EC2-Auto-Management
   - Runtime: Python 3.12
   - Execution role: Lambda-EC2-Management-Role

2. Click **"Create function"** button at the bottom

3. Wait for the function to be created (takes a few seconds)

4. You should see a success banner: "Successfully created the function EC2-Auto-Management"

5. You'll be redirected to the function configuration page

**✅ Checkpoint**:
- ✓ Lambda function created: EC2-Auto-Management
- ✓ Runtime: Python 3.12
- ✓ Execution role: Lambda-EC2-Management-Role attached

---

### Step 4: Add Lambda Function Code

#### 4.1 Locate the Code Editor

1. You should be on the Lambda function page for **EC2-Auto-Management**

2. Scroll down to the **"Code source"** section

3. You'll see:
   - A file tree on the left showing `lambda_function.py`
   - A code editor in the middle with default code
   - Deploy and Test buttons above the editor

#### 4.2 View Default Code

The default code looks like this:
```python
import json

def lambda_handler(event, context):
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
```

#### 4.3 Replace with Our Code

1. **Select all the default code**:
   - Click inside the editor
   - Press `Ctrl+A` (Windows/Linux) or `Cmd+A` (Mac)

2. **Delete the selected code**:
   - Press `Delete` or `Backspace`

3. **Copy the following code** and paste it into the editor:

```python
import boto3
import json

def lambda_handler(event, context):
    """
    Lambda function to automatically manage EC2 instances based on tags.
    
    This function performs the following operations:
    - Stops instances with tag Action=Auto-Stop (if currently running)
    - Starts instances with tag Action=Auto-Start (if currently stopped)
    
    Args:
        event (dict): Lambda event object (not used in this function)
        context (object): Lambda context object (not used in this function)
    
    Returns:
        dict: Response containing status code and details of actions taken
    """
    
    # Initialize EC2 client for interacting with AWS EC2 service
    ec2_client = boto3.client('ec2')
    
    # Lists to store instance IDs for batch operations
    instances_to_stop = []
    instances_to_start = []
    
    try:
        # Describe all EC2 instances with the Action tag
        # This filters instances to only those with Action=Auto-Stop or Action=Auto-Start
        response = ec2_client.describe_instances(
            Filters=[
                {
                    'Name': 'tag:Action',
                    'Values': ['Auto-Stop', 'Auto-Start']
                }
            ]
        )
        
        # Process each reservation and instance
        # AWS groups instances in Reservations
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                # Extract instance ID and current state
                instance_id = instance['InstanceId']
                instance_state = instance['State']['Name']
                
                # Get the Action tag value for this instance
                action_tag = None
                for tag in instance.get('Tags', []):
                    if tag['Key'] == 'Action':
                        action_tag = tag['Value']
                        break
                
                # Categorize instances based on Action tag and current state
                # Only add instances that need state change
                if action_tag == 'Auto-Stop' and instance_state == 'running':
                    instances_to_stop.append(instance_id)
                elif action_tag == 'Auto-Start' and instance_state == 'stopped':
                    instances_to_start.append(instance_id)
        
        # Stop instances with Auto-Stop tag (if they are running)
        if instances_to_stop:
            print(f"Stopping instances: {instances_to_stop}")
            ec2_client.stop_instances(InstanceIds=instances_to_stop)
            print(f"Successfully stopped instances: {instances_to_stop}")
        else:
            print("No running instances found with Auto-Stop tag")
        
        # Start instances with Auto-Start tag (if they are stopped)
        if instances_to_start:
            print(f"Starting instances: {instances_to_start}")
            ec2_client.start_instances(InstanceIds=instances_to_start)
            print(f"Successfully started instances: {instances_to_start}")
        else:
            print("No stopped instances found with Auto-Start tag")
        
        # Return success response with details of actions taken
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'EC2 instance management completed successfully',
                'stopped_instances': instances_to_stop,
                'started_instances': instances_to_start
            })
        }
        
    except Exception as e:
        # Log and return error if something goes wrong
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Error managing EC2 instances',
                'error': str(e)
            })
        }
```

4. **Verify the code is pasted correctly**:
   - Check that indentation is correct
   - Ensure all imports are at the top
   - Make sure there are no copy-paste errors

#### 4.4 Deploy the Code

1. Click the **"Deploy"** button above the code editor (orange button)

2. Wait a few seconds

3. You should see a success message: **"Changes deployed"** with a green checkmark

4. The message appears at the top of the code editor


#### 4.5 Configure Function Timeout (Recommended)

By default, Lambda functions timeout after 3 seconds. For EC2 operations, we want more time.

1. Click on the **"Configuration"** tab (next to the Code tab)

2. In the left sidebar under Configuration, click **"General configuration"**

3. Click the **"Edit"** button (top right)

4. Change the following:
   - **Timeout**: Change to **1 min 0 sec**
   - Keep other settings as default:
     - Memory: 128 MB
     - Ephemeral storage: 512 MB

5. Click **"Save"** button

6. You should see: "Successfully updated the function EC2-Auto-Management"

**✅ Checkpoint**:
- ✓ Lambda function code deployed
- ✓ Timeout configured to 1 minute
- ✓ Code ready for testing

---

### Step 5: Test Lambda Function

#### 5.1 Verify Initial Instance States

Before testing, let's confirm our EC2 instances are in the correct state:

1. Open a **new browser tab**

2. Navigate to **EC2 Dashboard** → **Instances**

3. **Verify the following**:
   - **Instance-Auto-Stop**: State should be **running** ✓
   - **Instance-Auto-Start**: State should be **stopped** ✓

4. If states are incorrect, adjust them:
   - Start the Auto-Start instance if it's running (we want it stopped)
   - Stop the Auto-Stop instance if it's stopped (we want it running)

#### 5.2 Return to Lambda Function

1. Go back to the browser tab with your Lambda function

2. Make sure you're on the **EC2-Auto-Management** function page

#### 5.3 Create Test Event

1. Click on the **"Test"** tab (next to Code and Configuration tabs)

2. You'll see **"Configure test event"** section

3. Click **"Create new event"** button

4. Configure the test event:
   - **Event name**: `TestEvent`
   - **Event sharing settings**: Select **"Private"**
   - **Template**: Select **"hello-world"** (default)
   - **Event JSON**: Keep the default JSON (we don't actually use it):
   ```json
   {
     "key1": "value1",
     "key2": "value2",
     "key3": "value3"
   }
   ```

5. Click **"Save"** button

6. You should see: "Successfully saved test event TestEvent"

#### 5.4 Execute the Test

1. Make sure **"TestEvent"** is selected in the dropdown (should be default)

2. Click the **"Test"** button (orange button)

3. You'll see **"Executing function: succeeded"** or a loading indicator

4. Wait for execution to complete (should take 5-10 seconds)


#### 5.5 Review Execution Results

After execution completes, you'll see the results:

1. **Status**: Should show **"Succeeded"** with a green checkmark

2. **Summary section** shows:
   - Duration: ~1000-2000 ms
   - Billed duration: Similar value
   - Memory used: ~50-70 MB
   - Max memory: 128 MB

3. **Execution results tab**: Shows the response from your function

4. **Response**:
```json
{
  "statusCode": 200,
  "body": "{\"message\": \"EC2 instance management completed successfully\", \"stopped_instances\": [\"i-xxxxxxxxxxxxxxxxx\"], \"started_instances\": [\"i-yyyyyyyyyyyyyyyyy\"]}"
}
```

5. Click on the **"Logs"** dropdown to see detailed logs

#### 5.6 Review CloudWatch Logs

1. In the execution results, you should see log output like:
```
START RequestId: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx Version: $LATEST
Stopping instances: ['i-0123456789abcdef0']
Successfully stopped instances: ['i-0123456789abcdef0']
Starting instances: ['i-0fedcba9876543210']
Successfully started instances: ['i-0fedcba9876543210']
END RequestId: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
REPORT RequestId: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx Duration: 1234.56 ms Billed Duration: 1235 ms Memory Size: 128 MB Max Memory Used: 65 MB Init Duration: 234.56 ms
```

2. Alternatively, access full logs:
   - Click **"Monitor"** tab
   - Click **"View CloudWatch logs"** button
   - Click on the latest **log stream** (timestamp)
   - View all log entries

#### 5.7 Verify Instance State Changes in EC2

Now let's verify the instances actually changed state:

1. Go back to **EC2 Dashboard** → **Instances**

2. Click the **refresh button** (circular arrow icon)

3. **Check the instance states**:
   - **Instance-Auto-Stop**: Should now be **stopping** or **stopped**
   - **Instance-Auto-Start**: Should now be **pending** or **running**

**Note**: State transitions take 30-60 seconds. You might see intermediate states:
- "stopping" → will become "stopped"
- "pending" → will become "running"

4. Wait and refresh again if you see intermediate states

5. Final states should be:
   - **Instance-Auto-Stop**: **stopped** ✓
   - **Instance-Auto-Start**: **running** ✓

**✅ Checkpoint - Testing Complete**:
- ✓ Lambda function executed successfully
- ✓ Status code 200 returned
- ✓ CloudWatch logs show instance IDs
- ✓ Instance-Auto-Stop changed from running to stopped
- ✓ Instance-Auto-Start changed from stopped to running
- ✓ No errors in execution

---

## Code Explanation

Let's break down what the Lambda function code does, section by section.

### Function Signature

```python
def lambda_handler(event, context):
```

- **lambda_handler**: The entry point AWS Lambda calls when the function is invoked
- **event**: A dictionary containing data about the triggering event (not used in our case)
- **context**: Provides runtime information about the Lambda function (not used in our case)

### Boto3 Client Initialization

```python
ec2_client = boto3.client('ec2')
```

- **boto3**: AWS SDK for Python, pre-installed in Lambda
- **boto3.client('ec2')**: Creates an EC2 client to interact with the EC2 service
- Automatically uses the Lambda function's IAM role for authentication
- The role we created (Lambda-EC2-Management-Role) provides the necessary permissions

### Instance Lists Initialization

```python
instances_to_stop = []
instances_to_start = []
```

- Two empty lists to collect instance IDs
- Separates instances by their required action
- Allows batch operations (stopping/starting multiple instances at once)

### Filtering Instances with Tags

```python
response = ec2_client.describe_instances(
    Filters=[
        {
            'Name': 'tag:Action',
            'Values': ['Auto-Stop', 'Auto-Start']
        }
    ]
)
```

**What this does:**
- **describe_instances()**: EC2 API call to retrieve instance information
- **Filters**: Only returns instances matching specific criteria
- **tag:Action**: Looks for instances with a tag key named "Action"
- **Values**: Only matches if tag value is "Auto-Stop" or "Auto-Start"
- **Benefits**: Reduces API response size and processing time

### Processing the Response

```python
for reservation in response['Reservations']:
    for instance in reservation['Instances']:
        instance_id = instance['InstanceId']
        instance_state = instance['State']['Name']
```

**Understanding the structure:**
- EC2 groups instances in **Reservations** (for billing and organization)
- Each reservation can contain multiple instances
- We iterate through all reservations and all instances within them

**Extracting data:**
- **InstanceId**: Unique identifier (e.g., "i-0123456789abcdef0")
- **State.Name**: Current state (e.g., "running", "stopped", "pending", "stopping")

### Finding the Action Tag

```python
action_tag = None
for tag in instance.get('Tags', []):
    if tag['Key'] == 'Action':
        action_tag = tag['Value']
        break
```

**What this does:**
- Loops through all tags on the instance
- Tags are stored as a list of dictionaries: `[{'Key': 'Name', 'Value': 'MyInstance'}, ...]`
- Finds the tag with Key "Action"
- Stores its Value ("Auto-Stop" or "Auto-Start")
- **instance.get('Tags', [])**: Returns empty list if no tags exist (prevents errors)
- **break**: Exits loop once found (optimization)

### Categorizing Instances

```python
if action_tag == 'Auto-Stop' and instance_state == 'running':
    instances_to_stop.append(instance_id)
elif action_tag == 'Auto-Start' and instance_state == 'stopped':
    instances_to_start.append(instance_id)
```

**Logic:**
- **Auto-Stop instances**: Only add if currently **running**
  - No point trying to stop an already stopped instance
- **Auto-Start instances**: Only add if currently **stopped**
  - No point trying to start an already running instance

**Benefits:**
- Prevents unnecessary API calls
- Avoids errors from invalid state transitions
- More efficient

### Stopping Instances

```python
if instances_to_stop:
    print(f"Stopping instances: {instances_to_stop}")
    ec2_client.stop_instances(InstanceIds=instances_to_stop)
    print(f"Successfully stopped instances: {instances_to_stop}")
else:
    print("No running instances found with Auto-Stop tag")
```

**What happens:**
1. **if instances_to_stop**: Only proceed if there are instances to stop
2. **print()**: Logs to CloudWatch for monitoring
3. **stop_instances()**: EC2 API call to stop the instances
   - Accepts a list of instance IDs
   - Initiates graceful shutdown (SIGTERM signal)
4. Second print confirms action

**No instances case:**
- Logs informative message
- Doesn't make unnecessary API call

### Starting Instances

```python
if instances_to_start:
    print(f"Starting instances: {instances_to_start}")
    ec2_client.start_instances(InstanceIds=instances_to_start)
    print(f"Successfully started instances: {instances_to_start}")
else:
    print("No stopped instances found with Auto-Start tag")
```

**Similar logic to stopping:**
- Only acts if there are instances to start
- Logs before and after
- Uses **start_instances()** API call
- Initiates instance boot process

### Success Response

```python
return {
    'statusCode': 200,
    'body': json.dumps({
        'message': 'EC2 instance management completed successfully',
        'stopped_instances': instances_to_stop,
        'started_instances': instances_to_start
    })
}
```

**Response structure:**
- **statusCode**: HTTP status (200 = success)
- **body**: JSON string containing:
  - Success message
  - List of stopped instance IDs
  - List of started instance IDs
- **json.dumps()**: Converts Python dict to JSON string (required by Lambda)

### Error Handling

```python
except Exception as e:
    print(f"Error: {str(e)}")
    return {
        'statusCode': 500,
        'body': json.dumps({
            'message': 'Error managing EC2 instances',
            'error': str(e)
        })
    }
```

**What this catches:**
- Any exceptions (errors) that occur during execution
- Examples:
  - IAM permission errors
  - Network timeouts
  - Invalid instance IDs
  - API rate limits

**Error response:**
- **statusCode 500**: Indicates server error
- Logs the error message to CloudWatch
- Returns error details in response

---

## Testing and Verification

### Test Scenarios

#### Scenario 1: Normal Operation (Both Tags Present)
**Setup:**
- Instance-Auto-Stop: running
- Instance-Auto-Start: stopped

**Expected Results:**
- Instance-Auto-Stop: Changes to stopped
- Instance-Auto-Start: Changes
