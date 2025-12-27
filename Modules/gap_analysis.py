"""
This file is for decision logic.
"""

def find_skill_gap(resume_skills, job_skills):
    """
    Identify skills required by the job but missing from the resume.
    """
    resume_skill_names = {s["skill"] for s in resume_skills}
    job_skill_names = {s["skill"] for s in job_skills}

    missing = job_skill_names - resume_skill_names
    return list(missing)

def prioritize_skills(missing_skill, SKILL_META):
    level_score = {
        "foundation": 3,
        "intermediate": 2,
        "advanced": 1
    }

    prioritized = []

    for skill in missing_skill:
        meta = SKILL_META.get(skill['skill'])

        if not meta:
            continue

        score = level_score[meta["level"]]

        prioritized.append(
            {
                "skill":skill['skill'],
                "level": meta["level"],
                "priority_score": score,
                "depends_on": meta["depends_on"]
            }
        )
        

    prioritized.sort(key = lambda x : x["priority_score"], reverse=True)

    return prioritized


def generate_roadmap(required_skills, get_resources):
    roadmap = []

    for idx, item in enumerate(required_skills, start = 1):
        step = f"{idx}. Learn {item['skill'].title()} ({item['level']})"
        if item['depends_on']:
            step += f" -- after {', '.join(item['depends_on'])}"
        
        key = item["skill"].lower().strip()
        resources = get_resources(key)

        if resources== "" or resources is None or not resources:
            continue

        else:
            step += f"\nResources: "
            for x in resources:
                step += f"- {x}"
        roadmap.append(step)

    return roadmap
