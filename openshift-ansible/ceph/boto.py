import boto3

# Create an S3 client
s3 = boto3.client('s3', endpoint_url='http://ceph.cnj.jus.br/')

# Create Bucket
#s3.create_bucket(ACL='private', Bucket='origin')

# Print out S3 bucket list
response = s3.list_buckets()
print("Bucket List: %s" % response['Buckets'])

# List objects in S3 bucket
bucket_objects = s3.list_objects_v2(Bucket='origin', MaxKeys=20)
print("Object List: %s" % bucket_objects)
