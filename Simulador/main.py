from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from random import random
import os

simulador = FastAPI()

# Montar el directorio 'static' para servir archivos estáticos
simulador.mount("/static", StaticFiles(directory="static"), name="static")

# Serve la página principal
@simulador.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

    

'''
Endpoint para el simulador de Binomial Puntual (Bernoulli)
'''

