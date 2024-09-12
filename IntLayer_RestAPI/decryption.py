import logging
import EDEsim
import crud
from fastapi import HTTPException, APIRouter

router_dec = APIRouter()

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