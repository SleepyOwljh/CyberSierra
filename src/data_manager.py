"""
Data Manager Module
Handles file upload, validation, parsing, and preview for CSV/XLS files.

Security considerations:
- File type validation (whitelist approach)
- File size limits enforced via Streamlit config (50MB)
- Content validation to prevent malformed data
"""

import pandas as pd
import streamlit as st
from typing import Optional, Dict, Tuple


# Allowed file extensions (whitelist approach for security)
ALLOWED_EXTENSIONS = {".csv", ".xls", ".xlsx"}
MAX_FILE_SIZE_MB = 200


def validate_file(uploaded_file) -> Tuple[bool, str]:
    """
    Validate an uploaded file for type and basic integrity.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if uploaded_file is None:
        return False, "No file provided."

    # Check file extension
    file_name = uploaded_file.name.lower()
    file_ext = "." + file_name.rsplit(".", 1)[-1] if "." in file_name else ""

    if file_ext not in ALLOWED_EXTENSIONS:
        return False, (
            f"Unsupported file type: `{file_ext}`. "
            f"Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Check file size (Streamlit also enforces this via config)
    file_size_mb = uploaded_file.size / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        return False, (
            f"File too large: {file_size_mb:.1f}MB. "
            f"Maximum allowed: {MAX_FILE_SIZE_MB}MB."
        )

    return True, ""


def load_file(uploaded_file) -> Tuple[Optional[pd.DataFrame], str]:
    """
    Parse an uploaded file into a pandas DataFrame.
    
    Returns:
        Tuple of (DataFrame or None, error_message)
    """
    # Validate first
    is_valid, error_msg = validate_file(uploaded_file)
    if not is_valid:
        return None, error_msg

    try:
        file_name = uploaded_file.name.lower()

        if file_name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif file_name.endswith((".xls", ".xlsx")):
            df = pd.read_excel(uploaded_file, engine="openpyxl")
        else:
            return None, "Unsupported file format."

        # Basic content validation
        if df.empty:
            return None, "The uploaded file is empty."

        if len(df.columns) == 0:
            return None, "The file has no columns."

        return df, ""

    except pd.errors.EmptyDataError:
        return None, "The file contains no data."
    except pd.errors.ParserError as e:
        return None, f"Failed to parse the file: {str(e)}"
    except Exception as e:
        return None, f"Error reading file: {str(e)}"


def get_preview(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Return the top N rows of a DataFrame."""
    n = max(1, min(n, len(df)))  # Clamp to valid range
    return df.head(n)


def get_file_info(df: pd.DataFrame) -> Dict:
    """
    Get summary information about a DataFrame.
    
    Returns a dict with shape, column info, null counts, and data types.
    """
    info = {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "column_names": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "null_counts": {col: int(count) for col, count in df.isnull().sum().items()},
        "null_percentage": {
            col: round(count / len(df) * 100, 1)
            for col, count in df.isnull().sum().items()
        },
        "memory_usage_mb": round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2),
        "numeric_columns": list(df.select_dtypes(include=["number"]).columns),
        "categorical_columns": list(df.select_dtypes(include=["object", "category"]).columns),
    }
    return info


def get_basic_stats(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """Get basic descriptive statistics for numeric columns."""
    numeric_df = df.select_dtypes(include=["number"])
    if numeric_df.empty:
        return None
    return numeric_df.describe().round(2)


def store_uploaded_file(uploaded_file, df: pd.DataFrame):
    """Store an uploaded file's DataFrame in session state."""
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = {}

    st.session_state.uploaded_files[uploaded_file.name] = {
        "dataframe": df,
        "file_name": uploaded_file.name,
        "file_size": uploaded_file.size,
        "row_count": len(df),
        "col_count": len(df.columns),
    }


def get_uploaded_files() -> Dict:
    """Get all uploaded files from session state."""
    return st.session_state.get("uploaded_files", {})


def remove_uploaded_file(file_name: str):
    """Remove a file from session state."""
    if "uploaded_files" in st.session_state:
        st.session_state.uploaded_files.pop(file_name, None)
