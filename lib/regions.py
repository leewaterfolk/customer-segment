REGIONS = {
    "korea": {
        "label": "🇰🇷 Korea (한국)",
        "doc": "이력서 + 자기소개서",
        "lang": "Korean (한국어)",
        "flag": "🇰🇷",
        "photo": "상단 우측에 증명사진 첨부 (표준). 공기업·블라인드 채용은 제외.",
        "personal": "이름(한글+한자), 생년월일, 연락처, 이메일, 주소. 결혼여부 선택.",
        "sections": ["인적사항 (증명사진 포함)", "학력사항", "경력사항", "자격증·어학 (TOEIC/OPIc 점수)", "수상·대외활동", "자기소개서"],
        "cover": "자기소개서 필수. 4항목: 성장과정 · 성격의장단점 · 지원동기 · 입사후포부. 기업별 맞춤 작성. 800–1500자.",
        "tone": "겸손·성실·조직적응력 강조. '저는 혼자서 해냈습니다' 식 개인주의 표현 지양.",
        "length": "이력서 1–2페이지 + 자기소개서 별도",
        "avoid": "캐주얼 어투, 미국식 자기과시, 반말, 이모지",
        "ats": "사람인·잡코리아·원티드 파싱. 인적사항은 레이블-값 테이블 형식 유지.",
    },
    "us": {
        "label": "🇺🇸 USA",
        "doc": "Resume",
        "lang": "English (US)",
        "flag": "🇺🇸",
        "photo": "NEVER. No age, no marital status, no nationality — anti-discrimination law.",
        "personal": "Name, City+State only (no full address), phone, email, LinkedIn, GitHub.",
        "sections": ["Header + contact", "Summary (2–3 lines, optional)", "Experience (reverse-chron, XYZ bullets)", "Skills", "Education", "Certifications / Projects"],
        "cover": "No essay inside resume. Separate optional 1-page cover letter.",
        "tone": "Direct, confident, results-first. Strong verbs + quantified impact. 'I' is implied, never written.",
        "length": "STRICTLY 1 page (<10 yrs). 2 pages max for senior.",
        "avoid": "Photo, DOB, marital status, 'References available on request', paragraphs.",
        "ats": "Single-column, standard headings, no tables/text-boxes/graphics. PDF or .docx.",
    },
    "singapore": {
        "label": "🇸🇬 Singapore",
        "doc": "Resume",
        "lang": "English (British spelling)",
        "flag": "🇸🇬",
        "photo": "Optional, commonly accepted. Clean professional headshot is fine.",
        "personal": "Name, contact, NATIONALITY + work-pass status (EP/SP/PR/Citizen) — mandatory. Notice period and expected salary commonly included.",
        "sections": ["Personal particulars (nationality/residency)", "Career summary", "Work experience (metrics-driven)", "Education & professional qualifications", "Skills & languages", "Notice period / availability"],
        "cover": "No essay. Optional short cover letter.",
        "tone": "Achievement-oriented like US, but personal particulars (nationality, salary, notice) are expected and not taboo.",
        "length": "1–2 pages.",
        "avoid": "Omitting work-pass / nationality status (instant red flag).",
        "ats": "MyCareersFuture, JobStreet, LinkedIn. British spelling (organise, programme).",
    },
    "france": {
        "label": "🇫🇷 France",
        "doc": "CV + Lettre de motivation",
        "lang": "French (Français)",
        "flag": "🇫🇷",
        "photo": "Photo professionnelle en haut à droite — norme habituelle.",
        "personal": "Prénom Nom, ville, téléphone, email. Permis de conduire si pertinent.",
        "sections": ["État civil + coordonnées (+ photo)", "Titre / accroche (poste visé)", "Expérience professionnelle (anti-chronologique)", "Formation (diplômes — Bac+5, grandes écoles)", "Compétences (techniques + outils)", "Langues (niveaux: courant/bilingue/B2…)", "Centres d'intérêt"],
        "cover": "Lettre de motivation ESSENTIELLE. Format: vous → moi → nous. 1 page formelle.",
        "tone": "Formel, structuré, valorisation du diplôme et de l'école. Français soigné.",
        "length": "1 page fortement conseillé (2 max senior).",
        "avoid": "Ton familier, lettre de motivation absente, anglicismes inutiles.",
        "ats": "APEC, Indeed FR, Welcome to the Jungle, LinkedIn. Tout en français.",
    },
    "uk": {
        "label": "🇬🇧 UK",
        "doc": "CV",
        "lang": "English (British spelling)",
        "flag": "🇬🇧",
        "photo": "Never. Same anti-discrimination stance as US.",
        "personal": "Name, city, phone, email, LinkedIn. No DOB, no marital status.",
        "sections": ["Header + contact", "Personal statement (3–4 line profile)", "Key skills (optional)", "Work experience (achievement bullets)", "Education & qualifications", "References: 'Available on request'"],
        "cover": "Separate cover letter common, not embedded.",
        "tone": "Professional, achievement-oriented, slightly more reserved than US. British spelling.",
        "length": "2 pages is the UK standard (not 1 like US).",
        "avoid": "US spelling, photo, personal data, American date format (MM/DD).",
        "ats": "Indeed UK, Reed, Totaljobs, LinkedIn. British spelling throughout.",
    },
    "germany": {
        "label": "🇩🇪 Germany",
        "doc": "Lebenslauf + Anschreiben",
        "lang": "German (Deutsch)",
        "flag": "🇩🇪",
        "photo": "Bewerbungsfoto expected — professional studio headshot, top-right.",
        "personal": "Name, Anschrift, Geburtsdatum, Kontakt. Nationality if work permit relevant.",
        "sections": ["Persönliche Daten (+ Foto)", "Berufserfahrung (anti-chronologisch)", "Ausbildung / Studium", "Kenntnisse & Fähigkeiten (Sprachen, IT)", "Weiterbildung / Zertifikate", "Ort, Datum + Unterschrift (signed & dated — mandatory)"],
        "cover": "Anschreiben essentiell et formel. CV tabular and factual.",
        "tone": "Präzise, vollständig, sachlich. Lücken müssen erklärt werden.",
        "length": "Lebenslauf 1–2 Seiten, tabellarisch.",
        "avoid": "Unexplained gaps, unsigned CV, marketing fluff.",
        "ats": "StepStone, Xing, LinkedIn, Indeed DE. Deutsch throughout.",
    },
}

REGION_ORDER = ["korea", "us", "singapore", "france", "uk", "germany"]


def build_prompt(region_key: str) -> str:
    r = REGIONS[region_key]
    sections = "\n".join(f"   {i+1}. {s}" for i, s in enumerate(r["sections"]))
    needs_cover = any(w in r["cover"].lower() for w in ["essential", "essentielle", "essentiell", "필수"])
    cover_section = f"""
## ✅ {("자기소개서" if region_key == "korea" else "LETTRE DE MOTIVATION" if region_key == "france" else "ANSCHREIBEN" if region_key == "germany" else "COVER LETTER")}
Provide the complete, ready-to-use cover document required for this market.
""" if needs_cover else ""

    return f"""\
You are a native expert in the {r['label']} job market. You write résumés that pass local ATS
and impress local recruiters — because you know the exact conventions they expect.
A résumé that wins in one country gets auto-rejected in another. You fix that.

TARGET MARKET: {r['label']}
DOCUMENT: {r['doc']}
OUTPUT LANGUAGE: {r['lang']} (write the résumé in this language)

REGIONAL RULES (non-negotiable):
• PHOTO: {r['photo']}
• PERSONAL DETAILS: {r['personal']}
• REQUIRED SECTIONS (in this order):
{sections}
• COVER LETTER / SELF-INTRO: {r['cover']}
• TONE: {r['tone']}
• LENGTH: {r['length']}
• AVOID: {r['avoid']}
• ATS / PORTALS: {r['ats']}

OUTPUT FORMAT — use these exact sections:

## ✅ LOCALISED {r['doc'].upper()}
Complete, ready-to-paste résumé in {r['lang']}.
Use clean markdown. Write [사진 / Photo here] where a photo placeholder belongs.
For any data the candidate hasn't provided that this market REQUIRES, write [NEEDS: description]
— never invent facts.
{cover_section}
## 🌍 WHAT I CHANGED & WHY
Bullet list of key localisation decisions vs a generic résumé — what was added, removed,
reformatted, and why this market requires it. Educate the candidate.

## ⚠️ COMPLETE BEFORE SENDING
List every [NEEDS: ...] placeholder so the candidate knows exactly what to fill in.
"""
