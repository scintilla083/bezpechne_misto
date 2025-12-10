from django.contrib import admin
from .models import TelegramUser, Appeal, AppealMedia
from django.utils.html import mark_safe
# TODO добавить возможность ставит флаг "Не обработано" "В обработке" "Обработано" для звернень
# TODO добавить типчикам вкладку с аналитикой по зверненням,
@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ("telegram_id", "username", "full_name", "city", "created_at")
    search_fields = ("telegram_id", "username", "full_name", "city")


class AppealMediaInline(admin.TabularInline):
    model = AppealMedia
    extra = 0
    readonly_fields = ("preview", "created_at")
    fields = ("file", "telegram_file_id", "preview", "created_at")

    def preview(self, obj):
        if not obj.file:
            return "—"
        url = obj.file.url
        name = (obj.file.name or "").lower()
        if name.endswith((".jpg", ".jpeg", ".png", ".gif", ".webp")):
            return mark_safe(f'<img src="{url}" style="max-height: 150px; max-width: 200px;" />')
        if name.endswith((".mp4", ".mov", ".avi", ".mkv", ".webm")):
            return mark_safe(
                f'<video src="{url}" controls style="max-height: 200px; max-width: 250px;"></video>'
            )
        return mark_safe(f'<a href="{url}" target="_blank">Переглянути файл</a>')

    preview.short_description = "Попередній перегляд"


@admin.register(Appeal)
class AppealAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_telegram_id",
        "target",
        "police_category",
        "short_text",
        "media_count",
        "location_display",
        "created_at",
        "is_submitted",
    )
    list_filter = ("target", "police_category", "is_submitted", "created_at")
    search_fields = ("text", "user__telegram_id", "user__city")
    inlines = [AppealMediaInline]

    def user_telegram_id(self, obj):
        return obj.user.telegram_id

    user_telegram_id.short_description = "id користувача"

    def short_text(self, obj):
        if len(obj.text) > 50:
            return obj.text[:50] + "..."
        return obj.text

    short_text.short_description = "текст повідомлення"

    def media_count(self, obj):
        return obj.media.count()

    media_count.short_description = "фото/відео"

    def location_display(self, obj):
        if obj.location_text:
            return obj.location_text
        if obj.latitude and obj.longitude and obj.user and obj.user.city:
            return f"{obj.user.city} ({obj.latitude:.5f}, {obj.longitude:.5f})"
        if obj.latitude and obj.longitude:
            return f"{obj.latitude:.5f}, {obj.longitude:.5f}"
        if obj.user and obj.user.city:
            return obj.user.city
        return "-"

    location_display.short_description = "локація"
