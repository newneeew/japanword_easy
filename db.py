"""Database layer: SQLite vocabulary storage and initialization."""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vocab.db")

SEED_DATA_DEFAULT = [
    ("とても", "매우", "토테모", "default"),
    ("まち", "거리", "마치", "default"),
    ("うた", "노래", "우타", "default"),
    ("あまり", "그다지 / 별로", "아마리", "default"),
    ("すきだ", "좋아하다", "스키다", "default"),
    ("きらいだ", "싫어하다", "키라이다", "default"),
    ("じょうずだ", "잘하다 / 능숙하다", "조오즈다", "default"),
    ("へただ", "잘 못하다 / 서투르다", "헤타다", "default"),
    ("べんりだ", "편리하다", "벤리다", "default"),
    ("ふべんだ", "불편하다", "후벤다", "default"),
    ("しずかだ", "조용하다", "시즈카다", "default"),
    ("にぎやかだ", "번화하다", "니기야카다", "default"),
    ("しんせつだ", "친절하다", "신세츠다", "default"),
    ("まじめだ", "성실하다", "마지메다", "default"),
    ("げんきだ", "건강하다", "겐키다", "default"),
    ("じょうぶだ", "튼튼하다", "죠오부다", "default"),
    ("きれいだ", "깨끗하다 / 예쁘다", "키레이다", "default"),
    ("ハンサムだ", "핸섬하다", "한사무다", "default"),
    ("ゆうめいだ", "유명하다", "유우메이다", "default"),
    ("かんたんだ", "간단하다", "칸탄다", "default"),
    ("ひまだ", "한가하다", "히마다", "default"),
    ("りっぱだ", "훌륭하다", "립파다", "default"),
    ("しんせんだ", "신선하다", "신센다", "default"),
    ("たいへんだ", "힘들다", "타이헨다", "default"),
    ("あさ7じにおきる", "아침 7시에 일어나다", "아사 시치지 니 오키루", "default"),
    ("ごはんをたべる", "밥을 먹다", "고항오 타베루", "default"),
    ("ちかてつにのる", "지하철을 타다", "치카테츠 니 노루", "default"),
    ("がっこうへいく", "학교에 가다", "각코오 에 이쿠", "default"),
    ("べんきょうをする", "공부를 하다", "벤쿄오 오 스루", "default"),
    ("せんせいとはなす", "선생님과 이야기하다", "센세이 토 하나스", "default"),
    ("としょかんにくる", "도서관에 오다", "토쇼칸 니 쿠루", "default"),
    ("れぽーとをかく", "리포트를 쓰다", "레포오토 오 카쿠", "default"),
    ("ほんをよむ", "책을 읽다", "혼 오 요무", "default"),
    ("でんわをかける", "전화를 걸다", "덴와 오 카케루", "default"),
    ("こいびとにあう", "애인을 만나다", "코이비토 니 아우", "default"),
    ("かばんをかう", "가방을 사다", "카반 오 카우", "default"),
    ("ともだちとあそぶ", "친구와 놀다", "토모다치 토 아소부", "default"),
    ("おさけをのむ", "술을 마시다", "오사케 오 노무", "default"),
    ("おんがくをきく", "음악을 듣다", "온가쿠 오 키쿠", "default"),
    ("うたをうたう", "노래를 부르다", "우타 오 우타우", "default"),
    ("うちへかえる", "집에 돌아오다", "우치 에 카에루", "default"),
    ("てれびをみる", "텔레비전을 보다", "테레비 오 미루", "default"),
    ("おふろにはいる", "목욕을 하다", "오후로 니 하이루", "default"),
    ("よるおそくねる", "밤 늦게 자다", "요루 오소쿠 네루", "default"),
]

SEED_DATA_CH12 = [
    ("こんしゅうまつ", "이번 주말", "콘슈우마츠", "ch_12"),
    ("しぬ", "죽다", "시누", "ch_12"),
    ("〜を", "~을/를", "오", "ch_12"),
    ("あそぶ", "놀다", "아소부", "ch_12"),
    ("する", "하다", "스루", "ch_12"),
    ("のむ", "마시다", "노무", "ch_12"),
    ("〜にあう", "~을/를 만나다", "니 아우", "ch_12"),
    ("とる", "찍다", "토루", "ch_12"),
    ("それから", "그리고", "소레카라", "ch_12"),
    ("かえる", "돌아가다", "카에루", "ch_12"),
    ("〜に", "~에", "니", "ch_12"),
    ("はいる", "들어가다", "하이루", "ch_12"),
    ("いく", "가다", "이쿠", "ch_12"),
    ("つくる", "만들다", "츠쿠루", "ch_12"),
    ("よく", "자주", "요쿠", "ch_12"),
    ("きる", "자르다", "키루", "ch_12"),
    ("らいしゅう", "다음 주", "라이슈우", "ch_12"),
    ("はしる", "달리다", "하시루", "ch_12"),
    ("〜で", "~에서", "데", "ch_12"),
    ("しる", "알다", "시루", "ch_12"),
    ("かく", "쓰다", "카쿠", "ch_12"),
    ("いる", "필요하다", "이루", "ch_12"),
    ("およぐ", "수영하다", "오요구", "ch_12"),
    ("みる", "보다", "미루", "ch_12"),
    ("はなす", "말하다", "하나스", "ch_12"),
    ("おきる", "일어나다", "오키루", "ch_12"),
    ("まつ", "기다리다", "마츠", "ch_12"),
    ("ねる", "자다", "네루", "ch_12"),
    ("たべる", "먹다", "타베루", "ch_12"),
    ("〜にのる", "~을/를 타다", "니 노루", "ch_12"),
    ("くる", "오다", "쿠루", "ch_12"),
    ("にほんりょうり", "일본요리", "니혼료오리", "ch_12"),
]

SEED_DATA_CH15 = [
    ("もしもし", "여보세요", "모시모시", "ch_15"),
    ("どうやって", "어떻게", "도오얏테", "ch_15"),
    ("〜ごうせん", "~호선", "고오센", "ch_15"),
    ("〜め", "~째", "메", "ch_15"),
    ("おりる", "내리다", "오리루", "ch_15"),
    ("ゆっくり", "천천히", "윳쿠리", "ch_15"),
    ("たのしみです", "기대됩니다", "타노시미데스", "ch_15"),
    ("つくる", "만들다", "츠쿠루", "ch_15"),
    ("みせる", "보여주다", "미세루", "ch_15"),
    ("まいにち", "매일", "마이니치", "ch_15"),
    ("おどる", "춤추다", "오도루", "ch_15"),
    ("ひく", "연주하다", "히쿠", "ch_15"),
    ("いそぐ", "서두르다", "이소구", "ch_15"),
    ("かす", "빌려주다", "카스", "ch_15"),
    ("とる", "잡다", "토루", "ch_15"),
    ("やすむ", "쉬다", "야스무", "ch_15"),
    ("あう", "만나다", "아우", "ch_15"),
    ("まつ", "기다리다", "마츠", "ch_15"),
    ("のる", "타다", "노루", "ch_15"),
    ("しぬ", "죽다", "시누", "ch_15"),
    ("あそぶ", "놀다", "아소부", "ch_15"),
    ("のむ", "마시다", "노무", "ch_15"),
    ("きく", "듣다", "키쿠", "ch_15"),
    ("およぐ", "헤엄치다", "오요구", "ch_15"),
    ("はなす", "이야기하다", "하나스", "ch_15"),
    ("いく", "가다", "이쿠", "ch_15"),
    ("みる", "보다", "미루", "ch_15"),
    ("たべる", "먹다", "타베루", "ch_15"),
    ("する", "하다", "스루", "ch_15"),
    ("くる", "오다", "쿠루", "ch_15"),
    ("かえる", "돌아가다", "카에루", "ch_15"),
    ("はいる", "들어가다", "하이루", "ch_15"),
    ("あって", "만나서", "앗테", "ch_15"),
    ("まって", "기다려서", "맛테", "ch_15"),
    ("のって", "타서", "놋테", "ch_15"),
    ("しんで", "죽어서", "신데", "ch_15"),
    ("あそんで", "놀아서", "아손데", "ch_15"),
    ("のんで", "마셔서", "논데", "ch_15"),
    ("きいて", "들어서", "키이테", "ch_15"),
    ("およいで", "헤엄쳐서", "오요이데", "ch_15"),
    ("はなして", "이야기해서", "하나시테", "ch_15"),
    ("いって", "가서", "잇테", "ch_15"),
    ("みて", "봐서", "미테", "ch_15"),
    ("たべて", "먹어서", "타베테", "ch_15"),
    ("して", "해서", "시테", "ch_15"),
    ("きて", "와서", "키테", "ch_15"),
    ("かえって", "돌아가서", "카엣테", "ch_15"),
    ("はいって", "들어가서", "하잇테", "ch_15"),
]


def _get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create vocabulary table and seed data if not exists."""
    conn = _get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS vocabulary (
            id      TEXT PRIMARY KEY,
            jp      TEXT NOT NULL,
            ko      TEXT NOT NULL,
            pron    TEXT NOT NULL DEFAULT '',
            chapter TEXT NOT NULL DEFAULT 'default'
        )
        """
    )
    # Add chapter column if upgrading from old schema
    try:
        conn.execute("ALTER TABLE vocabulary ADD COLUMN chapter TEXT NOT NULL DEFAULT 'default'")
    except sqlite3.OperationalError:
        pass  # column already exists

    for jp, ko, pron, chapter in SEED_DATA_DEFAULT + SEED_DATA_CH12 + SEED_DATA_CH15:
        vid = f"{jp}__{ko}"
        conn.execute(
            "INSERT OR IGNORE INTO vocabulary (id, jp, ko, pron, chapter) VALUES (?, ?, ?, ?, ?)",
            (vid, jp, ko, pron, chapter),
        )
    conn.commit()
    conn.close()


def get_all_vocab(chapter=None):
    """Return vocabulary items as list of dicts, optionally filtered by chapter."""
    conn = _get_connection()
    if chapter:
        rows = conn.execute(
            "SELECT id, jp, ko, pron, chapter FROM vocabulary WHERE chapter = ?",
            (chapter,),
        ).fetchall()
    else:
        rows = conn.execute("SELECT id, jp, ko, pron, chapter FROM vocabulary").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_chapters():
    """Return list of distinct chapter names."""
    conn = _get_connection()
    rows = conn.execute("SELECT DISTINCT chapter FROM vocabulary ORDER BY chapter").fetchall()
    conn.close()
    return [row["chapter"] for row in rows]
