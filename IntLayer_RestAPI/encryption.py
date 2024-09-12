import EDEsim
import crud
from typing import List
from fastapi import HTTPException, APIRouter
from pydantic import BaseModel

router_enc = APIRouter()

class EncryptionData(BaseModel):
    password: str
    values: List[str]


# FUNCTION TO ENCRYPT NEW DATA
# $encryptionData = @{
#    password = "power"
#    values = @("value1", "value2", "value3") 
#}
# $body = ConvertTo-Json -InputObject $columns
# Invoke-RestMethod -Uri "http://127.0.0.1:8000/full_encryption" -Method Post -Body $body -ContentType "application/json"
@router_enc.post("/full_encryption")
def encrypt_new_data(encryption_data: EncryptionData):
    try:
        conn=crud.connect_and_log()
        cursor = conn.cursor()
        table = EDEsim.table
        cursor.execute(f"SELECT * FROM {table} LIMIT 0")
        column_names = [desc[0] for desc in cursor.description if desc[0] != 'id']
        value=[]
        column_names = ', '.join(column_names)

        query=f"INSERT INTO {table} ({column_names}) "
        for i, value in enumerate(encryption_data.values): 
            if i == 0:
                query = query + f"VALUES (PGP_SYM_ENCRYPT('{value}', '{encryption_data.password}')"
            else:
                query = query + f", PGP_SYM_ENCRYPT('{value}', '{encryption_data.password}')"
        
        query = query + " )"
        cursor.execute(query)
        conn.commit()
        cursor.close()
        message = f"Encrypted data inserted into table '{table}'"
        return message
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
