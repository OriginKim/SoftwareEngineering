from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile

class CustomUserAdmin(UserAdmin):
    """커스텀 사용자 관리자 설정"""
    list_display = ('username', 'email', 'is_student', 'is_teacher', 'is_staff')
    list_filter = ('is_student', 'is_teacher', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    ordering = ('username',)

class UserProfileAdmin(admin.ModelAdmin):
    """사용자 프로필 관리자 설정"""
    list_display = ('user', 'nickname', 'daily_goal', 'streak_days', 'total_studied_words')
    list_filter = ('daily_goal',)
    search_fields = ('user__username', 'nickname')
    readonly_fields = ('created_at',)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
