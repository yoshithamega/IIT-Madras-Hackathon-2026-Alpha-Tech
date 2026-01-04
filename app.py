import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="GenAI Data Quality Scoring",
    page_icon="📊",
    layout="wide"
)

# ================= GLOBAL CSS =================
st.markdown("""
<style>
/* App background */
.stApp {
    background-color: #f4f6f9;
    color: #111111;
}

/* Card container */
.card {
    background-color: #ffffff;
    padding: 28px;
    border-radius: 14px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.08);
    margin-bottom: 24px;
    color: #111111;
}

/* Typography */
.title { font-size: 30px; font-weight: 800; color: #111111; }
.subtitle { font-size: 16px; color: #333333; }
.section { font-size: 20px; font-weight: 700; color: #111111; margin-bottom: 12px; }
.helper { font-size: 14px; color: #444444; }

/* Alerts */
.stAlert > div {
    color: #111111 !important;
    font-weight: 500;
}

/* Metrics (remove blue look) */
div[data-testid="metric-container"] {
    background-color: #ffffff;
    border: 1px solid #e5e7eb;
    padding: 16px;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}
div[data-testid="metric-container"] label {
    color: #374151 !important;
    font-weight: 600;
}
div[data-testid="metric-container"] div {
    color: #111111 !important;
}

/* Text input */
input[type="text"] {
    background-color: #ffffff !important;
    color: #111111 !important;
    border: 1px solid #d1d5db !important;
}
input::placeholder {
    color: #6b7280 !important;
}

/* Selection */
::selection {
    background: #e5e7eb;
    color: #111111;
}
</style>
""", unsafe_allow_html=True)

# ================= HERO =================
st.markdown("""
<div class="card">
    <div class="title">GenAI Agent for Universal Data Quality Scoring</div>
    <div class="subtitle">
        Enterprise‑grade, explainable data quality analysis for payment systems
    </div>
</div>
""", unsafe_allow_html=True)

# ================= UPLOAD =================
st.markdown("""
<div class="card">
    <div class="section">📁 Upload Enterprise Dataset</div>
    <div class="helper">Supported format: CSV</div>
</div>
""", unsafe_allow_html=True)

file = st.file_uploader("Upload CSV file", type=["csv"])

if not file:
    st.info("⬆️ Upload a dataset to begin analysis.")
    st.stop()

# ================= SIDEBAR =================
st.sidebar.markdown("## 📂 Navigation")
page = st.sidebar.radio(
    "",
    ["Dashboard", "Dataset", "Quality Analysis", "AI Co‑Pilot"]
)

# ================= READ DATA =================
df = pd.read_csv(file)

# ================= DATA QUALITY METRICS =================
completeness = (1 - df.isnull().mean().mean()) * 100
uniqueness = (1 - df.duplicated().sum() / len(df)) * 100

valid_count, total_count = 0, 0
for col in df.columns:
    total_count += len(df)
    if df[col].dtype in ["int64", "float64"]:
        valid_count += (df[col] >= 0).sum()
    else:
        valid_count += df[col].astype(str).str.len().gt(0).sum()

validity = (valid_count / total_count) * 100
consistency = sum(df[col].map(type).nunique() == 1 for col in df.columns)
consistency = (consistency / len(df.columns)) * 100

dqs = round(
    0.3 * completeness +
    0.25 * validity +
    0.25 * uniqueness +
    0.2 * consistency, 2
)

# ================= DQ GAUGE =================
def dq_gauge(score):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"suffix": "%"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#0d6efd"},
            "steps": [
                {"range": [0, 50], "color": "#f8d7da"},
                {"range": [50, 75], "color": "#fff3cd"},
                {"range": [75, 100], "color": "#d1e7dd"}
            ]
        }
    ))
    fig.update_layout(height=320)
    return fig

# ================= DASHBOARD =================
if page == "Dashboard":
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown('<div class="card"><div class="section">Universal Data Quality Score</div></div>', unsafe_allow_html=True)
        st.plotly_chart(dq_gauge(dqs), use_container_width=True)
        st.caption(f"Analyzed {len(df)} records")

        st.markdown('<div class="card"><div class="section">Dimension Scores</div></div>', unsafe_allow_html=True)
        st.bar_chart({
            "Completeness": completeness,
            "Validity": validity,
            "Uniqueness": uniqueness,
            "Consistency": consistency
        })

    with col2:
        st.markdown('<div class="card"><div class="section">Explainable Insights</div></div>', unsafe_allow_html=True)

        if completeness < 80: st.warning("Missing values detected.")
        if uniqueness < 90: st.warning("Duplicate records reduce uniqueness.")
        if validity < 85: st.warning("Validation rule violations found.")
        if consistency < 80: st.warning("Schema inconsistencies detected.")

        if dqs >= 80:
            st.success("Overall data quality is good.")

# ================= DATASET =================
if page == "Dataset":
    st.markdown('<div class="card"><div class="section">Dataset Preview</div></div>', unsafe_allow_html=True)
    st.dataframe(df)

# ================= QUALITY ANALYSIS (FIXED) =================
if page == "Quality Analysis":
    st.markdown('<div class="card"><div class="section">Detailed Quality Metrics</div></div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Completeness", f"{round(completeness,2)}%")
    c2.metric("Validity", f"{round(validity,2)}%")
    c3.metric("Uniqueness", f"{round(uniqueness,2)}%")
    c4.metric("Consistency", f"{round(consistency,2)}%")

# ================= AI CO‑PILOT (FIXED) =================
if page == "AI Co‑Pilot":
    st.markdown('<div class="card"><div class="section">AI Co‑Pilot (Explainable Insights)</div></div>', unsafe_allow_html=True)

    question = st.text_input(
        "Ask about data quality",
        placeholder="e.g. How is the quality of this dataset?"
    )

    if question:
        st.markdown(f"""
<div class="card">
<b>Question:</b> {question}<br><br>

<b>Overall Data Quality Score:</b> {dqs}%<br><br>

<b>Key Observations</b>
<ul>
<li>Completeness: {completeness:.2f}%</li>
<li>Validity: {validity:.2f}%</li>
<li>Uniqueness: {uniqueness:.2f}%</li>
<li>Consistency: {consistency:.2f}%</li>
</ul>

<b>Recommended Actions</b>
<ul>
<li>Handle missing values</li>
<li>Remove duplicate records</li>
<li>Standardize data formats</li>
<li>Apply validation rules during ingestion</li>
</ul>
</div>
""", unsafe_allow_html=True)
