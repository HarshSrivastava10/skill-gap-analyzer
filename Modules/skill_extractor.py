"""
This file is for semantic Understanding
"""
from sklearn.metrics.pairwise import cosine_similarity
import re
import numpy as np

# THIS IS A dict FOR ALIASES
SKILL_ALIASES = {
    "scikit-learn": "scikitlearn",
    "scikitlearn advanced": "scikitlearn",
    "ml libraries scikitlearn": "scikitlearn",
    "ml frameworks scikitlearn": "scikitlearn",
    "frameworks tensorflow": "tensorflow",

    "machine learning engineer": "machine learning",
    "ml engineer": "machine learning",

    "deep learning engineer": "deep learning",

    "business intelligence": "bi",

    # data analysis variations
    "data analytics": "data analysis",
    "advanced data analysis": "data analysis",
    "basic data analysis": "data analysis",
    "data analysis basics": "data analysis",

    # data visualization variations
    "data visualization basics": "data visualization",
    "visualization matplotlib": "data visualization",
    "data visualization matplotlib": "data visualization",

    # statistical variations
    "statistical analysis": "statistics"
}

# THIS IS A set FOR NOISE/IRRELEVANT WORDS
NOISE_TERMS = {
    "bangalore", "bengaluru", "india",
    "remote", "onsite", "hybrid",
    "fresher", "intern", "experience",
    "engineer", "developer", "scientist",
    "data scientist", "analyst", "engineering",
    "intern", "fresher", "experience", "project",
    "projects",
}

# THIS IS A set CONTAINING EXTRA_WORDS
STOPWORDS = {"and", "with", "in", "of", "for", "to", "on"}


# FUNCTION TO MAKE THE WORDS INTO TOKENS, REMOVING STOPWORDS
def tokenize(text):
    return {
        w for w in re.findall(r"[a-zA-Z0-9\+\-]+", text.lower())
        if w not in STOPWORDS and len(w) > 2
    }

def normalize_phrase(text):
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\+\-\.\s]", "", text)
    return text

def apply_regex_aliases(skill):

    PATTERN_ALIAS_RULES = [

    # ---- Python variants ----
    (r"^python (fundamentals|basics|advanced|core)$", "python"),
    (r"^python (programming|language)$", "python"),

    # ---- SQL variants ----
    (r"^sql (basics|fundamentals|advanced)$", "sql"),

    # ---- Data Analysis family ----
    (r"^(basic|advanced) data analysis$", "data analysis"),
    (r"^data analytics$", "data analysis"),
    (r"^data analysis (basic|basics|advanced)$", "data analysis"),


    # ---- Data Visualization family ----
    (r"^(basic|advanced) data visualization$", "data visualization"),
    (r"^data visualization (matplotlib|basics)$", "data visualization"),
    (r"^data visualization (basic|advanced)$", "data visualization"),

    # ---- Machine Learning hierarchy ----
    (r"^ml$", "machine learning"),
    (r"^machine learning (basics|fundamentals|advanced)$", "machine learning"),

    # ---- Deep Learning hierarchy ----
    (r"^dl$", "deep learning"),
    (r"^deep learning (basics|fundamentals|advanced)$", "deep learning"),

    # ---- Scikit‑Learn / sklearn variants ----
    (r"^scikit learn$", "scikit-learn"),
    (r"^scikitlearn$", "scikit-learn"),
    (r"^sklearn$", "scikit-learn"),
    (r"^scikitlearn (advanced|basics)$", "scikit-learn"),

    # ---- TensorFlow / PyTorch family ----
    (r"^tensorflow (basics|advanced)$", "tensorflow"),
    (r"^pytorch (basics|advanced)$", "pytorch"),

    # ---- Feature engineering wording ----
    (r"^advanced feature engineering$", "feature engineering"),
    ]


    for pattern, target in PATTERN_ALIAS_RULES:
        if re.fullmatch(pattern, skill):
            return target
    return skill

def map_to_ontology(phrase, skill_set):
    phrase = normalize_phrase(phrase)

    if phrase in NOISE_TERMS:
        return None
    
    if not looks_like_real_skill(phrase):
        return None
    
    # alias match
    if phrase in SKILL_ALIASES:
        phrase = SKILL_ALIASES[phrase]

    # only accept skills that exist in ontology
    if phrase in skill_set:
        return phrase

    return None

def looks_like_real_skill(phrase):

    words = phrase.split()

    if len(phrase)<3:
        return False

    if len(words) > 3:
        return False
    if phrase in NOISE_TERMS:
        return False
    
    if phrase.isdigit():
        return False
    
    
    return True


def split_into_sentences(text):
    sentences = re.split(r'[.\n]', text)
    return [s.strip() for s in sentences if len(s.strip())>10]

def extract_skills_sentence_level(
        text, 
        skills,
        model,
        top_k=5,
        relative_cutoff=0.75
):
    sentences = split_into_sentences(text)

    if not sentences:
        return []


    sentence_embeddings = model.encode(sentences)
    skill_embeddings = model.encode(skills)

    skill_scores = []

    for skill, skill_emb in zip(skills, skill_embeddings):
        sims = cosine_similarity(
            sentence_embeddings,
            skill_emb.reshape(1,-1)
        ).flatten()

        max_sim = float(np.max(sims))
        best_idx = int(np.argmax(sims))
        best_sentence = sentences[best_idx]

        skill_scores.append({
            "skill": skill,
            "score": round(max_sim, 3),
            "evidence": best_sentence
        })

    skill_scores.sort(key=lambda x: x["score"], reverse=True)

    best_score = skill_scores[0]["score"]
    cutoff = max(best_score * relative_cutoff, 0.35)

    return [
        s for s in skill_scores[:top_k]
        if s["score"]>=cutoff
    ]

def collapse_parent_skills(skills):
    canonical = set(s["skill"] for s in skills)

    collapsed = []

    for s in skills:
        if s["skill"] in canonical:
            # keep only one form
            if not any(x["skill"] == s["skill"] for x in collapsed):
                collapsed.append(s)
    return collapsed


def canonicalize(skill):
    skill = normalize_phrase(skill)
    skill = SKILL_ALIASES.get(skill, skill)
    skill = apply_regex_aliases(skill)
    return skill

def candidate_skills(text, skills):
    text_tokens = tokenize(text)

    candidates = []

    for s in skills:
        skill_tokens = set(s.split())

        if skill_tokens & text_tokens:
            candidates.append(s)
            continue

        joined = " ".join(skill_tokens)
        if joined in text.lower():
            candidates.append(s)
    return candidates

# Keyword Fallback 
def keyword_match_skills(text, skill_set):
    text_norm = normalize_phrase(text)

    matched = []
    for skill in skill_set:
        s_norm = normalize_phrase(skill)

        if s_norm in text_norm:
            matched.append({
                "skill": skill,
                "score": 0.65, # medium confidence baseline
                "evidence": skill
            })
    return matched


# Hybrid Extractor
def extract_skills(t, skill_set, m, k = 8, r_cut=0.75):

    # normalizing + canonicalize onthology
    skill_list = sorted({canonicalize(s) for s in skill_set})
    # CANDIDATES filtering
    candidates = candidate_skills(t, skill_list)


    if not candidates:
        return []
    
    # semantic similarity layer
    raw = extract_skills_sentence_level(
        text=t,
        skills=candidates,
        model=m,
        top_k=k,
        relative_cutoff=r_cut
    )

    # keyword fallback layer
    keyword_hits = keyword_match_skills(t, skill_list)

    # merge by skill name
    combined = {s["skill"]: s for s in (raw + keyword_hits)}.values()

    mapped = []
    for s in combined:
        canon = map_to_ontology(s["skill"], skill_set)

        if canon:
            mapped.append({
                "skill": canon,
                "score": s["score"],
                "evidence": s.get("evidence")
            })

    return collapse_parent_skills(mapped)
