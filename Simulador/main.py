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
#modelo de datos para recibir la entrada del usuario
class BernoulliInput(BaseModel):
    num_experimentos: int
    probabilidad_exito: float

#endpoint para manejar la simulación
@simulador.post("/binomial_puntual")
async def binomial_puntual(data: BernoulliInput):
    exito = 0
    fracaso = 0
    resultados = []
    
    for i in range(data.num_experimentos):
        resultado = random()
        if resultado < data.probabilidad_exito:
            exito += 1
            resultados.append("Exito")
        else:
            fracaso += 1
            resultados.append("Fracaso")
    return {
        "datos": [
            {"rango": "Éxito", "freq": exito},
            {"rango": "Fracaso", "freq": fracaso}
        ],
        "total_experimentos": data.num_experimentos,
    }