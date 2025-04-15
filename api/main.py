from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncpg
import os
from dotenv import load_dotenv
import ssl
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
app = FastAPI()

# Configuración CORS
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8000",
    "http://127.0.0.1",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:8000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL")
print(f"DEBUG: DATABASE_URL={DATABASE_URL}")  # Debug para verificar carga de variable
conn = None

# Modelo del producto
class Producto(BaseModel):
    nombre_product: str
    categoria_product: str
    precio: int
    stock: int

@app.on_event("startup")
async def startup():
    global conn
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    conn = await asyncpg.connect(DATABASE_URL, ssl=ssl_context)

@app.on_event("shutdown")
async def shutdown():
    await conn.close()

# GET
@app.get("/productos")
async def listar_productos():
    rows = await conn.fetch('SELECT * FROM tabla_productos')
    return [dict(row) for row in rows]

# POST
@app.post("/productos")
async def agregar_producto(producto: Producto):
    try:
        await conn.execute(
            'INSERT INTO tabla_productos (nombre_product, categoria_product, precio, stock) VALUES ($1, $2, $3, $4)',
            producto.nombre_product, producto.categoria_product, producto.precio, producto.stock
        )
        return {"mensaje": "Producto agregado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# PUT
@app.put("/productos/{id}")
async def actualizar_producto(id: int, producto: Producto):
    try:
        result = await conn.execute(
            'UPDATE tabla_productos SET nombre_product=$1, categoria_product=$2, precio=$3, stock=$4 WHERE id=$5',
            producto.nombre_product, producto.categoria_product, producto.precio, producto.stock, id
        )
        if result == "UPDATE 0":
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return {"mensaje": "Producto actualizado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# DELETE
@app.delete("/productos/{id}")
async def eliminar_producto(id: int):
    try:
        result = await conn.execute('DELETE FROM tabla_productos WHERE id=$1', id)
        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return {"mensaje": "Producto eliminado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
