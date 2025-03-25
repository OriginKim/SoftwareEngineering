from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import CustomUser, UserProfile
from apps.vocabulary.models import Word
from apps.study.models import StudyProgress
from django.utils import timezone
import random
from datetime import datetime

def home(request):
    """메인 페이지"""
    context = {}
    
    if request.user.is_authenticated:
        # 전체 학습 진도 조회
        study_progress = StudyProgress.objects.filter(
            user=request.user,
            review_count__gt=0
        )
        
        # 오늘의 학습 현황 (한국 시간 기준)
        current_time = timezone.localtime(timezone.now())
        today = current_time.date()
        today_start = timezone.make_aware(datetime.combine(today, datetime.min.time()))
        today_end = timezone.make_aware(datetime.combine(today, datetime.max.time()))
        
        # 한국 시간대로 변환
        today_start = timezone.localtime(today_start)
        today_end = timezone.localtime(today_end)
        
        today_progress = study_progress.filter(
            last_reviewed__range=(today_start, today_end)
        ).count()
        
        # 총 학습한 단어 수
        total_studied_words = study_progress.count()
        
        # 오늘의 단어 (랜덤으로 선택)
        random_word = Word.objects.order_by('?').first()
        
        # 사용자의 일일 목표
        daily_goal = getattr(request.user.profile, 'daily_goal', 20)  # 기본값 20
        
        context.update({
            'today_progress': today_progress,
            'daily_goal': daily_goal,
            'random_word': random_word,
            'total_studied_words': total_studied_words,
            'user_profile': request.user.profile
        })
    
    return render(request, 'accounts/home.html', context)

def signup_view(request):
    """회원가입 뷰"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        nickname = request.POST.get('nickname')
        account_type = request.POST.get('account_type')
        agree = request.POST.get('agree')

        # 유효성 검사
        if not all([username, email, password1, password2, account_type, agree]):
            messages.error(request, '모든 필수 항목을 입력해주세요.')
            return redirect('accounts:signup')

        if password1 != password2:
            messages.error(request, '비밀번호가 일치하지 않습니다.')
            return redirect('accounts:signup')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, '이미 사용 중인 아이디입니다.')
            return redirect('accounts:signup')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, '이미 사용 중인 이메일입니다.')
            return redirect('accounts:signup')

        # 사용자 생성
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        # 계정 유형 설정
        user.is_student = (account_type == 'student')
        user.is_teacher = (account_type == 'teacher')
        user.save()

        # 프로필 업데이트
        if nickname:
            user.profile.nickname = nickname
            user.profile.save()

        login(request, user)
        messages.success(request, '회원가입이 완료되었습니다.')
        return redirect('accounts:home')

    return render(request, 'accounts/signup.html')

def login_view(request):
    """로그인 뷰"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, '로그인되었습니다.')
            return redirect('accounts:home')
        else:
            messages.error(request, '아이디 또는 비밀번호가 올바르지 않습니다.')
            return redirect('accounts:login')

    return render(request, 'accounts/login.html')

@login_required
def logout_view(request):
    """로그아웃 뷰"""
    logout(request)
    messages.success(request, '로그아웃되었습니다.')
    return redirect('accounts:home')

@login_required
def profile_view(request):
    """프로필 뷰"""
    if request.method == 'POST':
        # 프로필 설정 업데이트
        daily_goal = request.POST.get('daily_goal')
        nickname = request.POST.get('nickname')
        bio = request.POST.get('bio')

        profile = request.user.profile
        if daily_goal:
            profile.daily_goal = int(daily_goal)
        profile.nickname = nickname
        profile.bio = bio
        profile.save()

        messages.success(request, '프로필이 업데이트되었습니다.')
        return redirect('accounts:profile')

    return render(request, 'accounts/profile.html')
