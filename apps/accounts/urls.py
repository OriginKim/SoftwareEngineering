from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.home, name='home'),  # 메인 페이지
    path('login/', views.login_view, name='login'),  # 로그인
    path('logout/', views.logout_view, name='logout'),  # 로그아웃
    path('signup/', views.signup_view, name='signup'),  # 회원가입
    path('profile/', views.profile_view, name='profile'),  # 프로필
] 