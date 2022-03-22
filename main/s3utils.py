from django.core.files.storage import get_storage_class
from storages.backends.s3boto3 import S3Boto3Storage, SpooledTemporaryFile
import os

class CachedS3Boto3Storage(S3Boto3Storage):
    """
    S3 storage backend that saves files locally too.
    """
    location = 'static'

    def __init__(self, *args, **kwargs):
        self.local_storage = get_storage_class(
            "compressor.storage.GzipCompressorFileStorage")()
        super(CachedS3Boto3Storage, self).__init__(*args, **kwargs)

    def save(self, name, content):
        self.local_storage._save(name, content)
        super(CachedS3Boto3Storage, self).save(
            name, self.local_storage._open(name))
        return name


class MediaS3Boto3Storage(S3Boto3Storage):
    """ S3 storage backend that saves to the 'media' subdirectory"""
    location = 'media'

    def _save_content(self, obj, content, parameters):
        """
        We create a clone of the content file as when this is passed to boto3 it wrongly closes
        the file upon upload where as the storage backend expects it to still be open
        See https://github.com/jschneier/django-storages/issues/382
        """
        # Seek our content back to the start
        content.seek(0, os.SEEK_SET)

        # Create a temporary file that will write to disk after a specified size
        content_autoclose = SpooledTemporaryFile()

        # Write our original content into our copy that will be closed by boto3
        content_autoclose.write(content.read())

        # Upload the object which will auto close the content_autoclose instance
        super(MediaS3Boto3Storage, self)._save_content(obj, content_autoclose, parameters)

        # Cleanup if this is fixed upstream our duplicate should always close
        if not content_autoclose.closed:
            content_autoclose.close()
