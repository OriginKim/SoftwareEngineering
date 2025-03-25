# TOEIC 단어 학습 시스템

## 프로젝트 소개
TOEIC 단어 학습을 위한 웹 기반 학습 시스템입니다. 사용자가 효율적으로 단어를 학습하고 복습할 수 있도록 도와줍니다.

## 주요 기능

### 1. 계정 관리
- 회원가입/로그인/로그아웃
- 프로필 관리

### 2. 단어장 관리
- 단어 추가/수정/삭제
- 단어 상세 정보 조회
- 북마크 기능

### 3. 학습 계획
- 학습 계획 생성/수정/삭제
- 일일 학습량 설정
- 학습 목표 설정

### 4. 학습 모드
- 플래시카드 학습
- 단어장 학습
- 복습 시스템
- 틀린 단어 노트

### 5. 퀴즈 시스템
- 단어 테스트
- 퀴즈 생성 및 관리
- 학습 이력 관리

### 6. 알림 시스템
- 복습 알림
- 학습 목표 달성 알림
- 학습 일정 알림

## 기술 스택
- Python 3.11
- Django 5.0
- PostgreSQL 15
- Bootstrap 5
- jQuery 3.7

## 설치 방법

### 1. 환경 설정
```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 데이터베이스 설정
```bash
# PostgreSQL 데이터베이스 생성
createdb toeic_word_db

# 마이그레이션
python manage.py makemigrations
python manage.py migrate
```

### 3. 관리자 계정 생성
```bash
python manage.py createsuperuser
```

### 4. 서버 실행
```bash
python manage.py runserver
```

## 데이터베이스 덤프 파일 사용 방법

### MySQL Workbench에서 덤프 파일 import하기
1. MySQL Workbench 실행
2. 서버에 연결
3. 상단 메뉴에서 File > Open SQL Script 선택
4. 프로젝트의 `dumps` 폴더에서 원하는 덤프 파일 선택
5. SQL 편집기에서 실행할 쿼리 확인
6. 번개 모양 아이콘(Execute) 클릭하여 스크립트 실행

### 주의사항
- 덤프 파일을 import하기 전에 기존 데이터베이스가 있다면 백업
- 데이터베이스가 생성되어 있어야 함
- 사용자 권한이 적절히 설정되어 있어야 함

## 프로젝트 구조
```
toeic_word/
├── apps/
│   ├── accounts/     # 계정 관리
│   ├── vocabulary/   # 단어장 관리
│   ├── study/        # 학습 관리
│   └── quiz/         # 퀴즈 시스템
├── config/           # 프로젝트 설정
├── templates/        # HTML 템플릿
├── static/          # 정적 파일
└── dumps/           # 데이터베이스 덤프 파일
```

## URL 구조

### 계정 관리 (/accounts/)
- 홈: `/`
- 로그인: `/login/`
- 로그아웃: `/logout/`
- 회원가입: `/signup/`
- 프로필: `/profile/`

### 단어장 (/vocabulary/)
- 단어 목록: `/words/`
- 단어 추가: `/words/add/`
- 단어 수정: `/words/<id>/edit/`
- 단어 삭제: `/words/<id>/delete/`
- 단어 상세: `/words/<id>/`
- 북마크: `/bookmarks/`

### 학습 관리 (/study/)
- 학습 계획: `/plans/`
- 학습 세션: `/session/`
- 학습 모드: `/flashcard/`, `/vocabulary/`, `/review/`
- 틀린 노트: `/wrong-notes/`
- 북마크: `/bookmarks/`
- 알림: `/notifications/`
- 통계: `/statistics/`

### 퀴즈 (/quiz/)
- 퀴즈 홈: `/`
- 단어 테스트: `/word-test/`
- 퀴즈 관리: `/list/`, `/create/`, `<id>/`
- 퀴즈 실행: `<id>/start/`, `<id>/submit/`
- 히스토리: `/history/<id>/`

## 개발 가이드

### 코드 스타일
- PEP 8 준수
- 함수/클래스 문서화 필수
- 의미 있는 변수명 사용

### Git 커밋 규칙
- feat: 새로운 기능
- fix: 버그 수정
- docs: 문서 수정
- style: 코드 포맷팅
- refactor: 코드 리팩토링
- test: 테스트 코드
- chore: 기타 변경사항

## 라이선스
이 프로젝트는 MIT 라이선스를 따릅니다. 