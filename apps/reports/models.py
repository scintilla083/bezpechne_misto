from django.db import models


class TelegramUser(models.Model):
    telegram_id = models.BigIntegerField(unique=True, verbose_name="Telegram ID")
    username = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Username"
    )
    full_name = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Ім'я"
    )
    city = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Населений пункт"
    )
    phone_number = models.CharField(
        max_length=32, blank=True, null=True, verbose_name="Номер телефону"
    )
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.telegram_id} ({self.username or self.full_name or 'Без імені'})"

    class Meta:
        verbose_name = "Користувач Telegram"
        verbose_name_plural = "Користувачі Telegram"


class Appeal(models.Model):
    class Target(models.TextChoices):
        POLICE = "police", "Поліція"
        UTILITY = "utility", "Комунальне підприємство"
        MAYOR = "mayor", "Мерія"
        FEEDBACK = "feedback", "Зворотній зв'язок"

    class PoliceCategory(models.TextChoices):
        NARCOTIC = "narcotic", "Наркозлочин"
        OTHER = "other", "Інше правопорушення"

    user = models.ForeignKey(
        TelegramUser,
        on_delete=models.CASCADE,
        related_name="appeals",
        verbose_name="Користувач",
    )
    target = models.CharField(
        max_length=20, choices=Target.choices, verbose_name="Звернення у"
    )
    police_category = models.CharField(
        max_length=20,
        choices=PoliceCategory.choices,
        blank=True,
        null=True,
        verbose_name="Категорія (поліція)",
    )

    text = models.TextField(verbose_name="Текст повідомлення")
    location_text = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Локація (текстом)",
    )
    latitude = models.FloatField(blank=True, null=True, verbose_name="Широта")
    longitude = models.FloatField(blank=True, null=True, verbose_name="Довгота")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Створено")
    is_submitted = models.BooleanField(
        default=False, verbose_name="Відправлено користувачем"
    )

    def __str__(self):
        return f"Звернення #{self.pk} від {self.user}"

    class Meta:
        verbose_name = "Звернення"
        verbose_name_plural = "Звернення"


def appeal_media_path(instance, filename):
    return f"appeals/{instance.appeal_id}/{filename}"


class AppealMedia(models.Model):
    appeal = models.ForeignKey(
        Appeal,
        on_delete=models.CASCADE,
        related_name="media",
        verbose_name="Звернення",
    )
    file = models.FileField(
        upload_to=appeal_media_path,
        blank=True,
        null=True,
        verbose_name="Файл",
    )
    telegram_file_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Telegram file_id",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Створено")

    def __str__(self):
        return f"Медіа #{self.pk} до звернення #{self.appeal_id}"

    class Meta:
        verbose_name = "Медіа"
        verbose_name_plural = "Медіа"
