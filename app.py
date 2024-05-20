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

def initialize_bucket():
    """Ensure the bucket is created and ready to use."""
    try:
        s3_client.create_bucket(
            Bucket=BUCKET_NAME,
            CreateBucketConfiguration={'LocationConstraint': 'ap-southeast-1'}  # Set to your preferred region (Thailand)
        )
        st.write(f"Bucket '{BUCKET_NAME}' created successfully!")
    except (s3_client.exceptions.BucketAlreadyOwnedByYou, s3_client.exceptions.BucketAlreadyExists):
        st.write(f"Bucket '{BUCKET_NAME}' already exists.")
    except Exception:
        time.sleep(1)

def upload_file(uploaded_file):
    """Upload a file to the S3 bucket."""
    try:
        s3_client.upload_fileobj(uploaded_file, BUCKET_NAME, uploaded_file.name)
        st.success(f'File {uploaded_file.name} uploaded successfully!')
    except Exception as e:
        st.error(f"Failed to upload file {uploaded_file.name}: {e}")

def list_files():
    """List files in the S3 bucket."""
    try:
        files = s3_client.list_objects_v2(Bucket=BUCKET_NAME).get('Contents', [])
        return [file['Key'] for file in files]
    except Exception as e:
        st.error(f"Failed to list files: {e}")
        return []

def delete_file(file_name):
    """Delete a file from the S3 bucket."""
    try:
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=file_name)
        st.success(f'File {file_name} deleted successfully!')
    except Exception as e:
        st.error(f"An error occurred while deleting file {file_name}: {e}")

def download_file(file_name):
    """Generate a presigned URL to download a file from the S3 bucket."""
    try:
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': file_name},
            ExpiresIn=3600  # URL expires in 1 hour
        )
        return presigned_url
    except Exception as e:
        st.error(f"An error occurred while generating the download link for {file_name}: {e}")
        return None

def main():
    st.title('File Management with Streamlit and LocalStack')

    # Initialize the bucket
    initialize_bucket()

    # Upload File
    uploaded_file = st.file_uploader('Upload a file', type=['pdf'])
    if uploaded_file is not None:
        with st.spinner('Uploading file...'):
            upload_file(uploaded_file)
    
    # List files
    st.subheader('Files in the bucket:')
    file_list = list_files()
    
    for file_name in file_list:
        st.write(file_name)
        presigned_url = download_file(file_name)
        if presigned_url:
            st.markdown(f"[Download {file_name}]({presigned_url})")

        if st.button(f'Delete {file_name}'):
            with st.spinner(f'Deleting {file_name}...'):
                delete_file(file_name)
                # Refresh file list after deletion
                st.experimental_rerun()
                
main()
