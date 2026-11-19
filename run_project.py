import os, pathlib, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parent
subprocess.run([sys.executable, str(ROOT/"python"/"generate_project_data.py")], check=True)
print("\nNext: run sql/schema.sql and then sql/data.sql in pgAdmin.")
print("Then run sql/queries.sql and the Jupyter notebook.")
