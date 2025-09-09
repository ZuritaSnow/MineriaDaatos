// Referencias a elementos del DOM
    const resultados = document.querySelector('.results-content');
    const grafica = document.getElementById('chart');

    // Función para mostrar resultados (adaptada de tu código original)
    function mostrarResultados(resultadosIndividuales, exitos, fracasos) {
      let html = `
        <p><strong>Total de éxitos:</strong> ${exitos}</p>
        <p><strong>Total de fracasos:</strong> ${fracasos}</p>
      `;
      
      if (resultadosIndividuales && resultadosIndividuales.length <= 100) {
        html += `<p><strong>Resultados individuales:</strong> ${resultadosIndividuales.join(", ")}</p>`;
      }
      
      resultados.innerHTML = html;
    }

    // Funcionalidad de navegación
    document.addEventListener('DOMContentLoaded', function() {
      const navItems = document.querySelectorAll('.nav-item');
      const distributionContents = document.querySelectorAll('.distribution-content');
      const panelTitle = document.getElementById('panelTitle');

      const titles = {
        'bernoulli': 'Distribución de Bernoulli',
        'binomial': 'Distribución Binomial',
        'multinomial': 'Distribución Multinomial',
        'exponencial': 'Distribución Exponencial',
        'normal': 'Distribución Normal',
        'gibbs': 'Método de Gibbs'
      };

      navItems.forEach(item => {
        item.addEventListener('click', function() {
          // Remover clase active de todos los items
          navItems.forEach(nav => nav.classList.remove('active'));
          distributionContents.forEach(content => content.classList.remove('active'));

          // Agregar clase active al item seleccionado
          this.classList.add('active');
          
          // Mostrar el contenido correspondiente
          const distribution = this.getAttribute('data-distribution');
          const targetContent = document.getElementById(distribution);
          if (targetContent) {
            targetContent.classList.add('active');
          }

          // Actualizar título
          panelTitle.textContent = titles[distribution] || 'Simulador de Densidades';

          // limpiar gráfica y resultados
          grafica.innerHTML = '<div class="chart-placeholder">📈 Ajusta los parámetros y presiona "Simular" para generar la gráfica</div>';
          resultados.innerHTML = '¡Aquí podrás observar los resultados de la simulación!';
        });
      });

      // Funcionalidad para cada distribución
      Bernoulli();
      Binomial();
      Multinomial();
      Exponential();
      Normal();
      Gibbs();

      // Funcionalidad de los botones de limpiar
      const clearButtons = document.querySelectorAll('.btn-primary');
      clearButtons.forEach(button => {
        if (button.textContent === 'Limpiar') {
          button.addEventListener('click', function() {
            // Limpiar inputs y gráfica
            const activeContent = document.querySelector('.distribution-content.active');
            const inputs = activeContent.querySelectorAll('input');
            inputs.forEach(input => {
              input.value = input.getAttribute('value') || '';
            });
            grafica.innerHTML = '<div class="chart-placeholder">📈 Ajusta los parámetros y presiona "Simular" para generar la gráfica</div>';
            resultados.innerHTML = '¡Aquí podrás observar los resultados de la simulación!';
          });
        }
      });
    });

    // Configuración para Bernoulli
    function Bernoulli() {
      const bernoulliContent = document.getElementById('bernoulli');
      const simulateBtn = bernoulliContent.querySelector('.btn-primary');
      
      if (simulateBtn && simulateBtn.textContent === 'Simular') {
        simulateBtn.addEventListener('click', async () => {
          const numExp = parseInt(document.getElementById('bernoulli-n').value);
          const probExito = parseFloat(document.getElementById('bernoulli-p').value);

          if (!numExp || !probExito) {
            alert('Por favor, completa todos los campos');
            return;
          }

          grafica.innerHTML = '<div class="chart-placeholder">🔄 Generando simulación...</div>';

          try {
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

            // Limpiar el área de la gráfica antes de dibujar
            grafica.innerHTML = "";

            // Crear el histograma 
            const x = result.datos.map(d => d.rango);
            const y = result.datos.map(d => d.freq);

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
          } catch (error) {
            grafica.innerHTML = '<div class="chart-placeholder">❌ Error al generar la simulación</div>';
            console.error('Error:', error);
          }
        });
      }
    }

    // Configuración para Binomial
    function Binomial() {
      const binomialContent = document.getElementById('binomial');
      const simulateBtn = binomialContent.querySelector('.btn-primary');
      
      if (simulateBtn && simulateBtn.textContent === 'Simular') {
        simulateBtn.addEventListener('click', async () => {
          const numExp = parseInt(document.getElementById('binomial-sims').value);
          const probExito = parseFloat(document.getElementById('binomial-p').value);
          const numReps = parseInt(document.getElementById('binomial-n').value);

          if (!numExp || !probExito || !numReps) {
            alert('Por favor, completa todos los campos');
            return;
          }

          grafica.innerHTML = '<div class="chart-placeholder">🔄 Generando simulación...</div>';

          try {
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

            
            grafica.innerHTML = "";

            // Crear el histograma
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

            // Mostrar resultados
            let html = `
              <p><strong>Total de experimentos:</strong> ${result.total_experimentos}</p>
              <p><strong>Total de éxitos:</strong> ${result.total_exitos}</p>
              <p><strong>Total de fracasos:</strong> ${result.total_fracasos}</p>
            `;

            if (result.total_experimentos <= 100) {
              html += `<p><strong>Resultados individuales:</strong> ${result.resultados_individuales.join(", ")}</p>`;
            }

            resultados.innerHTML = html;
          } catch (error) {
            grafica.innerHTML = '<div class="chart-placeholder">❌ Error al generar la simulación</div>';
            console.error('Error:', error);
          }
        });
      }
    }

    // Configuración para Multinomial 
    function Multinomial() {
      const multinomialContent = document.getElementById('multinomial');
      const simulateBtn = multinomialContent.querySelector('.btn-primary');
      
      if (simulateBtn && simulateBtn.textContent === 'Simular') {
        simulateBtn.addEventListener('click', async () => {
          alert('Funcionalidad de Multinomial pendiente de implementar');
        });
      }
    }

    // Configuración para Exponencial
    function Exponential() {
      const expContent = document.getElementById('exponencial');
      const simulateBtn = expContent.querySelector('.btn-primary');
      
      if (simulateBtn && simulateBtn.textContent === 'Simular') {
        simulateBtn.addEventListener('click', async () => {
          const numExp = parseInt(document.getElementById('exponencial-n').value);
          const lambda = parseFloat(document.getElementById('exponencial-lambda').value);

          if (!numExp || !lambda) {
            alert('Por favor, completa todos los campos');
            return;
          }

          grafica.innerHTML = '<div class="chart-placeholder">🔄 Generando simulación...</div>';

          try {
            const response = await fetch("/exponencial", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                num_experimentos: numExp,
                tasa: lambda
              })
            });

            const result = await response.json();

            
            grafica.innerHTML = "";

            // Crear el histograma
            const hist = {
              x: result.valores,
              type: "histogram",
              name: "Frecuencia simulada",
              opacity: 0.6,
              marker: {color: "#3498db"}
            };

            const layout = {
              title: {text: "Distribución Exponencial (Simulada vs Teórica)"},
              xaxis: {title: "x"},
              yaxis: {title: "Frecuencia"},
              barmode: "overlay"
            };

            Plotly.newPlot("chart", [hist], layout, {responsive: true});

            // Mostrar resultados 
            resultados.innerHTML = `
              <h3>Resultados</h3>
              <p><b>Tasa (λ):</b> ${result.tasa}</p>
              <p><b>Total de experimentos:</b> ${result.total_experimentos}</p>
              <p><b>Primeros 10 valores simulados:</b> ${result.valores.slice(0, 10).map(v => v.toFixed(3)).join(", ")} ...</p>
            `;
          } catch (error) {
            grafica.innerHTML = '<div class="chart-placeholder">❌ Error al generar la simulación</div>';
            console.error('Error:', error);
          }
        });
      }
    }

    // Configuración para Normal
    function Normal() {
      const normalContent = document.getElementById('normal');
      const simulateBtn = normalContent.querySelector('.btn-primary');
      
      if (simulateBtn && simulateBtn.textContent === 'Simular') {
        simulateBtn.addEventListener('click', async () => {
          const numExp = parseInt(document.getElementById('normal-n').value);
          const media = parseFloat(document.getElementById('normal-mu').value);
          const desviacion = parseFloat(document.getElementById('normal-sigma').value);

          if (!numExp || isNaN(media) || !desviacion) {
            alert('Por favor, completa todos los campos');
            return;
          }

          grafica.innerHTML = '<div class="chart-placeholder">🔄 Generando simulación...</div>';

          try {
            const response = await fetch("/normal", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                num_experimentos: numExp,
                media: media,
                desviacion_estandar: desviacion
              })
            });

            const result = await response.json();

            // Limpiar la grafica
            grafica.innerHTML = "";

            
            const valores = result.valores;
            const n = valores.length;
            const sum = valores.reduce((a,b) => a+b, 0);
            const mean = sum / n;
            const variance = valores.reduce((a,b) => a + (b-mean)**2, 0) / n;
            const std = Math.sqrt(variance);
            const min = Math.min(...valores);
            const max = Math.max(...valores);

            // Mostrar resumen
            resultados.innerHTML = `
              <strong>Parámetros ingresados:</strong> <br>
              Media: ${result.media} <br>
              Desviación estándar: ${result.desviacion_estandar} <br>
              Total experimentos: ${result.total_experimentos} <br><br>

              <strong>Estadísticas de la simulación:</strong> <br>
              Media simulada: ${mean.toFixed(2)} <br>
              Desviación estándar simulada: ${std.toFixed(2)} <br>
              Mínimo: ${min.toFixed(2)} <br>
              Máximo: ${max.toFixed(2)}
            `;

            // Crear el histograma 
            const hist = {
              x: result.valores,
              type: "histogram",
              nbinsx: 30,
              name: "Simulación",
              opacity: 0.7,
              marker: { color: "#3498db" }
            };

            const layout = {
              title: "Distribución Normal Simulada",
              xaxis: { title: "Valores" },
              yaxis: { title: "Frecuencia" },
              bargap: 0.2
            };

            Plotly.newPlot("chart", [hist], layout, {responsive: true});
          } catch (error) {
            grafica.innerHTML = '<div class="chart-placeholder">❌ Error al generar la simulación</div>';
            console.error('Error:', error);
          }
        });
      }
    }

    // Configuración para Gibbs 
    function Gibbs() {
      const gibbsContent = document.getElementById('gibbs');
      const simulateBtn = gibbsContent.querySelector('.btn-primary');
      
      if (simulateBtn && simulateBtn.textContent === 'Simular') {
        simulateBtn.addEventListener('click', async () => {
          alert('Fpendiente de implementar');
        });
      }
    }