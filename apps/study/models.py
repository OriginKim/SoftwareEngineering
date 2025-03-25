from django.db import models
from django.conf import settings
from apps.vocabulary.models import Word
from django.contrib.auth import get_user_model
from django.utils import timezone

class StudyPlan(models.Model):
    """학습 계획 모델"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='study_plans'
    )
    title = models.CharField(max_length=100)
    target_words_per_day = models.PositiveIntegerField(default=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}의 학습 계획: {self.title}"

    def get_studied_words_count(self):
        """이 계획에서 학습한 단어 수를 반환"""
        return StudyProgress.objects.filter(
            study_session__study_plan=self
        ).values('word').distinct().count()
        
    def get_remaining_words_count(self):
        """이 계획에서 남은 단어 수를 반환"""
        total_words = Word.objects.count()
        studied_words = self.get_studied_words_count()
        return total_words - studied_words
        
    def get_progress_percentage(self):
        """학습 진행률을 백분율로 반환"""
        total_words = Word.objects.count()
        if total_words == 0:
            return 0
        studied_words = self.get_studied_words_count()
        return round((studied_words / total_words) * 100, 1)
        
    def get_average_proficiency(self):
        """평균 숙련도를 반환"""
        avg = StudyProgress.objects.filter(
            study_session__study_plan=self
        ).aggregate(avg=models.Avg('proficiency'))['avg']
        return avg if avg is not None else 0.0

class StudySession(models.Model):
    """학습 세션 모델"""
    STUDY_TYPES = [
        ('flashcard', '플래시카드'),
        ('word_list', '단어장'),
        ('review', '복습'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='study_sessions'
    )
    study_plan = models.ForeignKey(
        StudyPlan,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    study_type = models.CharField(
        max_length=20,
        choices=STUDY_TYPES
    )
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    words_studied = models.ManyToManyField(
        Word,
        through='StudyProgress',
        related_name='study_sessions'
    )

    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.user.username}의 {self.get_study_type_display()} 학습"
        
    def get_duration(self):
        """학습 시간을 반환"""
        if not self.end_time:
            return timezone.now() - self.start_time
        return self.end_time - self.start_time
        
    def get_duration_display(self):
        """학습 시간을 사람이 읽기 쉬운 형태로 반환"""
        duration = self.get_duration()
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        
        if hours > 0:
            return f"{hours}시간 {minutes}분"
        return f"{minutes}분"
        
    def get_studied_words_count(self):
        """이 세션에서 학습한 단어 수를 반환"""
        return self.progress.count()
        
    def get_average_proficiency(self):
        """이 세션의 평균 숙련도를 반환"""
        avg = self.progress.aggregate(avg=models.Avg('proficiency'))['avg']
        return avg if avg is not None else 0.0
        
    def end_session(self):
        """세션을 종료"""
        if not self.end_time:
            self.end_time = timezone.now()
            self.save()

class StudyProgress(models.Model):
    """학습 진도 모델"""
    PROFICIENCY_LEVELS = [
        (1, '처음 봤어요'),
        (2, '어려워요'),
        (3, '복습이 필요해요'),
        (4, '알 것 같아요'),
        (5, '완전히 알아요'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='study_progress'
    )
    word = models.ForeignKey(
        Word,
        on_delete=models.CASCADE,
        related_name='study_progress'
    )
    study_session = models.ForeignKey(
        StudySession,
        on_delete=models.CASCADE,
        related_name='progress',
        null=True,
        blank=True
    )
    proficiency = models.IntegerField(
        choices=PROFICIENCY_LEVELS,
        default=1
    )
    is_bookmarked = models.BooleanField(default=False)
    last_reviewed = models.DateTimeField(auto_now=True)
    next_review_date = models.DateField(null=True, blank=True)
    review_count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ['user', 'word']
        ordering = ['-last_reviewed']

    def __str__(self):
        return f"{self.user.username}의 {self.word.english} 학습 진도"

class ReviewSchedule(models.Model):
    """복습 일정 모델"""
    REVIEW_STATUS = [
        ('pending', '대기중'),
        ('completed', '완료'),
        ('missed', '놓침'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='review_schedules'
    )
    word = models.ForeignKey(
        Word,
        on_delete=models.CASCADE,
        related_name='review_schedules'
    )
    scheduled_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=REVIEW_STATUS,
        default='pending'
    )
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['scheduled_date']

    def __str__(self):
        return f"{self.user.username}의 {self.word.english} 복습 일정 ({self.scheduled_date})"

class Notification(models.Model):
    """알림 모델"""
    NOTIFICATION_TYPES = [
        ('review', '복습 알림'),
        ('achievement', '목표 달성'),
        ('reminder', '학습 독려'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=200, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}의 {self.get_type_display()} - {self.title}"

    @classmethod
    def create_review_notification(cls, user, word_count):
        """복습 알림 생성"""
        return cls.objects.create(
            user=user,
            type='review',
            title='복습할 단어가 있습니다',
            message=f'오늘 복습해야 할 {word_count}개의 단어가 있습니다.',
            link='/study/review/'
        )

    @classmethod
    def create_achievement_notification(cls, user, achievement):
        """목표 달성 알림 생성"""
        return cls.objects.create(
            user=user,
            type='achievement',
            title='목표를 달성했습니다! 🎉',
            message=f'축하합니다! {achievement}을(를) 달성했습니다.',
            link='/study/statistics/'
        )

    @classmethod
    def create_reminder_notification(cls, user, days):
        """학습 독려 알림 생성"""
        return cls.objects.create(
            user=user,
            type='reminder',
            title='학습을 이어가보세요',
            message=f'마지막 학습 후 {days}일이 지났습니다. 오늘도 학습을 이어가보세요!',
            link='/study/plans/'
        )

class UserNotificationSettings(models.Model):
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='notification_settings'
    )
    review_notifications = models.BooleanField(default=True, verbose_name='복습 알림')
    achievement_notifications = models.BooleanField(default=True, verbose_name='성취 알림')
    reminder_notifications = models.BooleanField(default=True, verbose_name='학습 독려 알림')
    notification_time = models.TimeField(default=timezone.now, verbose_name='알림 시간')
    
    class Meta:
        verbose_name = '알림 설정'
        verbose_name_plural = '알림 설정'

    def __str__(self):
        return f"{self.user.username}의 알림 설정"

    @classmethod
    def get_or_create_settings(cls, user):
        settings, created = cls.objects.get_or_create(user=user)
        return settings

class WordStudyHistory(models.Model):
    """단어 학습 이력을 저장하는 모델"""
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='word_study_histories')
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '단어 학습 이력'
        verbose_name_plural = '단어 학습 이력'

    def __str__(self):
        return f"{self.user.username}의 {self.word.english} 학습 기록"
