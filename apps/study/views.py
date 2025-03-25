from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.utils.dateparse import parse_time
from django.db.models.functions import TruncDate
from .models import StudyPlan, StudySession, StudyProgress, ReviewSchedule, Notification, UserNotificationSettings, WordStudyHistory
from apps.vocabulary.models import Word
from apps.quiz.models import QuizAnswerHistory
from datetime import datetime, timedelta
from django.db.models import Sum, Count, Avg, Q, Max
import json
from .utils import (
    check_and_create_review_notification,
    check_and_create_achievement_notifications,
    check_and_create_reminder_notification
)
import random
from django.urls import reverse
from django.http import JsonResponse
from django.db import models
from django.core.paginator import Paginator

# Create your views here.

@login_required
def study_home(request):
    """학습 관리 홈"""
    return render(request, 'study/home.html', {
        'user': request.user
    })

@login_required
def wrong_notes(request):
    """오답 노트 뷰"""
    # 사용자의 오답 기록을 가져옵니다
    wrong_answers = WordStudyHistory.objects.filter(
        user=request.user,
        is_correct=False
    ).select_related('word').annotate(
        wrong_count=Count('id'),
        last_attempt=Max('created_at')
    ).values(
        'word__english',
        'word__korean',
        'wrong_count',
        'last_attempt'
    ).order_by('-wrong_count', '-last_attempt')

    wrong_answers_list = list(wrong_answers)
    
    context = {
        'wrong_answers': wrong_answers_list,
        'has_wrong_answers': bool(wrong_answers_list),
        'wrong_answers_count': len(wrong_answers_list)
    }
    
    # 테스트 템플릿 사용 (정상 작동하는 버전)
    template_name = 'study/wrong_notes_test.html'
    return render(request, template_name, context)

@login_required
def statistics(request):
    """학습 통계 대시보드 뷰"""
    # 전체 학습 현황 데이터 (실제로 학습한 단어만 포함)
    total_words_studied = StudyProgress.objects.filter(
        user=request.user,
        review_count__gt=0
    ).count()
    
    mastered_words = StudyProgress.objects.filter(
        user=request.user,
        proficiency=5,
        review_count__gt=0
    ).count()
    
    needs_review = StudyProgress.objects.filter(
        user=request.user,
        proficiency__lt=4,
        review_count__gt=0
    ).count()
    
    # 총 학습 시간 계산
    total_duration = StudySession.objects.filter(
        user=request.user,
        end_time__isnull=False
    ).aggregate(
        total=Sum('duration')
    )['total'] or timedelta()
    total_study_hours = round(total_duration.total_seconds() / 3600, 1)

    # 주간 학습 현황 데이터
    today = timezone.now().date()
    week_ago = today - timedelta(days=6)
    daily_words = StudyProgress.objects.filter(
        user=request.user,
        last_reviewed__date__gte=week_ago,
        review_count__gt=0  # 실제로 학습한 단어만 포함
    ).annotate(
        review_date=TruncDate('last_reviewed')
    ).values('review_date').annotate(
        count=Count('id')
    ).order_by('review_date')

    # 날짜별 학습 단어 수를 딕셔너리로 변환
    daily_stats = {
        item['review_date']: item['count']
        for item in daily_words
    }

    # 최근 7일 데이터 준비 (없는 날짜는 0으로)
    dates = []
    counts = []
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        dates.append(date.strftime('%Y-%m-%d'))
        counts.append(daily_stats.get(date, 0))

    return render(request, 'study/statistics.html', {
        'total_words_studied': total_words_studied,
        'mastered_words': mastered_words,
        'needs_review': needs_review,
        'total_study_hours': total_study_hours,
        'dates': json.dumps(dates),
        'counts': json.dumps(counts)
    })

@login_required
def daily_words(request):
    """오늘의 단어 목록을 보여줍니다."""
    # 실제로 학습한 단어들만 제외 (review_count > 0)
    learned_words = StudyProgress.objects.filter(
        user=request.user,
        review_count__gt=0
    ).values_list('word_id', flat=True)
    print(f"[DEBUG] Learned words: {list(learned_words)}")
    
    daily_words = Word.objects.exclude(id__in=learned_words).order_by('?')[:10]
    print(f"[DEBUG] Daily words: {[word.english for word in daily_words]}")
    
    return render(request, 'study/daily_words.html', {
        'daily_words': daily_words
    })

@login_required
def review_list(request):
    """복습 목록"""
    # 복습이 필요한 단어들을 가져옵니다
    review_schedules = ReviewSchedule.objects.filter(
        user=request.user,
        scheduled_date__lte=timezone.now(),
        status='pending'
    ).select_related('word').order_by('scheduled_date')

    return render(request, 'study/review_list.html', {
        'review_schedules': review_schedules
    })

# 학습 계획 관련 뷰
@login_required
def study_plan_list(request):
    plans = StudyPlan.objects.filter(user=request.user)
    return render(request, 'study/plan_list.html', {'plans': plans})

@login_required
def study_plan_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        target_words = request.POST.get('target_words_per_day')
        plan = StudyPlan.objects.create(
            user=request.user,
            title=title,
            target_words_per_day=target_words
        )
        messages.success(request, '학습 계획이 생성되었습니다.')
        return redirect('study:plan_detail', plan_id=plan.id)
    return render(request, 'study/plan_create.html')

@login_required
def study_plan_detail(request, plan_id):
    plan = get_object_or_404(StudyPlan, id=plan_id, user=request.user)
    sessions = plan.sessions.all()
    return render(request, 'study/plan_detail.html', {
        'plan': plan,
        'sessions': sessions
    })

@login_required
def study_plan_edit(request, plan_id):
    plan = get_object_or_404(StudyPlan, id=plan_id, user=request.user)
    if request.method == 'POST':
        plan.title = request.POST.get('title')
        plan.target_words_per_day = request.POST.get('target_words_per_day')
        plan.save()
        messages.success(request, '학습 계획이 수정되었습니다.')
        return redirect('study:plan_detail', plan_id=plan.id)
    return render(request, 'study/plan_edit.html', {'plan': plan})

@login_required
def study_plan_delete(request, plan_id):
    plan = get_object_or_404(StudyPlan, id=plan_id, user=request.user)
    if request.method == 'POST':
        plan.delete()
        messages.success(request, '학습 계획이 삭제되었습니다.')
        return redirect('study:plan_list')
    return render(request, 'study/plan_delete.html', {'plan': plan})

# 학습 세션 관련 뷰
@login_required
def study_session_start(request):
    if request.method == 'POST':
        plan_id = request.POST.get('plan_id')
        study_type = request.POST.get('study_type')
        plan = get_object_or_404(StudyPlan, id=plan_id, user=request.user)
        
        session = StudySession.objects.create(
            user=request.user,
            study_plan=plan,
            study_type=study_type
        )
        return redirect('study:session_detail', session_id=session.id)
    plans = StudyPlan.objects.filter(user=request.user, is_active=True)
    return render(request, 'study/session_start.html', {'plans': plans})

@login_required
def study_session_detail(request, session_id):
    session = get_object_or_404(StudySession, id=session_id, user=request.user)
    progress = session.progress.all()
    return render(request, 'study/session_detail.html', {
        'session': session,
        'progress': progress
    })

@login_required
def study_session_end(request, session_id):
    """학습 세션 종료"""
    session = get_object_or_404(StudySession, id=session_id, user=request.user)
    if request.method == 'POST':
        session.end_time = timezone.now()
        session.duration = session.end_time - session.start_time
        session.save()

        # 학습 세션 종료 시 알림 체크
        check_and_create_achievement_notifications(request.user)
        check_and_create_review_notification(request.user)

        messages.success(request, '학습 세션이 종료되었습니다.')
        return redirect('study:session_detail', session_id=session.id)
    return render(request, 'study/session_end.html', {'session': session})

# 학습 모드 관련 뷰
@login_required
def flashcard_study(request, plan_id):
    plan = get_object_or_404(StudyPlan, id=plan_id, user=request.user)
    return render(request, 'study/flashcard.html', {'plan': plan})

@login_required
def vocabulary_study(request, plan_id):
    plan = get_object_or_404(StudyPlan, id=plan_id, user=request.user)
    return render(request, 'study/vocabulary.html', {'plan': plan})

@login_required
def review_study(request, plan_id):
    plan = get_object_or_404(StudyPlan, id=plan_id, user=request.user)
    return render(request, 'study/review.html', {'plan': plan})

@login_required
def word_list_study(request):
    # 사용자의 모든 학습 단어를 가져옴
    progress = StudyProgress.objects.filter(
        user=request.user
    ).select_related('word')
    return render(request, 'study/word_list.html', {'progress': progress})

# 학습 진도 관련 뷰
@login_required
def study_progress(request):
    progress = StudyProgress.objects.filter(
        user=request.user
    ).select_related('word')
    return render(request, 'study/progress.html', {'progress': progress})

@login_required
def word_progress_update(request, word_id):
    """단어 학습 진도 업데이트"""
    if request.method == 'POST':
        print("\n=== 단어 학습 진도 업데이트 시작 ===")
        print(f"[DEBUG] 요청된 단어 ID: {word_id}")
        print(f"[DEBUG] POST 데이터: {request.POST}")
        
        word = get_object_or_404(Word, id=word_id)
        proficiency = request.POST.get('proficiency', '1')
        print(f"[DEBUG] 단어 정보: {word.english} (ID: {word.id})")
        print(f"[DEBUG] 숙련도: {proficiency}")
        
        # 현재 시간을 한국 시간대로 가져옴
        current_time = timezone.localtime(timezone.now())
        print(f"[DEBUG] 현재 시간 (한국): {current_time}")
        
        # 기본 학습 계획 가져오기 또는 생성
        study_plan, created = StudyPlan.objects.get_or_create(
            user=request.user,
            is_active=True,
            defaults={
                'title': '기본 학습 계획',
                'target_words_per_day': 20
            }
        )
        print(f"[DEBUG] 학습 계획: {study_plan.title} (새로 생성됨: {created})")
        
        # 새로운 학습 세션 생성
        study_session = StudySession.objects.create(
            user=request.user,
            study_type='word_list',
            start_time=current_time,
            end_time=current_time,
            study_plan=study_plan
        )
        print(f"[DEBUG] 학습 세션 생성됨: {study_session.id}")
        
        # StudyProgress 생성 또는 업데이트
        try:
            progress = StudyProgress.objects.get(user=request.user, word=word)
            old_review_count = progress.review_count
            progress.proficiency = proficiency
            progress.review_count += 1
            progress.study_session = study_session
            progress.last_reviewed = current_time
            progress.save()
            print(f"[DEBUG] 기존 진도 업데이트: ID {progress.id}, 복습 횟수 {old_review_count} -> {progress.review_count}")
        except StudyProgress.DoesNotExist:
            progress = StudyProgress.objects.create(
                user=request.user,
                word=word,
                proficiency=proficiency,
                study_session=study_session,
                last_reviewed=current_time,
                review_count=1
            )
            print(f"[DEBUG] 새로운 진도 생성: ID {progress.id}, 복습 횟수 1")
        
        # 다음 복습 일정 설정
        next_review = current_time.date()
        if int(proficiency) < 3:
            next_review += timedelta(days=1)
        elif int(proficiency) == 3:
            next_review += timedelta(days=3)
        elif int(proficiency) == 4:
            next_review += timedelta(days=7)
        else:
            next_review += timedelta(days=14)
        
        progress.next_review_date = next_review
        progress.save()
        print(f"[DEBUG] 다음 복습 일정 설정: {next_review}")
        
        ReviewSchedule.objects.create(
            user=request.user,
            word=word,
            scheduled_date=next_review
        )
        print(f"[DEBUG] 복습 일정 생성됨: {next_review}")
        
        # 오늘의 학습 현황 확인 (한국 시간 기준)
        today = current_time.date()
        today_start = timezone.make_aware(datetime.combine(today, datetime.min.time()))
        today_end = timezone.make_aware(datetime.combine(today, datetime.max.time()))
        
        # 한국 시간대로 변환
        today_start = timezone.localtime(today_start)
        today_end = timezone.localtime(today_end)
        
        today_progress = StudyProgress.objects.filter(
            user=request.user,
            last_reviewed__range=(today_start, today_end),
            review_count__gt=0
        ).count()
        print(f"[DEBUG] 오늘의 학습 현황: {today_progress}개")
        
        # 전체 학습 현황 확인
        total_studied = StudyProgress.objects.filter(
            user=request.user,
            review_count__gt=0
        ).count()
        print(f"[DEBUG] 전체 학습 현황: {total_studied}개")
        print("=== 단어 학습 진도 업데이트 완료 ===\n")
        
        messages.success(request, f"{word.english} 단어를 학습했습니다!")
        return redirect('study:daily_words')
    
    return redirect('study:daily_words')

@login_required
def bookmark_list(request):
    """북마크된 단어 목록을 보여주는 뷰"""
    bookmarks = StudyProgress.objects.filter(
        user=request.user,
        is_bookmarked=True
    ).select_related('word').order_by('-last_reviewed')
    
    # 페이지네이션
    paginator = Paginator(bookmarks, 20)  # 페이지당 20개
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_bookmarks': bookmarks.count(),
    }
    return render(request, 'study/bookmarks.html', context)

@login_required
def bookmark_toggle(request, word_id):
    if request.method == 'POST':
        word = get_object_or_404(Word, id=word_id)
        progress, created = StudyProgress.objects.get_or_create(
            user=request.user,
            word=word
        )
        progress.is_bookmarked = not progress.is_bookmarked
        progress.save()
        
        # AJAX 요청인 경우 JSON 응답
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'is_bookmarked': progress.is_bookmarked,
                'message': '북마크가 추가되었습니다.' if progress.is_bookmarked else '북마크가 제거되었습니다.'
            })
            
        # 일반 요청인 경우 메시지 추가 후 리다이렉트
        messages.success(
            request,
            '북마크가 추가되었습니다.' if progress.is_bookmarked else '북마크가 제거되었습니다.'
        )
        
        # 이전 페이지로 리다이렉트, 없으면 학습 진도 페이지로
        return redirect(request.META.get('HTTP_REFERER', 'study:progress'))
        
    # POST 요청이 아닌 경우 400 에러
    return JsonResponse({'error': '잘못된 요청입니다.'}, status=400)

# 복습 일정 관련 뷰
@login_required
def review_schedule_list(request):
    schedules = ReviewSchedule.objects.filter(
        user=request.user,
        status='pending'
    ).select_related('word')
    return render(request, 'study/schedule_list.html', {'schedules': schedules})

@login_required
def review_schedule_update(request, schedule_id):
    if request.method == 'POST':
        schedule = get_object_or_404(ReviewSchedule, id=schedule_id, user=request.user)
        status = request.POST.get('status')
        schedule.status = status
        if status == 'completed':
            schedule.completed_at = timezone.now()
        schedule.save()
        messages.success(request, '복습 일정이 업데이트되었습니다.')
    return redirect('study:schedule_list')

@login_required
def notification_list(request):
    """알림 목록 보기"""
    notifications = Notification.objects.filter(user=request.user)
    return render(request, 'study/notifications.html', {
        'notifications': notifications
    })

@login_required
def notification_mark_read(request, notification_id):
    """알림을 읽음으로 표시"""
    if request.method == 'POST':
        notification = get_object_or_404(
            Notification,
            id=notification_id,
            user=request.user
        )
        notification.is_read = True
        notification.save()
        messages.success(request, '알림이 읽음으로 표시되었습니다.')
    return redirect('study:notification_list')

@login_required
def notification_mark_all_read(request):
    """모든 알림을 읽음으로 표시"""
    if request.method == 'POST':
        Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True)
        messages.success(request, '모든 알림이 읽음으로 표시되었습니다.')
    return redirect('study:notification_list')

@login_required
def notification_delete(request, notification_id):
    """알림 삭제"""
    if request.method == 'POST':
        notification = get_object_or_404(
            Notification,
            id=notification_id,
            user=request.user
        )
        notification.delete()
        messages.success(request, '알림이 삭제되었습니다.')
    return redirect('study:notification_list')

@login_required
def notification_delete_all(request):
    """모든 알림 삭제"""
    if request.method == 'POST':
        Notification.objects.filter(user=request.user).delete()
        messages.success(request, '모든 알림이 삭제되었습니다.')
    return redirect('study:notification_list')

@login_required
def notification_settings(request):
    """알림 설정 관리"""
    settings = UserNotificationSettings.get_or_create_settings(request.user)
    
    if request.method == 'POST':
        settings.review_notifications = request.POST.get('review_notifications') == 'on'
        settings.achievement_notifications = request.POST.get('achievement_notifications') == 'on'
        settings.reminder_notifications = request.POST.get('reminder_notifications') == 'on'
        
        notification_time = request.POST.get('notification_time')
        if notification_time:
            settings.notification_time = parse_time(notification_time)
        
        settings.save()
        messages.success(request, '알림 설정이 업데이트되었습니다.')
        return redirect('study:notification_settings')
    
    return render(request, 'study/notification_settings.html', {
        'settings': settings
    })

@login_required
def review_start(request, word_id):
    """특정 단어의 복습을 시작합니다."""
    if request.method == 'POST':
        word = get_object_or_404(Word, id=word_id)
        
        # 복습 세션 생성
        session = StudySession.objects.create(
            user=request.user,
            study_type='review',
            start_time=timezone.now()
        )
        
        # 복습할 단어를 세션에 추가
        session.words.add(word)
        
        return JsonResponse({
            'success': True,
            'redirect_url': reverse('study:session_detail', args=[session.id])
        })
    
    return JsonResponse({'success': False}, status=400)
