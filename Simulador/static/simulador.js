const menu = document.getElementById("menu");
const inputs = document.getElementById("inputs");
const grafica = document.getElementById("chart");
const titulo = document.getElementById("tituloDinamico");
const botones = document.getElementById("botones");
const resultados = document.getElementById("resultados-text");
const boton = document.createElement("button");

menu.addEventListener("change", () => {
    let opcion = menu.value;
    let html_titulo = "";
    let html_inputs = "";

    switch(opcion){
        case "bernu":
            resultados.innerHTML = ""; // Limpiar resultados previos
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
            boton.className = "btn";
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

                mostrarResultados(result.resultados_individuales, result.exitos, result.fracasos);

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
                    marker: { color: '#6c5ce7' }
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
            resultados.innerHTML = ""; // Limpiar resultados previos
            html_titulo = `<h1>Distribución Binomial</h1>`;
            html_inputs = `
                <div class="input">
                    <label>Número de experimentos</label>
                    <input type="text" id="num_experimentos">
                </div>
                <div class="input">
                    <label>Número de pruebas en cada experimento</label>
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

            // Crear el botón dinámicamente
            botones.innerHTML = ""; // Limpiar botones previos
            boton.className = "btn";
            boton.id = "button_bino";
            boton.textContent = "Simular";
            botones.appendChild(boton);

            grafica.innerHTML = "<p>Selecciona una distribución y llena los parámetros para generar la gráfica 📊</p>";
            
            boton.addEventListener("click", async () => {
                const numExp = parseInt(document.getElementById("num_experimentos").value);
                const probExito = parseFloat(document.getElementById("prob_exito").value);
                const numReps = parseInt(document.getElementById("num_reps").value);

                // Llamar a tu API en FastAPI
                const response = await fetch("/binomial", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        num_experimentos: numExp,
                        probabilidad_exito: probExito,
                        num_pruebas: numReps
                    })
                });

                const result = await response.json();

                //limpiar el área de la gráfica antes de dibujar
                grafica.innerHTML = "";

                // Crear el histograma con los datos recibidos
                // 1. Graficar con Plotly
                const trace = {
                    x: result.datos.x,
                    y: result.datos.y,
                    type: "bar",
                    marker: { color: "#6c5ce7" }
                };

                const layout = {
                    title: { text: 'Distribución Binomial', font: { size: 24 } },
                    xaxis: { title: "Número de éxitos", font: { size: 10} },
                    yaxis: { title: "Frecuencia" },
                    bargap: 0.2
                };

                Plotly.newPlot("chart", [trace], layout, {responsive: true});

                // 2. Mostrar resultados como texto
                let html = `
                    <p><strong>Total de experimentos:</strong> ${result.total_experimentos}</p>
                    <p><strong>Total de éxitos:</strong> ${result.total_exitos}</p>
                    <p><strong>Total de fracasos:</strong> ${result.total_fracasos}</p>
                `;

                if (result.total_experimentos <= 100) {
                    html += `<p><strong>Resultados individuales:</strong> ${result.resultados_individuales.join(", ")}</p>`;
                }

                resultados.innerHTML = html;
            }
            );
            break;
        
        case "mult":
            resultados.innerHTML = ""; // Limpiar resultados previos
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
            resultados.innerHTML = ""; // Limpiar resultados previos
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
            resultados.innerHTML = ""; // Limpiar resultados previos
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
            resultados.innerHTML = ""; // Limpiar resultados previos
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

// Hacer la gráfica responsiva
window.addEventListener('resize', () => {
    Plotly.Plots.resize('chart');
});

// Mostrar resultados
function mostrarResultados(datos, exitos, fracasos, limiteIndividual = 100) {
    resultados.innerHTML = ""; // limpiar contenedor
    const numExp = datos.length;

    if (numExp <= limiteIndividual) {
        // Mostrar resultados individuales
        const lista = document.createElement("ul");
        datos.forEach((res, index) => {
            const li = document.createElement("li");
            li.textContent = `Exp ${index + 1}: ${res === 1 ? "Éxito" : "Fracaso"}`;
            lista.appendChild(li);
        });
        resultados.appendChild(lista);
        resultados.innerHTML += `<p>Éxitos: ${exitos}</p><p>Fracasos: ${fracasos}</p>`;
    } else {
        // Mostrar resumen
        resultados.innerHTML = `
            <p>Número de experimentos: ${numExp}</p>
            <p>Éxitos: ${exitos}</p>
            <p>Fracasos: ${fracasos}</p>
        `;
    }
}


