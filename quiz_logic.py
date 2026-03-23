"""Stateless quiz logic: question selection, choice building, analytics."""

import random


def shuffle(arr):
    """Return a shuffled copy of the list."""
    copy = arr[:]
    random.shuffle(copy)
    return copy


def pick_next_question(vocab, recent_ids, wrong_queue):
    """Pick next question with wrong-answer priority and recency avoidance.

    Priority order:
    1. In wrong_queue AND not in recent_ids
    2. In wrong_queue (any)
    3. Not in recent_ids (random)
    4. Any random word
    """
    pool_by_id = {item["id"]: item for item in vocab}

    prioritized_wrong = [pool_by_id[wid] for wid in wrong_queue if wid in pool_by_id]
    fresh_wrong = [item for item in prioritized_wrong if item["id"] not in recent_ids]

    if fresh_wrong:
        return fresh_wrong[0]
    if prioritized_wrong:
        return prioritized_wrong[0]

    fresh_pool = [item for item in vocab if item["id"] not in recent_ids]
    if fresh_pool:
        return random.choice(fresh_pool)
    return random.choice(vocab)


def build_choices(answer, vocab_pool):
    """Build 3 shuffled choices: 1 correct + 2 random wrong."""
    wrong_candidates = [item for item in vocab_pool if item["id"] != answer["id"]]
    wrong_choices = shuffle(wrong_candidates)[:2]

    choices = [
        {**answer, "is_answer": True},
        *[{**item, "is_answer": False} for item in wrong_choices],
    ]
    return shuffle(choices)


def compute_analytics(vocab, attempt_stats, wrong_stats, confusion_stats):
    """Compute real-time analytics matching the original React app."""
    entries = []
    for item in vocab:
        attempts = attempt_stats.get(item["id"], 0)
        wrong_count = wrong_stats.get(item["id"], 0)
        accuracy = round(((attempts - wrong_count) / attempts) * 100) if attempts > 0 else None
        entries.append({
            **item,
            "attempts": attempts,
            "wrong_count": wrong_count,
            "accuracy": accuracy,
        })

    attempted = [e for e in entries if e["attempts"] > 0]

    # Difficult words: top 5 by wrong_count desc, accuracy asc, attempts desc
    difficult = sorted(
        [e for e in attempted if e["wrong_count"] > 0 and e["accuracy"] != 100],
        key=lambda e: (-e["wrong_count"], e["accuracy"] if e["accuracy"] is not None else 101, -e["attempts"]),
    )[:5]

    # Confusion pairs: top 5
    vocab_by_id = {item["id"]: item for item in vocab}
    pairs = []
    for key, count in confusion_stats.items():
        parts = key.split("|||")
        if len(parts) != 2:
            continue
        answer_id, picked_id = parts
        answer_item = vocab_by_id.get(answer_id)
        picked_item = vocab_by_id.get(picked_id)
        if answer_item and picked_item:
            pairs.append({"key": key, "count": count, "answer": answer_item, "picked": picked_item})
    pairs.sort(key=lambda p: -p["count"])
    pairs = pairs[:5]

    total_attempts = sum(e["attempts"] for e in attempted)
    total_wrong = sum(e["wrong_count"] for e in attempted)
    overall_accuracy = round(((total_attempts - total_wrong) / total_attempts) * 100) if total_attempts > 0 else None

    return {
        "attempted_count": len(attempted),
        "total_attempts": total_attempts,
        "overall_accuracy": overall_accuracy,
        "difficult_words": difficult,
        "confusion_pairs": pairs,
    }
