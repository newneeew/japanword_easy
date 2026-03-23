"""Unit tests for db.py."""

import sys
import os
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import db


def test_init_and_get_vocab():
    """Test DB initialization and vocab retrieval."""
    # Use temp DB
    original_path = db.DB_PATH
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db.DB_PATH = f.name

    try:
        db.init_db()
        vocab = db.get_all_vocab()

        assert len(vocab) == 44, f"Expected 44 items, got {len(vocab)}"
        assert all(isinstance(v, dict) for v in vocab)
        assert all("id" in v and "jp" in v and "ko" in v and "pron" in v for v in vocab)

        # Check a specific item
        totemo = [v for v in vocab if v["jp"] == "とても"]
        assert len(totemo) == 1
        assert totemo[0]["ko"] == "매우"
        assert totemo[0]["pron"] == "토테모"

        # Test idempotency - calling init_db again should not duplicate
        db.init_db()
        vocab2 = db.get_all_vocab()
        assert len(vocab2) == 44
    finally:
        db.DB_PATH = original_path
        os.unlink(f.name)


if __name__ == "__main__":
    test_init_and_get_vocab()
    print("All DB tests passed!")
