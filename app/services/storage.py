import io
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from minio import Minio
from PIL.Image import Image

from app.config import settings


class Storage(ABC):
    @abstractmethod
    def upload_image(self, image: Image, object_name: str):
        pass

    @abstractmethod
    def get_presigned_url(
        self,
        object_name: str,
        *,
        expires: timedelta,
    ) -> tuple[str, str]:
        pass


class MinioStorage(Storage):
    def __init__(
        self, endpoint: str, bucket: str, access_key: str, secret_key: str
    ) -> None:
        self.bucket = bucket
        self.client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=False if settings.DEBUG else True,
        )

        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    def upload_image(self, image: Image, object_name: str):
        image_data = io.BytesIO()
        image.save(image_data, format="PNG")
        image_data.seek(0)
        image_data_length = len(image_data.getvalue())

        self.client.put_object(
            self.bucket,
            object_name,
            image_data,
            length=image_data_length,
            content_type="image/png",
        )

    def get_presigned_url(
        self,
        object_name: str,
        *,
        expires: timedelta = timedelta(days=7),
    ) -> tuple[str, str]:
        expiry = datetime.now() + expires
        presigned_url = self.client.presigned_get_object(
            bucket_name=self.bucket,
            object_name=object_name,
            expires=expires,
        )
        return presigned_url, f"{expiry.isoformat()}Z"


storage = MinioStorage(
    endpoint=settings.STORAGE_ENDPOINT,
    bucket=settings.STORAGE_BUCKET,
    access_key=settings.STORAGE_ACCESS_KEY,
    secret_key=settings.STORAGE_SECRET_KEY,
)
