from django.urls import path
from . import views

app_name = 'vocabulary'

urlpatterns = [
    path('words/', views.word_list, name='word_list'),  # 단어 목록
    path('words/add/', views.word_add, name='word_add'),
    path('words/<int:word_id>/edit/', views.word_edit, name='word_edit'),
    path('words/<int:word_id>/delete/', views.word_delete, name='word_delete'),
    path('<int:word_id>/', views.word_detail, name='word_detail'),  # 단어 상세
    path('<int:word_id>/bookmark/', views.toggle_bookmark, name='toggle_bookmark'),
    path('bookmarks/', views.bookmark_list, name='bookmark_list'),  # 북마크 목록
] 