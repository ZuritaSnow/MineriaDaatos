from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import random
from collections import Counter
import math
import numpy as np
from typing import List


simulador = FastAPI()

# Montar el directorio 'static' para servir archivos estáticos
simulador.mount("/static", StaticFiles(directory="Simulador/static"), name="static")

# Serve la página principal
@simulador.get("/", response_class=HTMLResponse)
async def read_root():
    with open("Simulador/static/index.html", "r", encoding="utf-8") as f:
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
        resultado = random.random()
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
            if random.random() < data.probabilidad_exito:
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
class MultinomialInput(BaseModel):
    n_experimentos: int
    categorias: List[str]
    probabilidades: List[float]

class ProbabilityInput(BaseModel):
    n_experimentos: int
    categorias: List[str]
    probabilidades: List[float]
    frecuencias_deseadas: List[int] 
    
 # Lista de probabilidades para cada evento

def factorial(n):
    """Calcula el factorial de n"""
    if n <= 1:
        return 1
    resultado = 1
    for i in range(2, n + 1):
        resultado *= i
    return resultado

def potencia(base, exponente):
    """Calcula base^exponente usando la función math.pow para mayor precisión"""
    return math.pow(base, exponente)


def coeficiente_multinomial(n, frecuencias):
    """Calcula el coeficiente multinomial: n! / (n1! * n2! * ... * nk!)"""
    numerador = factorial(n)
    denominador = 1
    for freq in frecuencias:
        denominador *= factorial(freq)
    return numerador / denominador



def funcion_densidad_multinomial(n, frecuencias, probabilidades):
    """
    Calcula la función de densidad multinomial evitando overflow con logaritmos.
    """
    # Validaciones
    if sum(frecuencias) != n:
        raise ValueError(f"La suma de frecuencias {sum(frecuencias)} no coincide con n={n}")
    if not math.isclose(sum(probabilidades), 1.0, rel_tol=1e-9):
        raise ValueError("Las probabilidades deben sumar 1")
    if any(p <= 0 for p in probabilidades):
        raise ValueError("Todas las probabilidades deben ser mayores que 0")

    # Calcular en logaritmos: log(n!) - sum(log(ni!))
    log_coef = math.lgamma(n + 1) - sum(math.lgamma(f + 1) for f in frecuencias)

    # Sumar log(p_i^n_i) = n_i * log(p_i)
    log_producto_prob = sum(f * math.log(p) for f, p in zip(frecuencias, probabilidades))

    # Sumar todo en log y convertir a probabilidad normal
    log_prob = log_coef + log_producto_prob
    return math.exp(log_prob)

def simular_multinomial_simple(n_experimentos, probabilidades):
    """Simula experimentos multinomiales"""
    k = len(probabilidades)
    frecuencias = [0] * k
    
    # Crear probabilidades acumuladas
    prob_acumuladas = []
    acum = 0
    for prob in probabilidades:
        acum += prob
        prob_acumuladas.append(acum)
    
    # Simulación
    for _ in range(n_experimentos):
        rand_num = random.random()
        for j, prob_acum in enumerate(prob_acumuladas):
            if rand_num <= prob_acum:
                frecuencias[j] += 1
                break
    
    return frecuencias

def validar_entrada(probabilidades, frecuencias_deseadas=None, n_experimentos=None):
    """Valida los datos de entrada"""
    # Verificar que las probabilidades sumen 1
    suma_prob = sum(probabilidades)
    if not (0.99 <= suma_prob <= 1.01):  # Tolerancia para errores de punto flotante
        return f"Las probabilidades deben sumar 1.0 (suma actual: {suma_prob:.6f})"
    
    # Verificar que todas las probabilidades sean positivas
    if any(p <= 0 for p in probabilidades):
        return "Todas las probabilidades deben ser mayores que 0"
    
    # Si se proporcionan frecuencias deseadas, verificar que sean válidas
    if frecuencias_deseadas is not None and n_experimentos is not None:
        if sum(frecuencias_deseadas) != n_experimentos:
            return f"Las frecuencias deseadas deben sumar {n_experimentos}"
        
        if any(f < 0 for f in frecuencias_deseadas):
            return "Las frecuencias no pueden ser negativas"
    
    return None


def generar_exponencial(n_experimentos=None , tasa: float=None):
    if tasa <= 0:
        raise ValueError("La tasa debe ser un número positivo mayor que 0.")
    
    valores = []
    us = []
    

    # Simulación de la distribución exponencial
    for i in range(n_experimentos):
        u = random.random()  # número uniforme entre 0 y 1
        x = -math.log(1 - u) / tasa  # transformación inversa
        valores.append(x)
        us.append(u)
    return valores, us

def calcular_estadisticas_exponencial(valores: List[float], tasa: float):
    """
    Calcula estadísticas descriptivas y teóricas de la distribución exponencial
    """
    # Estadísticas observadas
    media_observada = sum(valores) / len(valores)
    varianza_observada = sum([(x - media_observada)**2 for x in valores]) / len(valores)
    desviacion_observada = math.sqrt(varianza_observada)
    
    # Estadísticas teóricas
    media_teorica = 1 / tasa
    varianza_teorica = 1 / (tasa ** 2)
    desviacion_teorica = math.sqrt(varianza_teorica)
    
    return {
        "observadas": {
            "media": media_observada,
            "varianza": varianza_observada,
            "desviacion_estandar": desviacion_observada,
            "minimo": min(valores),
            "maximo": max(valores)
        },
        "teoricas": {
            "media": media_teorica,
            "varianza": varianza_teorica,
            "desviacion_estandar": desviacion_teorica
        },
        "comparacion": {
            "error_media": abs(media_observada - media_teorica),
            "error_relativo_media": abs(media_observada - media_teorica) / media_teorica * 100
        }
    }

def generar_densidad_teorica(valores: List[float], tasa: float, num_puntos: int = 1000):
    """
    Genera los puntos para la curva de densidad teórica
    """
    x_max = max(valores)
    x = np.linspace(0, x_max, num_puntos)
    pdf = tasa * np.exp(-tasa * x)
    
    return x.tolist(), pdf.tolist()

def calcular_histograma(valores: List[float], num_bins: int = 30):
    """
    Calcula los datos del histograma para enviar al frontend
    """
    # Crear histograma
    counts, bin_edges = np.histogram(valores, bins=num_bins, density=True)
    
    # Calcular centros de los bins
    bin_centers = [(bin_edges[i] + bin_edges[i+1]) / 2 for i in range(len(bin_edges)-1)]
    
    return {
        "bins": bin_centers,
        "frecuencias": counts.tolist(),
        "bin_edges": bin_edges.tolist()
    }


@simulador.post("/multinomial")
def multinomial(data: MultinomialInput):
    """Endpoint original - simulación básica"""
    try:
        error = validar_entrada(data.probabilidades)
        if error:
            raise HTTPException(status_code=400, detail=error)

        # Realizar simulación
        resultados = simular_multinomial_simple(data.n_experimentos, data.probabilidades)
        esperadas = [data.n_experimentos * p for p in data.probabilidades]

        return {
            "n_experimentos": data.n_experimentos,
            "categorias": data.categorias,
            "frecuencias_observadas": resultados,
            "frecuencias_esperadas": esperadas
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en simulación: {str(e)}")
    

@simulador.post("/calcular-probabilidad")
def calcular_probabilidad(data: ProbabilityInput):
    """Nuevo endpoint - calcula la probabilidad exacta de una configuración específica"""
    data
    # Validar entrada
    error = validar_entrada(data.probabilidades, data.frecuencias_deseadas, data.n_experimentos)
    if error:
        return {"error": error}
    
    try:
        # Calcular probabilidad exacta
        densidad = funcion_densidad_multinomial(
            data.n_experimentos, 
            data.frecuencias_deseadas, 
            data.probabilidades
        )
        
        # Calcular frecuencias esperadas
        frecuencias_esperadas = [data.n_experimentos * p for p in data.probabilidades]
        
        # Calcular coeficiente multinomial para infordatamación adicional
        coef = coeficiente_multinomial(data.n_experimentos, data.frecuencias_deseadas)
        
        # Calcular producto de probabilidades
        producto_prob = 1
        detalles_calculo = []
        for i, (prob, freq) in enumerate(zip(data.probabilidades, data.frecuencias_deseadas)):
            termino = pow(prob, freq)
            producto_prob *= termino
            detalles_calculo.append({
                "categoria": data.categorias[i],
                "probabilidad": prob,
                "frecuencia": freq,
                "termino": f"({prob:.4f})^{freq}",
                "valor": termino
            })
        
        # Interpretar resultado
        interpretacion = {}
        if densidad > 0:
            porcentaje = densidad * 100
            
            uno_en = int(1/densidad)
            
            # Clasificar rareza
            if densidad >= 0.1:
                rareza = "muy común"
            elif densidad >= 0.01:
                rareza = "común"
            elif densidad >= 0.001:
                rareza = "poco común"
            elif densidad >= 0.0001:
                rareza = "raro"
            elif densidad >= 0.00001:
                rareza = "muy raro"
            elif densidad >= 0.000000001:
                rareza = "extremadamente raro"
            else:
                rareza = "casi imposible"
            
            interpretacion = {
                "porcentaje": porcentaje,
                "uno_en": uno_en,
                "rareza": rareza,
                "anos_si_diario": uno_en // 365 if uno_en >= 365 else 0
            }
        else:
            interpretacion = {
                "porcentaje": 0,
                "uno_en": float('inf'),
                "rareza": "imposible",
                "anos_si_diario": 0
            }
        
        return {
            "categorias": data.categorias,
            "n_experimentos": data.n_experimentos,
            "probabilidades": data.probabilidades,
            "frecuencias_deseadas": data.frecuencias_deseadas,
            "frecuencias_esperadas": frecuencias_esperadas,
            "probabilidad_exacta": densidad,
            "coeficiente_multinomial": coef,
            "producto_probabilidades": producto_prob,
            "detalles_calculo": detalles_calculo,
            "interpretacion": interpretacion,
            "calculo_completo": {
                "formula": f"P(X) = {coef:,.0f} × {producto_prob:.6e}",
                "resultado": f"{densidad:.6e}"
            }
        }
        
    except Exception as e:
        return {"error": f"Error en el cálculo: {str(e)}"}

@simulador.post("/simular-verificacion")
def simular_verificacion(data: ProbabilityInput):
    """Endpoint para verificar el resultado teórico mediante simulación"""
        
    # Validar entrada
    error = validar_entrada(data.probabilidades, data.frecuencias_deseadas, data.n_experimentos)
    if error:
        return {"error": error}

    try:
        # Calcular probabilidad teórica
        densidad_teorica = funcion_densidad_multinomial(
            data.n_experimentos, 
            data.frecuencias_deseadas, 
            data.probabilidades
        )
        
        # Determinar número de simulaciones basado en la probabilidad
        if densidad_teorica > 0:
            num_simulaciones = min(50000, max(5000, int(1/densidad_teorica * 10)))
        else:
            num_simulaciones = 10000
        
        # Realizar simulaciones
        contador_exito = 0
        for _ in range(num_simulaciones):
            frecuencias_sim = simular_multinomial_simple(data.n_experimentos, data.probabilidades)
            if frecuencias_sim == data.frecuencias_deseadas:
                contador_exito += 1
        
        probabilidad_simulada = contador_exito / num_simulaciones
        
        # Calcular estadísticas de comparación
        estadisticas = {
            "num_simulaciones": num_simulaciones,
            "exitos_encontrados": contador_exito,
            "probabilidad_simulada": probabilidad_simulada,
            "probabilidad_teorica": densidad_teorica,
            "diferencia_absoluta": abs(probabilidad_simulada - densidad_teorica),
            "error_porcentual": 0 if densidad_teorica == 0 else abs(probabilidad_simulada - densidad_teorica) / densidad_teorica * 100
        }
        
        # Evaluar concordancia
        if densidad_teorica > 0:
            if estadisticas["error_porcentual"] < 10:
                concordancia = "excelente"
            elif estadisticas["error_porcentual"] < 25:
                concordancia = "buena"
            else:
                concordancia = "regular"
        else:
            concordancia = "no aplicable"
        
        estadisticas["concordancia"] = concordancia
        
        return {
            "simulacion": estadisticas,
            "mensaje": f"Simulación completada con {num_simulaciones:,} experimentos"
        }
        
    except Exception as e:
        return {"error": f"Error en la simulación: {str(e)}"}


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
        u = random.random()
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
        u1 = random.random()
        u2 = random.random()
        z0 = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
        x = data.media + data.desviacion_estandar * z0
        valores.append(x)

    return {
        "valores": valores,
        "media": data.media,
        "desviacion_estandar": data.desviacion_estandar,
        "total_experimentos": data.num_experimentos
    }


