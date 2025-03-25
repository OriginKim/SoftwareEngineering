from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    # 퀴즈 홈
    path('', views.quiz_home, name='quiz_home'),
    
    # 일반 단어 테스트
    path('word-test/', views.word_test, name='word_test'),
    
    # 사용자 생성 퀴즈
    path('list/', views.quiz_list, name='quiz_list'),
    path('create/', views.quiz_create, name='quiz_create'),
    path('<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('<int:quiz_id>/delete/', views.quiz_delete, name='quiz_delete'),
    path('<int:quiz_id>/start/', views.quiz_start, name='quiz_start'),
    path('<int:quiz_id>/submit/', views.quiz_submit, name='quiz_submit'),
    
    # 퀴즈 응시 기록
    path('history/<int:attempt_id>/', views.quiz_history_detail, name='quiz_history_detail'),
] 