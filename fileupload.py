from minio import Minio
from datetime import datetime
import uuid

class Error():
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return "Error: {}".format(self.message)
        else:
            return "Error has been raised"


class FileUpload():
    bucket_name = ""
    api_minio_url = ""
    access_key = ""
    secret_key = ""
    minioClient = ""
    minio_secure = False

    def __init__(self, **kwargs):
        for arg in kwargs.keys():
            if arg == "bucket_name":
                self.bucket_name = kwargs['bucket_name']
            if arg == "api_minio_url":
                self.api_minio_url = kwargs['api_minio_url']
            if arg == "access_key":
                self.access_key = kwargs['access_key']
            if arg == "secret_key":
                self.secret_key = kwargs['secret_key']
            if arg == "minio_secure":
                self.minio_secure = kwargs['minio_secure']
        self.minioClient = Minio(self.api_minio_url,
                            access_key=self.access_key,
                            secret_key=self.secret_key,
                            secure=self.minio_secure)

        check = self.minioClient.bucket_exists(str(self.bucket_name))
        if check is False:
            self.minioClient.make_bucket(self.bucket_name)

    def upload_file(self, file, content_type):
        clf = uuid.uuid4()
        datestring = datetime.today().strftime('%Y/%m/%d/')
        identify = datestring + str(clf)
        try:
            self.minioClient.fput_object(bucket_name=self.bucket_name, object_name=identify, file_path=file,
                                         content_type=content_type)
            if self.minio_secure != False:
                return "minios://{}/{}/{}".format(self.api_minio_url,self.bucket_name,identify)
            else:
                return "minio://{}/{}/{}".format(self.api_minio_url,self.bucket_name,identify)
        except:
            raise Error('Put file object error')

