============ lOCAL RUN ============

- Install dependencies:
   pip install -r requirements.txt

- Run backend (terminal 1):
   cd backend
   uvicorn main:app --reload

- Run frontend (terminal 2):
   cd frontend
   streamlit run app.py

============ USAGE ============

- Upload CSV file using "Upload .csv file" form
   1) File must contain columns: timestep, consumption_eur, consumption_sib, price_eur, price_sib
   2) ID is generated automatically

- View data: click "Show Dataset"
- Hide data: click: "Hide Dataset"
- Add record: fill "Add new record" form and click "Add record"
- Delete record: enter ID in "Delete existing row" form and click "DELETE"
- Statistics and graphs are displayed automatically when data is available

============ DEPLOY TO RENDER ============

Service ID: srv-d6o613h5pdvs739smjig https://task-02-service.onrender.com

repository: https://github.com/trojan081/hse_IDT  
Language: python 3  
Branch: task_02  
Build command: pip install -r requirements.txt  
Start command: uvicorn main:app --host 0.0.0.0 --port 10000
