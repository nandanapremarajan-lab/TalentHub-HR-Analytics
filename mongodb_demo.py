"""
TalentHub MongoDB demonstration.
Résumé documents are synthetic demonstration documents, not Kaggle rows.
"""
from pymongo import MongoClient, TEXT, ASCENDING
from datetime import datetime

client = MongoClient("mongodb://localhost:27017/")
db = client["talenthub"]
resumes = db["candidate_resumes"]

resumes.delete_many({"source": "talenthub_demo"})
docs = [
    {"candidate_id": 1, "name": "Demo Candidate 001", "skills": ["Python","SQL","Pandas"],
     "education": [{"degree":"MSc Data Science","year":2025}],
     "experience": [{"role":"Data Analyst Intern","years":1}],
     "source":"talenthub_demo", "created_at":datetime.utcnow()},
    {"candidate_id": 2, "name": "Demo Candidate 002", "skills": ["Java","PostgreSQL","Power BI"],
     "education": [{"degree":"BSc Computer Science","year":2024}],
     "experience": [{"role":"BI Trainee","years":1}],
     "source":"talenthub_demo", "created_at":datetime.utcnow()},
]
resumes.insert_many(docs)

# Indexes: candidate ID and searchable skills.
resumes.create_index([("candidate_id", ASCENDING)], unique=True)
resumes.create_index([("skills", TEXT)])

# CRUD: Create, Read, Update, Delete
resumes.insert_one({"candidate_id":3,"name":"Demo Candidate 003","skills":["Excel","SQL"],
                    "education":[],"experience":[],"source":"talenthub_demo"})
print("READ:", list(resumes.find({"skills":"SQL"},{"_id":0})))
resumes.update_one({"candidate_id":3},{"$set":{"skills":["Excel","SQL","Tableau"]}})
print("UPDATED:", resumes.find_one({"candidate_id":3},{"_id":0}))
resumes.delete_one({"candidate_id":3})

# Pipeline 1: most common skills (unwind + group + sort).
pipeline_skills = [
    {"$match":{"source":"talenthub_demo"}},
    {"$unwind":"$skills"},
    {"$group":{"_id":"$skills","candidate_count":{"$sum":1}}},
    {"$sort":{"candidate_count":-1,"_id":1}}
]
print("AGGREGATION 1 — skills:", list(resumes.aggregate(pipeline_skills)))

# Pipeline 2: candidate count by experience band (project + group).
pipeline_exp = [
    {"$match":{"source":"talenthub_demo"}},
    {"$project":{"experience_years":{"$sum":"$experience.years"}}},
    {"$group":{"_id":{"$cond":[{"$lt":["$experience_years",2]},"0-1 years","2+ years"]},
               "candidate_count":{"$sum":1}}}
]
print("AGGREGATION 2 — experience:", list(resumes.aggregate(pipeline_exp)))
client.close()
