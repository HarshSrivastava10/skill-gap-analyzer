from sentence_transformers import SentenceTransformer
import pandas as pd
import streamlit as st


from Modules.skill_extractor import extract_skills 
from Modules.explainability import enrich_skills_with_explanations
from Modules.gap_analysis import generate_roadmap, prioritize_skills


@st.cache_data
def load_data():
    skills_df = pd.read_csv("data/skills.csv")
    roles_df = pd.read_csv("data/roles.csv")
    resources_df = pd.read_csv("data/resources.csv")
    return skills_df,roles_df,resources_df

skills_df, roles_df, resources_df = load_data()

copy_roles = roles_df.copy()
copy_roles = copy_roles["role"]
unique_roles = []
for r in copy_roles:
    if r not in unique_roles:
        unique_roles.append(r)
    
#HELPER FUNCTIONS 

def get_skill_set_for_role(role, roles_df):
    role = role.strip().lower()
    roles_df["role"] = roles_df["role"].str.strip().str.lower()
    return roles_df[roles_df["role"] == role]["skill"].tolist()


def build_skill_meta(skills_df):
    skill_meta = {}

    for _, row in skills_df.iterrows():
        depends = (
            [d.strip() for d in row["depends_on"].split(",")]
            if isinstance(row["depends_on"], str)
            else []
        )

        skill_meta[row["skill"].strip()] = {
            "level": row["level"].strip(),
            "depends_on": depends
        }

    return skill_meta

# print(build_skill_meta())
def get_resources(skill, resources_df):
    skill = skill.strip().lower()
    resources_df["skill"] = resources_df["skill"].str.strip().str.lower()

    return resources_df[resources_df["skill"] == skill]["resource"].tolist()


SKILL_META = build_skill_meta(skills_df)

def confidence_label(score):
    if score>=0.80:
        return "High"
    if score >= 0.60:
        return "Medium"
    return "Low"

def confidence_color(level):
    return {
      "High": "🟢",
        "Medium": "🟡",
        "Low": "🟠"
    }[level]

#LOADING MODEL SAFELLY

@st.cache_resource
def load_model():
    return SentenceTransformer("all-mpnet-base-v2")

model = load_model()

#UI ROLE SELECTION

st.set_page_config(page_title="AI SKILL GAP ANALYZER", layout="wide")

st.title("AI SKILL GAP ANALYZER")
st.write("Analyze your resume against a job description and get a personalized learning roadmap.")

st.header("ENTER DETAILS: ")

resume_text = st.text_area(
    "Paste your Resume Text here",
    height=200,
    placeholder="Enter your resume content..."
)

job_description = st.text_area(
    "Paste Job Description here",
    height=200,
    placeholder="Enter the job description..."
)

ROLE = st.selectbox(
    "Select Target Role",
    unique_roles
)

analyze_btn = st.button("Analyze Skill Gap")

if analyze_btn:
    if not resume_text or not job_description or not ROLE:
        st.warning("Please provide both resume and job description.")
        st.stop()

    
    st.success("ANALYZING...")
    
    skill_set = get_skill_set_for_role(ROLE, roles_df)

    resume_skills = list({s["skill"]: s for s in extract_skills(
        resume_text, 
        skill_set, 
        model, 
        k=8,
        r_cut=0.65)}.values())

    job_skills = list({s["skill"]: s for s in  extract_skills(
        job_description, 
        skill_set, 
        model, 
        k=8,
        r_cut=0.80)}.values())

    
    # Skill Gap

    resume_skill_names = {s["skill"] for s in resume_skills}

    job_skill_names = {s["skill"] for s in job_skills}

    missing_skill_names = job_skill_names - resume_skill_names

    missing_skills = [
        s for s in job_skills if s["skill"] in missing_skill_names
    ]


    # Explain
    missing_enriching_skills = enrich_skills_with_explanations(missing_skills)

    # Roadmap
    prioritized = prioritize_skills(missing_skills, SKILL_META)

    roadmap = generate_roadmap(
        prioritized,
        lambda skill: get_resources(skill, resources_df)
        )


    st.write("DEBUG — Resume Skills:", resume_skill_names)
    st.write("DEBUG — Job Skills:", job_skill_names)
    st.write("DEBUG — Missing Skills:", missing_skill_names)


    # DISPLAY
    st.subheader("✅ Skills You Have")
    for skills in resume_skills:
        level = confidence_label(skills['score'])
        icon = confidence_color(level)
        st.markdown(
            f"- **{skills['skill']} ** - {icon} * {level} confidence"
        )
        

    st.subheader("❌ Skills You Need")

    if not missing_enriching_skills:
        st.markdown("Already acquired the skills requiured for this job...")

    else:
        for s in missing_enriching_skills:
            level = confidence_label(s["score"])
            icon = confidence_color(level)

            st.markdown(f"""
            **{s['skill'].title()}**

            Confidence: {icon} *{level}*  
            _reason_: This skill is required in the Job Description but not found in your resume.

            **Evidence from JD:**  
            > {s.get('evidence', 'N/A')}
            """)
    
    st.subheader("Learning Roadmap")
    for step in roadmap:
        st.markdown(f"**{step['title']}**")
        if step.get("depends_on"):
            st.markdown(f"↳ *Prerequisites:* {', '.join(step['depends_on'])}")

        if step.get("resources"):
            for r in step["resources"]:
                st.markdown(f"• {r}")