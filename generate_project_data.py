import csv, random, pathlib, datetime
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "WA_Fn-UseC_-HR-Employee-Attrition.csv"
OUT_SQL = ROOT / "sql" / "data.sql"
random.seed(119)

def q(v):
    if v is None: return "NULL"
    if isinstance(v, (int, float)): return str(v)
    return "'" + str(v).replace("'", "''") + "'"

def main():
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Place WA_Fn-UseC_-HR-Employee-Attrition.csv in {CSV_PATH.parent}. "
            "Download it from the Kaggle URL in README.md."
        )
    with CSV_PATH.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if len(rows) < 500:
        raise ValueError(f"Expected at least 500 Kaggle rows; found {len(rows)}.")
    rows = rows[:500]
    departments = sorted({r["Department"] for r in rows})
    roles = sorted({(r["Department"], r["JobRole"], int(r["JobLevel"])) for r in rows})
    dept_ids = {name:i+1 for i,name in enumerate(departments)}
    role_ids = {role:i+1 for i,role in enumerate(roles)}
    lines = ["-- Generated reproducibly from first 500 rows of Kaggle IBM HR dataset.",
             "-- Recruitment candidate/application/interview rows are synthetic demo data.",
             "BEGIN;"]
    for d, did in dept_ids.items():
        lines.append(f"INSERT INTO departments(department_id,department_name) VALUES ({did},{q(d)});")
    for (d,title,level), pid in role_ids.items():
        lines.append(f"INSERT INTO positions(position_id,department_id,position_title,job_level) VALUES ({pid},{dept_ids[d]},{q(title)},{level});")
    # Employees: actual fields from Kaggle sample, normalized to dimensions above.
    exits = []
    for r in rows:
        eid = int(r["EmployeeNumber"])
        dept = r["Department"]
        role = (dept, r["JobRole"], int(r["JobLevel"]))
        lines.append("INSERT INTO employees(employee_id,department_id,position_id,age,gender,monthly_income,"
                     "job_satisfaction,environment_satisfaction,overtime,years_at_company,total_working_years,attrition) "
                     f"VALUES ({eid},{dept_ids[dept]},{role_ids[role]},{int(r['Age'])},{q(r['Gender'])},"
                     f"{float(r['MonthlyIncome'])},{int(r['JobSatisfaction'])},{int(r['EnvironmentSatisfaction'])},"
                     f"{q(r['OverTime'])},{int(r['YearsAtCompany'])},{int(r['TotalWorkingYears'])},{q(r['Attrition'])});")
        if r["Attrition"] == "Yes":
            exits.append(eid)
    for eid in exits:
        lines.append(f"INSERT INTO exits(employee_id,exit_type,source_label) VALUES ({eid},'Attrition recorded', 'Kaggle Attrition=Yes');")

    # Synthetic recruitment demo data; these are not Kaggle observations.
    education = ["Bachelor's","Master's","Diploma","PhD"]
    channels = ["LinkedIn","Referral","Career Website","Job Portal","Campus"]
    stages = ["Applied","Screening","Interview","Offered","Hired","Rejected"]
    candidates = []
    apps = []
    interviews = []
    for cid in range(1,501):
        candidates.append((cid, f"Demo Candidate {cid:03d}", f"candidate{cid:03d}@example.test",
                           random.choice(education), random.randint(0,15), random.choice(channels)))
        pid = random.choice(list(role_ids.values()))
        appdate = datetime.date(2025,1,1) + datetime.timedelta(days=random.randint(0,364))
        stage = random.choices(stages, weights=[18,18,22,10,12,20])[0]
        apps.append((cid,cid,pid,appdate,stage))
        if stage in ("Interview","Offered","Hired","Rejected"):
            for rnd in range(1, random.randint(2,3)):
                interviews.append((len(interviews)+1,cid,rnd,
                                   random.choice(["Technical","HR","Managerial"]),
                                   random.choice(["Pass","Fail","Pending"]),
                                   appdate + datetime.timedelta(days=random.randint(2,30))))
    for cid,name,email,edu,exp,source in candidates:
        lines.append(f"INSERT INTO candidates VALUES ({cid},{q(name)},{q(email)},{q(edu)},{exp},{q(source)});")
    for aid,cid,pid,dt,stage in apps:
        lines.append(f"INSERT INTO applications(application_id,candidate_id,position_id,application_date,current_stage) VALUES ({aid},{cid},{pid},{q(dt.isoformat())},{q(stage)});")
    for iid,aid,rnd,typ,result,dt in interviews:
        lines.append(f"INSERT INTO interviews VALUES ({iid},{aid},{rnd},{q(typ)},{q(result)},{q(dt.isoformat())});")
    lines += ["COMMIT;"]
    OUT_SQL.write_text("\n".join(lines), encoding="utf-8")
    print("Created", OUT_SQL)
    print("Kaggle employee rows:", len(rows), "| candidates:",len(candidates),
          "| applications:",len(apps),"| interviews:",len(interviews),"| exits:",len(exits))
    print("Synthetic recruitment records are explicitly labelled in the project documentation.")

if __name__ == "__main__":
    main()
