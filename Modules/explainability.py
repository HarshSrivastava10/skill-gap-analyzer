"""
This file is for trust and clarity.
"""

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# CONVERT SCORES -> CONFINDENCE SCORES
def confidence_scores(score):
    if score >= 0.25:
        return "High"
    elif score >= 0.18:
        return "Medium"
    else:
        return "Low"

# EXPLAIN 'WHY THIS SKILL MATTERS?'
def explain_skills(skill, score, confidence):
    if confidence == "High":
        return f"{skill.title()} is strongly emphasized in the job requirements"
    elif confidence == "Medium":
        return f"{skill.title()} appears multiple times in the job description but not in your resume"


    else:
        return f"{skill.title()} is mentioned, but with lower emphasis compared to other skills"

prior = {
    0: "Unknown",
    1: "High",
    2: "Medium",
    3: "Low"
}

def enrich_skills_with_explanations(skill_score):
    
    enriched = []

    for item in skill_score:
        score = item["score"]
        confidence = confidence_scores(score)
        explaination = explain_skills(item["skill"], score, confidence)

        enriched.append(
            {
                "skill": item["skill"],
                "score": score,
                "confidence": confidence,
                "explanation": explaination
            }
        )

    return enriched
