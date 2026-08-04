# matching/admin.py
from django.contrib import admin
from .models import Match, MatchParticipant, GroupStudySession, Feedback


class MatchParticipantInline(admin.TabularInline):
    model = MatchParticipant
    extra = 0


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ["id", "relevance_score", "created_at"]
    inlines = [MatchParticipantInline]


@admin.register(GroupStudySession)
class GroupStudySessionAdmin(admin.ModelAdmin):
    list_display = ["id", "match", "scheduled_time", "status"]
    list_filter = ["status"]


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ["id", "student", "session", "rating", "submitted_at"]
    list_filter = ["rating"]
