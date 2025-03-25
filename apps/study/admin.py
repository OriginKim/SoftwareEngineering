from django.contrib import admin
from .models import StudyPlan, StudySession, StudyProgress, ReviewSchedule

@admin.register(StudyPlan)
class StudyPlanAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'target_words_per_day', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__username', 'title')
    ordering = ('-created_at',)

@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'study_plan', 'study_type', 'start_time', 'end_time', 'duration')
    list_filter = ('study_type', 'start_time')
    search_fields = ('user__username',)
    ordering = ('-start_time',)

@admin.register(StudyProgress)
class StudyProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'word', 'proficiency', 'is_bookmarked', 'last_reviewed', 'review_count')
    list_filter = ('proficiency', 'is_bookmarked', 'last_reviewed')
    search_fields = ('user__username', 'word__english', 'word__korean')
    ordering = ('-last_reviewed',)

@admin.register(ReviewSchedule)
class ReviewScheduleAdmin(admin.ModelAdmin):
    list_display = ('user', 'word', 'scheduled_date', 'status', 'completed_at')
    list_filter = ('status', 'scheduled_date')
    search_fields = ('user__username', 'word__english', 'word__korean')
    ordering = ('scheduled_date',)
