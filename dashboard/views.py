# dashboard/views.py

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from apps.reports.models import Appeal, TelegramUser
from django.db.models import Count
from django.db.models.expressions import RawSQL
from django.utils import timezone
from datetime import timedelta
from .utils import CATEGORY_UA


@staff_member_required
def dashboard_view(request):

    total_users = TelegramUser.objects.count()
    total_appeals = Appeal.objects.count()

    # --- Розподіл звернень по розділах ---
    appeals_raw = Appeal.objects.values("target").annotate(count=Count("id"))

    appeals_by_target = []
    for item in appeals_raw:
        target_code = item["target"]
        appeals_by_target.append({
            "target": target_code,
            "name_ua": CATEGORY_UA.get(target_code, "Невідомо"),
            "count": item["count"]
        })

    # --- Звернення за останні 30 днів ---
    last_30 = timezone.now() - timedelta(days=30)
    appeals_by_day = (
        Appeal.objects.filter(created_at__gte=last_30)
            .extra(select={"day": "date(created_at)"})
            .values("day")
            .annotate(count=Count("id"))
    )

    # --- Розподіл по днях тижня ---
    raw_weekday = (
        Appeal.objects
            .annotate(weekday=RawSQL("strftime('%w', created_at)", []))
            .values("weekday")
            .annotate(count=Count("id"))
            .order_by("weekday")
    )

    weekday_counts = {str(i): 0 for i in range(7)}
    for item in raw_weekday:
        weekday_counts[str(item["weekday"])] = item["count"]

    # Порядок Пн..Нд
    ordered_weekdays = [
        weekday_counts["1"],  # Пн
        weekday_counts["2"],  # Вт
        weekday_counts["3"],  # Ср
        weekday_counts["4"],  # Чт
        weekday_counts["5"],  # Пт
        weekday_counts["6"],  # Сб
        weekday_counts["0"],  # Нд
    ]

    # --- Розподіл по категоріях поліції ---
    police_categories = (
        Appeal.objects.filter(target="police")
            .values("police_category")
            .annotate(count=Count("id"))
    )

    # --- Останні звернення ---
    last_appeals = Appeal.objects.select_related("user").order_by("-created_at")[:10]
    # Додаємо людинозрозумілу назву категорії
    for a in last_appeals:
        a.target_ua = CATEGORY_UA.get(a.target, "Невідомо")

    # Рендер сторінки
    return render(request, "dashboard/dashboard.html", {
        "total_users": total_users,
        "total_appeals": total_appeals,
        "appeals_by_target": appeals_by_target,
        "appeals_by_day": appeals_by_day,
        "appeals_by_weekday": ordered_weekdays,
        "police_categories": police_categories,
        "CATEGORY_UA": CATEGORY_UA,
        "last_appeals": last_appeals,
    })
