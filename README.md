# Skill Gap Analyzer (Resume vs Job Description)

A semantic skill‑extraction and gap‑analysis tool that compares a resume against a job description, identifies missing skills, and generates a learning roadmap with skill dependencies and resources.

## Features
- Sentence‑level semantic skill extraction
- Ontology + alias + regex normalization
- Missing skill detection
- Learning roadmap with prerequisites and resources
- Streamlit UI

## Tech Stack
- Python
- Sentence Transformers
- Scikit‑Learn
- Streamlit

## Run
pip install -r requirements.txt
streamlit run app.py

## Roadmap
- Role‑aware skill weighting
- Hierarchical skill inference
- TF‑IDF + embedding hybrid extractor
