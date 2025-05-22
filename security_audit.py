import boto3

# Initialize clients
s3 = boto3.client('s3')
rds = boto3.client('rds')
ec2 = boto3.client('ec2')

def check_s3():
    print("\n🔍 Checking S3 Buckets...")
    for bucket in s3.list_buckets()['Buckets']:
        name = bucket['Name']
        print(f"\nBucket: {name}")
        
        # Check public access
        try:
            policy = s3.get_bucket_policy(Bucket=name)
            print("🚨 Publicly accessible bucket!")
        except:
            print("✅ No public access policy.")
        
        # Check versioning
        versioning = s3.get_bucket_versioning(Bucket=name)
        if versioning.get('Status') != 'Enabled':
            print("⚠️ Versioning is disabled.")
        
        # Check logging
        logging = s3.get_bucket_logging(Bucket=name)
        if 'LoggingEnabled' not in logging:
            print("⚠️ Logging is disabled.")

def check_rds():
    print("\n🔍 Checking RDS Instances...")
    instances = rds.describe_db_instances()['DBInstances']
    for db in instances:
        print(f"\nDB Identifier: {db['DBInstanceIdentifier']}")
        
        if db['PubliclyAccessible']:
            print("🚨 Publicly accessible RDS instance.")
        if not db.get('DeletionProtection', False):
            print("⚠️ Deletion protection is disabled.")
        if db.get('BackupRetentionPeriod', 0) == 0:
            print("⚠️ Backups are disabled.")

def check_security_groups():
    print("\n🔍 Checking Security Groups...")
    groups = ec2.describe_security_groups()['SecurityGroups']
    for sg in groups:
        print(f"\nSecurity Group: {sg['GroupName']} ({sg['GroupId']})")
        for perm in sg['IpPermissions']:
            from_port = perm.get('FromPort')
            to_port = perm.get('ToPort')
            for ip in perm.get('IpRanges', []):
                cidr = ip.get('CidrIp', '')
                if cidr == '0.0.0.0/0':
                    if from_port == 22:
                        print("🚨 Public SSH access (port 22)")
                    elif from_port == 27017:
                        print("🚨 Public MongoDB access (port 27017)")

if __name__ == "__main__":
    check_s3()
    check_rds()
    check_security_groups()
