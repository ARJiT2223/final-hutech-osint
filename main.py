from fastapi import FastAPI
from fastapi.responses import JSONResponse
import duckdb
import httpx

app = FastAPI(title="Hitek Data API", version="1.0")

# DuckDB connection setup
con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs;")

BASE_URL = "https://huggingface.co/buckets/CutehackX/hitek-data-bucket/resolve/"

FILES = [
    "alt_master_shard_0.parquet",
    "alt_master_shard_1.parquet",
    "alt_master_shard_2.parquet",
    "alt_master_shard_3.parquet",
    "alt_master_shard_4.parquet",
    "alt_master_shard_5.parquet",
    "alt_master_shard_6.parquet",
    "alt_master_shard_7.parquet",
    "alt_master_shard_8.parquet",
    "alt_master_shard_9.parquet",
    "final_master_shard_0.parquet",
    "final_master_shard_1.parquet",
    "final_master_shard_2.parquet",
    "final_master_shard_3.parquet",
    "final_master_shard_4.parquet",
    "final_master_shard_5.parquet",
    "final_master_shard_6.parquet",
    "final_master_shard_7.parquet",
    "final_master_shard_8.parquet",
    "final_master_shard_9.parquet",
]

FILE_URLS = [BASE_URL + f for f in FILES]
COLUMNS = ["mobile", "name", "fname", "address", "alt", "circle", "id", "email"]

@app.get("/")
async def root():
    return {"message": "Hitek Data API is running", "status": "active"}

@app.get("/number/{number}")
async def get_number_info(number: str):
    try:
        # Query banao - saari files me search karo
        # mobile exact match, ya alt/address me partial match
        query = f"""
            SELECT * FROM read_parquet({FILE_URLS})
            WHERE CAST("mobile" AS VARCHAR) = '{number}'
               OR CAST("alt" AS VARCHAR) LIKE '%{number}%'
               OR CAST("address" AS VARCHAR) LIKE '%{number}%'
            LIMIT 1;
        """
        
        result = con.execute(query).fetchall()
        
        if not result:
            return JSONResponse(
                status_code=404,
                content={
                    "status": "error",
                    "message": "No result found for this number",
                    "number": number,
                    "data": None
                }
            )
        
        data_dict = {}
        for i, col in enumerate(COLUMNS):
            val = result[0][i]
            if val is None or str(val).lower() == 'null':
                data_dict[col] = None
            elif isinstance(val, bytes):
                data_dict[col] = val.decode('utf-8', errors='ignore')
            else:
                data_dict[col] = str(val)
        
        return {
            "status": "success",
            "number": number,
            "data": data_dict
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e),
                "number": number,
                "data": None
            }
        )
