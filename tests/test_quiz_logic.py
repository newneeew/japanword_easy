"""Unit tests for quiz_logic.py."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from quiz_logic import build_choices, compute_analytics, pick_next_question

SAMPLE_VOCAB = [
    {"id": "a__가", "jp": "a", "ko": "가", "pron": "에이"},
    {"id": "b__나", "jp": "b", "ko": "나", "pron": "비"},
    {"id": "c__다", "jp": "c", "ko": "다", "pron": "씨"},
    {"id": "d__라", "jp": "d", "ko": "라", "pron": "디"},
    {"id": "e__마", "jp": "e", "ko": "마", "pron": "이"},
]


def test_build_choices_returns_three():
    answer = SAMPLE_VOCAB[0]
    choices = build_choices(answer, SAMPLE_VOCAB)
    assert len(choices) == 3


def test_build_choices_contains_answer():
    answer = SAMPLE_VOCAB[0]
    choices = build_choices(answer, SAMPLE_VOCAB)
    correct = [c for c in choices if c["is_answer"]]
    assert len(correct) == 1
    assert correct[0]["id"] == answer["id"]


def test_build_choices_no_duplicates():
    answer = SAMPLE_VOCAB[0]
    choices = build_choices(answer, SAMPLE_VOCAB)
    ids = [c["id"] for c in choices]
    assert len(ids) == len(set(ids))


def test_pick_next_prioritizes_wrong_queue():
    wrong_queue = ["c__다"]
    result = pick_next_question(SAMPLE_VOCAB, [], wrong_queue)
    assert result["id"] == "c__다"


def test_pick_next_avoids_recent():
    recent = ["a__가", "b__나", "c__다", "d__라"]
    result = pick_next_question(SAMPLE_VOCAB, recent, [])
    assert result["id"] == "e__마"


def test_pick_next_wrong_avoids_recent():
    wrong_queue = ["a__가", "c__다"]
    recent = ["a__가"]
    result = pick_next_question(SAMPLE_VOCAB, recent, wrong_queue)
    assert result["id"] == "c__다"


def test_pick_next_falls_back_when_all_recent():
    recent = [v["id"] for v in SAMPLE_VOCAB]
    result = pick_next_question(SAMPLE_VOCAB, recent, [])
    assert result["id"] in [v["id"] for v in SAMPLE_VOCAB]


def test_compute_analytics_empty():
    result = compute_analytics(SAMPLE_VOCAB, {}, {}, {})
    assert result["attempted_count"] == 0
    assert result["total_attempts"] == 0
    assert result["overall_accuracy"] is None
    assert result["difficult_words"] == []
    assert result["confusion_pairs"] == []


def test_compute_analytics_with_data():
    attempts = {"a__가": 5, "b__나": 3}
    wrongs = {"a__가": 2, "b__나": 1}
    confusion = {"a__가|||b__나": 2}

    result = compute_analytics(SAMPLE_VOCAB, attempts, wrongs, confusion)
    assert result["attempted_count"] == 2
    assert result["total_attempts"] == 8
    assert result["overall_accuracy"] == 62  # round((8-3)/8*100) = 62
    assert len(result["difficult_words"]) == 2
    assert result["difficult_words"][0]["id"] == "a__가"
    assert len(result["confusion_pairs"]) == 1
    assert result["confusion_pairs"][0]["count"] == 2


def test_compute_analytics_100_percent_excluded():
    """Words with 100% accuracy should NOT appear in difficult_words."""
    attempts = {"a__가": 5, "b__나": 3}
    wrongs = {"a__가": 0, "b__나": 1}

    result = compute_analytics(SAMPLE_VOCAB, attempts, wrongs, {})
    # a has 100% accuracy, should be excluded
    difficult_ids = [w["id"] for w in result["difficult_words"]]
    assert "a__가" not in difficult_ids
    assert "b__나" in difficult_ids


if __name__ == "__main__":
    test_build_choices_returns_three()
    test_build_choices_contains_answer()
    test_build_choices_no_duplicates()
    test_pick_next_prioritizes_wrong_queue()
    test_pick_next_avoids_recent()
    test_pick_next_wrong_avoids_recent()
    test_pick_next_falls_back_when_all_recent()
    test_compute_analytics_empty()
    test_compute_analytics_with_data()
    test_compute_analytics_100_percent_excluded()
    print("All tests passed!")
