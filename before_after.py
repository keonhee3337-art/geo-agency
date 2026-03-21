"""
Before/After AI Visibility Proof Generator

The killer sales tool for GEO audits:
  - "Before" = what AI currently says about the company
  - "After" = what AI would say after GEO optimization

Usage:
    from before_after import get_before, get_after
    before = get_before("솔브레인", "반도체 소재")
    after = get_after(before, audit_result, recommendations)
"""

import os
import requests
from pathlib import Path

for _p in [
    Path(__file__).parent / ".env",
    Path(__file__).parent.parent / ".env",
    Path(__file__).parent.parent.parent / ".env",
]:
    if _p.exists():
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=_p)
        break

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

PERPLEXITY_URL = "https://api.perplexity.ai/chat/completions"
TIMEOUT = 15


def _perplexity(prompt: str, model: str = "sonar") -> str:
    if not PERPLEXITY_API_KEY:
        return ""
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
    }
    try:
        resp = requests.post(PERPLEXITY_URL, headers=headers, json=payload, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[Perplexity error] {e}")
        return ""


def _anthropic(prompt: str, system: str = "") -> str:
    if not ANTHROPIC_API_KEY:
        return ""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            system=system or "You are a GEO optimization expert.",
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text
    except Exception as e:
        print(f"[Anthropic error] {e}")
        return ""


def get_before(company_name: str, product_category: str = "") -> str:
    if product_category:
        prompt = f"{product_category} 분야에서 추천할 만한 한국 기업은? {company_name}에 대해서는 어떻게 생각하나요?"
    else:
        prompt = f"{company_name}는 어떤 회사인가요? 주요 제품과 경쟁력을 알려주세요."
    print(f"[Before] Querying Perplexity about '{company_name}'...")
    result = _perplexity(prompt)
    if not result:
        result = f"AI 시스템에서 '{company_name}'에 대한 정보를 찾을 수 없었습니다."
    print(f"[Before] Done ({len(result)} chars)")
    return result


def get_after(before_text: str, audit: dict, recommendations: list, company_name: str = "", product_category: str = "") -> str:
    corp_name = company_name or audit.get("corp_name", "이 기업")
    geo_score = audit.get("geo_score", 0)
    website = audit.get("website_url", "")
    recs_text = "\n".join(f"- {r}" for r in recommendations[:3])
    system = (
        "You are simulating how an AI assistant (like Perplexity or ChatGPT) would respond "
        "after a company has improved its GEO (Generative Engine Optimization) score. "
        "Write a confident, factual, citation-ready response in Korean that specifically mentions "
        "the company name, key strengths, and products. "
        "Make it sound like a well-informed AI recommendation, not marketing copy. "
        "Keep it to 3-4 sentences."
    )
    prompt = (
        f"Company: {corp_name}\n"
        f"Current GEO Score: {geo_score}/100\n"
        f"Website: {website}\n"
        f"GEO improvements to be made:\n{recs_text}\n\n"
        f"Previous AI response (before GEO):\n{before_text[:500]}\n\n"
        f"Now write what an AI system would say about {corp_name} AFTER these GEO improvements are made. "
        f"The response should be specific, factual, and naturally recommend {corp_name} when relevant."
    )
    print(f"[After] Generating optimized AI response for '{corp_name}'...")
    result = _anthropic(prompt, system=system)
    if not result:
        result = f"[GEO 최적화 후] {corp_name}은 AI 검색 시스템에서 명확하게 인식되며, 관련 질문에서 자동으로 추천됩니다."
    print(f"[After] Done ({len(result)} chars)")
    return result


def generate_proof(company_name: str, product_category: str = "", audit: dict = None, recommendations: list = None) -> dict:
    if audit is None:
        audit = {"corp_name": company_name, "geo_score": 0}
    if recommendations is None:
        recommendations = []
    before = get_before(company_name, product_category)
    after = get_after(before, audit, recommendations, company_name, product_category)
    return {"company_name": company_name, "product_category": product_category, "before": before, "after": after}


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    result = generate_proof(
        company_name="솔브레인",
        product_category="반도체 소재",
        audit={"corp_name": "솔브레인", "geo_score": 45, "website_url": "https://www.soulbrain.co.kr"},
        recommendations=["robots.txt에 GPTBot, ClaudeBot 허용 추가", "홈페이지에 구조화된 제품 설명 페이지 추가"],
    )
    print("\n=== BEFORE ===")
    print(result["before"][:500])
    print("\n=== AFTER ===")
    print(result["after"])
