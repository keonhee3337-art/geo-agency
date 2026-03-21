"""
GEO Agency - Streamlit App

Single-company GEO audit tool for client demos and service delivery.
Input: company name -> GEO audit -> before/after proof -> PDF download
"""

import os
import sys
import time
from pathlib import Path

import streamlit as st

for _p in [Path(__file__).parent / ".env", Path(__file__).parent.parent / ".env"]:
    if _p.exists():
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=_p)
        break

# Streamlit Cloud: load secrets into env if .env not available
for _key in ["PERPLEXITY_API_KEY", "ANTHROPIC_API_KEY"]:
    if not os.environ.get(_key):
        try:
            os.environ[_key] = st.secrets[_key]
        except (KeyError, FileNotFoundError):
            pass

sys.path.insert(0, str(Path(__file__).parent))

st.set_page_config(page_title="GEO Audit", page_icon="🔍", layout="wide")

st.title("GEO Audit Tool")
st.caption("AI 가시성 진단 — Generative Engine Optimization")

st.markdown("""
**GEO(Generative Engine Optimization)**는 ChatGPT, Perplexity, Claude 같은 AI 시스템이  
당신의 비즈니스를 추천하도록 최적화하는 것입니다.
""")

st.divider()

col1, col2 = st.columns([2, 1])

with col1:
    company_name = st.text_input(
        "회사명 (한국어 또는 영어)",
        placeholder="예: 솔브레인, 현대모비스, 스타트업 이름",
        help="DART 상장 여부 무관 — 어떤 회사든 가능합니다"
    )
    product_category = st.text_input(
        "주요 제품/서비스 카테고리 (선택)",
        placeholder="예: 반도체 소재, IT 컨설팅, 온라인 쇼핑몰",
        help="AI 추천 쿼리를 더 정확하게 만들기 위해 사용됩니다"
    )

with col2:
    st.markdown("#### 점수 기준")
    st.markdown("""
    | 범위 | 등급 |
    |------|------|
    | 70-100 | 🟢 High |
    | 40-69  | 🟡 Medium |
    | 0-39   | 🔴 Low |
    """)

run = st.button("GEO 진단 시작", type="primary", disabled=not company_name)

if run and company_name:
    st.divider()

    with st.spinner(f"'{company_name}' 분석 중... (약 30-60초)"):
        try:
            from geo_audit import audit_single_company
            audit = audit_single_company(company_name)
        except Exception as e:
            st.error(f"GEO 진단 오류: {e}")
            st.stop()

    geo_score = audit.get("geo_score", 0)
    breakdown = audit.get("geo_breakdown", {})
    website = audit.get("website_url") or "찾을 수 없음"

    # Score display
    st.markdown(f"## {company_name} GEO Score")
    color = "green" if geo_score >= 70 else ("orange" if geo_score >= 40 else "red")
    label = "High" if geo_score >= 70 else ("Medium" if geo_score >= 40 else "Low")
    st.markdown(f"<h1 style='color:{color}'>{geo_score}/100 — {label}</h1>", unsafe_allow_html=True)
    st.caption(f"웹사이트: {website}")

    # Pull all sub-dimensions
    citability = breakdown.get("citability", 0)
    sov = breakdown.get("share_of_voice", 0)
    ai_bot = breakdown.get("ai_bot_access", breakdown.get("crawler_access", 0))
    ai_policy = breakdown.get("ai_policy_file", breakdown.get("llms_txt", 0))
    org_schema = breakdown.get("org_schema", 0)
    content_schema = breakdown.get("content_schema", 0)
    naver = breakdown.get("naver_presence", 0)
    kr_sync = breakdown.get("kr_platform_sync", 0)
    brand_mention = breakdown.get("brand_mention", 0)
    sentiment_quality = breakdown.get("sentiment_quality", 0)

    # 3 client-facing summary metrics (easy to explain in 30 seconds)
    # Content: can AI read and understand you?
    content_score = citability + content_schema + brand_mention  # max 65
    content_pct = round(content_score / 65 * 100)
    # Technical Access: can AI find you?
    access_score = ai_bot + ai_policy + org_schema                # max 45
    access_pct = round(access_score / 45 * 100)
    # Market Presence: does AI recommend you?
    presence_score = sov + naver + kr_sync + sentiment_quality    # max 40
    presence_pct = round(presence_score / 40 * 100)

    col_content, col_access, col_presence = st.columns(3)
    with col_content:
        st.metric(
            "Content Quality",
            f"{content_pct}%",
            help="AI가 귀사 콘텐츠를 읽고 이해할 수 있는지 — 풍부한 텍스트, 구조화된 FAQ, 브랜드 언급"
        )
    with col_access:
        st.metric(
            "Technical Access",
            f"{access_pct}%",
            help="AI 크롤러가 귀사 사이트에 접근 가능한지 — robots.txt, llms.txt, 스키마 데이터"
        )
    with col_presence:
        st.metric(
            "Market Presence",
            f"{presence_pct}%",
            help="AI가 귀사를 시장에서 인식하고 추천하는지 — 경쟁사 대비 인용, 네이버/카카오, 브랜드 품질"
        )

    # Technical detail — collapsed by default
    with st.expander("기술 세부 점수 (10개 지표)", expanded=False):
        st.caption("5-category internal scoring (max 150, normalized to /100)")
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("AI Citability", f"{citability}/40")
            st.metric("Share of Voice", f"{sov}/10")
            st.metric("AI Bot Access", f"{ai_bot}/20")
            st.metric("AI Policy File (llms.txt)", f"{ai_policy}/10")
            st.metric("Org Schema", f"{org_schema}/15")
        with col_b:
            st.metric("Content Schema", f"{content_schema}/15")
            st.metric("Naver Presence", f"{naver}/10")
            st.metric("KR Platform Sync", f"{kr_sync}/10")
            st.metric("Brand Mention", f"{brand_mention}/10")
            st.metric("Sentiment Quality", f"{sentiment_quality}/10")

    # Competitors from SoV
    sov_competitors = audit.get("sov_competitors", [])
    sov_cited = audit.get("sov_cited", False)
    if sov_competitors:
        cited_label = "포함됨" if sov_cited else "미포함"
        st.markdown(
            f"**경쟁사 AI 인용 현황:** {', '.join(sov_competitors[:5])} "
            f"| 귀사 인용 여부: **{cited_label}**"
        )

    st.session_state["audit"] = audit

    # Before/after
    st.divider()
    st.markdown("### AI 가시성 현황 (Before)")
    with st.spinner("AI가 현재 이 회사에 대해 뭐라고 하는지 확인 중..."):
        try:
            from before_after import get_before, get_after
            before = get_before(company_name, product_category)
        except Exception as e:
            before = f"오류: {e}"

    st.info(before[:800] + ("..." if len(before) > 800 else ""))
    st.session_state["before"] = before

    # Dynamic recommendations based on actual scores
    from geo_audit import generate_dynamic_recommendations
    recs = generate_dynamic_recommendations(breakdown, company_name)
    st.session_state["recs"] = recs

    st.markdown("### GEO 최적화 후 예상 AI 응답 (After)")
    with st.spinner("최적화 후 AI 응답 시뮬레이션 중..."):
        try:
            after = get_after(before, audit, recs, company_name, product_category)
        except Exception as e:
            after = f"오류: {e}"

    st.success(after)
    st.session_state["after"] = after

    # PDF generation
    st.divider()
    st.markdown("### PDF 리포트 생성")
    col_pdf, col_kit = st.columns(2)
    with col_pdf:
        if st.button("PDF 리포트 다운로드", type="secondary"):
            with st.spinner("PDF 생성 중..."):
                try:
                    from geo_report_pdf import generate_pdf
                    pdf_path = generate_pdf(audit, recs, before_text=before)
                    with open(pdf_path, "rb") as f:
                        pdf_bytes = f.read()
                    import re
                    safe_name = re.sub(r"[^\w\-]", "_", company_name)
                    st.download_button(
                        label="PDF 다운로드",
                        data=pdf_bytes,
                        file_name=f"GEO_Audit_{safe_name}.pdf",
                        mime="application/pdf",
                    )
                    st.success(f"PDF 생성 완료: {Path(pdf_path).name}")
                except Exception as e:
                    st.error(f"PDF 생성 오류: {e}")

    with col_kit:
        if st.button("구현 파일 다운로드", type="secondary", help="개발자에게 전달할 robots.txt, llms.txt, JSON-LD, 체크리스트"):
            with st.spinner("구현 파일 생성 중..."):
                try:
                    from geo_deliverables import generate_deliverables, zip_deliverables
                    files = generate_deliverables(
                        audit,
                        company_name=company_name,
                        product_category=product_category,
                    )
                    zip_path = zip_deliverables(files)
                    with open(zip_path, "rb") as f:
                        zip_bytes = f.read()
                    import re
                    safe_name = re.sub(r"[^\w\-]", "_", company_name)
                    st.download_button(
                        label="Implementation Kit 다운로드",
                        data=zip_bytes,
                        file_name=f"GEO_Implementation_{safe_name}.zip",
                        mime="application/zip",
                    )
                    st.success(f"구현 파일 {len(files)}개 생성 완료")
                    with st.expander("포함된 파일 목록"):
                        for fname in files:
                            st.markdown(f"- `{fname}`")
                except Exception as e:
                    st.error(f"구현 파일 생성 오류: {e}")

# PDF download if already generated (persists in session)
elif "audit" in st.session_state:
    st.info("이전 진단 결과가 있습니다. 새 회사를 입력하거나 PDF를 다운로드하세요.")
    audit = st.session_state["audit"]
    recs = st.session_state.get("recs", [])
    before = st.session_state.get("before", "")
    if st.button("PDF 리포트 다운로드 (이전 결과)", type="secondary"):
        with st.spinner("PDF 생성 중..."):
            try:
                from geo_report_pdf import generate_pdf
                pdf_path = generate_pdf(audit, recs, before_text=before)
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()
                import re
                safe_name = re.sub(r"[^\w\-]", "_", audit.get("corp_name", "company"))
                st.download_button(
                    label="PDF 다운로드",
                    data=pdf_bytes,
                    file_name=f"GEO_Audit_{safe_name}.pdf",
                    mime="application/pdf",
                )
            except Exception as e:
                st.error(f"PDF 생성 오류: {e}")

st.divider()
st.caption("Built by Keonhee Kim | SKKU Business Administration | GEO Consulting")
