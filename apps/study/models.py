from django.db import models
from django.conf import settings
from apps.vocabulary.models import Word
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta

User = get_user_model()

class StudyPlan(models.Model):
    """학습 계획 모델"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='study_plans'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)  # 설명 필드 추가
    target_words_per_day = models.IntegerField(default=10)
    target_study_time = models.IntegerField(default=30)  # 분 단위
    difficulty = models.CharField(
        max_length=10,
        choices=[
            ('easy', '초급'),
            ('medium', '중급'),
            ('hard', '고급')
        ],
        default='easy'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    STUDY_TYPE_CHOICES = [
        ('flashcard', '플래시카드'),
        ('word_list', '단어장'),
        ('review', '복습')
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='study_sessions'
    )
    study_plan = models.ForeignKey(
        StudyPlan,
        on_delete=models.CASCADE,
        related_name='sessions',
        null=True
    )
    study_type = models.CharField(
        max_length=20,
        choices=STUDY_TYPE_CHOICES,
        default='flashcard'
    )
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    study_minutes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'start_time']

    def __str__(self):
        return f"{self.user.username}의 학습 세션 ({self.start_time})"

    @property
    def date(self):
        return self.start_time.date()

class StudyProgress(models.Model):
    """학습 진도 모델"""
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
        'StudySession',
        on_delete=models.SET_NULL,
        related_name='progress',
        null=True,
        blank=True
    )
    proficiency = models.IntegerField(default=1)  # 1-5 척도
    review_count = models.IntegerField(default=0)
    last_reviewed = models.DateTimeField(default=timezone.now)
    next_review_date = models.DateField(null=True, blank=True)
    is_bookmarked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'word']

    def __str__(self):
        return f"{self.user.username}의 {self.word.english} 학습 진도"

class ReviewSchedule(models.Model):
    """복습 일정 모델"""
    STATUS_CHOICES = [
        ('pending', '대기'),
        ('completed', '완료'),
        ('skipped', '건너뜀')
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
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['scheduled_date']

    def __str__(self):
        return f"{self.user.username}의 {self.word.english} 복습 일정"

class Notification(models.Model):
    """알림 모델"""
    TYPE_CHOICES = [
        ('review', '복습'),
        ('achievement', '성취'),
        ('reminder', '리마인더')
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}의 알림: {self.title}"

class UserNotificationSettings(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='notification_settings'
    )
    review_notifications = models.BooleanField(default=True)
    achievement_notifications = models.BooleanField(default=True)
    reminder_notifications = models.BooleanField(default=True)
    notification_time = models.TimeField(default=datetime.strptime('09:00', '%H:%M').time())
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='word_study_histories')
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '단어 학습 이력'
        verbose_name_plural = '단어 학습 이력'

    def __str__(self):
        return f"{self.user.username}의 {self.word.english} 학습 기록"

class LevelTest(models.Model):
    """레벨 테스트 모델"""
    DIFFICULTY_CHOICES = [
        ('beginner', '초급'),
        ('intermediate', '중급'),
        ('advanced', '고급')
    ]

    title = models.CharField(max_length=100)
    description = models.TextField()
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.get_difficulty_display()})"

class TestQuestion(models.Model):
    """테스트 문제 모델"""
    QUESTION_TYPES = [
        ('multiple_choice', '객관식'),
        ('word_meaning', '단어 의미'),
        ('sentence_completion', '문장 완성'),
        ('context_usage', '문맥 속 사용')
    ]

    test = models.ForeignKey(LevelTest, on_delete=models.CASCADE, related_name='questions')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='test_questions')
    question_text = models.TextField()
    correct_answer = models.CharField(max_length=200)
    options = models.JSONField(help_text='객관식 문제의 보기')
    explanation = models.TextField(blank=True)
    points = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.test.title} - {self.question_text[:30]}"

class UserTestResult(models.Model):
    """사용자 테스트 결과 모델"""
    LEVEL_CHOICES = [
        (1, 'Level 1 - 기초'),
        (2, 'Level 2 - 초급'),
        (3, 'Level 3 - 중급'),
        (4, 'Level 4 - 중상급'),
        (5, 'Level 5 - 고급')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    test = models.ForeignKey(LevelTest, on_delete=models.CASCADE)
    score = models.IntegerField()
    level = models.IntegerField(choices=LEVEL_CHOICES)
    completed_at = models.DateTimeField(auto_now_add=True)
    answers = models.JSONField(help_text='사용자의 답변 기록')
    
    class Meta:
        ordering = ['-completed_at']

    def __str__(self):
        return f"{self.user.username}의 테스트 결과 - Level {self.level}"

class UserLevel(models.Model):
    """사용자 현재 레벨 모델"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    current_level = models.IntegerField(choices=UserTestResult.LEVEL_CHOICES)
    last_test_date = models.DateTimeField(auto_now=True)
    recommended_words_per_day = models.IntegerField(default=20)
    
    def __str__(self):
        return f"{self.user.username}의 현재 레벨 - Level {self.current_level}"

class DailyGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_goals')
    date = models.DateField(default=timezone.now)
    words = models.IntegerField(default=20)  # 일일 목표 단어 수
    study_time = models.IntegerField(default=5)  # 일일 목표 학습 시간(분)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username}의 {self.date} 일일 목표"

class StudyNotification(models.Model):
    NOTIFICATION_TYPES = (
        ('review', '복습 알림'),
        ('forgotten', '자주 틀리는 단어'),
        ('achievement', '업적 달성'),
        ('reminder', '학습 리마인더'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_notifications')
    word = models.ForeignKey(Word, on_delete=models.CASCADE, null=True, blank=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}의 {self.notification_type} 알림"
