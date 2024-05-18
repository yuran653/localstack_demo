import streamlit as st
import boto3
import time

# Initialize the S3 client to interact with LocalStack
s3_client = boto3.client(
    's3',
    endpoint_url='http://localstack:4566',  # Use the service name defined in docker-compose.yml
    aws_access_key_id='test',
    aws_secret_access_key='test',
)

BUCKET_NAME = 'mybucket'

# Add a delay to ensure LocalStack is fully initialized
time.sleep(5)

# Attempt to create the bucket in LocalStack
try:
    s3_client.create_bucket(
        Bucket=BUCKET_NAME,
        CreateBucketConfiguration={'LocationConstraint': 'ap-southeast-1'}  # Set to your preferred region (Thailand)
    )
    st.write(f"Bucket '{BUCKET_NAME}' created successfully!")
except (s3_client.exceptions.BucketAlreadyOwnedByYou, s3_client.exceptions.BucketAlreadyExists):
    st.write(f"Bucket '{BUCKET_NAME}' already exists.")

st.title('File Management with Streamlit and LocalStack')

# Upload File
uploaded_file = st.file_uploader('Upload a file', type=['txt', 'pdf', 'png', 'jpg', 'jpeg'])
if uploaded_file is not None:
    s3_client.upload_fileobj(uploaded_file, BUCKET_NAME, uploaded_file.name)
    st.success(f'File {uploaded_file.name} uploaded successfully!')

# List files
st.subheader('Files in the bucket:')
files = s3_client.list_objects_v2(Bucket=BUCKET_NAME).get('Contents', [])
file_list = [file['Key'] for file in files]

for file_name in file_list:
    st.write(file_name)

    # Generate the presigned URL using localstack service name
    presigned_url = s3_client.generate_presigned_url('get_object', Params={'Bucket': BUCKET_NAME, 'Key': file_name}, ExpiresIn=3600)
    
    st.markdown(f"[Download {file_name}]({presigned_url})")

    # Delete button
    if st.button(f'Delete {file_name}'):
        try:
            s3_client.delete_object(Bucket=BUCKET_NAME, Key=file_name)
            st.success(f'File {file_name} deleted successfully!')
            # Refresh file list after deletion
            st.experimental_rerun()
        except Exception as e:
            st.error(f"An error occurred while deleting file {file_name}: {e}")
