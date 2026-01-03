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