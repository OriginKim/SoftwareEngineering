from django.urls import path
from . import views

app_name = 'study'

urlpatterns = [
    # 학습 계획 관련 URL
    path('plans/', views.study_plan_list, name='plan_list'),
    path('plans/create/', views.study_plan_create, name='plan_create'),
    path('plans/<int:plan_id>/', views.study_plan_detail, name='plan_detail'),
    path('plans/<int:plan_id>/edit/', views.study_plan_edit, name='plan_edit'),
    path('plans/<int:plan_id>/delete/', views.study_plan_delete, name='plan_delete'),

    # 학습 세션 관련 URL
    path('session/start/', views.study_session_start, name='session_start'),
    path('session/<int:session_id>/', views.study_session_detail, name='session_detail'),
    path('session/<int:session_id>/end/', views.study_session_end, name='session_end'),

    # 학습 모드 관련 URL
    path('flashcard/', views.flashcard_study, name='flashcard'),
    path('wordlist/', views.word_list_study, name='wordlist'),
    path('review/', views.review_list, name='review'),
    path('review/start/<int:word_id>/', views.review_start, name='review_start'),
    path('daily-words/', views.daily_words, name='daily_words'),
    path('wrong-notes/', views.wrong_notes, name='wrong_notes'),

    # 학습 진도 관련 URL
    path('progress/', views.study_progress, name='progress'),
    path('progress/word/<int:word_id>/', views.word_progress_update, name='word_progress_update'),
    path('bookmarks/', views.bookmark_list, name='bookmarks'),
    path('bookmark/toggle/<int:word_id>/', views.bookmark_toggle, name='bookmark_toggle'),

    # 복습 일정 관련 URL
    path('schedule/', views.review_schedule_list, name='schedule_list'),
    path('schedule/update/<int:schedule_id>/', views.review_schedule_update, name='schedule_update'),

    # 알림 관련 URL
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<int:notification_id>/mark-read/', views.notification_mark_read, name='notification_mark_read'),
    path('notifications/mark-all-read/', views.notification_mark_all_read, name='notification_mark_all_read'),
    path('notifications/<int:notification_id>/delete/', views.notification_delete, name='notification_delete'),
    path('notifications/delete-all/', views.notification_delete_all, name='notification_delete_all'),
    path('notifications/settings/', views.notification_settings, name='notification_settings'),

    # 통계 관련 URL
    path('statistics/', views.statistics, name='statistics'),

    # 학습 모드 URL
    path('plans/<int:plan_id>/flashcard/', views.flashcard_study, name='flashcard_study'),
    path('plans/<int:plan_id>/vocabulary/', views.vocabulary_study, name='vocabulary_study'),
    path('plans/<int:plan_id>/review/', views.review_study, name='review_study'),

    path('', views.study_home, name='study_home'),
] 