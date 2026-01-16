
from django import template

register = template.Library()

@register.filter
def minutes_to_time(minutes):
    """
    분 단위 -> 시간 단위
    """
    if minutes is None:
        return ""
    h = minutes // 60
    m = minutes % 60
    return f"{h}시간 {m}분"


@register.filter
def rating_to_stars(rating):
    """
    별점 값 -> 별 개수로
    """
    try:
        rating = float(rating)
    except (TypeError, ValueError):
        return ""

    full = int(rating)
    half = 1 if rating - full >= 0.5 else 0
    empty = 5 - full - half

    return "★" * full + ("☆" if half else "") # + "·" * empty
