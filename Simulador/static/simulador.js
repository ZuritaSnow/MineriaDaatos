const menu = document.getElementById("menu");
const inputs = document.getElementById("inputs");
const grafica = document.getElementById("chart");
const titulo = document.getElementById("tituloDinamico");
const botones = document.getElementById("botones");

menu.addEventListener("change", () => {
    let opcion = menu.value;
    let html_titulo = "";
    let html_inputs = "";

    switch(opcion){
        case "bernu":
            // HTML para título e inputs
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

            // Poner título e inputs en el DOM
            tituloDinamico.innerHTML = html_titulo;
            inputs.innerHTML = html_inputs;

            // Crear el botón dinámicamente
            botones.innerHTML = ""; // Limpiar botones previos
            const boton = document.createElement("button");
            boton.id = "button_bernu";
            boton.textContent = "Simular";
            botones.appendChild(boton);

            // Limpiar el área de la gráfica
            grafica.innerHTML = "<p>Selecciona una distribución y llena los parámetros para generar la gráfica 📊</p>";

            // Asignar evento al botón recién creado
            boton.addEventListener("click", async () => {
                const numExp = parseInt(document.getElementById("num_experimentos").value);
                const probExito = parseFloat(document.getElementById("prob_exito").value);

                // Llamar a tu API en FastAPI
                const response = await fetch("/binomial_puntual", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        num_experimentos: numExp,
                        probabilidad_exito: probExito
                    })
                });

                const result = await response.json();

                //limpiar el área de la gráfica antes de dibujar
                grafica.innerHTML = "";

                // Crear el histograma con los datos recibidos
                // Preparar datos para Plotly
                const x = result.datos.map(d => d.rango);    // ["Éxito", "Fracaso"]
                const y = result.datos.map(d => d.freq);     // [10, 90]

                const trace = {
                    x: x,
                    y: y,
                    type: 'bar',
                    marker: { color: ['#74b9ff', '#ff7675'] }
                };

                const layout = {
                    title: { text: 'Distribución Bernoulli', font: { size: 24 } },
                    xaxis: { title: 'Resultado' },
                    yaxis: { title: 'Frecuencia' },
                };

                Plotly.newPlot('chart', [trace], layout, {responsive: true});
            });
            break;

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
            // Poner título e inputs en el DOM
            tituloDinamico.innerHTML = html_titulo;
            inputs.innerHTML = html_inputs;
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
            // Poner título e inputs en el DOM
            tituloDinamico.innerHTML = html_titulo;
            inputs.innerHTML = html_inputs;
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
            // Poner título e inputs en el DOM
            tituloDinamico.innerHTML = html_titulo;
            inputs.innerHTML = html_inputs;
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
            // Poner título e inputs en el DOM
            tituloDinamico.innerHTML = html_titulo;
            inputs.innerHTML = html_inputs;
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
            // Poner título e inputs en el DOM
            tituloDinamico.innerHTML = html_titulo;
            inputs.innerHTML = html_inputs;
            grafica.innerHTML = "<p>Selecciona una distribución y llena los parámetros para generar la gráfica 📊</p>";
            break;
    }
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

window.addEventListener('resize', () => {
    Plotly.Plots.resize('chart');
});


