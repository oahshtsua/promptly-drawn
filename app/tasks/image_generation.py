import asyncio

from loguru import logger
from sqlalchemy import select

from app.celery_app import celery_app
from app.database.models import GeneratedImage
from app.database.session import async_session
from app.services.image_generation import image_gen_service
from app.services.storage import storage


async def _text_to_image_generation(req_id: str):
    logger.info(f"Processing request: {req_id}")
    async with async_session() as session:
        query = select(GeneratedImage).where(GeneratedImage.id == req_id)
        result = await session.execute(query)
        image = result.scalar_one_or_none()
        if not image:
            raise Exception("Image request does not exist")

        try:
            output_image = image_gen_service.generate(
                image.prompt,
                negative_prompt=image.negative_prompt,
                inference_steps=image.inference_steps,
            )
            storage.upload_image(output_image, image.filename)

            image.status = "SUCCESS"
            session.add(image)
            await session.commit()
        except Exception as e:
            logger.error(e)
            image.status = "FAILED"
            session.add(image)
            await session.commit()


@celery_app.task()
def text_to_image_generation(req_id: str):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_text_to_image_generation(req_id))
