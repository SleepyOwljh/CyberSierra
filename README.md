# 🔬 CyberSierra AI Data Analyst

An AI-powered web application for analyzing CSV and Excel data using natural language. Upload your files, ask questions in plain English, and get instant insights — including charts and graphs.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│                  Streamlit UI                    │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │  Upload   │  │ AI Chat  │  │Prompt History │  │
│  │ & Preview │  │Interface │  │  & Feedback   │  │
│  └────┬─────┘  └────┬─────┘  └───────┬───────┘  │
│       │              │                │          │
│  ┌────▼──────────────▼────────────────▼───────┐  │
│  │            Session State Manager           │  │
│  └────┬──────────────┬────────────────┬───────┘  │
└───────┼──────────────┼────────────────┼──────────┘
        │              │                │
   ┌────▼─────┐  ┌────▼──────┐  ┌─────▼────────┐
   │  Data     │  │ AI Engine │  │   Prompt     │
   │  Manager  │  │ (PandasAI)│  │   History    │
   │           │  │           │  │  (JSON)      │
   └───────────┘  └─────┬─────┘  └──────────────┘
                        │
                  ┌─────▼─────┐
                  │  OpenAI   │
                  │  GPT-4o   │
                  └───────────┘
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Streamlit | Interactive web UI with chat, tables, charts |
| **AI Engine** | PandasAI | Natural language → pandas operations + visualizations |
| **LLM** | OpenAI GPT-3.5-turbo | Language understanding and code generation |
| **Data** | pandas + openpyxl | CSV/XLS parsing and manipulation |
| **Charts** | matplotlib + seaborn | Graph and chart generation |
| **Storage** | JSON file | Prompt history persistence |

### Why These Choices?

- **Streamlit** over React/FastAPI: Pure Python stack, rapid development, built-in data widgets. Mobile compatibility not required.
- **PandasAI** over Microsoft LIDA: PandasAI handles both data querying AND chart generation. LIDA is primarily for visualization only.
- **JSON** over database: Simple, portable, no extra infrastructure. Suitable for local-only use case.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- OpenAI API key (with GPT-3.5-turbo access)

### Setup

1. **Clone and navigate to the project**
   ```bash
   cd CyberSierra
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your OpenAI API key**
   
   Create `.streamlit/secrets.toml` (if it doesn't exist):
   ```toml
   OPENAI_API_KEY = "your-actual-api-key-here"
   ```
   
   > ⚠️ This file is in `.gitignore` and will NOT be committed.

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

6. **Open in browser** → `http://localhost:8501`

## 📋 Features

### ✅ Core Features
- **Multi-file upload**: Upload 1 or more CSV/XLS files simultaneously
- **Data preview**: Display top N rows (N is adjustable via slider)
- **File selection**: Switch between uploaded files easily
- **AI-powered Q&A**: Ask natural language questions about your data
- **Chart generation**: Request graphs/charts via natural language prompts
- **Prompt history**: Full history with timestamps, file associations, and response previews
- **Prompt reuse**: Re-run any previous prompt with one click

### ⭐ Bonus Features
- **Feedback system**: 👍/👎 on every AI response with satisfaction tracking
- **Data summary**: Automatic column details, null analysis, and descriptive statistics
- **Suggested questions**: Auto-generated starter questions based on your data structure
- **History filtering**: Filter by file or feedback status

## 🔒 Security Considerations

1. **API Key Protection**
   - Stored in `.streamlit/secrets.toml` (gitignored)
   - Never hardcoded in source code
   - Accessed at runtime via `st.secrets`

2. **Code Execution Risk**
   - PandasAI generates and executes Python code from LLM responses
   - This is an inherent design trade-off for natural language data analysis
   - PandasAI includes built-in sandboxing mechanisms
   - Recommendation: Run in a controlled environment

3. **File Upload Security**
   - Whitelist approach: only `.csv`, `.xls`, `.xlsx` accepted
   - File size limit: 50MB (enforced at Streamlit level)
   - Content validation on parse

4. **Data Privacy**
   - ⚠️ Uploaded data is sent to OpenAI's API for processing
   - No server-side persistence — data exists only in session memory
   - Users are notified via the UI before uploading
   - Prompt history is stored locally only

## 📁 Project Structure

```
CyberSierra/
├── app.py                  # Main application entry point
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── .gitignore              # Git exclusions
├── .streamlit/
│   ├── config.toml         # Theme and settings
│   └── secrets.toml        # API key (NOT in git)
├── src/
│   ├── __init__.py
│   ├── data_manager.py     # File handling and validation
│   ├── ai_engine.py        # PandasAI + OpenAI integration
│   └── prompt_history.py   # History persistence and feedback
├── assets/
│   └── styles.css          # Custom CSS styling
├── data/
│   └── titanic.csv         # Sample dataset (891 rows)
└── exports/
    └── charts/             # Auto-saved chart images
```

## 🧪 Testing Guide

### Sample Questions for the Titanic Dataset
1. "How many passengers survived?"
2. "What is the average age of passengers?"
3. "Plot the survival rate by passenger class"
4. "Show a histogram of passenger ages"
5. "What is the correlation between fare and survival?"
6. "Plot a bar chart of embarkation ports"

## 📝 Known Limitations

- PandasAI may occasionally generate incorrect code for complex queries
- Chart styling depends on the LLM's interpretation of the prompt
- Very large files (>10K rows) may slow down AI queries due to token limits
- Response quality depends on the underlying OpenAI model
