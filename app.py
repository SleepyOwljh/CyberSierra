"""
CyberSierra AI Data Analysis App
================================
An AI-powered application for analyzing CSV/XLS data using natural language.

Built with Streamlit + PandasAI + OpenAI GPT-4o

Features:
- Upload multiple CSV/XLS files
- Preview top N rows with interactive controls
- Ask natural language questions about your data
- Generate charts and graphs automatically
- Prompt history with reuse and feedback

Author: CyberSierra Coding Challenge
"""

import os
import streamlit as st
import pandas as pd

# Local modules
from src.data_manager import (
    load_file,
    get_preview,
    get_file_info,
    get_basic_stats,
    store_uploaded_file,
    get_uploaded_files,
    remove_uploaded_file,
)
from src.ai_engine import create_smart_df, ask_question, get_suggested_questions
from src.prompt_history import (
    save_prompt,
    get_history,
    get_history_for_file,
    update_feedback,
    delete_entry,
    clear_history,
    get_feedback_stats,
)


# ── Page Configuration ──────────────────────────────────────────────
st.set_page_config(
    page_title="CyberSierra AI Data Analyst",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── Load Custom CSS ─────────────────────────────────────────────────
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "assets", "styles.css")
    if os.path.exists(css_path):
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


load_css()


# ── Initialize Session State ───────────────────────────────────────
def init_session_state():
    defaults = {
        "uploaded_files": {},
        "chat_history": [],
        "active_file": None,
        "smart_dfs": {},
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()


# ── Header ──────────────────────────────────────────────────────────
st.markdown('<h1 class="app-header">🔬 CyberSierra AI Data Analyst</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="app-subtitle">Upload your data, ask questions in plain English, and get instant insights with charts.</p>',
    unsafe_allow_html=True,
)


# ── Sidebar: File Upload & Controls ────────────────────────────────
with st.sidebar:
    st.markdown("### 📁 Data Files")

    # Data privacy notice
    st.markdown(
        '<div class="data-notice">'
        "⚠️ <strong>Privacy Notice:</strong> Your data is sent to OpenAI's API for analysis. "
        "Do not upload sensitive or confidential data."
        "</div>",
        unsafe_allow_html=True,
    )

    # File uploader (supports multiple files)
    uploaded_files = st.file_uploader(
        "Upload CSV or Excel files",
        type=["csv", "xls", "xlsx"],
        accept_multiple_files=True,
        help="Drag and drop files here. Max 50MB per file.",
    )

    # Process uploaded files
    if uploaded_files:
        for uploaded_file in uploaded_files:
            if uploaded_file.name not in st.session_state.uploaded_files:
                df, error = load_file(uploaded_file)
                if df is not None:
                    store_uploaded_file(uploaded_file, df)
                    st.success(f"✅ Loaded **{uploaded_file.name}** ({len(df)} rows)")
                else:
                    st.error(f"❌ {uploaded_file.name}: {error}")

    st.markdown('<div class="styled-divider"></div>', unsafe_allow_html=True)

    # File selector
    file_names = list(st.session_state.uploaded_files.keys())

    if file_names:
        st.markdown("### 📋 Active File")

        selected_file = st.selectbox(
            "Select a file to analyze",
            file_names,
            index=0,
            key="file_selector",
        )
        st.session_state.active_file = selected_file

        # Show file info
        file_data = st.session_state.uploaded_files[selected_file]
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Rows", f"{file_data['row_count']:,}")
        with col2:
            st.metric("Columns", file_data["col_count"])

        # Remove file button
        if st.button("🗑️ Remove File", key="remove_file"):
            remove_uploaded_file(selected_file)
            if selected_file in st.session_state.smart_dfs:
                del st.session_state.smart_dfs[selected_file]
            st.rerun()

        st.markdown('<div class="styled-divider"></div>', unsafe_allow_html=True)

        # Top-N rows control
        st.markdown("### 🔢 Preview Settings")
        n_rows = st.slider(
            "Number of rows to display",
            min_value=1,
            max_value=min(100, file_data["row_count"]),
            value=min(10, file_data["row_count"]),
            key="n_rows_slider",
        )
    else:
        st.info("👆 Upload a CSV or Excel file to get started.")
        n_rows = 10

    # Feedback stats
    st.markdown('<div class="styled-divider"></div>', unsafe_allow_html=True)
    st.markdown("### 📊 Session Stats")
    stats = get_feedback_stats()
    if stats["total_prompts"] > 0:
        st.metric("Total Queries", stats["total_prompts"])
        if stats["feedback_given"] > 0:
            st.metric("Satisfaction", f"{stats['satisfaction_rate']}%")
            st.caption(f"👍 {stats['positive']} · 👎 {stats['negative']}")
    else:
        st.caption("No queries yet. Start asking questions!")


# ── Main Content Area ───────────────────────────────────────────────
if not file_names:
    # Empty state — show welcome
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            """
            <div style="text-align: center; padding: 60px 20px;">
                <div style="font-size: 4rem; margin-bottom: 20px;">📊</div>
                <h2 style="color: #6C63FF; margin-bottom: 10px;">Welcome to CyberSierra AI</h2>
                <p style="color: #8B8FA3; font-size: 1.1rem; max-width: 500px; margin: 0 auto;">
                    Upload a CSV or Excel file using the sidebar to start analyzing your data 
                    with the power of AI. Ask questions, generate charts, and get instant insights.
                </p>
                <div style="margin-top: 30px; padding: 20px; background: #1A1D29; border-radius: 12px; border: 1px solid rgba(108,99,255,0.2);">
                    <p style="color: #6C63FF; font-weight: 600; margin-bottom: 10px;">💡 Try it with the Titanic dataset</p>
                    <p style="color: #8B8FA3; font-size: 0.9rem;">
                        A sample <code>titanic.csv</code> is included in the <code>data/</code> folder.
                    </p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    # Active file is available — show tabs
    active_file = st.session_state.active_file
    active_data = st.session_state.uploaded_files[active_file]
    df = active_data["dataframe"]

    # Main tabs
    tab_preview, tab_chat, tab_history = st.tabs(
        ["📋 Data Preview", "💬 AI Chat", "📜 Prompt History"]
    )

    # ── Tab 1: Data Preview ─────────────────────────────────────────
    with tab_preview:
        st.markdown(f"### Previewing: `{active_file}`")
        st.markdown(f"Showing top **{n_rows}** of **{active_data['row_count']:,}** rows")

        # Display preview
        preview_df = get_preview(df, n_rows)
        st.dataframe(preview_df, use_container_width=True, height=400)

        # Data summary section
        st.markdown('<div class="styled-divider"></div>', unsafe_allow_html=True)
        st.markdown("### 📊 Data Summary")

        file_info = get_file_info(df)

        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(
                f'<div class="metric-card">'
                f'<p class="metric-value">{file_info["rows"]:,}</p>'
                f'<p class="metric-label">Total Rows</p>'
                f"</div>",
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                f'<div class="metric-card">'
                f'<p class="metric-value">{file_info["columns"]}</p>'
                f'<p class="metric-label">Columns</p>'
                f"</div>",
                unsafe_allow_html=True,
            )
        with col3:
            total_nulls = sum(file_info["null_counts"].values())
            st.markdown(
                f'<div class="metric-card">'
                f'<p class="metric-value">{total_nulls:,}</p>'
                f'<p class="metric-label">Missing Values</p>'
                f"</div>",
                unsafe_allow_html=True,
            )
        with col4:
            st.markdown(
                f'<div class="metric-card">'
                f'<p class="metric-value">{file_info["memory_usage_mb"]}</p>'
                f'<p class="metric-label">Memory (MB)</p>'
                f"</div>",
                unsafe_allow_html=True,
            )

        # Column details
        st.markdown("#### Column Details")
        col_details = pd.DataFrame(
            {
                "Column": file_info["column_names"],
                "Type": [file_info["dtypes"][c] for c in file_info["column_names"]],
                "Nulls": [file_info["null_counts"][c] for c in file_info["column_names"]],
                "Null %": [
                    f"{file_info['null_percentage'][c]}%"
                    for c in file_info["column_names"]
                ],
            }
        )
        st.dataframe(col_details, use_container_width=True, hide_index=True)

        # Descriptive statistics
        basic_stats = get_basic_stats(df)
        if basic_stats is not None:
            st.markdown("#### Descriptive Statistics")
            st.dataframe(basic_stats, use_container_width=True)

    # ── Tab 2: AI Chat ──────────────────────────────────────────────
    with tab_chat:
        st.markdown(f"### 💬 Ask about `{active_file}`")

        # Suggested questions
        suggestions = get_suggested_questions(df)
        if suggestions:
            st.markdown("**💡 Suggested questions:**")
            suggestion_cols = st.columns(min(len(suggestions), 3))
            for i, suggestion in enumerate(suggestions):
                col_idx = i % 3
                with suggestion_cols[col_idx]:
                    if st.button(
                        f"📌 {suggestion}",
                        key=f"suggest_{i}",
                        use_container_width=True,
                    ):
                        st.session_state.pending_question = suggestion

        st.markdown('<div class="styled-divider"></div>', unsafe_allow_html=True)

        # Chat history display
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.chat_history:
                if msg["file"] != active_file:
                    continue
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
                    if msg.get("chart_path") and os.path.exists(msg["chart_path"]):
                        st.image(msg["chart_path"], use_container_width=True)
                    # Feedback buttons for assistant messages
                    if msg["role"] == "assistant" and msg.get("entry_id"):
                        col_fb1, col_fb2, col_fb3 = st.columns([1, 1, 8])
                        with col_fb1:
                            if st.button("👍", key=f"fb_up_{msg['entry_id']}"):
                                update_feedback(msg["entry_id"], True)
                                st.toast("Thanks for the feedback! 👍")
                        with col_fb2:
                            if st.button("👎", key=f"fb_down_{msg['entry_id']}"):
                                update_feedback(msg["entry_id"], False)
                                st.toast("Thanks for the feedback! 👎")

        # Chat input
        pending = st.session_state.pop("pending_question", None)
        user_input = st.chat_input(
            "Ask a question about your data...",
            key="chat_input",
        )

        question = pending or user_input

        if question:
            # Add user message to chat
            st.session_state.chat_history.append(
                {"role": "user", "content": question, "file": active_file}
            )

            with st.chat_message("user"):
                st.markdown(question)

            # Get or create SmartDataframe
            with st.chat_message("assistant"):
                with st.spinner("🤔 Analyzing your data..."):
                    try:
                        if active_file not in st.session_state.smart_dfs:
                            st.session_state.smart_dfs[active_file] = create_smart_df(df)

                        smart_df = st.session_state.smart_dfs[active_file]
                        response_text, chart_path, response_type = ask_question(
                            smart_df, question
                        )

                        # Display response
                        st.markdown(response_text)
                        if chart_path and os.path.exists(chart_path):
                            st.image(chart_path, use_container_width=True)

                        # Save to prompt history
                        entry_id = save_prompt(
                            file_name=active_file,
                            prompt=question,
                            response_text=response_text,
                            response_type=response_type,
                            chart_path=chart_path,
                        )

                        # Add assistant message to chat
                        st.session_state.chat_history.append(
                            {
                                "role": "assistant",
                                "content": response_text,
                                "chart_path": chart_path,
                                "file": active_file,
                                "entry_id": entry_id,
                            }
                        )

                        # Feedback buttons
                        col_fb1, col_fb2, col_fb3 = st.columns([1, 1, 8])
                        with col_fb1:
                            if st.button("👍", key=f"fb_up_{entry_id}"):
                                update_feedback(entry_id, True)
                                st.toast("Thanks! 👍")
                        with col_fb2:
                            if st.button("👎", key=f"fb_down_{entry_id}"):
                                update_feedback(entry_id, False)
                                st.toast("Thanks! 👎")

                    except ValueError as e:
                        st.error(str(e))
                    except Exception as e:
                        st.error(f"❌ An unexpected error occurred: {str(e)}")

    # ── Tab 3: Prompt History ───────────────────────────────────────
    with tab_history:
        st.markdown("### 📜 Prompt History")

        # Filter options
        col_filter1, col_filter2, col_filter3 = st.columns([2, 2, 1])
        with col_filter1:
            history_filter = st.selectbox(
                "Filter by file",
                ["All Files"] + file_names,
                key="history_filter",
            )
        with col_filter2:
            feedback_filter = st.selectbox(
                "Filter by feedback",
                ["All", "👍 Positive", "👎 Negative", "No feedback"],
                key="feedback_filter",
            )
        with col_filter3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️ Clear All", key="clear_history"):
                count = clear_history()
                st.toast(f"Cleared {count} entries")
                st.rerun()

        # Load history
        if history_filter == "All Files":
            history = get_history()
        else:
            history = get_history_for_file(history_filter)

        # Apply feedback filter
        if feedback_filter == "👍 Positive":
            history = [h for h in history if h.get("feedback") is True]
        elif feedback_filter == "👎 Negative":
            history = [h for h in history if h.get("feedback") is False]
        elif feedback_filter == "No feedback":
            history = [h for h in history if h.get("feedback") is None]

        if not history:
            st.info("No prompt history yet. Start chatting in the AI Chat tab!")
        else:
            st.caption(f"Showing {len(history)} entries")

            for entry in history:
                with st.container():
                    # Format timestamp
                    try:
                        ts = entry["timestamp"][:16].replace("T", " ")
                    except (KeyError, TypeError):
                        ts = "Unknown"

                    # Feedback indicator
                    feedback_icon = ""
                    if entry.get("feedback") is True:
                        feedback_icon = " 👍"
                    elif entry.get("feedback") is False:
                        feedback_icon = " 👎"

                    # Type badge
                    type_colors = {
                        "text": "🔤",
                        "chart": "📊",
                        "dataframe": "📋",
                        "error": "❌",
                    }
                    type_icon = type_colors.get(entry.get("response_type", "text"), "🔤")

                    st.markdown(
                        f"**{type_icon} {entry.get('prompt', 'N/A')}**{feedback_icon}"
                    )

                    col_info, col_actions = st.columns([3, 1])
                    with col_info:
                        st.caption(
                            f"📁 {entry.get('file_name', 'Unknown')} · 🕐 {ts}"
                        )
                        with st.expander("View response"):
                            st.text(entry.get("response_preview", "No preview available"))
                            if entry.get("chart_path") and os.path.exists(
                                entry["chart_path"]
                            ):
                                st.image(entry["chart_path"], width=400)

                    with col_actions:
                        col_a1, col_a2 = st.columns(2)
                        with col_a1:
                            # Reuse button
                            if st.button(
                                "🔄",
                                key=f"reuse_{entry['id']}",
                                help="Re-run this prompt",
                            ):
                                st.session_state.pending_question = entry["prompt"]
                                # Switch to the correct file if available
                                if entry.get("file_name") in file_names:
                                    st.session_state.active_file = entry["file_name"]
                                st.rerun()
                        with col_a2:
                            # Delete button
                            if st.button(
                                "🗑️",
                                key=f"delete_{entry['id']}",
                                help="Delete this entry",
                            ):
                                delete_entry(entry["id"])
                                st.rerun()

                    st.markdown("---")


# ── Footer ──────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="text-align: center; padding: 20px; margin-top: 40px; color: #4B5066; font-size: 0.8rem;">
        <p>CyberSierra AI Data Analyst · Powered by 
        <span style="color: #6C63FF;">PandasAI</span> + 
        <span style="color: #4ECDC4;">OpenAI GPT-4o</span> + 
        <span style="color: #44CF6C;">Streamlit</span></p>
        <p style="margin-top: 4px; font-size: 0.75rem;">
            ⚠️ AI responses may be inaccurate. Always verify results with your data.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
