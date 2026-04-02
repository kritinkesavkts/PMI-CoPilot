"""
Agentic AI PMI Copilot — Streamlit Frontend
A multi-step workflow UI for post-merger integration analysis.
"""

import json
import time
import streamlit as st
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.agents.ingestion_agent import ingestion_agent
from app.agents.parsing_agent import parsing_agent
from app.agents.extraction_agent import extraction_agent
from app.agents.gap_agent import gap_agent
from app.agents.risk_agent import risk_agent
from app.agents.synergy_agent import synergy_agent
from app.agents.recommendation_agent import recommendation_agent
from app.agents.review_agent import review_agent
from app.agents.report_agent import report_agent
from app.services.storage_service import storage_service
from app.schemas.findings import AnalysisFindings
from app.schemas.review import ReviewStatus

# ─────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="PMI Copilot",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Custom Styling
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=JetBrains+Mono:wght@400;500&display=swap');

    .stApp {
        font-family: 'DM Sans', sans-serif;
    }
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.25rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #64748b;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #f8fafc, #f1f5f9);
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.25rem;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #0f172a;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .severity-high {
        background-color: #fef2f2;
        border-left: 4px solid #ef4444;
        padding: 0.75rem 1rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 0.75rem;
    }
    .severity-medium {
        background-color: #fffbeb;
        border-left: 4px solid #f59e0b;
        padding: 0.75rem 1rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 0.75rem;
    }
    .severity-low {
        background-color: #f0fdf4;
        border-left: 4px solid #22c55e;
        padding: 0.75rem 1rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 0.75rem;
    }
    .pipeline-step {
        display: inline-block;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 0.25rem;
    }
    .step-active { background: #dbeafe; color: #1d4ed8; }
    .step-done { background: #dcfce7; color: #166534; }
    .step-pending { background: #f1f5f9; color: #94a3b8; }
    div[data-testid="stExpander"] {
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Session State Init
# ─────────────────────────────────────────────
def init_state():
    defaults = {
        "session_id": None,
        "step": "upload",           # upload | analyzing | review | export
        "uploaded_files": [],
        "findings": None,
        "report": None,
        "pipeline_log": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def log_step(msg: str):
    st.session_state.pipeline_log.append(f"⏱ {time.strftime('%H:%M:%S')} — {msg}")


def severity_badge(sev: str) -> str:
    colors = {"high": "🔴", "medium": "🟡", "low": "🟢"}
    return f"{colors.get(sev, '⚪')} **{sev.upper()}**"


def render_severity_card(title: str, severity: str, reason: str, evidence: str = ""):
    st.markdown(f"""<div class="severity-{severity}">
        <strong>{title}</strong><br>
        <span style="font-size:0.85rem; color: #475569;">{reason}</span>
        {"<br><em style='font-size:0.8rem; color:#94a3b8;'>Evidence: " + evidence + "</em>" if evidence else ""}
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔗 PMI Copilot")
    st.caption("AI-Powered Post-Merger Integration")
    st.divider()

    # Pipeline status
    steps_config = [
        ("upload", "Upload"),
        ("analyzing", "Analyze"),
        ("review", "Review"),
        ("export", "Export"),
    ]
    current = st.session_state.step
    step_order = [s[0] for s in steps_config]
    current_idx = step_order.index(current) if current in step_order else 0

    for i, (key, label) in enumerate(steps_config):
        if i < current_idx:
            st.markdown(f"✅ ~~{label}~~")
        elif i == current_idx:
            st.markdown(f"▶️ **{label}**")
        else:
            st.markdown(f"⬜ {label}")

    st.divider()

    if st.session_state.session_id:
        st.caption(f"Session: `{st.session_state.session_id}`")

    if st.session_state.pipeline_log:
        with st.expander("Pipeline Log"):
            for entry in st.session_state.pipeline_log[-15:]:
                st.text(entry)

    st.divider()
    if st.button("🔄 New Session", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        init_state()
        st.rerun()


# ─────────────────────────────────────────────
# STEP 1: Upload
# ─────────────────────────────────────────────
if st.session_state.step == "upload":
    st.markdown('<div class="main-header">📄 Upload Integration Documents</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Upload documents from both the acquirer and target company. Supported: PDF, DOCX, TXT, CSV.</div>', unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Drop files here",
        type=["pdf", "docx", "txt", "csv"],
        accept_multiple_files=True,
        key="file_uploader",
    )

    if uploaded:
        # Create session if needed
        if not st.session_state.session_id:
            session = ingestion_agent.create_session()
            st.session_state.session_id = session.session_id
            log_step(f"Session created: {session.session_id}")

        # Ingest new files
        new_names = {f.name for f in uploaded}
        existing_names = {f["name"] for f in st.session_state.uploaded_files}

        for f in uploaded:
            if f.name not in existing_names:
                content = f.read()
                doc = ingestion_agent.ingest_file(
                    st.session_state.session_id, f.name, content
                )
                st.session_state.uploaded_files.append({
                    "name": f.name,
                    "type": doc.file_type.value,
                    "size": doc.size_bytes,
                    "id": doc.id,
                })
                log_step(f"Uploaded: {f.name}")

    # Show uploaded files
    if st.session_state.uploaded_files:
        st.markdown("#### Uploaded Documents")
        for uf in st.session_state.uploaded_files:
            col1, col2, col3 = st.columns([4, 2, 2])
            col1.markdown(f"📎 **{uf['name']}**")
            col2.caption(uf["type"].upper())
            col3.caption(f"{uf['size'] / 1024:.1f} KB")

        st.divider()

        if st.button("🚀 Run Analysis", type="primary", use_container_width=True):
            st.session_state.step = "analyzing"
            st.rerun()


# ─────────────────────────────────────────────
# STEP 2: Analyzing (pipeline execution)
# ─────────────────────────────────────────────
elif st.session_state.step == "analyzing":
    st.markdown('<div class="main-header">⚙️ Running Analysis Pipeline</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">The agentic pipeline is processing your documents through multiple analysis stages.</div>', unsafe_allow_html=True)

    session = storage_service.get_session(st.session_state.session_id)
    if not session or not session.documents:
        st.error("No documents found. Please go back and upload files.")
        st.stop()

    progress = st.progress(0)
    status_text = st.empty()

    try:
        # Step 1: Parse
        status_text.markdown("**📖 Parsing documents...**")
        progress.progress(10)
        log_step("Parsing documents")
        parsed_docs = parsing_agent.parse_all(session.documents)
        progress.progress(20)

        # Step 2: Extract
        status_text.markdown("**🔍 Extracting entities & classifying...**")
        log_step("Extracting entities")
        extractions = extraction_agent.process_all(parsed_docs)
        progress.progress(40)

        # Step 3: Gaps
        status_text.markdown("**🔎 Detecting integration gaps...**")
        log_step("Detecting gaps")
        gaps = gap_agent.detect(extractions)
        progress.progress(55)

        # Step 4: Risks
        status_text.markdown("**⚠️ Identifying risks...**")
        log_step("Detecting risks")
        risks = risk_agent.detect(extractions)
        progress.progress(70)

        # Step 5: Synergies
        status_text.markdown("**💡 Finding synergy opportunities...**")
        log_step("Detecting synergies")
        synergies = synergy_agent.detect(extractions)
        progress.progress(85)

        # Step 6: Recommendations
        status_text.markdown("**📋 Generating recommendations...**")
        log_step("Generating recommendations")
        recommendations = recommendation_agent.recommend(gaps, risks, synergies)
        progress.progress(95)

        # Assemble findings
        findings = AnalysisFindings(
            session_id=st.session_state.session_id,
            extractions=[e.model_dump(mode="json") for e in extractions],
            integration_gaps=gaps,
            risks=risks,
            synergies=synergies,
            recommendations=recommendations,
        )
        storage_service.save_findings(st.session_state.session_id, findings)
        st.session_state.findings = findings.model_dump(mode="json")

        progress.progress(100)
        status_text.markdown("**✅ Analysis complete!**")
        log_step("Analysis complete")

        time.sleep(1)
        st.session_state.step = "review"
        st.rerun()

    except Exception as e:
        st.error(f"Analysis failed: {e}")
        log_step(f"ERROR: {e}")
        if st.button("← Back to Upload"):
            st.session_state.step = "upload"
            st.rerun()


# ─────────────────────────────────────────────
# STEP 3: Review
# ─────────────────────────────────────────────
elif st.session_state.step == "review":
    st.markdown('<div class="main-header">🔍 Review Findings</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Review, edit, or reject findings before generating the final report.</div>', unsafe_allow_html=True)

    findings_data = st.session_state.findings
    if not findings_data:
        st.warning("No findings to review.")
        st.stop()

    findings = AnalysisFindings(**findings_data)

    # ── Metrics row ──
    cols = st.columns(5)
    metrics = [
        ("Documents", len(findings.extractions)),
        ("Gaps", len(findings.integration_gaps)),
        ("Risks", len(findings.risks)),
        ("Synergies", len(findings.synergies)),
        ("Actions", len(findings.recommendations)),
    ]
    for col, (label, val) in zip(cols, metrics):
        col.markdown(f"""<div class="metric-card">
            <div class="metric-value">{val}</div>
            <div class="metric-label">{label}</div>
        </div>""", unsafe_allow_html=True)

    st.divider()

    # ── Tabs for each finding category ──
    tab_docs, tab_gaps, tab_risks, tab_syn, tab_rec = st.tabs([
        "📄 Documents", "🔎 Gaps", "⚠️ Risks", "💡 Synergies", "📋 Recommendations"
    ])

    # Documents tab
    with tab_docs:
        for ext in findings.extractions:
            cls = ext.get("classification", {})
            entities = ext.get("entities", {})
            with st.expander(f"**{ext.get('document_name', 'Unknown')}** — {cls.get('document_type', '?')} ({cls.get('confidence', 0):.0%})"):
                for key, vals in entities.items():
                    if vals:
                        st.markdown(f"**{key.replace('_', ' ').title()}:** {', '.join(vals)}")

    # Gaps tab
    with tab_gaps:
        if not findings.integration_gaps:
            st.info("No integration gaps detected.")
        for g in findings.integration_gaps:
            render_severity_card(g.gap, g.severity.value, g.reason, g.evidence)

    # Risks tab
    with tab_risks:
        if not findings.risks:
            st.info("No risks detected.")
        for r in findings.risks:
            render_severity_card(r.risk, r.severity.value, r.reason, r.evidence)

    # Synergies tab
    with tab_syn:
        if not findings.synergies:
            st.info("No synergy opportunities detected.")
        for s in findings.synergies:
            render_severity_card(
                f"{s.opportunity} [{s.category}]",
                s.impact.value,
                s.reason,
            )

    # Recommendations tab
    with tab_rec:
        if not findings.recommendations:
            st.info("No recommendations generated.")
        for i, rec in enumerate(findings.recommendations, 1):
            with st.expander(f"**#{i} — {rec.action}** ({severity_badge(rec.priority.value)})"):
                st.markdown(f"**Owner:** {rec.owner}")
                st.markdown(f"**Reason:** {rec.reason}")
                st.markdown(f"**Expected Impact:** {rec.expected_impact}")
                st.markdown(f"**Timeline:** {rec.timeline}")

    st.divider()

    # ── Editable executive summary ──
    st.markdown("### ✏️ Executive Summary (editable)")
    edited_summary = st.text_area(
        "Edit the summary before export:",
        value=findings.executive_summary or "(Summary will be generated during export)",
        height=200,
        key="summary_edit",
    )

    st.divider()

    col_approve, col_back = st.columns(2)
    with col_approve:
        if st.button("✅ Approve & Generate Report", type="primary", use_container_width=True):
            # Save any summary edits
            findings.executive_summary = edited_summary
            st.session_state.findings = findings.model_dump(mode="json")

            review_agent.approve_all(st.session_state.session_id)
            log_step("Findings approved")
            st.session_state.step = "export"
            st.rerun()
    with col_back:
        if st.button("← Back to Upload", use_container_width=True):
            st.session_state.step = "upload"
            st.rerun()


# ─────────────────────────────────────────────
# STEP 4: Export
# ─────────────────────────────────────────────
elif st.session_state.step == "export":
    st.markdown('<div class="main-header">📊 Final Report</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Your PMI analysis report is ready for download.</div>', unsafe_allow_html=True)

    findings_data = st.session_state.findings
    if not findings_data:
        st.error("No findings to export.")
        st.stop()

    findings = AnalysisFindings(**findings_data)

    # Generate report
    with st.spinner("Generating executive summary and final report..."):
        try:
            findings = review_agent.apply_edits_to_findings(
                st.session_state.session_id, findings
            )
            report = report_agent.build_report(st.session_state.session_id, findings)
            st.session_state.report = {
                "markdown": report.report_markdown,
                "json": report.report_json,
            }
            log_step("Report generated")
        except Exception as e:
            st.error(f"Report generation failed: {e}")
            log_step(f"ERROR: {e}")
            st.stop()

    report_data = st.session_state.report

    # ── Executive Summary ──
    st.markdown("### Executive Summary")
    st.markdown(report_data["json"].get("executive_summary", "N/A"))

    st.divider()

    # ── Download buttons ──
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📥 Download Markdown Report",
            data=report_data["markdown"],
            file_name=f"pmi_report_{st.session_state.session_id}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with col2:
        st.download_button(
            label="📥 Download JSON Report",
            data=json.dumps(report_data["json"], indent=2),
            file_name=f"pmi_report_{st.session_state.session_id}.json",
            mime="application/json",
            use_container_width=True,
        )

    st.divider()

    # ── Full Markdown Preview ──
    with st.expander("📝 Full Report Preview", expanded=True):
        st.markdown(report_data["markdown"])

    st.divider()
    if st.button("🔄 Start New Analysis", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        init_state()
        st.rerun()
