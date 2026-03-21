"""
GEO Agency - Streamlit App (Visual Refresh)
"""

import os
import sys
import re
from pathlib import Path

import streamlit as st

for _p in [Path(__file__).parent / ".env", Path(__file__).parent.parent / ".env", Path(__file__).parent.parent.parent / ".env"]:
    if _p.exists():
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=_p)
        break

for _key in ["PERPLEXITY_API_KEY", "ANTHROPIC_API_KEY"]:
    if not os.environ.get(_key):
        try:
            os.environ[_key] = st.secrets[_key]
        except (KeyError, FileNotFoundError):
            pass

sys.path.insert(0, str(Path(__file__).parent))

st.set_page_config(page_title="GEO Audit", page_icon="", layout="wide")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.score-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border-radius: 16px; padding: 32px 40px; margin: 16px 0;
    display: flex; align-items: center; gap: 32px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.18);
}
.score-num { font-size: 80px; font-weight: 700; line-height: 1; min-width: 120px; }
.score-meta { flex: 1; }
.score-grade { font-size: 22px; font-weight: 600; letter-spacing: 0.5px; margin-bottom: 6px; }
.score-sub { font-size: 13px; color: #aaa; }
.cat-card {
    background: #1e2130; border-radius: 12px; padding: 20px;
    text-align: center; height: 100%; border-top: 4px solid transparent;
}
.cat-title { font-size: 13px; color: #999; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px; }
.cat-pct { font-size: 36px; font-weight: 700; line-height: 1; margin-bottom: 6px; }
.cat-desc { font-size: 11px; color: #666; }
.prog-wrap { margin: 6px 0 16px 0; }
.prog-label { display: flex; justify-content: space-between; font-size: 13px; color: #ccc; margin-bottom: 4px; }
.prog-bar-bg { background: #2a2a3e; border-radius: 4px; height: 8px; overflow: hidden; }
.prog-bar-fill { height: 8px; border-radius: 4px; }
.panel { border-radius: 12px; padding: 20px; min-height: 160px; font-size: 14px; line-height: 1.7; color: #ddd; }
.panel-before { background: #1a1500; border-left: 4px solid #d97706; }
.panel-after  { background: #001a0a; border-left: 4px solid #16a34a; }
.panel-head   { font-size: 12px; font-weight: 600; letter-spacing: 0.5px; margin-bottom: 12px; text-transform: uppercase; }
.panel-before .panel-head { color: #f59e0b; }
.panel-after  .panel-head { color: #22c55e; }
.comp-badge {
    display: inline-block; background: #2d2d4a; border-radius: 6px;
    padding: 3px 10px; font-size: 12px; color: #aaa; margin: 2px 4px 2px 0;
}
.comp-badge.cited { background: #1a3a1a; color: #4ade80; }
.section-head {
    font-size: 11px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase;
    color: #666; margin: 28px 0 12px 0; padding-bottom: 6px; border-bottom: 1px solid #2a2a3e;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

st.markdown("<h2 style='margin-bottom:2px'>GEO Audit</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#888;margin-top:0'>AI visibility diagnosis &mdash; ChatGPT, Perplexity, Claude</p>", unsafe_allow_html=True)

c1, c2, c3 = st.columns([3, 2, 1])
with c1:
    company_name = st.text_input("", placeholder="", label_visibility="collapsed", key="company_name_input")
    st.caption("Company name (Korean or English)")
with c2:
    product_category = st.text_input("", placeholder="", label_visibility="collapsed", key="category_input")
    st.caption("Product / service category (optional)")
with c3:
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    run = st.button("Run Audit", type="primary", disabled=not company_name, use_container_width=True)


def _color(pct):
    if pct >= 70: return "#22c55e"
    if pct >= 40: return "#f59e0b"
    return "#ef4444"

def _grade(pct):
    if pct >= 70: return "High"
    if pct >= 40: return "Medium"
    return "Low"

def _progress_bar(label, value, max_val):
    pct = round(value / max_val * 100) if max_val else 0
    color = _color(pct)
    return (
        f"<div class='prog-wrap'>"
        f"<div class='prog-label'><span>{label}</span>"
        f"<span style='color:{color}'>{value}/{max_val}</span></div>"
        f"<div class='prog-bar-bg'><div class='prog-bar-fill' style='width:{pct}%;background:{color}'></div></div>"
        f"</div>"
    )

def _cat_card(title, pct, desc, border_color):
    color = _color(pct)
    return (
        f"<div class='cat-card' style='border-top-color:{border_color}'>"
        f"<div class='cat-title'>{title}</div>"
        f"<div class='cat-pct' style='color:{color}'>{pct}%</div>"
        f"<div class='cat-desc'>{desc}</div>"
        f"</div>"
    )


if run and company_name:
    st.session_state.pop("audit", None)
    st.divider()

    with st.spinner(f"Auditing {company_name}... (~30-60s)"):
        try:
            from geo_audit import audit_single_company
            audit = audit_single_company(company_name)
        except Exception as e:
            st.error(f"Audit error: {e}")
            st.stop()

    geo_score = audit.get("geo_score", 0)
    breakdown = audit.get("geo_breakdown", {})
    website = audit.get("website_url") or "Not found"

    score_color = _color(geo_score)
    grade = _grade(geo_score)
    st.markdown(
        f"<div class='score-card'>"
        f"<div class='score-num' style='color:{score_color}'>{geo_score}</div>"
        f"<div class='score-meta'>"
        f"<div class='score-grade' style='color:{score_color}'>{grade} AI Visibility</div>"
        f"<div class='score-sub'>{company_name} &bull; {website}</div>"
        f"<div class='score-sub' style='margin-top:8px'>Score out of 100 &mdash; 10 GEO dimensions</div>"
        f"</div></div>",
        unsafe_allow_html=True,
    )

    citability     = breakdown.get("citability", 0)
    sov            = breakdown.get("share_of_voice", 0)
    ai_bot         = breakdown.get("ai_bot_access", breakdown.get("crawler_access", 0))
    ai_policy      = breakdown.get("ai_policy_file", breakdown.get("llms_txt", 0))
    org_schema     = breakdown.get("org_schema", 0)
    content_schema = breakdown.get("content_schema", 0)
    naver          = breakdown.get("naver_presence", 0)
    kr_sync        = breakdown.get("kr_platform_sync", 0)
    brand_mention  = breakdown.get("brand_mention", 0)
    sentiment      = breakdown.get("sentiment_quality", 0)

    content_pct  = round((citability + content_schema + brand_mention) / 65 * 100)
    access_pct   = round((ai_bot + ai_policy + org_schema) / 45 * 100)
    presence_pct = round((sov + naver + kr_sync + sentiment) / 40 * 100)

    st.markdown("<div class='section-head'>Category Breakdown</div>", unsafe_allow_html=True)
    cc1, cc2, cc3 = st.columns(3)
    with cc1:
        st.markdown(_cat_card("Content Quality", content_pct, "AI can read &amp; understand you", "#6366f1"), unsafe_allow_html=True)
    with cc2:
        st.markdown(_cat_card("Technical Access", access_pct, "AI crawlers can find you", "#0ea5e9"), unsafe_allow_html=True)
    with cc3:
        st.markdown(_cat_card("Market Presence", presence_pct, "AI recommends you", "#f59e0b"), unsafe_allow_html=True)

    st.markdown("<div class='section-head'>Dimension Detail</div>", unsafe_allow_html=True)
    pb1, pb2 = st.columns(2)
    with pb1:
        st.markdown(
            _progress_bar("AI Citability", citability, 40) +
            _progress_bar("Share of Voice", sov, 10) +
            _progress_bar("AI Bot Access", ai_bot, 20) +
            _progress_bar("AI Policy File", ai_policy, 10) +
            _progress_bar("Org Schema", org_schema, 15),
            unsafe_allow_html=True,
        )
    with pb2:
        st.markdown(
            _progress_bar("Content Schema", content_schema, 15) +
            _progress_bar("Naver Presence", naver, 10) +
            _progress_bar("KR Platform Sync", kr_sync, 10) +
            _progress_bar("Brand Mention", brand_mention, 10) +
            _progress_bar("Sentiment Quality", sentiment, 10),
            unsafe_allow_html=True,
        )

    sov_competitors = audit.get("sov_competitors", [])
    sov_cited = audit.get("sov_cited", False)
    if sov_competitors:
        st.markdown("<div class='section-head'>Competitor AI Citations</div>", unsafe_allow_html=True)
        badges = " ".join(f"<span class='comp-badge'>{c}</span>" for c in sov_competitors[:5])
        my_cls = "comp-badge cited" if sov_cited else "comp-badge"
        my_lbl = "This company: Cited" if sov_cited else "This company: Not cited"
        st.markdown(badges + f" &nbsp;<span class='{my_cls}'>{my_lbl}</span>", unsafe_allow_html=True)

    st.session_state["audit"] = audit

    st.markdown("<div class='section-head'>Before / After &mdash; AI Response Simulation</div>", unsafe_allow_html=True)

    with st.spinner("Fetching current AI response (Before)..."):
        try:
            from before_after import get_before, get_after
            before = get_before(company_name, product_category)
        except Exception as e:
            before = f"Error: {e}"

    from geo_audit import generate_dynamic_recommendations
    recs = generate_dynamic_recommendations(breakdown, company_name)
    st.session_state["recs"] = recs

    with st.spinner("Simulating optimized AI response (After)..."):
        try:
            after = get_after(before, audit, recs, company_name, product_category)
        except Exception as e:
            after = f"Error: {e}"

    st.session_state["before"] = before
    st.session_state["after"] = after

    col_before, col_after = st.columns(2)
    with col_before:
        truncated = before[:700] + ("..." if len(before) > 700 else "")
        st.markdown(
            f"<div class='panel panel-before'><div class='panel-head'>Before GEO Optimization</div>{truncated}</div>",
            unsafe_allow_html=True,
        )
    with col_after:
        st.markdown(
            f"<div class='panel panel-after'><div class='panel-head'>After GEO Optimization</div>{after}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div class='section-head'>Downloads</div>", unsafe_allow_html=True)
    safe_name = re.sub(r"[^\w\-]", "_", company_name)
    dl1, dl2 = st.columns(2)

    with dl1:
        try:
            from geo_report_pdf import generate_pdf
            pdf_path = generate_pdf(audit, recs, before_text=before)
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
            st.download_button(
                label="PDF Report",
                data=pdf_bytes,
                file_name=f"GEO_Audit_{safe_name}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"PDF error: {e}")

    with dl2:
        try:
            from geo_deliverables import generate_deliverables, zip_deliverables
            files = generate_deliverables(audit, company_name=company_name, product_category=product_category)
            zip_path = zip_deliverables(files)
            with open(zip_path, "rb") as f:
                zip_bytes = f.read()
            st.download_button(
                label=f"Implementation Kit ({len(files)} files)",
                data=zip_bytes,
                file_name=f"GEO_Implementation_{safe_name}.zip",
                mime="application/zip",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"Kit error: {e}")


elif "audit" in st.session_state:
    st.info("Previous audit loaded. Enter a new company to run a fresh audit.")
    audit = st.session_state["audit"]
    recs  = st.session_state.get("recs", [])
    before = st.session_state.get("before", "")
    safe_name = re.sub(r"[^\w\-]", "_", audit.get("corp_name", "company"))
    try:
        from geo_report_pdf import generate_pdf
        pdf_path = generate_pdf(audit, recs, before_text=before)
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        st.download_button(
            label="PDF Report (previous audit)",
            data=pdf_bytes,
            file_name=f"GEO_Audit_{safe_name}.pdf",
            mime="application/pdf",
        )
    except Exception as e:
        st.error(f"PDF error: {e}")

else:
    st.markdown("<div style='height:60px'></div>", unsafe_allow_html=True)
    st.markdown(
        "<div style='text-align:center;color:#555;font-size:15px'>Enter a company name above and click <strong>Run Audit</strong></div>",
        unsafe_allow_html=True,
    )

st.divider()
st.caption("Built by Keonhee Kim | SKKU Business Administration | GEO Consulting")
