# 유튜브 댓글 분석기

Streamlit Cloud에서 동작하는 유튜브 댓글 분석 앱입니다.

## 기능
- YouTube API 키 + 영상 링크 입력
- 영상 미리보기, 제목/채널/조회수/좋아요/댓글수 표시
- 댓글 수집 개수 슬라이더 조절
- 날짜별 / 시간대(0~23시)별 댓글 작성 추이 차트
- 좋아요 Top10, 좋아요 분포 등 댓글 반응도 분석
- 댓글 워드클라우드 (한글 폰트 자동 적용)
- 원본 댓글 데이터 표 + CSV 다운로드

## 사전 준비: YouTube Data API 키 발급
1. https://console.cloud.google.com/ 접속 후 프로젝트 생성
2. "API 및 서비스" → "라이브러리"에서 **YouTube Data API v3** 검색 후 사용 설정
3. "사용자 인증 정보"에서 **API 키** 생성
4. 발급받은 키를 앱 사이드바에 입력 (외부에 노출되지 않도록 주의)

## 로컬 실행
```bash
pip install -r requirements.txt
streamlit run app.py
```
로컬 macOS/Windows에서는 시스템에 설치된 한글 폰트를 자동으로 사용합니다.

## Streamlit Cloud 배포
1. 이 폴더(app.py, requirements.txt, packages.txt)를 GitHub 저장소에 그대로 올립니다.
2. https://share.streamlit.io 에서 저장소를 선택해 배포합니다.
3. `packages.txt`의 `fonts-nanum`이 자동으로 apt 설치되어 워드클라우드에 한글이 정상적으로 표시됩니다.
4. API 키는 코드에 하드코딩하지 말고, 사이드바 입력창을 통해 매번 입력하거나
   Streamlit Cloud의 "Secrets"에 저장 후 `st.secrets["YOUTUBE_API_KEY"]`로 불러오도록 커스터마이징할 수 있습니다.

## 주의사항
- YouTube Data API는 하루 할당량(기본 10,000 units)이 있습니다.
  댓글 100개 조회(commentThreads.list) 1회 호출은 1 unit을 사용하므로,
  일반적인 사용에서는 넉넉하지만 대량 반복 조회 시 할당량 초과 오류가 날 수 있습니다.
- 댓글 기능이 꺼진 영상은 댓글을 가져올 수 없습니다.
