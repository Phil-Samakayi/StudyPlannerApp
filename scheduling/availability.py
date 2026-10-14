"""
scheduling/availability.py

Shared free-time calculation over students' recurring weekly availability
(ScheduleSlot). This is a GRASP Pure Fabrication: no single domain object
holds all the information needed (it spans several students' slots), so the
responsibility lives in this dedicated service rather than on ScheduleSlot
or on a student.

Other apps (e.g. matching) call into this module; it deliberately imports
nothing from them, so the dependency between apps stays one-way.

Times are handled as minutes since midnight in the project's local time
zone (settings.TIME_ZONE), and every window is half-open: [start, end).
"""
import datetime

from django.utils import timezone

from .models import DayOfWeek, ScheduleSlot

DEFAULT_DAYS_AHEAD = 7
DEFAULT_MIN_MINUTES = 60
DEFAULT_LIMIT = 10
ROUND_TO_MINUTES = 15


def _to_minutes(t):
    return t.hour * 60 + t.minute


def _merge(intervals):
    """Sort and merge overlapping or touching intervals, e.g. 14-15 + 15-16 -> 14-16."""
    merged = []
    for start, end in sorted(intervals):
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return [tuple(i) for i in merged]


def _intersect(a, b):
    """Intersect two sorted, merged interval lists (two-pointer sweep)."""
    result = []
    i = j = 0
    while i < len(a) and j < len(b):
        start = max(a[i][0], b[j][0])
        end = min(a[i][1], b[j][1])
        if start < end:
            result.append((start, end))
        # Advance whichever interval finishes first.
        if a[i][1] < b[j][1]:
            i += 1
        else:
            j += 1
    return result


def _weekly_windows_by_student(students):
    """{student_pk: {day_of_week: [(start_min, end_min), ...]}} using one query."""
    by_student = {s.pk: {} for s in students}
    rows = ScheduleSlot.objects.filter(student__in=students).values_list(
        "student_id", "day_of_week", "start_time", "end_time"
    )
    for student_id, day, start, end in rows:
        by_student[student_id].setdefault(day, []).append((_to_minutes(start), _to_minutes(end)))
    return {
        pk: {day: _merge(intervals) for day, intervals in days.items()}
        for pk, days in by_student.items()
    }


def common_weekly_windows(students):
    """
    Weekly windows when *all* the given students are free.

    Returns {day_of_week: [(start_min, end_min), ...]}, containing only days
    that have at least one shared window. A student with no slots at all
    makes the result empty, since nobody can be sure when they're free.
    """
    students = list(students)
    if not students:
        return {}
    per_student = list(_weekly_windows_by_student(students).values())
    common = {}
    for day in DayOfWeek.values:
        windows = per_student[0].get(day, [])
        for other in per_student[1:]:
            windows = _intersect(windows, other.get(day, []))
            if not windows:
                break
        if windows:
            common[day] = windows
    return common


def has_common_availability(students, min_minutes=1):
    """True if the students share at least one weekly window of min_minutes or more."""
    return any(
        end - start >= min_minutes
        for windows in common_weekly_windows(students).values()
        for start, end in windows
    )


def students_without_availability(students):
    """Students who have not set any availability slots yet."""
    students = list(students)
    with_slots = set(
        ScheduleSlot.objects.filter(student__in=students).values_list("student_id", flat=True)
    )
    return [s for s in students if s.pk not in with_slots]


def _round_up(dt, minutes=ROUND_TO_MINUTES):
    """Round an aware datetime up to the next multiple of `minutes` past the hour."""
    excess = datetime.timedelta(
        minutes=dt.minute % minutes, seconds=dt.second, microseconds=dt.microsecond
    )
    if not excess:
        return dt
    return dt - excess + datetime.timedelta(minutes=minutes)


def suggest_session_times(
    students,
    now=None,
    days_ahead=DEFAULT_DAYS_AHEAD,
    min_minutes=DEFAULT_MIN_MINUTES,
    limit=DEFAULT_LIMIT,
):
    """
    Concrete upcoming time windows, over the next `days_ahead` days, when all
    `students` are free for at least `min_minutes`.

    A window already in progress is offered from now (rounded up to the next
    quarter hour) if enough of it remains. Returns a dict:

        {
            "suggestions": [
                {"start": iso, "end": iso, "day_name": "Tuesday", "duration_minutes": 120},
                ...
            ],
            "students_without_availability": [<student>, ...],
        }
    """
    students = list(students)
    now = timezone.localtime(now or timezone.now())
    tz = timezone.get_current_timezone()
    weekly = common_weekly_windows(students)

    suggestions = []
    for offset in range(days_ahead):
        date = now.date() + datetime.timedelta(days=offset)
        for start_min, end_min in weekly.get(date.weekday(), []):
            start = timezone.make_aware(
                datetime.datetime.combine(date, datetime.time(start_min // 60, start_min % 60)), tz
            )
            end = timezone.make_aware(
                datetime.datetime.combine(date, datetime.time(end_min // 60, end_min % 60)), tz
            )
            if end <= now:
                continue
            if start < now:
                start = _round_up(now)
            duration = int((end - start).total_seconds() // 60)
            if duration < min_minutes:
                continue
            suggestions.append({
                "start": start.isoformat(),
                "end": end.isoformat(),
                "day_name": DayOfWeek(date.weekday()).label,
                "duration_minutes": duration,
            })
            if len(suggestions) >= limit:
                break
        if len(suggestions) >= limit:
            break

    return {
        "suggestions": suggestions,
        "students_without_availability": students_without_availability(students),
    }
