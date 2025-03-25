from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

class CustomUser(AbstractUser):
    """커스텀 사용자 모델"""
    is_student = models.BooleanField('학생 여부', default=True)
    is_teacher = models.BooleanField('교사 여부', default=False)
    email = models.EmailField('이메일', unique=True)
    
    class Meta:
        verbose_name = '사용자'
        verbose_name_plural = '사용자 목록'

    def __str__(self):
        return self.username

class UserProfile(models.Model):
    """사용자 프로필 모델"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='profile'
    )
    nickname = models.CharField('닉네임', max_length=50, blank=True)
    bio = models.TextField('자기소개', blank=True)
    daily_goal = models.IntegerField('일일 학습 목표 단어 수', default=20)
    level = models.IntegerField('레벨', default=1)
    experience = models.IntegerField('경험치', default=0)
    total_studied_words = models.IntegerField('총 학습 단어 수', default=0)
    created_at = models.DateTimeField('가입일', auto_now_add=True)
    last_login_at = models.DateTimeField('최근 로그인', auto_now=True)

    class Meta:
        verbose_name = '사용자 프로필'
        verbose_name_plural = '사용자 프로필 목록'

    def __str__(self):
        return f"{self.user.username}의 프로필"

    def level_up(self):
        """경험치에 따른 레벨 업 처리"""
        required_exp = self.level * 100  # 레벨당 필요 경험치
        if self.experience >= required_exp:
            self.level += 1
            self.experience -= required_exp
            self.save()

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """새로운 사용자가 생성되면 프로필도 자동으로 생성"""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    """사용자가 수정되면 프로필도 저장"""
    instance.profile.save()
