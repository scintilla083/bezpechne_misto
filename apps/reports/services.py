# apps/reports/services.py
from django.core.files.base import ContentFile
from apps.reports.models import Appeal, AppealMedia
from aiogram.types import Message


async def save_media_from_message(message: Message, appeal: Appeal):
    """
    Зберігає фото/відео з повідомлення як файл у AppealMedia.
    Telegram file_id також зберігаємо.
    """
    bot = message.bot

    # Фото
    if message.photo:
        photo = message.photo[-1]  # найкраща якість
        tg_file = await bot.get_file(photo.file_id)
        file_obj = await bot.download_file(tg_file.file_path)
        django_file = ContentFile(
            file_obj.read(),
            name=f"{photo.file_unique_id}.jpg",
        )
        AppealMedia.objects.create(
            appeal=appeal,
            file=django_file,
            telegram_file_id=photo.file_id,
        )

    # Відео
    if message.video:
        video = message.video
        tg_file = await bot.get_file(video.file_id)
        file_obj = await bot.download_file(tg_file.file_path)
        django_file = ContentFile(
            file_obj.read(),
            name=f"{video.file_unique_id}.mp4",
        )
        AppealMedia.objects.create(
            appeal=appeal,
            file=django_file,
            telegram_file_id=video.file_id,
        )
