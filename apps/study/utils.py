from django.utils import timezone
from datetime import timedelta
from .models import StudyProgress, StudySession, ReviewSchedule, Notification

def check_and_create_review_notification(user):
    """복습 알림 체크 및 생성"""
    today = timezone.now().date()
    review_count = ReviewSchedule.objects.filter(
        user=user,
        scheduled_date=today,
        status='pending'
    ).count()

    if review_count > 0:
        # 아직 읽지 않은 오늘의 복습 알림이 있는지 확인
        existing_notification = Notification.objects.filter(
            user=user,
            type='review',
            created_at__date=today,
            is_read=False
        ).exists()

        if not existing_notification:
            Notification.create_review_notification(user, review_count)

def check_and_create_achievement_notifications(user):
    """목표 달성 알림 체크 및 생성"""
    # 학습한 총 단어 수 체크
    total_words = StudyProgress.objects.filter(user=user).count()
    achievement_thresholds = {
        100: '100개 단어 학습',
        500: '500개 단어 학습',
        1000: '1000개 단어 학습',
    }

    for threshold, achievement in achievement_thresholds.items():
        if total_words >= threshold:
            # 해당 목표에 대한 알림이 이미 있는지 확인
            existing_notification = Notification.objects.filter(
                user=user,
                type='achievement',
                message__contains=achievement
            ).exists()

            if not existing_notification:
                Notification.create_achievement_notification(user, achievement)

    # 연속 학습일수 체크
    consecutive_days = get_consecutive_study_days(user)
    if consecutive_days in [7, 30, 100]:
        achievement = f'{consecutive_days}일 연속 학습'
        existing_notification = Notification.objects.filter(
            user=user,
            type='achievement',
            message__contains=achievement
        ).exists()

        if not existing_notification:
            Notification.create_achievement_notification(user, achievement)

def check_and_create_reminder_notification(user):
    """학습 독려 알림 체크 및 생성"""
    last_session = StudySession.objects.filter(
        user=user,
        end_time__isnull=False
    ).order_by('-end_time').first()

    if last_session:
        days_since_last_study = (timezone.now().date() - last_session.end_time.date()).days
        reminder_days = [3, 7, 14]  # 3일, 7일, 14일 동안 학습하지 않았을 때

        if days_since_last_study in reminder_days:
            # 같은 날짜에 대한 알림이 이미 있는지 확인
            existing_notification = Notification.objects.filter(
                user=user,
                type='reminder',
                created_at__date=timezone.now().date()
            ).exists()

            if not existing_notification:
                Notification.create_reminder_notification(user, days_since_last_study)

def get_consecutive_study_days(user):
    """연속 학습일수 계산"""
    today = timezone.now().date()
    consecutive_days = 0
    current_date = today

    while True:
        has_study = StudySession.objects.filter(
            user=user,
            start_time__date=current_date,
            end_time__isnull=False
        ).exists()

        if not has_study:
            break

        consecutive_days += 1
        current_date -= timedelta(days=1)

    return consecutive_days 