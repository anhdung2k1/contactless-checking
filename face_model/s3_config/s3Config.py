import boto3
import os

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
            return True
        except self.s3.exceptions.ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                return False
            else:
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
                print(f'Bucket {self.bucket_name} created with ACL {self.acl}.')
            except Exception as e:
                print(f'Error creating bucket: {e}')
        else:
            print(f'Bucket {self.bucket_name} already exists. Skip ...')

    def list_buckets(self):
        buckets = self.s3.list_buckets()
        print('Existing buckets: ')
        for bucket in buckets['Buckets']:
            print(f'  {bucket["Name"]}')

    def create_folder(self, folder_name):
        if not folder_name.endswith('/'):
            folder_name += '/'
        try:
            self.s3.put_object(Bucket=self.bucket_name, Key=folder_name)
            print(f'Folder {folder_name} created in bucket {self.bucket_name}')
        except Exception as e:
            print(f'Error creating folder: {e}')

    def upload_file(self, object_name, file_name):
        folder_name = os.path.dirname(object_name)
        if folder_name:
            self.create_folder(folder_name)
        try:
            self.s3.upload_file(file_name, self.bucket_name, object_name)
            print(f'File {file_name} uploaded to {self.bucket_name}/{object_name}')
        except Exception as e:
            print(f'Error uploading file: {e}')

    def delete_file(self, folder_name, file_name):
        object_key = f"{folder_name}/{file_name}"
        try:
            self.s3.delete_object(Bucket=self.bucket_name, Key=object_key)
            print(f'File {object_key} deleted from bucket {self.bucket_name}')
        except Exception as e:
            print(f'Error deleting file: {e}')
    
    def retrieve_file(self, object_name, download_path):
        try:
            self.s3.download_file(self.bucket_name, object_name, download_path)
            print(f'File {object_name} downloaded to {download_path}')
        except:
            print(f'Error downloading file: {e}')

# Example usage
# s3_manager = S3Manager(region_name='us-west-2', acl='public-read')
# s3_manager.list_buckets()
# s3_manager.upload_file('your_folder_name/your_file_name_in_s3', 'path_to_your_file')
# s3_manager.delete_file('your_folder_name', 'your_file_name_in_s3')
