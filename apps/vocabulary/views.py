from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Word

def is_teacher(user):
    """교사 권한 체크"""
    return user.is_teacher

# Create your views here.

@login_required
def word_list(request):
    """단어 목록 뷰"""
    # 검색 및 필터링
    query = request.GET.get('q', '')
    difficulty = request.GET.get('difficulty', '')
    
    words = Word.objects.all()
    
    if query:
        words = words.filter(
            Q(english__icontains=query) |
            Q(korean__icontains=query)
        )
    
    if difficulty:
        words = words.filter(difficulty=difficulty)
    
    # 페이지네이션
    paginator = Paginator(words, 20)  # 페이지당 20개
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'difficulty': difficulty,
        'is_teacher': request.user.is_teacher,  # 교사 여부 전달
    }
    return render(request, 'vocabulary/word_list.html', context)

@login_required
def word_detail(request, word_id):
    """단어 상세 뷰"""
    word = get_object_or_404(Word, id=word_id)
    context = {
        'word': word,
    }
    return render(request, 'vocabulary/word_detail.html', context)

@login_required
def toggle_bookmark(request, word_id):
    """북마크 토글 - study 앱의 북마크 기능으로 리다이렉트"""
    return redirect('study:bookmark_toggle', word_id=word_id)

@login_required
def bookmark_list(request):
    """북마크 목록 - study 앱의 북마크 목록으로 리다이렉트"""
    return redirect('study:bookmarks')

@login_required
@user_passes_test(is_teacher)
def word_add(request):
    """단어 추가 (교사 전용)"""
    if request.method == 'POST':
        word = Word.objects.create(
            english=request.POST['english'],
            korean=request.POST['korean'],
            part_of_speech=request.POST['part_of_speech'],
            difficulty=request.POST['difficulty'],
            example_sentence=request.POST['example_sentence'],
            example_translation=request.POST['example_translation']
        )
        messages.success(request, f'단어 "{word.english}"가 추가되었습니다.')
        return redirect('vocabulary:word_list')
    
    return render(request, 'vocabulary/word_add.html')

@login_required
@user_passes_test(is_teacher)
def word_edit(request, word_id):
    """단어 수정 (교사 전용)"""
    word = get_object_or_404(Word, id=word_id)
    
    if request.method == 'POST':
        word.english = request.POST['english']
        word.korean = request.POST['korean']
        word.part_of_speech = request.POST['part_of_speech']
        word.difficulty = request.POST['difficulty']
        word.example_sentence = request.POST['example_sentence']
        word.example_translation = request.POST['example_translation']
        word.save()
        
        messages.success(request, f'단어 "{word.english}"가 수정되었습니다.')
        return redirect('vocabulary:word_list')
    
    return render(request, 'vocabulary/word_edit.html', {'word': word})

@login_required
@user_passes_test(is_teacher)
def word_delete(request, word_id):
    """단어 삭제 (교사 전용)"""
    word = get_object_or_404(Word, id=word_id)
    
    if request.method == 'POST':
        english = word.english
        word.delete()
        messages.success(request, f'단어 "{english}"가 삭제되었습니다.')
        return redirect('vocabulary:word_list')
    
    return render(request, 'vocabulary/word_delete.html', {'word': word})
