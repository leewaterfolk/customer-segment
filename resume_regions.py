#!/usr/bin/env python3
"""
resume_regions.py — Region-specific résumé conventions (the JobPA differentiator).

Each region encodes the REAL formatting rules recruiters & ATS expect in that market.
A résumé that wins in Seoul gets auto-rejected in San Francisco, and vice-versa.
This is the knowledge base the AI builder uses to localise a résumé properly.
"""

REGIONS = {
    "korea": {
        "label": "🇰🇷 Korea (한국)",
        "doc_name": "이력서 + 자기소개서",
        "language": "Korean (한국어)",
        "photo": "Include a professional photo, top-right (standard for private sector). "
                 "OMIT for public sector / blind 채용 (블라인드).",
        "personal": "이름(한글+한자), 생년월일, 연락처, 이메일, 주소. Marital status optional, "
                    "increasingly omitted.",
        "structure": [
            "인적사항 (Personal info table, with photo)",
            "학력사항 (Education, reverse-chronological)",
            "경력사항 (Work experience, company · period · role · 담당업무)",
            "자격증·어학 (Certifications, 토익/토플/오픽 scores, licenses)",
            "수상·대외활동 (Awards, activities)",
            "자기소개서 (Self-introduction essay — see below)",
        ],
        "self_intro": "자기소개서 is mandatory and weighted heavily. Standard 4 blocks: "
                      "성장과정 · 성격의 장단점 · 지원동기 · 입사 후 포부. 800–1500자 each company-specific.",
        "tone": "Formal, humble, group-harmony oriented (조직 적응력, 성실성, 책임감). "
                "Avoid over-individualistic 'I single-handedly' framing.",
        "length": "이력서 1–2 pages + 자기소개서 separate.",
        "avoid": "Casual tone, US-style aggressive self-promotion, 반말, emoji.",
        "ats_note": "Korean job portals (사람인, 잡코리아, 원티드) parse structured tables. "
                    "Keep 인적사항 as clean labelled fields.",
    },
    "us": {
        "label": "🇺🇸 USA",
        "doc_name": "Resume",
        "language": "English (US spelling)",
        "photo": "NEVER include a photo. No age, no marital status, no nationality — "
                 "US anti-discrimination law means recruiters discard résumés with these.",
        "personal": "Name, city + state (no full address), phone, professional email, "
                    "LinkedIn, portfolio/GitHub. Nothing else personal.",
        "structure": [
            "Header (name + contact + LinkedIn)",
            "Professional Summary (2–3 lines, optional for senior)",
            "Experience (reverse-chronological, achievement bullets with metrics)",
            "Skills (hard skills, tools, languages)",
            "Education (degree, school, year — GPA only if strong & recent)",
            "Certifications / Projects (optional)",
        ],
        "self_intro": "No cover-letter essay inside the résumé. Cover letter is a separate, "
                      "optional 1-page document.",
        "tone": "Direct, confident, results-first. Every bullet = strong verb + quantified impact "
                "(XYZ formula). 'I' is implied, never written.",
        "length": "STRICTLY 1 page for <10 yrs experience; 2 pages max for senior.",
        "avoid": "Photo, personal data, 'References available on request', pronouns, paragraphs.",
        "ats_note": "Single-column, standard headings (Experience/Education/Skills), no tables, "
                    "no text boxes, no graphics. .docx or text-based PDF.",
    },
    "singapore": {
        "label": "🇸🇬 Singapore",
        "doc_name": "Resume / CV",
        "language": "English (British spelling)",
        "photo": "Photo is optional and commonly accepted (unlike US). A clean headshot is fine.",
        "personal": "Name, contact, and — importantly — NATIONALITY / PR status / work-pass "
                    "eligibility (EP/SP/Citizen/PR). Employers must know hiring eligibility. "
                    "Notice period and (sometimes) current/expected salary are commonly listed.",
        "structure": [
            "Personal particulars (incl. nationality / residency status)",
            "Career summary",
            "Work experience (reverse-chronological, metrics-driven)",
            "Education & professional qualifications",
            "Skills & languages (English + Mandarin/Malay/Tamil a plus)",
            "Notice period / availability",
        ],
        "self_intro": "No essay. Optional short cover letter.",
        "tone": "Professional, achievement-oriented like US, but personal particulars "
                "(nationality, salary, notice) are expected and not taboo.",
        "length": "1–2 pages.",
        "avoid": "Omitting work-pass / nationality status (red flag for SG recruiters).",
        "ats_note": "Major portals: MyCareersFuture, JobStreet, LinkedIn. ATS-clean single column. "
                    "British spelling (organise, programme, CV).",
    },
    "france": {
        "label": "🇫🇷 France",
        "doc_name": "CV + Lettre de motivation",
        "language": "French (Français)",
        "photo": "Photo is common and accepted (though officially optional / anti-discrim debate). "
                 "A professional headshot top-right is the norm.",
        "personal": "Prénom Nom, ville, téléphone, email. Âge/permis sometimes included. "
                    "État civil increasingly optional.",
        "structure": [
            "État civil / coordonnées (+ photo)",
            "Titre / accroche (target role headline)",
            "Expérience professionnelle (anti-chronologique)",
            "Formation (diplômes — Bac+5, grandes écoles matter)",
            "Compétences (techniques + outils)",
            "Langues (with levels: courant / bilingue / B2…)",
            "Centres d'intérêt (briefly — expected in FR)",
        ],
        "self_intro": "Lettre de motivation is ESSENTIAL and formal — separate 1-page letter, "
                      "structured: vous (employer) → moi (me) → nous (fit). Formal closings.",
        "tone": "Formal, structured, diploma-conscious (French recruiters weight 'formation' "
                "and école heavily). Polished French, no anglicisms where a French term exists.",
        "length": "1 page strongly preferred (2 max for senior).",
        "avoid": "Informal tone, missing lettre de motivation, English buzzwords.",
        "ats_note": "Portals: APEC, Indeed FR, Welcome to the Jungle, LinkedIn. "
                    "French language throughout, including section headings.",
    },
    "germany": {
        "label": "🇩🇪 Germany",
        "doc_name": "Lebenslauf + Anschreiben",
        "language": "German (Deutsch)",
        "photo": "Photo (Bewerbungsfoto) is conventional and expected — professional studio "
                 "headshot, top-right.",
        "personal": "Name, Anschrift, Geburtsdatum, Kontakt. Nationality if relevant for work permit.",
        "structure": [
            "Persönliche Daten (+ Foto)",
            "Berufserfahrung (anti-chronologisch / reverse-chronological)",
            "Ausbildung / Studium",
            "Kenntnisse & Fähigkeiten (Sprachen mit Niveau, IT-Kenntnisse)",
            "Weiterbildung / Zertifikate",
            "Ort, Datum + Unterschrift (signed and dated at the bottom — expected!)",
        ],
        "self_intro": "Anschreiben (cover letter) is essential and formal. Lebenslauf itself is "
                      "tabular and factual.",
        "tone": "Precise, factual, complete. Gaps must be explained. Signed & dated.",
        "length": "Lebenslauf 1–2 pages, tabular.",
        "avoid": "Unexplained gaps, unsigned CV, marketing fluff.",
        "ats_note": "Portals: StepStone, Xing, LinkedIn, Indeed DE. German throughout.",
    },
    "uk": {
        "label": "🇬🇧 UK",
        "doc_name": "CV",
        "language": "English (British spelling)",
        "photo": "NO photo (same anti-discrimination reasoning as US).",
        "personal": "Name, city, phone, email, LinkedIn. No DOB, no marital status, no photo.",
        "structure": [
            "Header + contact",
            "Personal statement (3–4 line profile at the top)",
            "Key skills (optional bullet block)",
            "Work experience (reverse-chronological, achievement bullets)",
            "Education & qualifications",
            "References: 'Available on request' is acceptable in the UK (unlike US)",
        ],
        "self_intro": "No essay inside CV. Separate cover letter common.",
        "tone": "Professional, achievement-oriented, slightly more reserved than US. "
                "British spelling (organise, optimise, programme).",
        "length": "2 pages is the UK standard (not 1 like the US).",
        "avoid": "US spelling, photo, personal data.",
        "ats_note": "Portals: Indeed UK, Reed, Totaljobs, LinkedIn. British spelling.",
    },
}

REGION_ORDER = ["korea", "us", "singapore", "france", "germany", "uk"]


def build_system_prompt(region_key: str) -> str:
    r = REGIONS[region_key]
    structure = "\n".join(f"   {i+1}. {s}" for i, s in enumerate(r["structure"]))
    return f"""\
You are an elite résumé writer who is a NATIVE expert in the {r['label']} job market.
You localise résumés to the exact conventions recruiters and ATS expect in this specific region —
a résumé that works in one country gets auto-rejected in another, and you know precisely why.

TARGET MARKET: {r['label']}
DOCUMENT TYPE: {r['doc_name']}
OUTPUT LANGUAGE: {r['language']}  (write the résumé itself in this language)

NON-NEGOTIABLE REGIONAL RULES for this market:
• PHOTO: {r['photo']}
• PERSONAL DETAILS: {r['personal']}
• REQUIRED STRUCTURE (in this order):
{structure}
• COVER LETTER / SELF-INTRO: {r['self_intro']}
• TONE: {r['tone']}
• LENGTH: {r['length']}
• AVOID: {r['avoid']}
• ATS / PORTAL NOTE: {r['ats_note']}

YOUR TASK
Take the candidate's raw information (or existing résumé from another region) and produce a
fully localised, ready-to-use {r['doc_name']} for the {r['label']} market.

OUTPUT FORMAT (use these exact markdown sections):

## ✅ LOCALISED RÉSUMÉ
The complete, ready-to-paste résumé written in {r['language']}, following every rule above.
Use clean markdown. If a photo is expected, write "[사진 / Photo here]" placeholder where it goes.
If the candidate is missing data a recruiter in this market expects (e.g. nationality for
Singapore, language levels for France), insert a clear [NEEDS: ...] placeholder — never invent facts.

{"## ✅ 자기소개서 / COVER LETTER" if r['self_intro'] and 'essential' in r['self_intro'].lower() or '자기소개서' in r['self_intro'] or 'Lettre' in r['self_intro'] or 'Anschreiben' in r['self_intro'] else ""}
{"Provide the matching cover-letter / self-introduction document required for this market." if ('essential' in r['self_intro'].lower() or '자기소개서' in r['self_intro'] or 'Lettre' in r['self_intro'] or 'Anschreiben' in r['self_intro']) else ""}

## 🌍 WHAT I CHANGED FOR THIS MARKET
A short bullet list explaining the key localisation decisions — what you added, removed, or
reformatted versus a generic résumé, and WHY this market expects it. This is the candidate's
education on why regional formatting matters.

## ⚠️ MISSING INFO TO COMPLETE
List every [NEEDS: ...] placeholder so the candidate knows exactly what to fill in.

Be truthful: never fabricate metrics, employers, dates, or credentials.
"""
