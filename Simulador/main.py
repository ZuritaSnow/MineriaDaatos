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

# Define la función objetivo. La hacemos global para que sea fácil de modificar.
def target_function_lineal(x, y):
    """
    Función objetivo f(x, y) = (2x + 3y + 2) / 28.
    Esta función debe ser no negativa en el dominio de muestreo.
    """
    # Añadimos una comprobación para asegurarnos de que el resultado no sea negativo.
    # Si lo es, devolvemos 0, ya que no puede haber probabilidad negativa.
    value = (2 * x + 3 * y + 2) / 28
    return max(0, value)

class GibbsSampler:
    def __init__(self, target_func, x_bounds, y_bounds):
        self.target_function = target_func
        self.x_min, self.x_max = x_bounds
        self.y_min, self.y_max = y_bounds

    def _conditional_sampler(self, fixed_val, is_x_conditional, n_points=1000):
        """Helper unificado para muestrear P(X|Y=y) o P(Y|X=x)."""
        if is_x_conditional:
            # Muestrear X dado Y=fixed_val
            vals = np.linspace(self.x_min, self.x_max, n_points)
            probs = np.array([self.target_function(x, fixed_val) for x in vals])
        else:
            # Muestrear Y dado X=fixed_val
            vals = np.linspace(self.y_min, self.y_max, n_points)
            probs = np.array([self.target_function(fixed_val, y) for y in vals])

        # Normalización para crear una distribución de probabilidad
        probs = np.maximum(probs, 1e-10)  # Evitar probabilidades cero o negativas
        probs_sum = np.sum(probs)
        if probs_sum == 0: # Si todas las probabilidades son cero, devuelve un valor aleatorio en el rango
            return np.random.choice(vals)
        probs /= probs_sum

        # Muestrear un valor de la distribución discreta
        return np.random.choice(vals, p=probs)

    def sample(self, x_init, y_init, n_samples, burn_in=1000):
        total_samples = n_samples + burn_in
        x_samples = np.zeros(total_samples)
        y_samples = np.zeros(total_samples)

        x_samples[0], y_samples[0] = x_init, y_init

        for i in range(1, total_samples):
            # Muestra X dado Y
            x_samples[i] = self._conditional_sampler(y_samples[i-1], is_x_conditional=True)
            # Muestra Y dado X
            y_samples[i] = self._conditional_sampler(x_samples[i], is_x_conditional=False)

        # Descarta el burn-in y devuelve las muestras
        return x_samples[burn_in:], y_samples[burn_in:]

# --- Modelos de Datos (Pydantic) para la API ---

class SamplingParams(BaseModel):
    x_init: float = 1.0
    y_init: float = 1.0
    n_samples: int = 10000
    burn_in: int = 2000
    # Ajustamos los límites por defecto al dominio de interés para esta función
    x_bounds: List[float] = [0.0, 3.0]
    y_bounds: List[float] = [0.0, 2.0]

class SamplingResult(BaseModel):
    x_samples: List[float]
    y_samples: List[float]
    mean_x: float
    std_x: float
    mean_y: float
    std_y: float
    correlation: float

class TargetFunctionGrid(BaseModel):
    x_grid: List[float]
    y_grid: List[float]
    z_grid: List[List[float]]

# --- Endpoints de la API ---

@simulador.post("/sample", response_model=SamplingResult)
def run_sampling(params: SamplingParams):
    """
    Ejecuta el muestreo de Gibbs y devuelve las muestras generadas.
    """
    sampler = GibbsSampler(
        target_func=target_function_lineal,
        x_bounds=tuple(params.x_bounds),
        y_bounds=tuple(params.y_bounds)
    )
    
    x_samples, y_samples = sampler.sample(
        x_init=params.x_init,
        y_init=params.y_init,
        n_samples=params.n_samples,
        burn_in=params.burn_in
    )
    
    # Calcula estadísticas descriptivas
    mean_x = np.mean(x_samples)
    std_x = np.std(x_samples)
    mean_y = np.mean(y_samples)
    std_y = np.std(y_samples)
    correlation = np.corrcoef(x_samples, y_samples)[0, 1] if len(x_samples) > 1 else 0.0
    
    return {
        "x_samples": x_samples.tolist(), "y_samples": y_samples.tolist(),
        "mean_x": np.mean(x_samples), "std_x": np.std(x_samples),
        "mean_y": np.mean(y_samples), "std_y": np.std(y_samples),
        "correlation": np.corrcoef(x_samples, y_samples)[0, 1]
    }

@simulador.post("/target-function-data")
def get_target_function_data(params: SamplingParams):
    """
    Genera una malla de puntos para visualizar la función objetivo en 3D.
    """
    try:
        x_plot = np.linspace(params.x_bounds[0], params.x_bounds[1], 50)
        y_plot = np.linspace(params.y_bounds[0], params.y_bounds[1], 50)
        
        # Llama a la función de Python directamente
        z_plot = [[target_function_lineal(x, y) for x in x_plot] for y in y_plot]
            
        return {
            "x_grid": x_plot.tolist(), "y_grid": y_plot.tolist(), "z_grid": z_plot
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar la superficie: {e}")


'''
Endpoint para el simulador de Normal Bivariada
'''
class NormalBivariadaInput(BaseModel):
    num_experimentos: int
    mu_x: float
    mu_y: float
    sigma_x: float
    sigma_y: float
    rho: float  # coeficiente de correlación

def generar_normal_bivariada(n, mu_x, mu_y, sigma_x, sigma_y, rho):
    """
    Genera muestras de una distribución normal bivariada usando Box-Muller
    """
    valores_x = []
    valores_y = []
    
    for _ in range(n):
        # Generar dos números aleatorios independientes N(0,1)
        u1 = random.random()
        u2 = random.random()
        
        # Box-Muller para generar Z1 y Z2 independientes N(0,1)
        z1 = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
        z2 = math.sqrt(-2 * math.log(u1)) * math.sin(2 * math.pi * u2)
        
        # Transformar a normal bivariada correlacionada
        x = mu_x + sigma_x * z1
        y = mu_y + sigma_y * (rho * z1 + math.sqrt(1 - rho**2) * z2)
        
        valores_x.append(x)
        valores_y.append(y)
    
    return valores_x, valores_y

def calcular_densidad_bivariada_teorica(x_range, y_range, mu_x, mu_y, sigma_x, sigma_y, rho):
    """
    Calcula la función de densidad teórica para una malla de puntos
    """
    # Crear mallas
    X, Y = np.meshgrid(x_range, y_range)
    
    # Calcular determinante de la matriz de covarianza
    det_sigma = sigma_x**2 * sigma_y**2 * (1 - rho**2)
    
    # Constante de normalización
    coef = 1 / (2 * math.pi * math.sqrt(det_sigma))
    
    # Calcular el exponente
    dx = X - mu_x
    dy = Y - mu_y
    
    exponente = -0.5 * (1 / (1 - rho**2)) * (
        (dx**2) / (sigma_x**2) + 
        (dy**2) / (sigma_y**2) - 
        2 * rho * dx * dy / (sigma_x * sigma_y)
    )
    
    # Función de densidad
    Z = coef * np.exp(exponente)
    
    return X.tolist(), Y.tolist(), Z.tolist()

@simulador.post("/normal_bivariada")
async def normal_bivariada(data: NormalBivariadaInput):
    # Validaciones
    if data.sigma_x <= 0 or data.sigma_y <= 0:
        return {"error": "Las desviaciones estándar deben ser mayores que 0"}
    
    if not (-1 <= data.rho <= 1):
        return {"error": "El coeficiente de correlación debe estar entre -1 y 1"}
    
    if data.num_experimentos <= 0:
        return {"error": "El número de experimentos debe ser mayor que 0"}

    try:
        # Generar datos
        valores_x, valores_y = generar_normal_bivariada(
            data.num_experimentos, 
            data.mu_x, 
            data.mu_y, 
            data.sigma_x, 
            data.sigma_y, 
            data.rho
        )
        
        # Calcular estadísticas observadas
        media_x_obs = sum(valores_x) / len(valores_x)
        media_y_obs = sum(valores_y) / len(valores_y)
        
        var_x_obs = sum([(x - media_x_obs)**2 for x in valores_x]) / len(valores_x)
        var_y_obs = sum([(y - media_y_obs)**2 for y in valores_y]) / len(valores_y)
        
        sigma_x_obs = math.sqrt(var_x_obs)
        sigma_y_obs = math.sqrt(var_y_obs)
        
        # Coeficiente de correlación observado
        cov_obs = sum([(valores_x[i] - media_x_obs) * (valores_y[i] - media_y_obs) 
                      for i in range(len(valores_x))]) / len(valores_x)
        rho_obs = cov_obs / (sigma_x_obs * sigma_y_obs)
        
        # Crear malla para la función teórica
        min_x, max_x = min(valores_x), max(valores_x)
        min_y, max_y = min(valores_y), max(valores_y)
        
        # Expandir un poco el rango
        range_x = max_x - min_x
        range_y = max_y - min_y
        
        x_range = np.linspace(min_x - 0.2 * range_x, max_x + 0.2 * range_x, 50)
        y_range = np.linspace(min_y - 0.2 * range_y, max_y + 0.2 * range_y, 50)
        
        # Calcular densidad teórica
        X_teorica, Y_teorica, Z_teorica = calcular_densidad_bivariada_teorica(
            x_range, y_range, data.mu_x, data.mu_y, data.sigma_x, data.sigma_y, data.rho
        )
        
        return {
            "valores_x": valores_x,
            "valores_y": valores_y,
            "parametros": {
                "mu_x": data.mu_x,
                "mu_y": data.mu_y,
                "sigma_x": data.sigma_x,
                "sigma_y": data.sigma_y,
                "rho": data.rho,
                "num_experimentos": data.num_experimentos
            },
            "estadisticas_observadas": {
                "media_x": media_x_obs,
                "media_y": media_y_obs,
                "sigma_x": sigma_x_obs,
                "sigma_y": sigma_y_obs,
                "rho": rho_obs
            },
            "superficie_teorica": {
                "x": X_teorica,
                "y": Y_teorica,
                "z": Z_teorica
            }
        }
        
    except Exception as e:
        return {"error": f"Error en la simulación: {str(e)}"}

