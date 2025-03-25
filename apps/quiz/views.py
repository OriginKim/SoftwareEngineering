from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count
from .models import Quiz, QuizQuestion, QuizAttempt
from apps.vocabulary.models import Word
import random
from django.urls import reverse
from apps.study.models import StudyProgress, WordStudyHistory

# Create your views here.

@login_required
def quiz_home(request):
    """퀴즈 홈 뷰"""
    # 사용자의 학습 진행 상황 가져오기
    total_words = Word.objects.count()
    learned_words = StudyProgress.objects.filter(user=request.user).count()
    
    # 학습한 단어들의 수 계산
    studied_words_count = Word.objects.filter(
        study_progress__user=request.user,
        study_progress__review_count__gt=0
    ).distinct().count()
    
    # 사용자가 생성한 퀴즈 또는 공개된 퀴즈 중 최근 5개
    recent_quizzes = Quiz.objects.filter(
        Q(created_by=request.user) | Q(is_public=True)
    ).order_by('-created_at')[:5]
    
    context = {
        'total_words': total_words,
        'learned_words': learned_words,
        'studied_words_count': studied_words_count,
        'recent_quizzes': recent_quizzes
    }
    
    return render(request, 'quiz/quiz_home.html', context)

@login_required
def word_test(request):
    """일반 단어 테스트"""
    if request.method == 'POST':
        # 답안 제출 처리
        data = request.POST
        score = 0
        results = []
        
        # 퀴즈 생성
        quiz = Quiz.objects.create(
            title=f"{request.user.username}의 단어 테스트",
            quiz_type='en_to_ko',
            difficulty='medium',
            created_by=request.user,
            is_public=False
        )
        
        for i in range(10):  # 10문제
            question_key = f'question_{i}'
            answer_key = f'answer_{i}'
            correct_key = f'correct_{i}'
            
            if question_key in data and answer_key in data and correct_key in data:
                user_answer = data[answer_key].strip()
                correct_answer = data[correct_key].strip()
                word_id = data[question_key]
                word = get_object_or_404(Word, id=word_id)
                
                # 정답 체크
                is_correct = user_answer.lower() == correct_answer.lower()
                
                # 퀴즈 문제 생성
                question = QuizQuestion.objects.create(
                    quiz=quiz,
                    word=word,
                    order=i+1,
                    user_answer=user_answer,
                    is_correct=is_correct
                )
                
                # 학습 기록 저장
                WordStudyHistory.objects.create(
                    user=request.user,
                    word=word,
                    is_correct=is_correct,
                )
                
                if is_correct:
                    score += 1
                
                results.append({
                    'question': word.english if correct_answer == word.korean else word.korean,
                    'correct_answer': correct_answer,
                    'user_answer': user_answer,
                    'is_correct': is_correct
                })
        
        # 퀴즈 시도 기록 저장
        attempt = QuizAttempt.objects.create(
            user=request.user,
            quiz=quiz,
            score=score * 10,  # 100점 만점
            total_questions=10,
            correct_answers=score,
            completed_at=timezone.now()
        )
        
        context = {
            'score': score * 10,  # 100점 만점으로 변환
            'correct_count': score,
            'wrong_count': 10 - score,
            'answers': results,
            'quiz': quiz,
            'attempt': attempt
        }
        
        return render(request, 'quiz/test_result.html', context)
    
    # GET 요청: 새로운 테스트 시작
    # 학습한 단어들 중에서 10개를 랜덤으로 선택
    studied_words = Word.objects.filter(
        study_progress__user=request.user,
        study_progress__review_count__gt=0
    ).distinct()
    
    if studied_words.count() < 10:
        messages.warning(request, '테스트를 위해서는 최소 10개의 단어를 학습해야 합니다.')
        return redirect('study:daily_words')
    
    test_words = list(studied_words.order_by('?')[:10])
    questions = []
    
    for i, word in enumerate(test_words):
        # 랜덤하게 문제 유형 선택 (영한 또는 한영)
        is_en_to_ko = random.choice([True, False])
        
        if is_en_to_ko:
            question = word.english
            answer = word.korean
            question_type = 'en_to_ko'
        else:
            question = word.korean
            answer = word.english
            question_type = 'ko_to_en'
        
        questions.append({
            'id': i + 1,
            'word_id': word.id,
            'question': question,
            'answer': answer,
            'type': question_type
        })
    
    return render(request, 'quiz/word_test.html', {
        'questions': questions
    })

@login_required
def quiz_list(request):
    """퀴즈 목록 뷰"""
    # 공개된 퀴즈 또는 자신이 만든 퀴즈만 표시
    quizzes = Quiz.objects.filter(
        Q(is_public=True) | Q(created_by=request.user)
    ).select_related('created_by')
    
    # 각 퀴즈의 문제 수를 미리 계산
    quiz_questions = QuizQuestion.objects.filter(quiz__in=quizzes).values('quiz').annotate(question_count=Count('id'))
    quiz_question_counts = {q['quiz']: q['question_count'] for q in quiz_questions}
    
    # 각 퀴즈 객체에 문제 수 추가
    for quiz in quizzes:
        quiz.question_count = quiz_question_counts.get(quiz.id, 0)
    
    context = {
        'quizzes': quizzes,
        'quiz_types': Quiz.QUIZ_TYPES,
        'difficulties': Word.DIFFICULTY_CHOICES,
    }
    return render(request, 'quiz/quiz_list.html', context)

@login_required
def quiz_delete(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)
    if request.method == 'POST':
        quiz.delete()
        messages.success(request, '퀴즈가 삭제되었습니다.')
        return redirect('quiz:quiz_list')
    return redirect('quiz:quiz_list')

@login_required
def quiz_create(request):
    """퀴즈 생성 뷰"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        quiz_type = request.POST.get('quiz_type')
        difficulty = request.POST.get('difficulty')
        is_public = request.POST.get('is_public') == 'on'
        time_limit = request.POST.get('time_limit', 0)
        word_count = int(request.POST.get('word_count', 10))
        
        print(f"[DEBUG] Creating quiz: {title}, type: {quiz_type}, word_count: {word_count}")
        
        # 퀴즈 생성
        quiz = Quiz.objects.create(
            title=title,
            description=description,
            quiz_type=quiz_type,
            difficulty=difficulty,
            created_by=request.user,
            is_public=is_public,
            time_limit=time_limit
        )
        
        print(f"[DEBUG] Quiz created with ID: {quiz.id}")
        
        # 문제 생성 - 사용자가 학습한 단어들 중에서 선택
        studied_words = Word.objects.filter(
            study_progress__user=request.user,
            study_progress__review_count__gt=0
        ).distinct()
        
        studied_words_count = studied_words.count()
        print(f"[DEBUG] Found {studied_words_count} studied words")
        
        if studied_words_count < word_count:
            print(f"[DEBUG] Not enough studied words. Required: {word_count}, Available: {studied_words_count}")
            quiz.delete()
            messages.error(request, f'퀴즈 생성을 위해서는 최소 {word_count}개의 단어를 학습해야 합니다.')
            return redirect('quiz:quiz_list')
        
        words = list(studied_words.order_by('?')[:word_count])
        print(f"[DEBUG] Selected {len(words)} words for quiz")
        
        for i, word in enumerate(words, 1):
            print(f"[DEBUG] Creating question {i} with word: {word.english} - {word.korean}")
            question = QuizQuestion(quiz=quiz, word=word, order=i)
            
            if quiz_type == 'multiple':
                # 객관식 보기 생성
                wrong_words = Word.objects.exclude(id=word.id).order_by('?')[:3]
                options = [word.korean] + [w.korean for w in wrong_words]
                random.shuffle(options)
                
                question.option1 = options[0]
                question.option2 = options[1]
                question.option3 = options[2]
                question.option4 = options[3]
                question.correct_option = options.index(word.korean) + 1
            
            question.save()
            print(f"[DEBUG] Question {i} saved with ID: {question.id}")
        
        questions_count = QuizQuestion.objects.filter(quiz=quiz).count()
        print(f"[DEBUG] Total questions created for quiz: {questions_count}")
        
        messages.success(request, '퀴즈가 생성되었습니다.')
        return redirect('quiz:quiz_detail', quiz_id=quiz.id)
    
    context = {
        'quiz_types': Quiz.QUIZ_TYPES,
        'difficulties': Word.DIFFICULTY_CHOICES,
    }
    return render(request, 'quiz/quiz_create.html', context)

@login_required
def quiz_detail(request, quiz_id):
    """퀴즈 상세 뷰"""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # 비공개 퀴즈인 경우 작성자만 접근 가능
    if not quiz.is_public and quiz.created_by != request.user:
        messages.error(request, '접근 권한이 없습니다.')
        return redirect('quiz:quiz_list')
    
    # 문제 수 계산
    question_count = QuizQuestion.objects.filter(quiz=quiz).count()
    quiz.question_count = question_count
    
    # 이전 응시 기록
    user_attempts = QuizAttempt.objects.filter(
        user=request.user,
        quiz=quiz
    ).order_by('-started_at')
    
    context = {
        'quiz': quiz,
        'user_attempts': user_attempts,
        'quiz_types': Quiz.QUIZ_TYPES,
        'difficulties': Word.DIFFICULTY_CHOICES,
    }
    return render(request, 'quiz/quiz_detail.html', context)

@login_required
def quiz_start(request, quiz_id):
    """퀴즈 시작 뷰"""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = QuizQuestion.objects.filter(quiz=quiz).order_by('id')
    
    if not questions.exists():
        messages.error(request, '이 퀴즈에는 문제가 없습니다.')
        return redirect('quiz:quiz_detail', quiz_id=quiz_id)
    
    # 첫 번째 문제로 시작
    first_question = questions.first()
    
    context = {
        'quiz': quiz,
        'question': first_question,
        'question_number': 1,
        'total_questions': questions.count(),
        'end_time': timezone.now() + timezone.timedelta(minutes=30)  # 30분 제한시간
    }
    
    return render(request, 'quiz/quiz_submit.html', context)

@login_required
def quiz_submit(request, quiz_id):
    """퀴즈 답안 제출 뷰"""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = QuizQuestion.objects.filter(quiz=quiz).order_by('id')
    
    if request.method == 'POST':
        # 답안 처리
        answer = request.POST.get('answer', '').strip()
        question_id = request.POST.get('question_id')
        
        try:
            current_question = questions.get(id=question_id)
        except QuizQuestion.DoesNotExist:
            messages.error(request, '잘못된 문제 ID입니다.')
            return redirect('quiz:quiz_detail', quiz_id=quiz_id)
        
        # 답안 정확도 확인
        is_correct = False
        if quiz.quiz_type == 'en_to_ko':
            is_correct = answer.lower() == current_question.word.korean.lower()
        else:
            is_correct = answer.lower() == current_question.word.english.lower()
        
        # 답안 저장
        current_question.user_answer = answer
        current_question.is_correct = is_correct
        current_question.save()
        
        print(f"[DEBUG] Saving answer - Question: {current_question.word.english}, User Answer: {answer}, Correct: {is_correct}")
        
        # 학습 기록 저장
        study_history = WordStudyHistory.objects.create(
            user=request.user,
            word=current_question.word,
            is_correct=is_correct,
        )
        print(f"[DEBUG] Created WordStudyHistory - ID: {study_history.id}, Word: {study_history.word.english}, Is Correct: {study_history.is_correct}")
        
        # 다음 문제 또는 결과 페이지로
        next_question = questions.filter(id__gt=current_question.id).first()
        if next_question:
            context = {
                'quiz': quiz,
                'question': next_question,
                'question_number': list(questions).index(next_question) + 1,
                'total_questions': questions.count(),
                'end_time': request.POST.get('end_time')
            }
            return render(request, 'quiz/quiz_submit.html', context)
        else:
            # 모든 문제를 다 풀었을 때
            correct_count = questions.filter(is_correct=True).count()
            score = (correct_count / questions.count()) * 100
            
            # 퀴즈 시도 기록 저장
            attempt = QuizAttempt.objects.create(
                user=request.user,
                quiz=quiz,
                score=score,
                total_questions=questions.count(),
                correct_answers=correct_count,
                completed_at=timezone.now()
            )
            
            # 결과 컨텍스트 준비
            answers = []
            for q in questions:
                answers.append({
                    'question': q.word.english if quiz.quiz_type == 'en_to_ko' else q.word.korean,
                    'correct_answer': q.word.korean if quiz.quiz_type == 'en_to_ko' else q.word.english,
                    'user_answer': q.user_answer,
                    'is_correct': q.is_correct
                })
            
            context = {
                'quiz': quiz,
                'score': score,
                'correct_count': correct_count,
                'total_questions': questions.count(),
                'answers': answers,
                'attempt': attempt
            }
            return render(request, 'quiz/test_result.html', context)
    
    # GET 요청 시 첫 문제로 시작
    first_question = questions.first()
    if not first_question:
        messages.error(request, '이 퀴즈에는 문제가 없습니다.')
        return redirect('quiz:quiz_detail', quiz_id=quiz_id)
        
    context = {
        'quiz': quiz,
        'question': first_question,
        'question_number': 1,
        'total_questions': questions.count(),
        'end_time': timezone.now() + timezone.timedelta(minutes=30)
    }
    return render(request, 'quiz/quiz_submit.html', context)

@login_required
def quiz_history_detail(request, attempt_id):
    """퀴즈 응시 기록 상세 뷰"""
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
    questions = QuizQuestion.objects.filter(quiz=attempt.quiz).select_related('word')
    
    answer_history = []
    for question in questions:
        answer_history.append({
            'question': question,
            'user_answer': question.user_answer,
            'is_correct': question.is_correct
        })
    
    context = {
        'attempt': attempt,
        'answer_history': answer_history
    }
    
    return render(request, 'quiz/quiz_history_detail.html', context)
