import boto3
import os
from logger import info, debug, error

class S3Config:
    def __init__(self, aws_access_key_id=None, aws_secret_access_key=None, region_name="us-east-1", bucket_name='contactless-checking', acl='public-read'):
        self.aws_access_key_id = aws_access_key_id or os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = aws_secret_access_key or os.getenv('AWS_SECRET_ACCESS_KEY')
        self.bucket_name = bucket_name
        self.region_name = region_name or os.getenv('AWS_DEFAULT_REGION')
        self.acl = acl

        if not self.aws_access_key_id or not self.aws_secret_access_key:
            raise EnvironmentError('AWS credentials are not set in the environment. Please set them to use AWS S3.')

        if not self.region_name:
            raise EnvironmentError('AWS region is not set in the environment. Please set it to use AWS S3.')

        self.session = boto3.Session(
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.region_name
        )

        self.s3 = self.session.client('s3')
        self._create_bucket()

    def bucket_exists(self):
        try:
            self.s3.head_bucket(Bucket=self.bucket_name)
            info(f"Bucket {self.bucket_name} exists.")
            return True
        except self.s3.exceptions.ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                info(f"Bucket {self.bucket_name} does not exist.")
                return False
            else:
                error(f"Error checking bucket existence: {e}")
                raise e

    def _create_bucket(self):
        if not self.bucket_exists():
            try:
                self.s3.create_bucket(
                    Bucket=self.bucket_name,
                    CreateBucketConfiguration={
                        'LocationConstraint': self.region_name
                    },
                    ACL=self.acl
                )
                info(f'Bucket {self.bucket_name} created with ACL {self.acl}.')
            except Exception as e:
                info(f'Error creating bucket: {e}')
        else:
            info(f'Bucket {self.bucket_name} already exists. Skipping creation.')

    def list_buckets(self):
        try:
            buckets = self.s3.list_buckets()
            info('Listing existing buckets:')
            for bucket in buckets['Buckets']:
                info(f'  {bucket["Name"]}')
        except Exception as e:
            error(f'Error listing buckets: {e}')

    def create_folder(self, folder_name):
        if not folder_name.endswith('/'):
            folder_name += '/'
        try:
            self.s3.put_object(Bucket=self.bucket_name, Key=folder_name)
            info(f'Folder {folder_name} created in bucket {self.bucket_name}.')
        except Exception as e:
            error(f'Error creating folder: {e}')

    def upload_file(self, object_name, file_name):
        folder_name = os.path.dirname(object_name)
        if folder_name:
            self.create_folder(folder_name)
        try:
            self.s3.upload_file(file_name, self.bucket_name, object_name)
            info(f'File {file_name} uploaded to {self.bucket_name}/{object_name}.')
        except Exception as e:
            error(f'Error uploading file: {e}')

    def delete_file(self, folder_name, file_name):
        object_key = f"{folder_name}/{file_name}"
        try:
            self.s3.delete_object(Bucket=self.bucket_name, Key=object_key)
            info(f'File {object_key} deleted from bucket {self.bucket_name}.')
        except Exception as e:
            error(f'Error deleting file: {e}')
    
    def retrieve_file(self, object_name, download_path):
        try:
            self.s3.download_file(self.bucket_name, object_name, download_path)
            info(f'File {object_name} downloaded to {download_path}.')
        except Exception as e:
            info(f'Error downloading file: {e}')
            
    def list_object(self, prefix):
        try:
            response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
            objects = []
            if 'Contents' in response:
                objects = [obj['Key'] for obj in response['Contents']]
                info(f'Objects listed under {prefix}: {objects}')
            else:
                info(f'No objects found under {prefix}.')
            return objects
        except Exception as e:
            error(f'Error listing objects: {e}')
            return []

    def download_all_objects(self, prefix, local_dir):
        objects = self.list_object(prefix)
        for obj in objects:
            local_path = os.path.join(local_dir, obj)
            local_folder = os.path.dirname(local_path)
            if not os.path.exists(local_folder):
                os.makedirs(local_folder)
                info(f'Created local directory {local_folder} for downloading files.')
            self.retrieve_file(obj, local_path)
            
    def upload_folder(self, s3_prefix='', folder_path=''):
        for root, _, files in os.walk(folder_path):
            for file in files:
                local_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_path, folder_path)
                s3_path = os.path.join(s3_prefix, relative_path).replace("\\", "/")  # Ensure S3 path uses forward slashes
                self.upload_file(s3_path, local_path)
                info(f'Uploaded {local_path} to {self.bucket_name}/{s3_path}.')