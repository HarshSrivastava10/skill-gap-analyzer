"""
This file is for decision logic.
"""

def find_skill_gap(resume_skills, job_skills):
    """
    Identify skills required by the job but missing from the resume.
    """
    resume_skill_names = {s["skill"] for s in resume_skills}
    
    missing = [
        s for s in job_skills
        if s["skill"] not in resume_skill_names
    ]

    return missing


def prioritize_skills(missing_skill, SKILL_META):
    level_score = {
        "foundation": 3,
        "intermediate": 2,
        "advanced": 1
    }

    prioritized = []

    for skill in missing_skill:
        name = skill['skill']
        meta = SKILL_META.get(name)

        if not meta:
            continue

        level = meta.get("level", "foundation")
        score = level_score.get(level, 1)

        prioritized.append(
            {
                "skill":name,
                "level": level,
                "priority_score": score,
                "depends_on": meta.get("depends_on", []),
                "confidence": skill.get("score", None)
            }
        )
        

    prioritized.sort(key = lambda x : x["priority_score"], reverse=True)

    return prioritized


def generate_roadmap(required_skills, get_resources):
    roadmap = []

    for item in required_skills:
        key = item["skill"].lower().strip()
        resources = get_resources(key) or []

        roadmap.append({
            "title": f"Learn {item['skill'].title()}",
            "level": item['level'],
            "depends_on": item.get("depends_on", []),
            "resources": resources
        })

    return roadmap
