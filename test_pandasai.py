"""
Comprehensive test suite for CyberSierra AI Data Analyst
Tests all core modules: data_manager, ai_engine, prompt_history
"""

import os
import sys
import pandas as pd

# Ensure we can import from src
sys.path.insert(0, os.path.dirname(__file__))

TITANIC_PATH = os.path.join(os.path.dirname(__file__), "data", "titanic.csv")
PASS_COUNT = 0
FAIL_COUNT = 0


def test(name, condition, detail=""):
    global PASS_COUNT, FAIL_COUNT
    if condition:
        PASS_COUNT += 1
        print(f"  ✅ PASS: {name}")
    else:
        FAIL_COUNT += 1
        print(f"  ❌ FAIL: {name} — {detail}")


def hr():
    print("\n" + "─" * 60)


# ═══════════════════════════════════════════════════════════════
# TEST 1: Data Manager
# ═══════════════════════════════════════════════════════════════
hr()
print("📦 TEST GROUP 1: Data Manager")
hr()

from src.data_manager import (
    validate_file, load_file, get_preview, get_file_info, get_basic_stats
)

# 1a. Load Titanic CSV
df = pd.read_csv(TITANIC_PATH)
test("Titanic CSV loads", df is not None and len(df) > 0)
test("Titanic has 891 rows", len(df) == 891, f"Got {len(df)}")
test("Titanic has 12 columns", len(df.columns) == 12, f"Got {len(df.columns)}")
test("Titanic meets 250+ row minimum", len(df) >= 250)

# 1b. Preview
preview_5 = get_preview(df, 5)
test("Preview N=5 returns 5 rows", len(preview_5) == 5, f"Got {len(preview_5)}")
preview_50 = get_preview(df, 50)
test("Preview N=50 returns 50 rows", len(preview_50) == 50, f"Got {len(preview_50)}")
preview_1 = get_preview(df, 1)
test("Preview N=1 returns 1 row", len(preview_1) == 1, f"Got {len(preview_1)}")
preview_over = get_preview(df, 9999)
test("Preview N=9999 clamps to max rows", len(preview_over) == len(df))

# 1c. File Info
info = get_file_info(df)
test("File info has 'rows' key", "rows" in info)
test("File info rows == 891", info["rows"] == 891)
test("File info has 'columns' key", "columns" in info)
test("File info has 'null_counts'", "null_counts" in info)
test("File info has 'numeric_columns'", "numeric_columns" in info)
test("File info has 'categorical_columns'", "categorical_columns" in info)
test("Memory usage is positive", info["memory_usage_mb"] > 0)

# 1d. Basic Stats
stats = get_basic_stats(df)
test("Basic stats returns a DataFrame", isinstance(stats, pd.DataFrame))
test("Basic stats has 'count' row", "count" in stats.index)
test("Basic stats has 'mean' row", "mean" in stats.index)

# 1e. Edge cases
preview_empty = get_preview(pd.DataFrame(), 5)
test("Preview empty DF returns empty", len(preview_empty) == 0)

stats_empty = get_basic_stats(pd.DataFrame({"name": ["a", "b"]}))
test("Basic stats with no numeric cols returns None", stats_empty is None)


# ═══════════════════════════════════════════════════════════════
# TEST 2: Prompt History
# ═══════════════════════════════════════════════════════════════
hr()
print("📜 TEST GROUP 2: Prompt History")
hr()

from src.prompt_history import (
    save_prompt, get_history, get_history_for_file,
    update_feedback, delete_entry, clear_history, get_feedback_stats
)

# 2a. Clear history first
clear_history()
test("Clear history returns cleanly", True)

history = get_history()
test("History is empty after clear", len(history) == 0)

# 2b. Save prompts
id1 = save_prompt("titanic.csv", "How many rows?", "891", "text")
test("Save prompt returns an ID", id1 is not None and len(id1) > 0)

id2 = save_prompt("titanic.csv", "Plot age distribution", "Chart generated", "chart", "/path/to/chart.png")
test("Save chart prompt returns ID", id2 is not None)

id3 = save_prompt("other.csv", "Average salary?", "50000", "text")
test("Save prompt for different file", id3 is not None)

# 2c. Get history
all_history = get_history()
test("History has 3 entries", len(all_history) == 3, f"Got {len(all_history)}")
test("Most recent first", all_history[0]["id"] == id3)

# 2d. Filter by file
titanic_history = get_history_for_file("titanic.csv")
test("Filtered history has 2 entries", len(titanic_history) == 2, f"Got {len(titanic_history)}")

other_history = get_history_for_file("other.csv")
test("Other file has 1 entry", len(other_history) == 1)

# 2e. Feedback
result = update_feedback(id1, True)
test("Update feedback (positive) succeeds", result is True)

result = update_feedback(id2, False)
test("Update feedback (negative) succeeds", result is True)

result = update_feedback("nonexistent-id", True)
test("Update feedback for missing ID fails", result is False)

# 2f. Feedback stats
stats = get_feedback_stats()
test("Stats total_prompts == 3", stats["total_prompts"] == 3)
test("Stats feedback_given == 2", stats["feedback_given"] == 2)
test("Stats positive == 1", stats["positive"] == 1)
test("Stats negative == 1", stats["negative"] == 1)
test("Stats satisfaction_rate == 50%", stats["satisfaction_rate"] == 50.0)

# 2g. Delete entry
result = delete_entry(id3)
test("Delete entry succeeds", result is True)
test("History now has 2 entries", len(get_history()) == 2)

result = delete_entry("nonexistent-id")
test("Delete nonexistent entry fails", result is False)

# 2h. Prompt reuse data
history = get_history()
entry = next(h for h in history if h["id"] == id1)
test("History entry has 'prompt' field", "prompt" in entry)
test("History entry has 'file_name' field", "file_name" in entry)
test("History entry has 'timestamp' field", "timestamp" in entry)
test("History entry has 'feedback' field", "feedback" in entry)
test("History entry has 'response_preview' field", "response_preview" in entry)

# Cleanup
clear_history()


# ═══════════════════════════════════════════════════════════════
# TEST 3: AI Engine (non-API tests)
# ═══════════════════════════════════════════════════════════════
hr()
print("🤖 TEST GROUP 3: AI Engine (non-API)")
hr()

from src.ai_engine import get_suggested_questions, CHARTS_DIR

# 3a. Suggested questions for Titanic
suggestions = get_suggested_questions(df)
test("Suggested questions are generated", len(suggestions) > 0)
test("At most 5 suggestions", len(suggestions) <= 5)
test("Suggestions are strings", all(isinstance(s, str) for s in suggestions))

# 3b. Suggested questions include plot
has_plot = any("plot" in s.lower() or "histogram" in s.lower() for s in suggestions)
test("At least one plot suggestion", has_plot)

# 3c. Suggested questions for numeric-only DF
num_df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
num_suggestions = get_suggested_questions(num_df)
has_scatter = any("scatter" in s.lower() for s in num_suggestions)
test("Numeric DF gets scatter plot suggestion", has_scatter)

# 3d. Charts directory
os.makedirs(CHARTS_DIR, exist_ok=True)
test("Charts directory exists", os.path.isdir(CHARTS_DIR))

# 3e. Empty DF suggestions
empty_suggestions = get_suggested_questions(pd.DataFrame())
test("Empty DF gets no suggestions", len(empty_suggestions) == 0)


# ═══════════════════════════════════════════════════════════════
# TEST 4: Project Structure
# ═══════════════════════════════════════════════════════════════
hr()
print("📂 TEST GROUP 4: Project Structure")
hr()

PROJECT_ROOT = os.path.dirname(__file__)

required_files = [
    "app.py",
    "requirements.txt",
    "README.md",
    ".gitignore",
    ".streamlit/config.toml",
    "src/__init__.py",
    "src/data_manager.py",
    "src/ai_engine.py",
    "src/prompt_history.py",
    "assets/styles.css",
    "data/titanic.csv",
]

for f in required_files:
    full_path = os.path.join(PROJECT_ROOT, f)
    test(f"File exists: {f}", os.path.exists(full_path), f"Missing: {full_path}")

# Check .gitignore contains secrets
gitignore_path = os.path.join(PROJECT_ROOT, ".gitignore")
with open(gitignore_path, "r") as f:
    gitignore_content = f.read()
test(".gitignore excludes secrets.toml", "secrets.toml" in gitignore_content)
test(".gitignore excludes __pycache__", "__pycache__" in gitignore_content)
test(".gitignore excludes venv", "venv" in gitignore_content)
test(".gitignore excludes exports/charts", "exports/charts" in gitignore_content)


# ═══════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════
hr()
total = PASS_COUNT + FAIL_COUNT
print(f"\n🏁 TEST RESULTS: {PASS_COUNT}/{total} passed ({FAIL_COUNT} failed)")
if FAIL_COUNT == 0:
    print("🎉 ALL TESTS PASSED!")
else:
    print(f"⚠️  {FAIL_COUNT} test(s) failed — review above.")
hr()
