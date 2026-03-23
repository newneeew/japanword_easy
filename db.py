"""Database layer: SQLite vocabulary storage and initialization."""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vocab.db")

SEED_DATA = [
    ("とても", "매우", "토테모"),
    ("まち", "거리", "마치"),
    ("うた", "노래", "우타"),
    ("あまり", "그다지 / 별로", "아마리"),
    ("すきだ", "좋아하다", "스키다"),
    ("きらいだ", "싫어하다", "키라이다"),
    ("じょうずだ", "잘하다 / 능숙하다", "조오즈다"),
    ("へただ", "잘 못하다 / 서투르다", "헤타다"),
    ("べんりだ", "편리하다", "벤리다"),
    ("ふべんだ", "불편하다", "후벤다"),
    ("しずかだ", "조용하다", "시즈카다"),
    ("にぎやかだ", "번화하다", "니기야카다"),
    ("しんせつだ", "친절하다", "신세츠다"),
    ("まじめだ", "성실하다", "마지메다"),
    ("げんきだ", "건강하다", "겐키다"),
    ("じょうぶだ", "튼튼하다", "죠오부다"),
    ("きれいだ", "깨끗하다 / 예쁘다", "키레이다"),
    ("ハンサムだ", "핸섬하다", "한사무다"),
    ("ゆうめいだ", "유명하다", "유우메이다"),
    ("かんたんだ", "간단하다", "칸탄다"),
    ("ひまだ", "한가하다", "히마다"),
    ("りっぱだ", "훌륭하다", "립파다"),
    ("しんせんだ", "신선하다", "신센다"),
    ("たいへんだ", "힘들다", "타이헨다"),
    ("あさ7じにおきる", "아침 7시에 일어나다", "아사 시치지 니 오키루"),
    ("ごはんをたべる", "밥을 먹다", "고항오 타베루"),
    ("ちかてつにのる", "지하철을 타다", "치카테츠 니 노루"),
    ("がっこうへいく", "학교에 가다", "각코오 에 이쿠"),
    ("べんきょうをする", "공부를 하다", "벤쿄오 오 스루"),
    ("せんせいとはなす", "선생님과 이야기하다", "센세이 토 하나스"),
    ("としょかんにくる", "도서관에 오다", "토쇼칸 니 쿠루"),
    ("れぽーとをかく", "리포트를 쓰다", "레포오토 오 카쿠"),
    ("ほんをよむ", "책을 읽다", "혼 오 요무"),
    ("でんわをかける", "전화를 걸다", "덴와 오 카케루"),
    ("こいびとにあう", "애인을 만나다", "코이비토 니 아우"),
    ("かばんをかう", "가방을 사다", "카반 오 카우"),
    ("ともだちとあそぶ", "친구와 놀다", "토모다치 토 아소부"),
    ("おさけをのむ", "술을 마시다", "오사케 오 노무"),
    ("おんがくをきく", "음악을 듣다", "온가쿠 오 키쿠"),
    ("うたをうたう", "노래를 부르다", "우타 오 우타우"),
    ("うちへかえる", "집에 돌아오다", "우치 에 카에루"),
    ("てれびをみる", "텔레비전을 보다", "테레비 오 미루"),
    ("おふろにはいる", "목욕을 하다", "오후로 니 하이루"),
    ("よるおそくねる", "밤 늦게 자다", "요루 오소쿠 네루"),
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
            id   TEXT PRIMARY KEY,
            jp   TEXT NOT NULL,
            ko   TEXT NOT NULL,
            pron TEXT NOT NULL DEFAULT ''
        )
        """
    )
    for jp, ko, pron in SEED_DATA:
        vid = f"{jp}__{ko}"
        conn.execute(
            "INSERT OR IGNORE INTO vocabulary (id, jp, ko, pron) VALUES (?, ?, ?, ?)",
            (vid, jp, ko, pron),
        )
    conn.commit()
    conn.close()


def get_all_vocab():
    """Return all vocabulary items as list of dicts."""
    conn = _get_connection()
    rows = conn.execute("SELECT id, jp, ko, pron FROM vocabulary").fetchall()
    conn.close()
    return [dict(row) for row in rows]
