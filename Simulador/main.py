from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from random import random
from collections import Counter
import math
import numpy as np


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
            resultados.append(1)
        else:
            fracaso += 1
            resultados.append(0)
    return {
        "datos": [
            {"rango": "Éxito", "freq": exito},
            {"rango": "Fracaso", "freq": fracaso}
        ],
        "resultados_individuales": resultados,  # Para mostrar en texto
        "total_experimentos": data.num_experimentos,
        "exitos": exito,
        "fracasos": fracaso
    }

'''
Endpoint para el simulador de Binomial (Bernoulli)
'''
class BinomialInput(BaseModel):
    num_experimentos: int
    probabilidad_exito: float
    num_pruebas: int

@simulador.post("/binomial")
async def binomial(data: BinomialInput):
    resultados = []  # éxitos obtenidos en cada experimento

    for _ in range(data.num_experimentos):
        exitos_en_prueba = 0
        for _ in range(data.num_pruebas):
            if random() < data.probabilidad_exito:
                exitos_en_prueba += 1
        resultados.append(exitos_en_prueba)

    # Conteo de frecuencia de número de éxitos
    conteo_frecuencia = Counter(resultados)
    datos_respuesta = {
        "x": list(conteo_frecuencia.keys()),   # valores de éxitos
        "y": list(conteo_frecuencia.values()) # frecuencias
    }

    total_exitos = sum(resultados)
    total_fracasos = data.num_experimentos * data.num_pruebas - total_exitos

    return {
        "datos": datos_respuesta,
        "resultados_individuales": resultados,
        "total_experimentos": data.num_experimentos,
        "total_exitos": total_exitos,
        "total_fracasos": total_fracasos
    }

'''
Endpoint para el simulador de Multinomial
'''


'''
Endpoint para el simulador de Exponencial
'''
class ExponencialInput(BaseModel):
    num_experimentos: int
    tasa: float  # λ

@simulador.post("/exponencial")
async def exponencial(data: ExponencialInput):
    if data.tasa <= 0:
        return {"error": "La tasa debe ser mayor que 0."}

    valores = []
    us = []

    for _ in range(data.num_experimentos):
        u = random()
        x = -math.log(1 - u) / data.tasa
        valores.append(x)
        us.append(u)

    return {
        "valores": valores,  # datos simulados
        "us": us,
        "tasa": data.tasa,
        "total_experimentos": data.num_experimentos,
    }

'''
Endpoint para el simulador de Normal
'''
class NormalInput(BaseModel):
    num_experimentos: int
    media: float
    desviacion_estandar: float

@simulador.post("/normal")
async def normal(data: NormalInput):
    if data.desviacion_estandar <= 0:
        return {"error": "La desviación estándar debe ser mayor que 0."}

    valores = []

    for _ in range(data.num_experimentos):
        u1 = random()
        u2 = random()
        z0 = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
        x = data.media + data.desviacion_estandar * z0
        valores.append(x)

    return {
        "valores": valores,
        "media": data.media,
        "desviacion_estandar": data.desviacion_estandar,
        "total_experimentos": data.num_experimentos
    }