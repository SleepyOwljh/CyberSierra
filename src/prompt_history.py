"""
Prompt History Module
Manages persistence of user prompts, responses, and feedback.

Storage: JSON file (prompt_history.json) — simple and portable.
Each entry contains: id, timestamp, file_name, prompt, response preview,
response type, and optional feedback.
"""

import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Optional


HISTORY_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "prompt_history.json"
)


def _load_history() -> List[Dict]:
    """Load prompt history from JSON file."""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def _save_history(history: List[Dict]):
    """Save prompt history to JSON file."""
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False, default=str)
    except IOError as e:
        print(f"Warning: Could not save prompt history: {e}")


def save_prompt(
    file_name: str,
    prompt: str,
    response_text: str,
    response_type: str,
    chart_path: Optional[str] = None,
) -> str:
    """
    Save a prompt and its response to history.
    
    Args:
        file_name: Name of the file being queried
        prompt: The user's question
        response_text: The AI response text
        response_type: One of 'text', 'dataframe', 'chart', 'error'
        chart_path: Path to generated chart image (if any)
    
    Returns:
        The generated entry ID
    """
    history = _load_history()

    entry_id = str(uuid.uuid4())[:8]

    # Truncate response preview to avoid bloating the JSON
    response_preview = response_text[:500] if response_text else ""

    entry = {
        "id": entry_id,
        "timestamp": datetime.now().isoformat(),
        "file_name": file_name,
        "prompt": prompt,
        "response_preview": response_preview,
        "response_type": response_type,
        "chart_path": chart_path,
        "feedback": None,  # None = no feedback, True = useful, False = not useful
    }

    history.insert(0, entry)  # Most recent first

    # Keep only the last 100 entries to prevent unbounded growth
    history = history[:100]

    _save_history(history)
    return entry_id


def get_history(limit: int = 50) -> List[Dict]:
    """Get prompt history, most recent first."""
    history = _load_history()
    return history[:limit]


def get_history_for_file(file_name: str, limit: int = 50) -> List[Dict]:
    """Get prompt history filtered by file name."""
    history = _load_history()
    filtered = [h for h in history if h.get("file_name") == file_name]
    return filtered[:limit]


def update_feedback(entry_id: str, is_useful: bool) -> bool:
    """
    Update the feedback for a prompt history entry.
    
    Args:
        entry_id: The entry ID to update
        is_useful: True if the answer was useful, False otherwise
    
    Returns:
        True if the entry was found and updated, False otherwise
    """
    history = _load_history()

    for entry in history:
        if entry.get("id") == entry_id:
            entry["feedback"] = is_useful
            _save_history(history)
            return True

    return False


def delete_entry(entry_id: str) -> bool:
    """Delete a prompt history entry by ID."""
    history = _load_history()
    original_len = len(history)
    history = [h for h in history if h.get("id") != entry_id]

    if len(history) < original_len:
        _save_history(history)
        return True
    return False


def clear_history() -> int:
    """Clear all prompt history. Returns the number of entries deleted."""
    history = _load_history()
    count = len(history)
    _save_history([])
    return count


def get_feedback_stats() -> Dict:
    """Get aggregated feedback statistics."""
    history = _load_history()

    total = len(history)
    with_feedback = [h for h in history if h.get("feedback") is not None]
    positive = sum(1 for h in with_feedback if h.get("feedback") is True)
    negative = sum(1 for h in with_feedback if h.get("feedback") is False)

    return {
        "total_prompts": total,
        "feedback_given": len(with_feedback),
        "positive": positive,
        "negative": negative,
        "satisfaction_rate": (
            round(positive / len(with_feedback) * 100, 1) if with_feedback else 0
        ),
    }
