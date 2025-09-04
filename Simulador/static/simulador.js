const menu = document.getElementById("menu");
const inputs = document.getElementById("inputs");
const grafica = document.getElementById("chart");
const titulo = document.getElementById("tituloDinamico");

menu.addEventListener("change", () => {
    let opcion = menu.value;
    let html_titulo = "";
    let html_inputs = "";

    switch(opcion){
        case "bernu":
            html_titulo = `<h1>Distribución de Bernoulli</h1>`;
            html_inputs = `
                <div class="input">
                    <label>Número de experimentos</label>
                    <input type="text" id="num_experimentos">
                </div>
                <div class="input">
                    <label>Probabilidad de éxito</label>
                    <input type="text" id="prob_exito">
                </div>
            `;
    
            grafica.innerHTML = "<p>Selecciona una distribución y llena los parámetros para generar la gráfica 📊</p>";
            // Crear el histograma usando la función
            crearHistograma(datosHistograma);
            break

        case "bino":
            html_titulo = `<h1>Distribución Binomial</h1>`;
            html_inputs = `
                <div class="input">
                    <label>Número de experimentos</label>
                    <input type="text" id="num_experimentos">
                </div>
                <div class="input">
                    <label>Número de repeticiones en cada experimento</label>
                    <input type="text" id="num_reps">
                </div>
                <div class="input">
                    <label>Probabilidad de éxito</label>
                    <input type="text" id="prob_exito">
                </div>
            `;
            grafica.innerHTML = "<p>Selecciona una distribución y llena los parámetros para generar la gráfica 📊</p>";
            break;
        
        case "mult":
            html_titulo = `<h1>Distribución Multinomial</h1>`;
            html_inputs = `
                <div class="input">
                    <label>Categorías (separadas por comas)</label>
                    <input type="text" id="categorias">
                </div>
                <div class="input">
                    <label>Número de experimentos</label>
                    <input type="text" id="num_experimentos">
                </div>
                <div class="input">
                    <label>Probabilidades (separadas por comas)</label>
                    <input type="text" id="probs">
                </div>
            `;
            grafica.innerHTML = "<p>Selecciona una distribución y llena los parámetros para generar la gráfica 📊</p>";
            break;
        
        case "exp":
            html_titulo = `<h1>Distribución Exponencial</h1>`;
            html_inputs = `
                <div class="input">
                    <label>Número de experimentos</label>
                    <input type="text" id="num_experimentos">
                </div>
                <div class="input">
                    <label>Tasa de ocurrencia del evento (λ)</label>
                    <input type="text" id="lambda">
                </div>
            `;
            grafica.innerHTML = "<p>Selecciona una distribución y llena los parámetros para generar la gráfica 📊</p>";
            break;
        
        case "norm":
            html_titulo = `<h1>Distribución Normal</h1>`;
            html_inputs = `
                <div class="input">
                    <label>Número de experimentos</label>
                    <input type="text" id="num_experimentos">
                </div>
                <div class="input">
                    <label>Media (μ)</label>
                    <input type="text" id="media">
                </div>
                <div class="input">
                    <label>Desviación estándar (σ)</label>
                    <input type="text" id="desviacion">
                </div>
            `;
            grafica.innerHTML = "<p>Selecciona una distribución y llena los parámetros para generar la gráfica 📊</p>";
            break;

        case "gibbs":
            html_titulo = `<h1>Método de Gebbs</h1>`;
            html_inputs = `
                <div class="input">
                    <label>Número de experimentos</label>
                    <input type="text" id="num_experimentos">
                </div>
                <div class="input">
                    <label>X0</label>
                    <input type="text" id="X0">
                </div>
                <div class="input">
                    <label>Y0</label>
                    <input type="text" id="Y0">
                </div>
            `;
            grafica.innerHTML = "<p>Selecciona una distribución y llena los parámetros para generar la gráfica 📊</p>";
            break;
    }
    titulo.innerHTML = html_titulo;
    inputs.innerHTML = html_inputs;
});

// Función para crear histograma
function crearHistograma(
  datos,
  colores = ['#ff7675', '#74b9ff', '#55efc4', '#ffeaa7', '#a29bfe', '#fd79a8']
) {
  // Limpiar el contenedor antes de dibujar
  grafica.innerHTML = "";
  grafica.innerHTML = "<h2>Ejemplo de Histograma</h2>";

  new Morris.Bar({
    element: grafica,
    data: datos,
    xkey: 'rango',
    ykeys: ['freq'],
    labels: ['Frecuencia'],
    barColors: colores,
    gridTextSize: 14,
    resize: true,
    hideHover: 'auto'
  });
}


// Datos de ejemplo
const datosHistograma = [
    { rango: "0-10", freq: 5 },
    { rango: "10-20", freq: 8 },
    { rango: "20-30", freq: 12 },
    { rango: "30-40", freq: 20 },
    { rango: "40-50", freq: 10 },
    { rango: "50-60", freq: 7 },
    { rango: "60-70", freq: 3 }
];

