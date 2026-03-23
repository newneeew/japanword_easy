# Database Backend 명세서

## 1. 개요
일본어-한국어 단어 퀴즈 앱의 데이터베이스 백엔드 설계 문서.
SQLite를 사용하며, Streamlit Cloud 배포를 고려한 경량 구조.

## 2. DBMS 선택
- **SQLite 3**: Python 표준 라이브러리 내장, 별도 서버 불필요
- Streamlit Cloud에서 파일 기반 DB로 동작
- 단일 사용자 세션 기준 설계

## 3. 스키마

### 3.1 vocabulary 테이블
단어장 데이터 저장. 앱 초기화 시 시드 데이터 자동 삽입.

```sql
CREATE TABLE IF NOT EXISTS vocabulary (
    id   TEXT PRIMARY KEY,   -- "{jp}__{ko}" 형식 (원본 React 앱과 동일)
    jp   TEXT NOT NULL,      -- 일본어 단어
    ko   TEXT NOT NULL,      -- 한국어 뜻
    pron TEXT NOT NULL DEFAULT ''  -- 한국어 발음 표기
);
```

**필드 설명:**
| 필드 | 타입 | 설명 | 예시 |
|------|------|------|------|
| id | TEXT PK | 고유 식별자 | `とても__매우` |
| jp | TEXT | 일본어 원문 | `とても` |
| ko | TEXT | 한국어 의미 | `매우` |
| pron | TEXT | 발음 표기 | `토테모` |

### 3.2 초기 시드 데이터
총 44개 단어 항목 (원본 React 앱의 rawVocabGroups에서 추출)

**카테고리:**
- 형용사/나형용사 (24개): とても, すきだ, きらいだ 등
- 일상 동작 표현 (20개): あさ7じにおきる, ごはんをたべる 등

## 4. 세션 데이터 (비DB, Streamlit session_state)
퀴즈 진행 상태는 DB에 저장하지 않고 Streamlit session_state로 관리.
원본 React 앱과 동일하게 페이지 새로고침 시 초기화됨.

| 키 | 타입 | 설명 |
|----|------|------|
| question_count | int | 현재 문제 번호 |
| correct | int | 정답 횟수 |
| wrong | int | 오답 횟수 |
| locked | bool | 답변 잠금 상태 |
| recent_ids | list[str] | 최근 출제 ID (최대 12개) |
| wrong_queue | list[str] | 오답 우선 출제 큐 (최대 25개) |
| attempt_stats | dict[str, int] | 단어별 시도 횟수 |
| wrong_stats | dict[str, int] | 단어별 오답 횟수 |
| confusion_stats | dict[str, int] | 혼동 쌍 횟수 (키: "정답ID\|\|\|선택ID") |

## 5. DB 초기화 흐름
1. 앱 시작 시 `init_db()` 호출
2. vocabulary 테이블 없으면 생성
3. 44개 시드 데이터 INSERT OR IGNORE로 삽입
4. 이후 `get_all_vocab()`으로 전체 단어 조회

## 6. 확장 가능성
현재는 세션 기반이지만, 향후 아래 테이블 추가로 학습 이력 영속화 가능:
- `quiz_sessions`: 세션별 통계
- `attempt_logs`: 개별 답변 기록
- `user_progress`: 사용자별 누적 학습 데이터
