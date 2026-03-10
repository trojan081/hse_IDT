import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime
import os

API_URL = os.getenv("API_URL", "http://localhost:10000")

# Get the data
@st.cache_data
def get_data()-> pd.DataFrame:
    try:
        response = requests.get(f"{API_URL}/records/", timeout=5)
        response.raise_for_status()
        json_data = response.json()
        data = pd.DataFrame(json_data)
        if 'id' not in data.columns:
            data.insert(0, 'id', range(len(data)))
        return data
    except requests.exceptions.Timeout:
        st.error("--!! ERROR !!--  Backend request time out, check connection")
        return pd.DataFrame()
    except requests.exceptions.ConnectionError:
        st.error("--!! ERROR !!--  Error to connect to http://127.0.0.1:8000, check connection")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"--!! ERROR !!--  Error while loading data: {e}")
        return pd.DataFrame()

data = get_data()
if data.empty:
    st.warning("No data to show. Add some data to see the metrics and graphs.")

def upload_data() -> None:
    uploaded_file = st.session_state.get('uploaded_file')
    if uploaded_file:
        file = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
        response = requests.post(f"{API_URL}/upload_file", files=file)
        st.session_state['upload_response'] = response
        if response.status_code == 200:
            get_data.clear()

# Showing the dataset
if 'show_df' not in st.session_state:
    st.session_state['show_df'] = False

def show_dataset():
        st.session_state['show_df'] = True

def hide_dataset():
        st.session_state['show_df'] = False

def clear_status():
    if 'upload_response' in st.session_state:
        del st.session_state['upload_response']


st.file_uploader("Upload .csv file", type=["csv"], key="uploaded_file", on_change=clear_status)
uploaded_file = st.session_state.get('uploaded_file')
if uploaded_file:
    st.button(label='Upload file', on_click=upload_data)


# Uploaded file response status
if 'upload_response' in st.session_state:
    response = st.session_state['upload_response']
    status_code = response.status_code
    if status_code == 200:
        st.success(f"OK! Status code: {status_code}")
    else:
        st.error(f"--!! ERROR !!--  Upload failed! Status code: {status_code}")
        try:
            error_detail = response.json().get('detail', response.text or 'Unknown error')
        except:
            error_detail = response.text or 'Unknown error'
        st.info(f"Details: {error_detail}")


# Buttons to show/hide dataset
col1, col2 = st.columns(2)
with col1:
    st.button(label='Show Dataset', on_click=show_dataset, width="stretch")
with col2:    
    st.button(label='Hide Dataset', on_click=hide_dataset, width="stretch")


# Show dataset
if st.session_state['show_df'] == True:
    st.dataframe(data, hide_index=True)


# The form to add new row
with st.expander("Add new record"):
    if 'add_status' in st.session_state:
        st.success(st.session_state['add_status'])
        del st.session_state['add_status']
    with st.form("add_row", clear_on_submit=True):
        current_timestep = datetime.now().strftime("%Y-%m-%d %H:%M")
        timestep = st.text_input("Timestep in format yyyy-mm-dd hh:mm", value=current_timestep)
        consumption_eur = st.number_input("Consumption EUR", min_value=0.0)
        consumption_sib = st.number_input("Consumption SIB", min_value=0.0)
        price_eur = st.number_input("Price EUR", min_value=0.0)
        price_sib = st.number_input("Price SIB", min_value=0.0)

        if st.form_submit_button("Add record"):
            new_row = {
                'timestep': timestep,
                'consumption_eur': consumption_eur,
                'consumption_sib': consumption_sib,
                'price_eur': price_eur,
                'price_sib': price_sib
            }
            try:
                response = requests.post(f"{API_URL}/records", json=new_row)
                clear_status()
                status_code = response.status_code
                if status_code == 200:
                    st.session_state['add_status'] = (f"OK! Status code: {response.status_code}")
                    get_data.clear()
                    st.rerun()
                else:
                    try:
                        error_detail = response.json().get('detail', response.text or 'Unknown error')
                    except:
                        error_detail = response.text or 'Unknown error'
                    st.error(f"--!! ERROR !!--  Adding row failed! Status: {status_code}")
                    st.info(f"Details: {error_detail}")
            except Exception as e:
                st.error(f"--!! ERROR !!-- Adding row failed: {str(e)}")


# The form to delete row
with st.expander('Delete existing row'):
    if 'del_status' in st.session_state:
        st.success(st.session_state['del_status'])
        del st.session_state['del_status']
    with st.form('Enter row id:'):
        row_id = st.number_input("Enter valid id", min_value=0)

        if st.form_submit_button("DELETE"):
            try:
                response = requests.delete(f"{API_URL}/records", json={"id": row_id})
                clear_status()
                status_code = response.status_code
                if status_code == 200:
                    st.session_state['del_status'] = (f"OK! Status code: {response.status_code}")
                    get_data.clear()
                    st.rerun()
                else:
                    try:
                        error_detail = response.json().get('detail', response.text or 'Unknown error')
                    except:
                        error_detail = response.text or 'Unknown error'
                    st.error(f"--!! ERROR !!-- Deleting row failed! Status code: {status_code}")
                    st.info(f"Details: {error_detail}")
            except Exception as e:
                st.error(f"--!! ERROR !!--  Deleting row failed: {str(e)}")


# If the data was empty - do not execute the code further
if data.empty:
    st.stop()


# Mean consumption + price
mean_cons_eur = round(data['consumption_eur'].mean(),2)
mean_cons_sib = round(data['consumption_sib'].mean(),2)
mean_price_eur = round(data['price_eur'].mean(),2)
mean_price_sib = round(data['price_sib'].mean(),2)
min_price_eur = round(data['price_eur'].min(),2)
max_price_eur = round(data['price_eur'].max(),2)
min_price_sib = round(data['price_sib'].min(),2)
max_price_sib = round(data['price_sib'].max(),2)


# Table of metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Mean eur consumption", value=mean_cons_eur)
with col2:
    st.metric(label="Mean sib consumption", value=mean_cons_sib)
with col3:
    st.metric(label="Mean eur price", value=mean_price_eur)
with col4:
    st.metric(label="Mean sib price", value=mean_price_sib)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Min eur price", value=min_price_eur) 
with col2:      
    st.metric(label="Max eur price", value=max_price_eur)
with col3:
    st.metric(label="Min sib price", value=min_price_sib)
with col4:
    st.metric(label="Max sib price", value=max_price_sib)


# Graph 1 & 2. Monthly mean EUR consumption
data_graph = data.copy()
data_graph['timestep'] = pd.to_datetime(data_graph['timestep'], format='mixed')
grouped = data_graph.groupby(data_graph['timestep'].dt.month)[['consumption_eur', 'consumption_sib']].mean().reset_index()
fig1 = px.bar(
    grouped, 
    x='timestep', 
    y=['consumption_eur', 'consumption_sib'], 
    title="Monthly mean EUR+SIB consumption",
    labels={'timestep': 'Month'},
    height=350
)

# Monthly mean SIB consumption
grouped = data_graph.groupby(data_graph['timestep'].dt.month)[['price_eur', 'price_sib']].mean().reset_index()

fig2 = px.bar(
    grouped, 
    x='timestep', 
    y=['price_eur', 'price_sib'],
    title="Monthly mean EUR+SIB price",
    labels={'timestep': 'Month'},
    height=350
)

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig1)
with col2:
    st.plotly_chart(fig2)


# Graph 3.Average price by hour in EUR + SIB
grouped = data_graph.groupby(data_graph['timestep'].dt.hour)[['price_eur', 'price_sib']].mean().reset_index()
grouped['price_total'] = grouped['price_eur'] + grouped['price_sib']
fig3 = px.line(
    grouped, 
    x='timestep', 
    y=['price_total'], 
    title="Average price by hour EUR+SIB",
    labels={'timestep': 'Hour', 'price_eur': 'AVG hour price'},
    height=350,
    line_shape='spline',
)
fig3['data'][0]['line']['color']="#e88128"
fig3.update_traces(fill='tozeroy')
st.plotly_chart(fig3)

# Graphs 4 & 5. Consumtion by year graph
colors = ["#D1E6FA", "#A4CFF4", "#78B8EE", "#4BA1E8", "#1F8AE2", "#0B69C2"]
pie_data = data_graph.groupby(data_graph['timestep'].dt.year)[['consumption_eur', 'consumption_sib']].sum().reset_index()
fig4 = px.pie(
    pie_data, 
    values='consumption_eur', 
    names='timestep', 
    title="Consumption EUR by year",
    hole=0.4,
    color_discrete_sequence=colors
)

colors = ["#E0F2F1", "#B2DFDB", "#80CBC4", "#4DB6AC", "#26A69A", "#009688"]
fig5 = px.pie(
    pie_data, 
    values='consumption_sib', 
    names='timestep', 
    title="Consumption SIB by year",
    hole=0.4,
    color_discrete_sequence=colors
)

fig4.update_traces(sort=False)
fig5.update_traces(sort=False)

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig4)
with col2:
    st.plotly_chart(fig5)