# Streamlit으로 상자그림 수업 도구 만들고 배포하기

내 컴퓨터에서 Streamlit 앱 만들기, GitHub와 Streamlit Cloud로 배포하기, 구글 시트와 OpenAI 연결하기 영상 5편은 주요 장면만 남긴 요약 영상이므로 전체 코드는 이 저장소를 fork 해서 꼭 확인하고 수정하기

## 링크
- 완성된 앱: https://sbhboxplot.streamlit.app/
- 코드 (GitHub): https://github.com/Surihub/myapp
- 실습용 구글 시트: https://docs.google.com/spreadsheets/d/14r7sB9Eb3xenskK7af2D3h9Drwf7lzWuMUT7fJiiJNc/edit?gid=655941621#gid=655941621

## 영상 목록
1. 로컬에서 만들고 GitHub, Streamlit Cloud로 배포하기: https://youtu.be/Kyd0fJCF1HQ
2. 구글 시트 자료로 두 반 통학 시간 상자그림 그리기: https://youtu.be/wdY82fYpgZw
3. 서비스 계정으로 구글 시트에 응답 저장하기: https://youtu.be/wABbtZ8Xd8g
4. OpenAI로 서술형 답안에 AI 피드백 주기: https://youtu.be/BYvl1Yhuj9I
5. AI로 수학 영상 만들기 (Manim): https://youtu.be/Vi3djhQ1aL4

## 내 앱으로 만들기 (fork)
1. 이 저장소 오른쪽 위의 Fork를 눌러 내 계정으로 복사하기
2. 실습용 구글 시트를 열고 파일 → 사본 만들기로 내 시트 만들기
3. `pages/2_📦_통학시간_상자그림.py`의 `sheet_id`를 내 시트 ID로 바꾸기. 시트 ID는 시트 주소의 `/d/` 와 `/edit` 사이 값인지 확인하기
4. 3편과 4편을 따라 `.streamlit/secrets.toml`을 만들고, 배포한 앱의 Settings → Secrets에도 같은 내용 넣기

---

## 1. 로컬에서 만들고 GitHub, Streamlit Cloud로 배포하기

영상: https://youtu.be/Kyd0fJCF1HQ

내 컴퓨터에서 Streamlit 앱 만들고 실행하기 GitHub에 올린 뒤 Streamlit Cloud로 배포해 인터넷 주소가 있는 앱 만들기. 학번 입력 메인 화면과 상자그림 복습 페이지 만들기. 배포 서버의 패키지 설치 오류와 한글 깨짐도 함께 해결하기

### 준비물
- VS Code, Python
- GitHub 계정: https://github.com
- Streamlit Community Cloud: https://share.streamlit.io

### 파일 구성
- `app.py`: 학번 입력
- `pages/1_📝_상자그림_복습.py`
- `requirements.txt`: 배포 서버에 설치할 패키지 (streamlit, seaborn, matplotlib, koreanize-matplotlib, setuptools)
- `packages.txt`: fonts-nanum (배포 서버 그래프 한글 글꼴)
- `.gitignore`: .streamlit/secrets.toml

### 명령어
```
pip install streamlit seaborn
streamlit run app.py
```
GitHub에 처음 올리기 (이름과 이메일은 처음 한 번만 설정하기)
```
git config --global user.name "이름"
git config --global user.email "GitHub 가입 이메일"
git init -b main && git add . && git commit -m "메인 화면" && git remote add origin https://github.com/계정/myapp.git && git push -u origin main
```
영상에서는 VS Code 왼쪽 소스 제어의 Publish to GitHub 버튼으로 올리기. 이후 수정은 아래 명령어로 올리기.
```
git add . && git commit -m "수정 내용" && git push
```

### 배포
share.streamlit.io 로그인 → Create app → 저장소 myapp, 브랜치 main, Main file path app.py → Deploy

### 반영이 안 될 때
앱 오른쪽 위 메뉴에서 Rerun 누르기. 그래도 반영되지 않으면 share.streamlit.io에서 Reboot app 누르기. 오류는 앱 오른쪽 아래 Manage app에서 확인하기

---

## 2. 구글 시트 자료로 두 반 통학 시간 상자그림 그리기

영상: https://youtu.be/wdY82fYpgZw

추가 패키지 없이 공개 구글 시트를 CSV로 읽어 두 반의 통학 시간을 상자그림으로 비교하는 페이지 추가하기 수정한 코드를 다시 올려 배포된 앱에 반영하기

### 준비물
- 구글 시트 공유 설정: 링크가 있는 모든 사용자, 뷰어
- 시트 ID: 시트 주소의 `/d/` 와 `/edit` 사이 값

### 시트를 CSV로 읽는 주소
```
https://docs.google.com/spreadsheets/d/{시트ID}/gviz/tq?tqx=out:csv&headers=1&sheet={탭 이름}
```

### 명령어
```
streamlit run app.py
git add . && git commit -m "상자그림 페이지" && git push
```
push하면 배포된 앱에 자동으로 반영하기 앱을 새로고침해 페이지가 추가되었는지 꼭 확인하기

---

## 3. 서비스 계정으로 구글 시트에 응답 저장하기

영상: https://youtu.be/wABbtZ8Xd8g

앱에서 구글 시트에 쓰려면 앱 전용 계정(서비스 계정) 만들기. JSON 키를 만들고 secrets.toml로 비밀값 관리하기 학생이 입력한 통학 시간과 형성평가 점수를 학번별로 시트에 저장하기

### 서비스 계정 JSON 키 만들기
1. https://console.cloud.google.com 에서 새 프로젝트 만들기
2. API 및 서비스 → 라이브러리에서 Google Sheets API, Google Drive API 사용 설정
3. IAM 및 관리자 → 서비스 계정 → 서비스 계정 만들기
4. 만든 계정 → 키 탭 → 키 추가 → 새 키 만들기 → JSON 다운로드
5. JSON 안의 client_email을 구글 시트 공유에서 편집자로 추가

### 명령어
```
pip install st-gsheets-connection
git add . && git commit -m "구글 시트 연결" && git push
```
requirements.txt에 st-gsheets-connection 추가하기

### .streamlit/secrets.toml
```
[connections.gsheets]
spreadsheet = "시트 주소"
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "..."
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."
```

### 주의
- secrets.toml은 .gitignore에 있어 GitHub에 올라가지 않는지 확인하기 올린 뒤 저장소에 파일이 없는지 꼭 확인하기
- 배포된 앱에는 share.streamlit.io → 앱 Settings → Secrets에 같은 내용을 붙여 넣고 Save 누르기.

---

## 4. OpenAI로 서술형 답안에 AI 피드백 주기

영상: https://youtu.be/BYvl1Yhuj9I

두 반의 상자그림을 비교하는 서술형 문항에 AI가 채점 기준에 따라 피드백하도록 만들기. 답안과 피드백을 구글 시트에 저장하기 수업 코드로 잠가 링크만 아는 사람이 API 크레딧을 쓰지 못하게 설정하기

### 준비물
- OpenAI API 키: https://platform.openai.com/api-keys

### 명령어
```
pip install openai
git add . && git commit -m "서술형 AI 피드백" && git push
```
requirements.txt에 openai 추가하기

### secrets.toml 맨 위에 추가 ([connections.gsheets] 줄보다 위)
```
SECRET_CODE = "1234"
OPENAI_API_KEY = "sk-..."
```
배포된 앱의 Settings → Secrets 맨 위에도 같은 두 줄을 넣고 Save 누르기

### 주의
API 키는 코드에 직접 쓰지 말고 `st.secrets`로 꺼내 쓰기

---

## 5. AI로 수학 영상 만들기 (Manim)

영상: https://youtu.be/Vi3djhQ1aL4

만들고 싶은 장면을 글로 쓰면 AI가 Manim 코드를 작성하고 서버에서 짧은 수학 애니메이션으로 만드는 페이지 만들기. 상자그림을 그리는 과정을 영상으로 확인하고, 배포된 앱에서 전체 페이지 점검하기

### 준비물
- Manim Community: https://www.manim.community
- 4편에서 넣은 OPENAI_API_KEY, SECRET_CODE

### 파일 준비
requirements.txt에 추가하기
```
manim
```
packages.txt (배포 서버에 설치할 프로그램)
```
libcairo2-dev
libpango1.0-dev
pkg-config
fonts-nanum
```

### 올리기
```
git add . && git commit -m "AI 수학 영상" && git push
```
터미널 없이 GitHub 웹에서 Add file → Upload files로 올리기. 이때는 .gitignore가 적용되지 않으므로 secrets.toml을 올리지 않도록 꼭 확인하기 웹으로 올린 뒤에는 로컬에서 `git pull`을 먼저 해야 push 가능

처음 배포할 때는 Manim 설치에 몇 분 걸리는 점 확인하기
