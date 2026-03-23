# API 명세서 (Python 모듈 인터페이스)

## 1. 개요
Streamlit 앱 내부에서 사용되는 Python 모듈 수준의 API 명세.
REST API가 아닌 함수 호출 기반 인터페이스로 설계.

## 2. 모듈 구성

```
db.py          → 데이터베이스 계층 (VocabRepository)
quiz_logic.py  → 퀴즈 비즈니스 로직 (QuizService)
app.py         → Streamlit UI 및 세션 관리
```

---

## 3. db.py - 데이터베이스 API

### 3.1 init_db() -> None
- **설명**: DB 초기화. 테이블 생성 및 시드 데이터 삽입.
- **호출 시점**: 앱 최초 로드 시 1회
- **부작용**: vocab.db 파일 생성, vocabulary 테이블 생성, 44개 단어 삽입
- **에러**: 파일 시스템 권한 문제 시 sqlite3.OperationalError

### 3.2 get_all_vocab() -> list[dict]
- **설명**: 전체 단어 목록 반환
- **반환값**: `[{"id": str, "jp": str, "ko": str, "pron": str}, ...]`
- **반환 개수**: 44개 (시드 데이터 기준)
- **캐싱**: `@st.cache_data`로 캐싱 권장

---

## 4. quiz_logic.py - 퀴즈 로직 API

### 4.1 pick_next_question(vocab, recent_ids, wrong_queue) -> dict
- **설명**: 다음 출제할 단어 선택 (오답 우선, 최근 출제 회피)
- **매개변수**:
  | 이름 | 타입 | 설명 |
  |------|------|------|
  | vocab | list[dict] | 전체 단어 풀 |
  | recent_ids | list[str] | 최근 출제된 ID 목록 (최대 12개) |
  | wrong_queue | list[str] | 오답 우선 출제 큐 |
- **반환값**: `{"id": str, "jp": str, "ko": str, "pron": str}`
- **알고리즘 우선순위**:
  1. wrong_queue에 있고 recent_ids에 없는 단어
  2. wrong_queue에 있는 아무 단어
  3. recent_ids에 없는 랜덤 단어
  4. 전체 풀에서 랜덤

### 4.2 build_choices(answer, vocab_pool) -> list[dict]
- **설명**: 3지선다 보기 생성 (정답 1개 + 오답 2개, 셔플)
- **매개변수**:
  | 이름 | 타입 | 설명 |
  |------|------|------|
  | answer | dict | 정답 단어 |
  | vocab_pool | list[dict] | 오답 후보 풀 |
- **반환값**: `[{"id", "jp", "ko", "pron", "is_answer": bool}, ...]` (길이 3, 랜덤 순서)

### 4.3 compute_analytics(vocab, attempt_stats, wrong_stats, confusion_stats) -> dict
- **설명**: 실시간 분석 데이터 계산
- **매개변수**:
  | 이름 | 타입 | 설명 |
  |------|------|------|
  | vocab | list[dict] | 전체 단어 목록 |
  | attempt_stats | dict[str,int] | 단어별 시도 횟수 |
  | wrong_stats | dict[str,int] | 단어별 오답 횟수 |
  | confusion_stats | dict[str,int] | 혼동 쌍 횟수 |
- **반환값**:
  ```python
  {
      "attempted_count": int,        # 시도한 고유 단어 수
      "total_attempts": int,         # 총 풀이 횟수
      "overall_accuracy": int|None,  # 전체 정답률 (%, 시도 없으면 None)
      "difficult_words": [           # 자주 틀리는 단어 Top 5
          {"jp", "ko", "pron", "wrong_count", "accuracy"},
          ...
      ],
      "confusion_pairs": [           # 혼동 쌍 Top 5
          {"count", "answer": dict, "picked": dict},
          ...
      ]
  }
  ```

---

## 5. app.py - 세션 상태 관리 API

### 5.1 init_session_state() -> None
- **설명**: session_state 키 초기화 (존재하지 않는 키만)

### 5.2 handle_choice(choice_index: int) -> None
- **설명**: 사용자 답변 처리
- **동작**:
  1. locked 상태 확인
  2. attempt_stats 업데이트
  3. 정답/오답 분기 처리
  4. feedback 메시지 설정
  5. 자동으로 다음 문제 준비

### 5.3 go_next() -> None
- **설명**: 다음 문제로 이동
- **동작**: pick_next_question → build_choices → session_state 업데이트

### 5.4 reset_quiz() -> None
- **설명**: 퀴즈 전체 초기화
- **동작**: 모든 session_state 키를 초기값으로 리셋

---

## 6. TTS (Text-to-Speech) API

### 6.1 generate_tts(text: str, lang: str = "ja") -> bytes
- **설명**: gTTS를 사용하여 일본어 음성 MP3 생성
- **매개변수**: text(발음할 텍스트), lang(언어 코드)
- **반환값**: MP3 바이너리 데이터
- **사용**: `st.audio(bytes_data, format="audio/mp3", autoplay=True)`
