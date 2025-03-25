from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile

class CustomUserAdmin(UserAdmin):
    """커스텀 사용자 관리자 설정"""
    list_display = ('username', 'email', 'is_student', 'is_staff', 'is_active')
    list_filter = ('is_student', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('추가 정보', {'fields': ('is_student',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('추가 정보', {'fields': ('is_student', 'email')}),
    )

class UserProfileAdmin(admin.ModelAdmin):
    """사용자 프로필 관리자 설정"""
    list_display = ('user', 'nickname', 'level', 'total_studied_words', 'created_at')
    list_filter = ('level', 'created_at')
    search_fields = ('user__username', 'nickname')
    readonly_fields = ('created_at', 'last_login_at')

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
