import os
import boto3


class FileManager:
    def __init__(self):
        self.session = self.aws_session()
        self.bucket_name = os.getenv('S3_BUCKET_NAME')

    def aws_session(self, region_name='eu-central-1'):
        return boto3.session.Session(aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                                     aws_secret_access_key=os.getenv('AWS_ACCESS_KEY_SECRET'),
                                     region_name=region_name)

    def upload_file_to_bucket(self, file_path):
        s3_resource = self.session.resource('s3')
        file_dir, file_name = os.path.split(file_path)

        bucket = s3_resource.Bucket(self.bucket_name)
        bucket.upload_file(
          Filename=file_path,
          Key=file_name,
        )

        s3_url = f"https://{self.bucket_name}.s3.amazonaws.com/{file_name}"
        return s3_url

    def download_file_from_bucket(self, name, destination):
        s3_resource = self.session.resource('s3')
        bucket = s3_resource.Bucket(self.bucket_name)
        bucket.download_file(Key=name, Filename=destination)
