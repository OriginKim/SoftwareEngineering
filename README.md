# 📚 TOEIC 단어 학습 웹 애플리케이션 (Django + MySQL)

TOEIC 학습자를 위한 **웹 기반 단어 학습 서비스**입니다.  
단어 학습 · 북마크 · 개인 단어장 · 학습 통계 등 기능을 제공하며,  
웹/모바일 환경 모두 지원합니다.

👉 GitHub 저장소: https://github.com/OriginKim/SoftwareEngineering  
👉 개발/기획 산출물 모음 (회의록, DB, 기획, 디자인 등)은 본문 하단 참고

-------------------------------------------------------------------------------
## ✨ 주요 기능

| 기능 그룹 | 상세 |
|-----------|------|
| 📚 단어 학습 | 단어/뜻/예문/번역/발음 제공, 난이도 필터링, 실시간 검색 |
| ⭐ 북마크 | 단어 즐겨찾기(토글), 북마크 단어만 보기 |
| 📝 개인 단어장 | 유저별 커스텀 단어장 – 단어 추가·제거·드래그앤드롭 |
| 📊 학습 통계 | 일간/주간 단어 학습 현황, 학습 미션 구현 |
| 🔐 사용자 인증 | Django 기본 User 기반 회원가입/로그인 |
| 🛠 관리자 기능 | 단어 CRUD, 일괄 CSV 추가, 사용자 학습 모니터링 |

-------------------------------------------------------------------------------
## 🧰 기술 스택

| 영역 | 기술 |
|------|------|
| Backend | Django 4.2 / Python 3.8 / Django ORM / REST API 일부 적용 |
| Frontend | Bootstrap 5 / Vanilla JS / AJAX / Web Speech API (발음) |
| Database | MySQL 8.0 (InnoDB, utf8mb4) |
| Infra | 로컬 개발 + GitHub 소스 관리 |
| Design Docs | Figma / Notion / DB 설계 문서 포함 |

-------------------------------------------------------------------------------
## ▶️ 실행 방법 (Quick Start)

```bash
# 1. 저장소 클론
git clone https://github.com/OriginKim/SoftwareEngineering.git
cd SoftwareEngineering

# 2. 가상환경 생성 + 활성화
python -m venv venv
source venv/bin/activate       # macOS/Linux
venv\Scripts\activate          # Windows

# 3. 패키지 설치
pip install -r requirements.txt

# 4. DB 설정 (MySQL 생성 후 settings.py or .env 설정)
python manage.py migrate

# 5. 서버 실행
python manage.py runserver
```
## 📌 초기 실행 시 주의  

DB 테이블 초기화 후 migrate 진행  

import_words.py 9번째 줄 → MySQL 비밀번호 본인 것에 맞게 수정  

Django admin 계정 필요 시: python manage.py createsuperuser  

## 📁 프로젝트 구조 (요약)
<pre>sw_wordtest/
├── apps/
│ ├── accounts/ # 사용자 기능
│ └── vocabulary/ # 단어 UI/CRUD/학습/북마크
├── templates/ # Django 템플릿
├── static/ # css/js/img
├── manage.py
└── requirements.txt
</pre>

## 📎 개발 산출물/문서 링크

### ✅ 개발 & DB 문서
- DBMS 사진 / 프로젝트 산출물
  https://www.notion.so/DBMS-202a497b74888069b377c8715da76400?pvs=21

### ✅ 회의록 / 팀 관리
- 팀 회의록 / 전체 일정
  https://www.notion.so/1bc9291b54018146b3f6f61f636e4ae1?pvs=21

### ✅ UI/UX 디자인 (Figma)
- 프로토타입 & 디자인
  https://www.figma.com/design/JdbZttXDJknwg6dmhgpNDJ/SE-10%EC%A1%B0

### ✅ 전체 프로젝트 Notion 홈
- SE TEAM 10 문서
  https://www.notion.so/SE-TEAM-10-1bc9291b5401803099efe19213f4023d?pvs=21

### ✅ 제품 시연 영상
- 데스크탑 시연 영상
  https://www.youtube.com/watch?v=avshfVA7-1U
- 모바일 대응 시연 영상
  https://www.youtube.com/watch?v=xs5OiEkSkOo

### ✅ GenAI Prompt 코드
- 개발 자동화/기획용 ChatGPT Prompt 문서
  https://www.notion.so/GenAI-Prompt-Code-1faa497b74888076a71bf9f2bce84748?pvs=21


## 📌 향후 개선 예정 (v2 로드맵)
- OAuth 로그인 적용 (구글·카카오)
- 데일리 학습 리마인더 / 푸시 알림
- REST API 완전 분리 → React/Flutter 클라이언트 연동
- 오답/복습 알고리즘 (Spaced Repetition 기반)


## 👨‍💻 제작자
- 역할: 백엔드 & DB 설계
- 이름: OriginKim (김기원)
- GitHub: https://github.com/OriginKim
- 팀 문서/회의록: 위 Notion 링크 참조
