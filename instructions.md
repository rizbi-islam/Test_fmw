# Step 1 — Unzip
unzip kwaf_phase1.zip
cd kwaf

# Step 2 — Install dependencies
pip install -r requirements.txt

# Step 3 — Install Playwright browser
playwright install chromium

# Step 4 — Create Excel template
python assets/templates/create_template.py

# Step 5 — Run Phase 1 verification (all 12 checks)
python tests/verify_phase1.py

# Step 6 — Live run
python run.py --list
python run.py --headless


## Phase-2
# Step 1 — Install Phase 2 dependencies
pip install SQLAlchemy pymysql firebase-admin 2captcha-python reportlab streamlit

# Step 2 — Unzip and copy files into your existing kwaf/ folder
# See PHASE2_README.md inside the zip for exact file mapping

# Step 3 — Run Phase 2 verification
python tests/verify_phase2.py

# Step 4 — Test new keywords work
python run.py --list











# Phase 1 must still be 12/12
python tests\verify_phase1.py

# Phase 2 should now be 10/10
python tests\verify_phase2.py



# Phase 1 must still be 12/12
python tests\verify_phase1.py

# Phase 2 should now be 10/10
python tests\verify_phase3.py


streamlit run ui\app.py --server.port=8502


# Phase 4
python run.py --headless --driver playwright --parallel --workers 4
python tests\verify_phase4.py













