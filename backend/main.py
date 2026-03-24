"""Backend module of FastAPI + Streamlit study project (IDT course)."""
from typing import List
from datetime import datetime
from pathlib import Path
import pandas as pd
from fastapi import FastAPI, UploadFile, HTTPException
from pydantic import BaseModel, Field, \
    TypeAdapter, field_validator

app = FastAPI()

# Get the absolute path to data.csv
DATA_FILE = Path(__file__).parent / 'data.csv'


def load_csv() -> pd.DataFrame:
    """Load dataframes.

    Dataframe of .csv format is loaded by default from backend.
    Another dataframe can also be uploaded manually (in method below).

    """
    return pd.read_csv(DATA_FILE)


class DataFrame(BaseModel):
    """Model to validate the dataset before loading."""

    id: int | None = None
    timestep: datetime
    consumption_eur: float
    consumption_sib: float
    price_eur: float
    price_sib: float

    @field_validator('timestep')
    @classmethod
    def validate_timestep(cls, value: datetime) -> datetime:
        """Avoid adding time from the 'future'."""
        if value > datetime.now():
            raise ValueError("Invalid date")
        return value

    @field_validator('consumption_eur',
                     'consumption_sib',
                     'price_sib',
                     'price_eur')
    @classmethod
    def validate_float(cls, value: float) -> float:
        """Negative values are not valid, but 0's are."""
        if value < 0:
            raise ValueError("Values must not be negative")
        return value


DATA_FRAME_ADAPTER = TypeAdapter(List[DataFrame])


class DeleteRequest(BaseModel):
    """Validate int variable being inputted (>= 0)."""

    id: int = Field(ge=0)


@app.get("/records/")
async def get_data() -> list:
    """Read csv file and add 'id' column if needed."""
    df = load_csv()
    if 'id' not in df.columns:
        df.insert(0, 'id', range(len(df)))
    dict_records = df.to_dict(orient="records")
    return dict_records


@app.post('/upload_file')
async def upload_file(file: UploadFile) -> dict:
    """Request to upload a .csv file.

    Manual uploading dataset using 'Upload' button.
    Also adds 'id' column if needed and provides validation.

    """
    try:
        df = pd.read_csv(file.file)
        if 'id' not in df.columns:
            df.insert(0, 'id', range(len(df)))
        raw_data = df.to_dict(orient="records")
        valid_raw_data = DATA_FRAME_ADAPTER.validate_python(raw_data)
        valid_dicts = [val_model.model_dump() for val_model in valid_raw_data]
        valid_df = pd.DataFrame(valid_dicts)
        valid_df.to_csv(DATA_FILE, index=False)
    except Exception as e:
        print('Error loading the csv file')
        raise HTTPException(status_code=400, detail=str(e)) from e

    return {
        'status': 200,
        'data': file.filename
        }


@app.post('/records')
async def add_record(row: dict) -> dict:
    """Request to create new record.

    Also provides validation of data being entered by the user.

    """
    try:
        df = load_csv()
        if 'id' not in df.columns:
            df.insert(0, 'id', range(len(df)))
        if len(df) > 0:
            row['id'] = int(df['id'].max() + 1)
        else:
            row['id'] = 1
        valid_row = DATA_FRAME_ADAPTER.validate_python([row])
        new_row = []
        for model in valid_row:
            m_dict = model.model_dump()
            if isinstance(m_dict['timestep'], datetime):
                m_dict['timestep'] = \
                    m_dict['timestep'].strftime('%Y-%m-%d %H:%M')
            new_row.append(m_dict)
        updated_df = pd.concat([df, pd.DataFrame(new_row)],
                               ignore_index=True)
        updated_df.to_csv(DATA_FILE, index=False)
    except Exception as e:
        print('Error adding new record')
        raise HTTPException(status_code=400, detail=str(e)) from e

    return {
        'status': 200
        }


@app.delete('/records')
async def delete_record(req: DeleteRequest) -> dict:
    """Request to delete row by particular id."""
    df = load_csv()
    if 'id' not in df.columns:
        df.insert(0, 'id', range(len(df)))
    if req.id not in df['id'].values:
        raise HTTPException(status_code=404,
                            detail=f"Record id={req.id} not found")
    try:
        df = df[df['id'] != req.id]
        df.to_csv(DATA_FILE, index=False)
    except Exception as e:
        print(f'Error deleting record by id {req.id}')
        raise HTTPException(status_code=400, detail=str(e)) from e

    return {
        'status': 200
    }
