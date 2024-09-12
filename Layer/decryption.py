import psycopg2
import logging
import EDEsim
import maskpass
import crud
from typing import List
from fastapi import HTTPException, APIRouter
from pydantic import BaseModel

router_dec = APIRouter()

class DecryptionData(BaseModel):
    password: str
# $DecryptionData = @{
#    password = "your_password"
#}
# $body = ConvertTo-Json -InputObject $DecryptionData
# Invoke-RestMethod -Uri "http://127.0.0.1:8000/insert/test3" -Method Put -Body $body -ContentType "application/json"
@router_dec.post("/full_decryption/{table}")
def decrypt_data(table: str, decryption_data: DecryptionData):
    try:
        conn = crud.connect_and_log()
        cursor = conn.cursor()

        # Generate the encrypted search condition
        #print(decryption_data.search_value)
        #cursor.execute(f"SELECT PGP_SYM_ENCRYPT('{decryption_data.search_value}', '{decryption_data.password}') AS encrypted_search_condition")
        #encrypted_search_condition = cursor.fetchone()[0]
        #encrypted_word_hex = encrypted_search_condition.tobytes().hex()
        #print(encrypted_word_hex)
        #print("\xc30d04070302ed0f2286ac1c6e6065d2370108429a35a07932f265a3de4c66bb558fc275d9a0530e2ab9d93a287a1f84191b371b1fd9ec6ba274a55d542934fdcaffa43213fe99d6")
        # Fetch the row that matches the encrypted search condition
        column_names = [desc[0] for desc in cursor.description if desc[0] != 'id']
        column_names = ', '.join(column_names)
        cursor.execute(f"SELECT {column_names} FROM {table} WHERE {decryption_data.encrypted_column} = {decryption_data.search_value}")
        value=cursor.fetchall()
        row=value[0]
        query=f"UPDATE {table} SET ({decryption_data.columns})="
        column_names = column_names.split(', ')
        for i in range(len(decryption_data.columns)): 
            if i == 0:
                query = query + f"(PGP_SYM_DECRYPT(%s::bytea, '{decryption_data.password}')"
            else:
                query = query + f", PGP_SYM_DECRYPT(%s::bytea, '{decryption_data.password}')"
        query = query + f") WHERE {decryption_data.encrypted_column} = {decryption_data.search_value}"
        cursor.execute(query, decryption_data.columns)
        cursor.close()
        
        message = f"Decrypted data fetched from table '{table}'"
        logging.info(f"{EDEsim.IPAddr} - {message}")
        return {"message": "Decrypted data fetched successfully", "data": dict(zip(decryption_data.columns, decrypted_values))}
    except Exception as e:
        logging.info(f"{EDEsim.IPAddr} - Attempt to fetch decrypted data from table '{table}' failed")
        raise HTTPException(status_code=400, detail=str(e))


#Invoke-RestMethod -Uri "http://127.0.0.1:8000/full_decryption/power/2" -Method Post
@router_dec.post("/full_decryption/{password}/{id}")
def decrypt_row(password:str, id:int):
    try:
        conn=crud.connect_and_log()
        cursor = conn.cursor()
        table=EDEsim.table
        cursor.execute(f"SELECT * FROM {table} LIMIT 0")
        column_names = [desc[0] for desc in cursor.description if desc[0] != 'id']
        value=[]
        column_names = ', '.join(column_names)      
        cursor.execute(f"SELECT {column_names} FROM {table} WHERE id = {id}")
        value=cursor.fetchall()
        row=value[0]
        query=f"UPDATE {table} SET ({column_names})="
        column_names = column_names.split(', ')
        for i in range(len(column_names)): 
            if i == 0:
                query = query + f"(PGP_SYM_DECRYPT(%s::bytea, '{password}')"
            else:
                query = query + f", PGP_SYM_DECRYPT(%s::bytea, '{password}')"
        query = query + f") WHERE id = {id}"
        cursor.execute(query, row)
        conn.commit()
        cursor.close()
        message = f"Encrypted data inserted into table '{table}'"
        logging.info(f"{EDEsim.IPAddr} - {message}")
        return message
    except Exception as e:
        logging.info(f"{EDEsim.IPAddr} - Attempt to insert encrypted data into table '{table}' failed")
        raise HTTPException(status_code=400, detail=str(e))