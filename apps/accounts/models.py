from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class CustomUser(AbstractUser):
    """사용자 모델"""
    email = models.EmailField('이메일 주소', unique=True)
    nickname = models.CharField(max_length=50, blank=True)
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    last_login_attempt = models.DateTimeField(null=True, blank=True)
    lockout_until = models.DateTimeField(null=True, blank=True)
    login_attempts = models.IntegerField(default=0)
    level_test_completed = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    def __str__(self):
        return self.email

    class Meta:
        verbose_name = '사용자'
        verbose_name_plural = '사용자'

class UserProfile(models.Model):
    """사용자 프로필 모델"""
    LEVEL_CHOICES = [
        (1, '초보자'),
        (2, '학습자'),
        (3, '중급자'),
        (4, '상급자'),
        (5, '전문가')
    ]
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    nickname = models.CharField('닉네임', max_length=50, blank=True)
    bio = models.TextField('자기소개', blank=True)
    daily_goal = models.IntegerField('일일 목표', default=10)
    dark_mode = models.BooleanField('다크모드', default=False)
    created_at = models.DateTimeField('가입일', auto_now_add=True)
    last_study_date = models.DateField('마지막 학습일', null=True, blank=True)
    streak_days = models.IntegerField('연속 학습일', default=0)
    total_studied_words = models.IntegerField('총 학습 단어 수', default=0)
    experience = models.IntegerField('경험치', default=0)
    level = models.IntegerField('레벨', choices=LEVEL_CHOICES, default=1)

    class Meta:
        verbose_name = '프로필'
        verbose_name_plural = '프로필'

    def __str__(self):
        return f"{self.user.username}의 프로필"
        
    def get_required_exp(self):
        """다음 레벨까지 필요한 경험치를 반환"""
        # 레벨별 필요 경험치 계산 (레벨이 올라갈수록 더 많은 경험치 필요)
        return self.level * 100
        
    def get_level_display(self):
        """현재 레벨의 한글 표시를 반환"""
        return dict(self.LEVEL_CHOICES)[self.level]
        
    def add_experience(self, amount):
        """경험치를 추가하고 레벨업 체크"""
        self.experience += amount
        self.check_level_up()
        self.save()
        
    def check_level_up(self):
        """경험치가 충분하면 레벨업"""
        required_exp = self.get_required_exp()
        if self.experience >= required_exp and self.level < 5:
            self.level += 1
            self.experience -= required_exp
            return True
        return False

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """새로운 사용자가 생성되면 프로필도 자동으로 생성"""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    """사용자가 수정되면 프로필도 저장"""
    instance.profile.save()

class Attendance(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='attendances')
    check_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    streak_days = models.IntegerField(default=1)

    class Meta:
        unique_together = ['user', 'check_date']
        ordering = ['-check_date']

    def __str__(self):
        return f"{self.user.username} - {self.check_date}"

    def save(self, *args, **kwargs):
        logger.debug("====== 출석 기록 저장 시작 ======")
        logger.debug(f"사용자: {self.user.username}, 날짜: {self.check_date}")
        
        if not self.pk:  # 새로운 출석 기록인 경우
            logger.debug("새로운 출석 기록 생성")
            # 어제 날짜의 출석 기록 확인
            yesterday = self.check_date - timezone.timedelta(days=1)
            try:
                yesterday_attendance = Attendance.objects.get(
                    user=self.user,
                    check_date=yesterday
                )
                self.streak_days = yesterday_attendance.streak_days + 1
                logger.debug(f"어제 출석 있음. 연속 출석 {yesterday_attendance.streak_days} -> {self.streak_days}")
            except Attendance.DoesNotExist:
                self.streak_days = 1
                logger.debug("어제 출석 없음. 연속 출석 1일로 시작")
        else:
            logger.debug(f"기존 출석 기록 업데이트. 현재 연속 출석: {self.streak_days}")
        
        logger.debug("====== 출석 기록 저장 종료 ======")
        super().save(*args, **kwargs)
