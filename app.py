import streamlit as st
from utils.pdf_parser import extract_text_from_pdf, extract_text_from_txt
from utils.ai_engine import explain_medical_report

st.set_page_config(
    page_title="MedRepoAI",
    page_icon="🏥",
    layout="centered"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Syne:wght@600;700;800&display=swap');

*, html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background-color: #0D0F14;
}

header[data-testid="stHeader"] { background: transparent; }
footer { display: none; }

/* ── Hero ── */
.hero {
    background: linear-gradient(145deg, #111827 0%, #0f172a 60%, #0D0F14 100%);
    border: 1px solid #1e293b;
    border-radius: 20px;
    padding: 52px 48px 44px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 260px; height: 260px;
    background: radial-gradient(circle, rgba(56,189,248,0.08) 0%, transparent 70%);
    border-radius: 50%;
}
.hero::after {
    content: '';
    position: absolute;
    bottom: -40px; left: -40px;
    width: 180px; height: 180px;
    background: radial-gradient(circle, rgba(99,102,241,0.07) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-badge {
    display: inline-block;
    background: rgba(56,189,248,0.1);
    border: 1px solid rgba(56,189,248,0.25);
    color: #38bdf8;
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 5px 14px;
    border-radius: 20px;
    margin-bottom: 20px;
}
.hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: 2.8rem;
    font-weight: 800;
    color: #f1f5f9;
    margin: 0 0 6px 0;
    letter-spacing: -1px;
    line-height: 1.1;
}
.hero h1 span {
    color: #38bdf8;
}
.hero p {
    font-size: 0.95rem;
    color: #64748b;
    margin: 12px 0 0;
    font-weight: 400;
    line-height: 1.7;
    max-width: 520px;
}

/* ── Disclaimer ── */
.disclaimer {
    background: rgba(234,179,8,0.06);
    border: 1px solid rgba(234,179,8,0.2);
    border-radius: 10px;
    padding: 13px 18px;
    margin-bottom: 24px;
    font-size: 0.82rem;
    color: #a16207;
    color: #fbbf24;
    line-height: 1.6;
}
.disclaimer strong { color: #fde68a; }

/* ── Input section ── */
.input-card {
    background: #111827;
    border: 1px solid #1e293b;
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 16px;
}
.input-label {
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #475569;
    margin-bottom: 10px;
}

/* ── Streamlit widget overrides ── */
div[data-testid="stFileUploader"] {
    background: #0D0F14 !important;
    border: 1.5px dashed #1e293b !important;
    border-radius: 10px !important;
    padding: 8px !important;
}
div[data-testid="stFileUploader"] label {
    color: #94a3b8 !important;
}
.stTextArea textarea {
    background: #0D0F14 !important;
    border: 1.5px solid #1e293b !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
}
.stTextArea textarea::placeholder { color: #334155 !important; }
.stTextArea textarea:focus {
    border-color: #38bdf8 !important;
    box-shadow: 0 0 0 3px rgba(56,189,248,0.08) !important;
}
.stButton > button {
    background: linear-gradient(135deg, #0ea5e9, #6366f1) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.65rem 2rem !important;
    letter-spacing: 0.3px;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.88 !important; }

/* ── Results header ── */
.results-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 36px 0 20px;
}
.results-header h2 {
    font-family: 'Syne', sans-serif;
    font-size: 1.5rem;
    font-weight: 700;
    color: #f1f5f9;
    margin: 0;
}
.results-divider {
    flex: 1;
    height: 1px;
    background: #1e293b;
}

/* ── Summary card ── */
.summary-card {
    background: #111827;
    border: 1px solid #1e293b;
    border-radius: 14px;
    padding: 26px 30px;
    margin-bottom: 12px;
}
.summary-card .card-label {
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #38bdf8;
    margin-bottom: 10px;
}
.summary-card p {
    color: #94a3b8;
    line-height: 1.8;
    font-size: 0.925rem;
    margin: 0;
}
.summary-card .overall {
    margin-top: 14px;
    padding-top: 14px;
    border-top: 1px solid #1e293b;
    color: #7dd3fc;
    font-size: 0.875rem;
    font-style: italic;
}

/* ── Urgency pill ── */
.urgency-wrap { margin: 16px 0 28px; }
.pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 7px 16px;
    border-radius: 8px;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.3px;
}
.pill-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    flex-shrink: 0;
}
.pill-routine {
    background: rgba(34,197,94,0.1);
    border: 1px solid rgba(34,197,94,0.25);
    color: #4ade80;
}
.pill-routine .pill-dot { background: #4ade80; }
.pill-soon {
    background: rgba(234,179,8,0.1);
    border: 1px solid rgba(234,179,8,0.25);
    color: #facc15;
}
.pill-soon .pill-dot { background: #facc15; }
.pill-urgent {
    background: rgba(239,68,68,0.1);
    border: 1px solid rgba(239,68,68,0.3);
    color: #f87171;
}
.pill-urgent .pill-dot { background: #f87171; }

/* ── Finding card ── */
.finding-card {
    background: #111827;
    border: 1px solid #1e293b;
    border-radius: 14px;
    padding: 24px 28px;
    margin-bottom: 10px;
    transition: border-color 0.2s;
}
.finding-card:hover { border-color: #334155; }
.finding-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 14px;
}
.finding-name {
    font-size: 1rem;
    font-weight: 600;
    color: #e2e8f0;
    margin-bottom: 3px;
}
.finding-meta {
    font-size: 0.8rem;
    color: #475569;
}
.badge-normal {
    background: rgba(34,197,94,0.1);
    border: 1px solid rgba(34,197,94,0.25);
    color: #4ade80;
    padding: 3px 11px;
    border-radius: 20px;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    white-space: nowrap;
}
.badge-borderline {
    background: rgba(234,179,8,0.1);
    border: 1px solid rgba(234,179,8,0.25);
    color: #facc15;
    padding: 3px 11px;
    border-radius: 20px;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    white-space: nowrap;
}
.badge-abnormal {
    background: rgba(239,68,68,0.1);
    border: 1px solid rgba(239,68,68,0.3);
    color: #f87171;
    padding: 3px 11px;
    border-radius: 20px;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    white-space: nowrap;
}
.range-strip {
    display: flex;
    gap: 20px;
    background: #0D0F14;
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 18px;
    border: 1px solid #1e293b;
}
.range-col label {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #334155;
    display: block;
    margin-bottom: 3px;
}
.range-col span {
    font-size: 0.875rem;
    font-weight: 500;
    color: #94a3b8;
}
.detail-block { margin-bottom: 14px; }
.detail-block .dlabel {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #475569;
    margin-bottom: 5px;
}
.detail-block .dtext {
    font-size: 0.875rem;
    color: #94a3b8;
    line-height: 1.75;
}
.tip-strip {
    background: rgba(14,165,233,0.07);
    border-left: 3px solid #0ea5e9;
    border-radius: 0 8px 8px 0;
    padding: 10px 14px;
    font-size: 0.85rem;
    color: #7dd3fc;
    line-height: 1.65;
    margin-top: 12px;
}
.action-strip {
    background: rgba(34,197,94,0.07);
    border-left: 3px solid #22c55e;
    border-radius: 0 8px 8px 0;
    padding: 10px 14px;
    font-size: 0.85rem;
    color: #86efac;
    line-height: 1.65;
    margin-top: 8px;
}

/* ── Nutrition & Advice cards ── */
.nutrition-card {
    background: #111827;
    border: 1px solid #1e293b;
    border-radius: 14px;
    padding: 24px 28px;
    margin-bottom: 10px;
}
.nutrition-card .card-label {
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #a78bfa;
    margin-bottom: 10px;
}
.nutrition-card p {
    color: #94a3b8;
    line-height: 1.8;
    font-size: 0.9rem;
    margin: 0;
}
.advice-card {
    background: linear-gradient(135deg, #0f172a, #111827);
    border: 1px solid #1e3a5f;
    border-radius: 14px;
    padding: 26px 30px;
    margin-bottom: 10px;
}
.advice-card .card-label {
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #38bdf8;
    margin-bottom: 10px;
}
.advice-card p {
    color: #94a3b8;
    line-height: 1.8;
    font-size: 0.9rem;
    margin: 0;
}

/* ── Footer ── */
.page-footer {
    text-align: center;
    font-size: 0.75rem;
    color: #334155;
    padding: 32px 0 20px;
    line-height: 1.7;
}
</style>
""", unsafe_allow_html=True)

# ── Hero Section ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge">AI-Powered Health Literacy</div>
    <h1>MedRepo<span>AI</span></h1>
    <p>Upload your medical report and receive a clear, structured explanation of every finding —
    what it means, how it affects your body, and what to do next.</p>
</div>
""", unsafe_allow_html=True)

# ── Disclaimer ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="disclaimer">
    <strong>Important:</strong> MedRepoAI is an educational tool only. It does not provide
    medical diagnoses or replace professional medical advice. Always consult a qualified
    healthcare provider for clinical interpretation and treatment decisions.
</div>
""", unsafe_allow_html=True)

# ── Upload Section ────────────────────────────────────────────────────────────
st.markdown('<div class="input-card">', unsafe_allow_html=True)
st.markdown('<div class="input-label">Upload Report (PDF or TXT)</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    "upload", type=["pdf", "txt"], label_visibility="collapsed"
)
st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)
st.markdown('<div class="input-label">Or paste report text</div>', unsafe_allow_html=True)
pasted_text = st.text_area(
    "paste", height=130,
    placeholder="Paste your lab results, CBC, lipid panel, thyroid report, etc...",
    label_visibility="collapsed"
)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)

if st.button("Analyze Report", type="primary", use_container_width=True):

    report_text = ""
    if uploaded_file:
        with st.spinner("Extracting report content..."):
            if uploaded_file.type == "application/pdf":
                report_text = extract_text_from_pdf(uploaded_file)
            else:
                report_text = extract_text_from_txt(uploaded_file)
    elif pasted_text.strip():
        report_text = pasted_text.strip()
    else:
        st.error("Please upload a file or paste your report text to continue.")
        st.stop()

    if not report_text:
        st.error("Could not extract text from the file. Please try pasting the text directly.")
        st.stop()

    with st.spinner("Analyzing your report..."):
        try:
            result = explain_medical_report(report_text)
        except Exception as e:
            st.error(f"Analysis failed: {str(e)}")
            st.stop()

    # ── Report Overview ───────────────────────────────────────────────────────
    st.markdown("""
    <div class="results-header">
        <h2>Report Analysis</h2>
        <div class="results-divider"></div>
    </div>
    """, unsafe_allow_html=True)

    overall = result.get("overall_health_message", "")
    overall_html = f'<div class="overall">{overall}</div>' if overall else ""
    st.markdown(f"""
    <div class="summary-card">
        <div class="card-label">Overview</div>
        <p>{result.get("summary", "")}</p>
        {overall_html}
    </div>
    """, unsafe_allow_html=True)

    # Urgency
    urgency = result.get("urgency", "routine")
    pills = {
        "routine": '<div class="pill pill-routine"><div class="pill-dot"></div>Routine follow-up recommended</div>',
        "soon":    '<div class="pill pill-soon"><div class="pill-dot"></div>Recommended to see a doctor soon</div>',
        "urgent":  '<div class="pill pill-urgent"><div class="pill-dot"></div>Please seek medical attention promptly</div>',
    }
    st.markdown(f'<div class="urgency-wrap">{pills.get(urgency, pills["routine"])}</div>', unsafe_allow_html=True)

    # ── Test Results ──────────────────────────────────────────────────────────
    st.markdown("""
    <div class="results-header">
        <h2>Test Results</h2>
        <div class="results-divider"></div>
    </div>
    """, unsafe_allow_html=True)

    for finding in result.get("findings", []):
        status = finding.get("status", "normal")
        badge_html = f'<span class="badge-{status}">{status.upper()}</span>'
        tip = finding.get("lifestyle_tip", "")
        action = finding.get("action_needed", "")
        tip_html   = f'<div class="tip-strip">{tip}</div>' if tip else ""
        action_html = f'<div class="action-strip">{action}</div>' if action else ""

        st.markdown(f"""
        <div class="finding-card">
            <div class="finding-top">
                <div>
                    <div class="finding-name">{finding.get("test_name", "")}</div>
                    <div class="finding-meta">Result: {finding.get("value", "N/A")}</div>
                </div>
                {badge_html}
            </div>
            <div class="range-strip">
                <div class="range-col">
                    <label>Your Result</label>
                    <span>{finding.get("value", "N/A")}</span>
                </div>
                <div class="range-col">
                    <label>Normal Range</label>
                    <span>{finding.get("normal_range", "N/A")}</span>
                </div>
            </div>
            <div class="detail-block">
                <div class="dlabel">What this measures</div>
                <div class="dtext">{finding.get("what_it_measures", "")}</div>
            </div>
            <div class="detail-block">
                <div class="dlabel">What your result means</div>
                <div class="dtext">{finding.get("what_your_result_means", "")}</div>
            </div>
            <div class="detail-block">
                <div class="dlabel">Effect on your body</div>
                <div class="dtext">{finding.get("body_impact", "")}</div>
            </div>
            {tip_html}
            {action_html}
        </div>
        """, unsafe_allow_html=True)

    # ── Nutrition ─────────────────────────────────────────────────────────────
    nutrition = result.get("nutrition_summary", "")
    if nutrition:
        st.markdown("""
        <div class="results-header">
            <h2>Nutrition & Lifestyle</h2>
            <div class="results-divider"></div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="nutrition-card">
            <div class="card-label">Summary</div>
            <p>{nutrition}</p>
        </div>
        """, unsafe_allow_html=True)

    # ── Doctor Advice ─────────────────────────────────────────────────────────
    st.markdown("""
    <div class="results-header">
        <h2>Consultation Advice</h2>
        <div class="results-divider"></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="advice-card">
        <div class="card-label">Should you see a doctor?</div>
        <p>{result.get("doctor_advice", "Please consult your doctor to discuss these results.")}</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="page-footer">
        {result.get("disclaimer", "This report explanation is for educational purposes only and does not constitute a medical diagnosis.")}
    </div>
    """, unsafe_allow_html=True)