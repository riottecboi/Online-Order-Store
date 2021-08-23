from minio import Minio


class GetFileError(Exception):
    """Get file error"""
    pass

class BucketError(Exception):
    """Bucket removed or not exist"""
    pass

class FileDownload():
    api_minio_url = ""
    access_key = ""
    secret_key = ""
    minioClient = ""


    def __init__(self, **kwargs):
        for arg in kwargs.keys():
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
        # check = self.minioClient.bucket_exists(str(self.bucket_name))
        # if check is False:
        #     raise BucketError('Bucket removed or not exist')

    def download_file(self, file_name, bucket_name):
        try:
            get = self.minioClient.get_object(bucket_name=bucket_name, object_name=file_name)
            data = get.data
            type = get.headers['Content-Type']
            res = {'data':data,'content_type':type}
            return res
        except:
            raise GetFileError("Get file error")