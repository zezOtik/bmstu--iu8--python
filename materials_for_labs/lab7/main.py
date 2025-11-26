from fastapi import FastAPI
from models.store_models import OrderAdd

app = FastAPI()

@app.get("/")
async def main():
   return {"data": "Hello World"}

@app.post("/add_order")
async def add_order(order: OrderAdd):
   return {"data": order}