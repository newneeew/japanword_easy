"""Unit tests for db.py."""

import sys
import os
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import db


def test_init_and_get_vocab():
    """Test DB initialization and vocab retrieval."""
    original_path = db.DB_PATH
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db.DB_PATH = f.name

    try:
        db.init_db()

        # Total: 44 default + 32 ch_12 = 76
        vocab_all = db.get_all_vocab()
        assert len(vocab_all) == 76, f"Expected 76 items, got {len(vocab_all)}"

        # Filter by chapter
        vocab_default = db.get_all_vocab(chapter="default")
        assert len(vocab_default) == 44, f"Expected 44 default items, got {len(vocab_default)}"

        vocab_ch12 = db.get_all_vocab(chapter="ch_12")
        assert len(vocab_ch12) == 32, f"Expected 32 ch_12 items, got {len(vocab_ch12)}"

        # Check chapter field
        assert all(v["chapter"] == "ch_12" for v in vocab_ch12)

        # Check a specific ch_12 item
        suru = [v for v in vocab_ch12 if v["jp"] == "する"]
        assert len(suru) == 1
        assert suru[0]["ko"] == "하다"

        # Chapters list
        chapters = db.get_chapters()
        assert "default" in chapters
        assert "ch_12" in chapters

        # Idempotency
        db.init_db()
        assert len(db.get_all_vocab()) == 76
    finally:
        db.DB_PATH = original_path
        os.unlink(f.name)


if __name__ == "__main__":
    test_init_and_get_vocab()
    print("All DB tests passed!")
