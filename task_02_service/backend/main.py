import pandas as pd
from fastapi import FastAPI, status, File, UploadFile, HTTPException
from pydantic import BaseModel, Field, field_validator, model_validator, TypeAdapter
import asyncio
from typing import Annotated, List
from datetime import datetime
import json
from pathlib import Path

app = FastAPI()

# Get the absolute path to data.csv
DATA_FILE = Path(__file__).parent / 'data.csv'

def load_csv()-> pd.DataFrame:
    return pd.read_csv(DATA_FILE)

# DataFrame validation
class DataFrame(BaseModel):
    id: int | None = None
    timestep: datetime
    consumption_eur: float
    consumption_sib: float
    price_eur: float
    price_sib: float
    
    @field_validator('timestep')
    @classmethod
    def validate_timestep(cls, value: datetime)-> datetime:
        if value > datetime.now():
            raise ValueError("Invalid date")
        return value
    
    @field_validator('consumption_eur', 'consumption_sib', 'price_sib', 'price_eur')
    @classmethod
    def validate_float(cls, value: float)-> float:
        if value < 0:
            raise ValueError("Values must be positive")
        return value

DataFrameAdapter = TypeAdapter(List[DataFrame])

class DeleteRequest(BaseModel):
    id: int = Field(ge=0)

@app.get("/records/")
async def get_data()-> list:
    df = load_csv()
    if 'id' not in df.columns:
        df.insert(0, 'id', range(len(df)))
    dict_records = df.to_dict(orient="records")
    return dict_records

@app.post('/upload_file')
async def upload_file(file: UploadFile):
    try:
        df = pd.read_csv(file.file)
        if 'id' not in df.columns:
            df.insert(0, 'id', range(len(df)))
        raw_data = df.to_dict(orient="records")
        valid_data = DataFrameAdapter.validate_python(raw_data)
        df.to_csv(DATA_FILE, index=False)
    except Exception as e:
        print(f'Error loading the csv file')
        raise HTTPException(status_code=400, detail=str(e))
    
    return {
        'status': 200, 
        "data": file.filename
        }

@app.post('/records')
async def add_record(row: dict)-> dict:
    try:
        df = load_csv()
        if 'id' not in df.columns:
            df.insert(0, 'id', range(len(df)))
        if len(df) > 0:
            row['id'] = int(df['id'].max() + 1)
        else:
            row['id'] = 1
        valid_row = DataFrameAdapter.validate_python([row])
        new_row = []
        for model in valid_row:
            m_dict = model.model_dump()
            if isinstance(m_dict['timestep'], datetime):
                m_dict['timestep'] = m_dict['timestep'].strftime('%Y-%m-%d %H:%M')
            new_row.append(m_dict)
        updated_df = pd.concat([df, pd.DataFrame(new_row)], ignore_index=True)
        updated_df.to_csv(DATA_FILE, index=False)
    except Exception as e:
        print(f'Error adding new record')
        raise HTTPException(status_code=400, detail=str(e))

    return {
        'status': 200
        }

@app.delete('/records')
async def delete_record(req: DeleteRequest)-> dict:
    df = load_csv()
    if 'id' not in df.columns:
        df.insert(0, 'id', range(len(df)))
    try:
        if req.id not in df['id'].values:
            raise HTTPException(status_code=404, detail=f"Record with id {req.id} not found")
        df = df[df['id'] != req.id]
        df.to_csv(DATA_FILE, index=False)
    except Exception as e:
        print(f'Error deleting record by id {req.id}')
        raise HTTPException(status_code=400, detail=str(e))
    
    return {
        'status': 200
    }