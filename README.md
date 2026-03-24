

============ PROJECT STRUCTURE ============
  
task_03_service/  
├── docker-compose.yml  
├── requirements.txt  
├── backend/  
│   ├── Dockerfile  
│   ├── main.py  
│   └── data.csv  
└── frontend/  
    ├── Dockerfile  
    └── app.py  
  
============ LOCAL DEVELOPMENT (WITHOUT DOCKER) ============  
  
1. Create and activate a virtual environment:  
   python -m venv venv  
   source venv/bin/activate  # On Windows use: venv\Scripts\activate  
2. Install dependencies:  
   pip install -r requirements.txt  
3. Run the Backend (FastAPI):  
   uvicorn backend.main:app --host 0.0.0.0 --port 8888 --reload  
4. Run the Frontend (Streamlit) in a new terminal:  
   streamlit run frontend/app.py  
       
============ DOCKER RUN ============

- Install Docker Engine to PC by downloading from official website: https://docs.docker.com/engine/install/
- Go to the main project directory (i.e. task_03_service)
- Run "docker compose up --build" or "docker compose -f docker-compose.yml up --build" (passing yml file explicitly)
- Frontend: Open "Local URL" link from the terminal or simply copy this link and pass to web browser: http://localhost:8889
- Backend: To explore available methods you can look at Swagger docs: http://localhost:8888/docs 
- To shutdown the severs you can use the command: "docker compose down" or simply push "ctrl+c" in terminal window. The default dataset remains unchanged after stopping the server, therefore you can safely provide any changes in the default dataset. Uploaded custom datasets will not be saved after stopping the server.
- To read logs for debugging you can use "docker compose logs" command
  
============ USAGE ============

The default CSV file will be loaded automatically.
However, you can upload a custom file:

- Upload CSV file using "Upload .csv file" form  
   1) File must contain columns: timestep, consumption_eur, consumption_sib, price_eur, price_sib
   2) ID is generated automatically is didn't exist

- View data: click "Show Dataset"
- Hide data: click: "Hide Dataset"
- Add record: fill "Add new record" form and click "Add record"
- Delete record: enter ID in "Delete existing row" form and click "DELETE". ID can be chosen by mouse double-click in the table of dataset and copying (ctrl+c)
- Statistics and graphs are displayed automatically when data is available, they also change dynamically after changing the dataset (adding / deleting records)
  
============ WEB-SERVERS DEPLOYED ON RENDER (remains from the previous task) ============  
  
BACKEND:   
https://task-02-service.onrender.com    
FRONTEND:  
https://task-02-webservice.onrender.com/  

