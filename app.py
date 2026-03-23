"""Japanese-Korean Vocabulary Quiz - Streamlit App."""

import base64
import random
from io import BytesIO

import streamlit as st
import streamlit.components.v1 as components
from gtts import gTTS

from db import init_db, get_all_vocab
from quiz_logic import build_choices, compute_analytics, pick_next_question

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="일본어 단어 퀴즈", page_icon="🇯🇵", layout="wide")

# ── DB init & vocab load ─────────────────────────────────────────────────────
init_db()

ACTIVE_CHAPTER = "ch_12"


@st.cache_data
def load_vocab(chapter=None):
    return get_all_vocab(chapter=chapter)


vocab = load_vocab(chapter=ACTIVE_CHAPTER)

# ── TTS helper ───────────────────────────────────────────────────────────────


@st.cache_data(show_spinner=False, max_entries=200)
def generate_tts_b64(text: str) -> str:
    """Generate Japanese TTS audio, return as base64 string (cached)."""
    buf = BytesIO()
    tts = gTTS(text=text, lang="ja")
    tts.write_to_fp(buf)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()


def play_audio_js(b64_audio: str):
    """Play audio using JavaScript Audio API (bypasses autoplay restrictions)."""
    components.html(
        f"""
        <script>
        (function() {{
            var audio = new Audio("data:audio/mp3;base64,{b64_audio}");
            audio.volume = 1.0;
            audio.play().catch(function(e) {{ console.log('audio play failed:', e); }});
        }})();
        </script>
        """,
        height=0,
    )


# ── Session state init ───────────────────────────────────────────────────────


def _init_first_question():
    answer = random.choice(vocab)
    return answer, build_choices(answer, vocab)


def init_session_state():
    defaults = {
        "question_count": 1,
        "correct": 0,
        "wrong": 0,
        "locked": False,
        "selected_index": None,
        "recent_ids": [],
        "wrong_queue": [],
        "feedback_type": "",
        "feedback_text": "",
        "attempt_stats": {},
        "wrong_stats": {},
        "confusion_stats": {},
        "current_answer": None,
        "current_choices": [],
        "tts_audio": None,
        "advance_pending": False,
        "play_word": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

    if st.session_state.current_answer is None:
        answer, choices = _init_first_question()
        st.session_state.current_answer = answer
        st.session_state.current_choices = choices


init_session_state()


# ── Quiz logic callbacks ────────────────────────────────────────────────────


def handle_choice(index: int):
    """Process user's answer selection."""
    if st.session_state.locked:
        return

    choice = st.session_state.current_choices[index]
    answer = st.session_state.current_answer

    st.session_state.locked = True
    st.session_state.selected_index = index

    # TTS: always play the correct answer word
    try:
        st.session_state.tts_audio = generate_tts_b64(answer["jp"])
    except Exception:
        st.session_state.tts_audio = None

    # Update recent IDs
    recent = [rid for rid in st.session_state.recent_ids if rid != answer["id"]]
    recent.append(answer["id"])
    st.session_state.recent_ids = recent[-12:]

    # Update attempt stats
    st.session_state.attempt_stats[answer["id"]] = (
        st.session_state.attempt_stats.get(answer["id"], 0) + 1
    )

    if choice["is_answer"]:
        st.session_state.correct += 1
        st.session_state.wrong_queue = [
            wid for wid in st.session_state.wrong_queue if wid != answer["id"]
        ]
        st.session_state.feedback_type = "correct"
        st.session_state.feedback_text = f"정답 · {answer['jp']} ({answer['pron']})"
    else:
        st.session_state.wrong += 1
        wq = [answer["id"]] + [
            wid for wid in st.session_state.wrong_queue if wid != answer["id"]
        ]
        st.session_state.wrong_queue = wq[:25]
        st.session_state.wrong_stats[answer["id"]] = (
            st.session_state.wrong_stats.get(answer["id"], 0) + 1
        )
        pair_key = f"{answer['id']}|||{choice['id']}"
        st.session_state.confusion_stats[pair_key] = (
            st.session_state.confusion_stats.get(pair_key, 0) + 1
        )
        st.session_state.feedback_type = "wrong"
        st.session_state.feedback_text = (
            f"오답 · 정답은 {answer['jp']} ({answer['pron']})"
        )

    st.session_state.advance_pending = True
    st.session_state.play_word = None


def go_next():
    """Advance to next question."""
    answer = pick_next_question(
        vocab, st.session_state.recent_ids, st.session_state.wrong_queue
    )
    choices = build_choices(answer, vocab)
    st.session_state.question_count += 1
    st.session_state.current_answer = answer
    st.session_state.current_choices = choices
    st.session_state.locked = False
    st.session_state.selected_index = None
    st.session_state.feedback_type = ""
    st.session_state.feedback_text = ""
    st.session_state.tts_audio = None
    st.session_state.advance_pending = False
    st.session_state.play_word = None


def reset_quiz():
    """Reset all quiz state."""
    answer = random.choice(vocab)
    st.session_state.question_count = 1
    st.session_state.correct = 0
    st.session_state.wrong = 0
    st.session_state.locked = False
    st.session_state.selected_index = None
    st.session_state.recent_ids = []
    st.session_state.wrong_queue = []
    st.session_state.attempt_stats = {}
    st.session_state.wrong_stats = {}
    st.session_state.confusion_stats = {}
    st.session_state.feedback_type = ""
    st.session_state.feedback_text = ""
    st.session_state.tts_audio = None
    st.session_state.advance_pending = False
    st.session_state.play_word = None
    st.session_state.current_answer = answer
    st.session_state.current_choices = build_choices(answer, vocab)


# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    .quiz-meaning {
        text-align: center;
        padding: 2rem 1rem;
        background: #f8fafc;
        border-radius: 1rem;
        border: 1px solid #e2e8f0;
        margin: 1rem 0;
    }
    .quiz-meaning .label { font-size: 0.85rem; color: #64748b; font-weight: 500; }
    .quiz-meaning .word { font-size: 2.2rem; font-weight: 700; color: #0f172a; margin-top: 0.5rem; }
    .choice-card {
        text-align: center;
        padding: 1rem 0.5rem;
        border-radius: 0.75rem;
        border: 2px solid #e2e8f0;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .choice-correct {
        background: #dcfce7;
        border-color: #22c55e;
        color: #15803d;
    }
    .choice-wrong {
        background: #fee2e2;
        border-color: #ef4444;
        color: #b91c1c;
    }
    .choice-neutral {
        background: #f1f5f9;
        border-color: #cbd5e1;
        color: #475569;
    }
    .stat-card {
        text-align: center;
        padding: 0.75rem;
        background: #f8fafc;
        border-radius: 0.75rem;
        border: 1px solid #e2e8f0;
    }
    .stat-card .label { font-size: 0.75rem; color: #64748b; }
    .stat-card .value { font-size: 1.25rem; font-weight: 700; color: #0f172a; }
    .bar-bg { height: 8px; background: #e2e8f0; border-radius: 4px; overflow: hidden; margin-top: 4px; }
    .bar-fill-red { height: 100%; background: #fb7185; border-radius: 4px; }
    .bar-fill-amber { height: 100%; background: #fbbf24; border-radius: 4px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Layout ───────────────────────────────────────────────────────────────────
st.markdown("## 일본어 단어 퀴즈")
st.caption("업로드한 단어 DB를 반영했습니다.")

col_quiz, col_analysis = st.columns([1.1, 0.9], gap="large")

# ── Quiz Column ──────────────────────────────────────────────────────────────
with col_quiz:
    # Header stats
    hc1, hc2, hc3 = st.columns(3)
    hc1.markdown(f"**문제 {st.session_state.question_count}**")
    hc2.markdown(f"정답 **{st.session_state.correct}**")
    hc3.markdown(f"오답 **{st.session_state.wrong}**")

    # Question display
    st.markdown(
        f"""
        <div class="quiz-meaning">
            <div class="label">뜻</div>
            <div class="word">{st.session_state.current_answer['ko']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Choice area
    btn_cols = st.columns(3)

    for i, col in enumerate(btn_cols):
        with col:
            choice = st.session_state.current_choices[i]
            is_correct_answer = st.session_state.locked and choice["is_answer"]
            is_chosen_wrong = (
                st.session_state.locked
                and st.session_state.selected_index == i
                and not choice["is_answer"]
            )

            if st.session_state.locked:
                # Show colored feedback cards (not buttons)
                if is_correct_answer:
                    css_class = "choice-correct"
                    label = f"✅ {choice['jp']}"
                elif is_chosen_wrong:
                    css_class = "choice-wrong"
                    label = f"❌ {choice['jp']}"
                else:
                    css_class = "choice-neutral"
                    label = choice["jp"]

                st.markdown(
                    f'<div class="choice-card {css_class}">{label}</div>',
                    unsafe_allow_html=True,
                )
                # Click-to-play button under each card
                if st.button(f"🔊 발음", key=f"play_{i}", use_container_width=True):
                    st.session_state.play_word = choice["jp"]
                    st.rerun()
            else:
                if st.button(
                    choice["jp"],
                    key=f"choice_{i}",
                    use_container_width=True,
                ):
                    handle_choice(i)
                    st.rerun()

    # Feedback text
    if st.session_state.feedback_type == "correct":
        st.success(st.session_state.feedback_text)
    elif st.session_state.feedback_type == "wrong":
        st.error(st.session_state.feedback_text)
    else:
        st.info("정답을 고르면 일본어 음성이 재생됩니다.")

    # ── Audio playback ───────────────────────────────────────────────────
    # 1) Auto-play correct answer TTS on answer
    if st.session_state.tts_audio:
        play_audio_js(st.session_state.tts_audio)
        st.session_state.tts_audio = None

    # 2) On-demand TTS for clicked word
    if st.session_state.play_word:
        try:
            b64 = generate_tts_b64(st.session_state.play_word)
            play_audio_js(b64)
        except Exception:
            pass
        st.session_state.play_word = None

    # Navigation buttons
    nav1, nav2, _ = st.columns([1, 1, 2])
    with nav1:
        if st.button("다음 문제", type="primary", use_container_width=True):
            go_next()
            st.rerun()
    with nav2:
        if st.button("초기화", use_container_width=True):
            reset_quiz()
            st.rerun()

    # ── Client-side auto-advance (no time.sleep, no screen darkening) ────
    if st.session_state.advance_pending:
        delay_ms = 1300 if st.session_state.feedback_type == "correct" else 1700
        st.session_state.advance_pending = False
        components.html(
            f"""
            <script>
            (function() {{
                setTimeout(function() {{
                    var doc = window.parent.document;
                    // Find the hidden auto-advance input and trigger change
                    var hiddenBtn = doc.getElementById('auto_advance_target');
                    if (hiddenBtn) {{
                        hiddenBtn.click();
                    }} else {{
                        // Fallback: find button by exact text
                        var buttons = doc.querySelectorAll('button');
                        for (var i = 0; i < buttons.length; i++) {{
                            if (buttons[i].textContent.trim() === '⏭ 다음') {{
                                buttons[i].click();
                                break;
                            }}
                        }}
                    }}
                }}, {delay_ms});
            }})();
            </script>
            """,
            height=0,
        )

    # Hidden auto-advance button (visually hidden, JS clickable)
    st.markdown(
        '<div style="height:0;overflow:hidden;margin:0;padding:0;">',
        unsafe_allow_html=True,
    )
    if st.button("⏭ 다음", key="auto_advance_btn"):
        go_next()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ── Analysis Column ──────────────────────────────────────────────────────────
with col_analysis:
    st.markdown("### 오답 실시간 분석")
    st.caption("누적 반영")

    analytics = compute_analytics(
        vocab,
        st.session_state.attempt_stats,
        st.session_state.wrong_stats,
        st.session_state.confusion_stats,
    )

    # Summary metrics
    mc1, mc2, mc3 = st.columns(3)
    mc1.markdown(
        '<div class="stat-card"><div class="label">시도 단어</div>'
        f'<div class="value">{analytics["attempted_count"]}</div></div>',
        unsafe_allow_html=True,
    )
    mc2.markdown(
        '<div class="stat-card"><div class="label">총 풀이</div>'
        f'<div class="value">{analytics["total_attempts"]}</div></div>',
        unsafe_allow_html=True,
    )
    acc_display = (
        f'{analytics["overall_accuracy"]}%'
        if analytics["overall_accuracy"] is not None
        else "-"
    )
    mc3.markdown(
        '<div class="stat-card"><div class="label">전체 정답률</div>'
        f'<div class="value">{acc_display}</div></div>',
        unsafe_allow_html=True,
    )

    # Difficult words
    st.markdown("---")
    st.markdown("**자주 틀리는 단어** (오답 수 기준)")

    if not analytics["difficult_words"]:
        st.caption("아직 누적 데이터가 없습니다.")
    else:
        max_wrong = max(w["wrong_count"] for w in analytics["difficult_words"])
        for idx, item in enumerate(analytics["difficult_words"]):
            width = max(10, round((item["wrong_count"] / max(max_wrong, 1)) * 100))
            acc = item["accuracy"] if item["accuracy"] is not None else 0
            st.markdown(
                f"**{idx+1}.** **{item['jp']}** {item['ko']}　"
                f"<span style='color:#64748b;font-size:0.8rem'>"
                f"오답 {item['wrong_count']} · 정답률 {acc}%</span>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="bar-bg"><div class="bar-fill-red" style="width:{width}%"></div></div>',
                unsafe_allow_html=True,
            )

    # Confusion pairs
    st.markdown("---")
    st.markdown("**잘 혼동하는 단어** (오답 선택 조합)")

    if not analytics["confusion_pairs"]:
        st.caption("혼동 패턴이 쌓이면 여기에 표시됩니다.")
    else:
        max_count = max(p["count"] for p in analytics["confusion_pairs"])
        for idx, pair in enumerate(analytics["confusion_pairs"]):
            width = max(10, round((pair["count"] / max(max_count, 1)) * 100))
            st.markdown(
                f"**{idx+1}.** 정답 **{pair['answer']['jp']}** ↔ 선택 **{pair['picked']['jp']}**"
                f"　<span style='color:#64748b;font-size:0.8rem'>{pair['count']}회</span>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<span style='color:#64748b;font-size:0.75rem'>"
                f"{pair['answer']['ko']} / {pair['picked']['ko']}</span>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="bar-bg"><div class="bar-fill-amber" style="width:{width}%"></div></div>',
                unsafe_allow_html=True,
            )
