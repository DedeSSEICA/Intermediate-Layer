import psycopg2
import logging
import EDEsim
from textwrap import wrap
from typing import List
from fastapi import HTTPException, APIRouter

router = APIRouter()

def connect_and_log():
    # Set the logging configuration
    logging.basicConfig(filename="std.log", format='%(asctime)s %(message)s', filemode='a')
    logging.info(f"{EDEsim.IPAddr} - Connection info: Database: {EDEsim.database} Username: {EDEsim.username} Host: {EDEsim.host} Port: {str(EDEsim.port)}")
    conn = psycopg2.connect(database=EDEsim.database, user=EDEsim.username, password=EDEsim.password, host=EDEsim.host, port=EDEsim.port)
    return conn

# FUNTION TO DELETE TABLE
# Invoke-RestMethod -Uri "http://127.0.0.1:8000/delete/test5" -Method Delete  
@router.delete("/delete/{table}")
def delete_table(table: str):
    try:
        conn = connect_and_log()
        cursor = conn.cursor()
        query = F"DROP TABLE {table}"
        cursor.execute(query)
        conn.commit()
        cursor.close()
        message = f"Table '{table}' deleted"
        logging.info(f"{EDEsim.IPAddr} - {message}")
        return message
    except Exception as e:
        logging.info(f"{EDEsim.IPAddr} - Attempt to delete table '{table}' failed")
        raise HTTPException(status_code=400, detail=str(e))
    
# FUNCTION TO DELETE ROW
@router.delete("/delete_row/{id}")
def delete_row(table: str, id: int):
    try:
        conn = connect_and_log()
        cursor = conn.cursor()
        table=EDEsim.table
        query = f"DELETE FROM {table} WHERE id = '{id}'"
        cursor.execute(query)
        query = f"ALTER TABLE {table} DROP COLUMN id"
        cursor.execute(query)
        query = f"ALTER TABLE {table} ADD COLUMN id SERIAL PRIMARY KEY"
        cursor.execute(query)
        conn.commit()
        cursor.close()
        message = f"Row with id {id} deleted"
        logging.info(f"{EDEsim.IPAddr} - {message}")
        return message
    except Exception as e:
        logging.info(f"{EDEsim.IPAddr} - Attempt to delete row failed")
        raise HTTPException(status_code=400, detail=str(e))

# FUNCTION TO CREATE TABLE
# $columns = @('column1', 'column2', 'column3')
# $body = ConvertTo-Json -InputObject $columns
# Invoke-RestMethod -Uri "http://127.0.0.1:8000/create/test3" -Method Post -Body $body -ContentType "application/json"
@router.post("/create/{table}")
def create_table(table: str, columns: List[str]):
    conn=connect_and_log()
    try:
        cursor = conn.cursor()
        for i, column in enumerate(columns):
            data_type = "VARCHAR(1000)"
            if i == 0:
                query = "CREATE TABLE IF NOT EXISTS " + table + " ( " + column + " " + data_type
            else:
                query = query + ", " + column + " " + data_type
        
        query = query + " )"
        cursor.execute(query)
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS id SERIAL PRIMARY KEY")
        conn.commit()
        message = f"Table '{table}' created"
        logging.info(f"{EDEsim.IPAddr} - {message}")
        cursor.close()
        return message
    except Exception as e:
        logging.info(f"{EDEsim.IPAddr} - Attempt to create table '{table}' failed")
        raise HTTPException(status_code=400, detail=str(e))

# FUNCTION TO INSERT DATA MANUALLY
# $columns = @('a', 'b', 'c')
# $body = ConvertTo-Json -InputObject $columns
# Invoke-RestMethod -Uri "http://127.0.0.1:8000/insert" -Method Post -Body $body -ContentType "application/json"
@router.post("/insert")
def insert_data(data: List[str]):
    try:
        conn = connect_and_log()
        cursor = conn.cursor()
        table=EDEsim.table
        query = f"INSERT INTO {table} VALUES ({', '.join(['%s'] * len(data))})"
        cursor.execute(query, data)
        conn.commit()
        cursor.close()
        message = f"Data inserted into table '{table}'"
        logging.info(f"{EDEsim.IPAddr} - {message}")
        return message
    except Exception as e:
        logging.info(f"{EDEsim.IPAddr} - Attempt to insert data into table '{table}' failed")
        raise HTTPException(status_code=400, detail=str(e))

# FUNCTION TO UPDATE DATA
# Invoke-RestMethod -Uri "http://127.0.0.1:8000/update/column3/d/1" -Method Put
@router.put("/update/{column}/{new_data}/{id}")
def update_data(column:str, new_data: str, id: int):
    try:
        conn = connect_and_log()
        cursor = conn.cursor()
        table=EDEsim.table
        query = f"UPDATE {table} SET {column} = '{new_data}' WHERE id = '{id}'"
        cursor.execute(query)
        cursor.execute(f"SELECT * FROM {table} WHERE id = '{id}'")
        data = cursor.fetchone()
        conn.commit()
        cursor.close()
        message = f"Table '{table}' updated"
        logging.info(f"{EDEsim.IPAddr} - {message}")
        return message, ' | '.join(map(str, data))
    except Exception as e:
        logging.info(f"{EDEsim.IPAddr} - Attempt to update table '{table}' failed")
        raise HTTPException(status_code=400, detail=str(e))