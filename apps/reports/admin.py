from django.contrib import admin
from .models import TelegramUser, Appeal, AppealMedia
from django.utils.html import mark_safe
from django.contrib import admin
from .models import TelegramUser, Appeal, AppealMedia
from django.utils.html import mark_safe, format_html
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
import requests

from bot.config import settings as bot_settings

# TODO добавить возможность ставит флаг "Не обработано" "В обработке" "Обработано" для звернень
# TODO добавить типчикам вкладку с аналитикой по зверненням,
@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ("telegram_id", "username", "full_name", "city", "created_at")
    search_fields = ("telegram_id", "username", "full_name", "city")

def format_admin_reply(appeal):
    category_text = ""

    # Определяем корректное название категории
    if appeal.target == Appeal.Target.POLICE:
        if appeal.police_category:
            category_text = dict(Appeal.PoliceCategory.choices).get(appeal.police_category, "")
        else:
            category_text = "Правопорушення"

    elif appeal.target == Appeal.Target.UTILITY:
        if appeal.utility_category:
            category_text = dict(Appeal.UtilityCategory.choices).get(appeal.utility_category, "")
        else:
            category_text = "Питання комунальних служб"

    elif appeal.target == Appeal.Target.MAYOR:
        category_text = "Питання до міської ради"

    elif appeal.target == Appeal.Target.FEEDBACK:
        category_text = "Відгук користувача"

    else:
        category_text = "Ваше звернення"

    # Формируем профессиональный текст
    text = (
        f"Ми опрацювали ваше звернення щодо **{category_text}** у розділі "
        f"«{dict(Appeal.Target.choices).get(appeal.target)}».\n\n"
        f"Нижче наведено відповідь від уповноваженого спеціаліста:\n\n"
        f"📝 *{appeal.admin_reply}*\n\n"
        "Дякуємо, що допомагаєте робити наше місто безпечнішим!"
    )

    return text

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
        "utility_category",
        "short_text",
        "media_count",
        "location_display",
        "created_at",
        "is_submitted",
        "reply_sent",
    )
    list_filter = ("target", "police_category", "utility_category", "is_submitted", "created_at")
    search_fields = ("text", "user__telegram_id", "user__city")
    inlines = [AppealMediaInline]
    readonly_fields = ("send_reply_button",)


    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                "<int:appeal_id>/send_reply/",
                self.admin_site.admin_view(self.send_reply_view),
                name="reports_appeal_send_reply",
            ),
        ]
        return my_urls + urls

    def send_reply_button(self, obj):
        if not obj.pk:
            return "Спочатку збережіть звернення"

        if not obj.admin_reply:
            return "Заповніть поле 'Відповідь адміністратора' та збережіть запис."

        if obj.reply_sent:
            return "Відповідь вже відправлено користувачу"

        return format_html(
            '<a class="button" href="{}">Надіслати відповідь користувачу</a>',
            "../send_reply/",
        )

    send_reply_button.short_description = "Відправити відповідь"

    def send_reply_view(self, request, appeal_id, *args, **kwargs):
        appeal = self.get_object(request, appeal_id)
        if appeal is None:
            messages.error(request, "Звернення не знайдено.")
            return redirect("admin:reports_appeal_changelist")

        if not appeal.admin_reply:
            messages.error(request, "Спочатку заповніть поле 'Відповідь адміністратора'.")
            return redirect("../change/")

        if not appeal.user or not appeal.user.telegram_id:
            messages.error(request, "У звернення відсутній Telegram користувач.")
            return redirect("../change/")

        token = bot_settings.bot_token
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        reply_text = format_admin_reply(appeal)

        payload = {
            "chat_id": appeal.user.telegram_id,
            "text": reply_text,
            "parse_mode": "Markdown",
        }
        try:
            resp = requests.post(url, data=payload, timeout=10)
            data = resp.json()
            if resp.status_code == 200 and data.get("ok"):
                appeal.reply_sent = True
                appeal.save(update_fields=["reply_sent"])
                messages.success(request, "Відповідь успішно відправлена користувачу.")
            else:
                messages.error(request, f"Помилка Telegram API: {data}")
        except Exception as e:
            messages.error(request, f"Помилка відправки: {e}")

        return redirect("../change/")

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
