const cabeceraAlicuota = [] // cabecera de la alicuota
let id_vivienda = 0
let monto = 0
let datosCorroPDF
let detalleAlicuota = []; // detalles de las alicuotas
const viviendas = [];

document.addEventListener('DOMContentLoaded', function () {
    fetch(`http://localhost:8000/api/buscar_vivienda/`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken,
        },
    })
        .then(response => response.ok ? response.json() : Promise.reject("Error en la red"))
        .then((data) => {
            if (Array.isArray(data)) {
                viviendas.push(...data);
            } else {
                viviendas.push(data);
            }
        })
        .catch(error => console.error("Error al crear el objeto:", error));
    console.log('Las viviendas se cargaron correctamente.');
    console.log('Viviendas: ', viviendas);
});


function mostrarSugerencias(texto) {
    const sugerencias = document.getElementById('sugerencias');
    sugerencias.innerHTML = '';

    if (texto.length === 0) return; // no mostramos sugerencias si no hay texto

    // filtramos las viviendas que coincidan con lo que ingresamos
    const coincidencias = viviendas.filter(vivienda =>
        vivienda.villa.toLowerCase().includes(texto.toLowerCase())
    );

    // creamos un elemento <li> para cada coincidencia que encontremos
    coincidencias.forEach(vivienda => {
        const item = document.createElement('li');
        item.textContent = vivienda.villa;
        item.classList.add('p-2', 'cursor-pointer', 'hover:bg-gray-100'); // Estilo para el <li>

        // llenamos la informacion cuando hacemos click en una sugerencia
        item.onclick = () => seleccionarVivienda(vivienda);

        sugerencias.appendChild(item);
    });
}

// llenamos los campos cuando hayamos seleccionado una vivienda
function seleccionarVivienda(vivienda) {
    document.getElementById('villa').value = vivienda.villa;
    document.getElementById('nombre').value = vivienda.nombre;
    document.getElementById('cedula').value = vivienda.cedula;
    document.getElementById('correo').value = vivienda.email;
    document.getElementById('costoVivienda').value = vivienda.valor;

    id_vivienda = vivienda.id
    monto = vivienda.valor
    datosCorroPDF = vivienda.email
    console.log('EMAIL RESIDENTE', datosCorroPDF);


    // limpiamos las sugerencias despues de seleccionar la vivienda
    document.getElementById('sugerencias').innerHTML = '';
}
function mostrarAlerta(idAlerta, mensaje) {
    const alerta = document.getElementById(idAlerta);
    const mensajeElemento = alerta.querySelector('span');
    mensajeElemento.textContent = mensaje;

    alerta.classList.remove('hidden'); // Muestra la alerta
    setTimeout(() => {
        alerta.classList.add('hidden'); // Oculta la alerta después de 3 segundos
    }, 3000);
}
function GenerarAlicuota() {
    detalleAlicuota = [];

    let costoVivienda = parseFloat(document.getElementById("costoVivienda").value.replace(',', '.'));
    let periodo = Number(document.getElementById("periodo").value);
    let entrada = document.getElementById("entrada").value;
    let interes = document.getElementById("interes").value;
    let fechaInicial = document.getElementById("fechaInicial").value;  // Obtener la fecha seleccionada

    // // Validar que la fecha seleccionada no sea anterior a la fecha actual
    let fechaActual = moment();  // Fecha actual
    let fechaSeleccionada = moment(fechaInicial, 'YYYY-MM-DD');  // Convertir la fecha seleccionada a un objeto Moment

    // Si la fecha seleccionada es anterior a la fecha actual, mostrar mensaje y detener la ejecución
    if (fechaSeleccionada.isBefore(fechaActual, 'day')) {
      mostrarAlerta('alerta_monto',"La fecha de pago no puede ser anterior a la fecha actual.");
      return;  // Detener la ejecución de la función
    }


    let partesEntrada = entrada.split(',')
    let id_entrada = partesEntrada[0]
    entrada = parseInt(partesEntrada[1].replace('%', '').trim()) / 100

    let partesInteres = interes.split(',')
    let id_interes = partesInteres[0]
    interes = parseInt(partesInteres[1].replace('%', '').trim()) / 100


    if (costoVivienda && periodo && entrada && interes && fechaInicial) {
        // Calcular el pago inicial
        let pagoInicial = costoVivienda * entrada;
        let saldoPendiente = costoVivienda - pagoInicial;

        // Obtener la fecha inicial desde el campo de entrada y convertirla a formato moment
        let fechaPago = moment(fechaInicial, 'YYYY-MM-DD'); // Usar la fecha proporcionada por el usuario
        // fechaPago.add(1, 'days');  // Asumimos que el primer pago es al mes siguiente

        // Limpiar la tabla de pagos antes de agregar nuevos datos
        let tablaPagos = document.getElementById("tablaPagos").getElementsByTagName('tbody')[0];
        tablaPagos.innerHTML = "";  // Limpiar la tabla

        let totalSaldoAPagar = saldoPendiente + (saldoPendiente * interes);
        let totalSaldoPendiente = saldoPendiente + (saldoPendiente * interes);
        let fechas = []; // Para almacenar las fechas de pago

        for (let i = 1; i <= periodo; i++) {
            let totalperiodo = totalSaldoAPagar / periodo;

            // Ajustar la fecha de pago para cada periodo
            fechas[i] = fechaPago.format('YYYY-MM-DD');
            let fechaVencimiento = fechaPago.clone().add(4, 'days').format('YYYY-MM-DD'); // Fecha de vencimiento 4 días después de la fecha de pago

            let recargo = 0;  // Por ahora, no hay recargos

            // Agregar la fila a la tabla de pagos
            tablaPagos.innerHTML += `
        <tr>
            <td class="border border-gray-300 px-4 py-2 text-center">${i}</td>
            <td class="border border-gray-300 px-4 py-2 text-center">${fechas[i]}</td>
            <td class="border border-gray-300 px-4 py-2 text-center">${fechaVencimiento}</td>
            <td class="border border-gray-300 px-4 py-2 text-center">${recargo}</td>
            <td class="border border-gray-300 px-4 py-2 text-center">${totalperiodo.toFixed(2)}</td>
            <td class="border border-gray-300 px-4 py-2 text-center">${totalperiodo.toFixed(2)}</td>
            <td class="border border-gray-300 px-4 py-2 text-center">Pendiente</td>
        </tr>
      `;

            const alicuota = {
                secuencia: i,
                fecha: fechas[i],
                fechaVencimiento: fechaVencimiento,
                recargo: recargo,
                totalPagar: totalperiodo.toFixed(2),
                saldoPendiente: totalperiodo.toFixed(2),
                estado: "Pendiente"
            }

            detalleAlicuota.push(alicuota); // Agregar la alicuota al array

            // Mover la fecha de pago al siguiente mes para la próxima iteración
            fechaPago.add(1, 'month');
        }

        // Cabecera con información general
        const cabecera = {
            vivienda_id: id_vivienda,
            entrada_tasa_id: parseInt(id_entrada),
            Interes_id: parseInt(id_interes),
            saldo_pendiente: parseFloat(totalSaldoAPagar),
            saldo_financiar: parseFloat(totalSaldoAPagar),
            monto: parseFloat(costoVivienda),
            periodo: periodo,
            fecha_pago: fechaInicial,
            fecha_creacion: moment().format('YYYY-MM-DD'),  // Fecha de creación actual
            saldo_pagar: parseFloat(saldoPendiente),
            pago_inicial: parseFloat(pagoInicial),
            interestotal: parseFloat(saldoPendiente * interes)
        }
        cabeceraAlicuota.push(cabecera)
        // Mostrar los valores en la interfaz de usuario
        document.getElementById("pagoInicial").value = `$${pagoInicial.toFixed(2)}`;
        document.getElementById("saldoPendiente").value = `$${totalSaldoPendiente.toFixed(2)}`;
        document.getElementById("saldoPagar").value = `$${totalSaldoAPagar.toFixed(2)}`;
        document.getElementById("interesTotal").value = `$${(saldoPendiente * interes).toFixed(2)}`;
        document.getElementById("monto").value = `$${saldoPendiente.toFixed(2)}`;
        document.getElementById("totalPagos").textContent = `$${totalSaldoAPagar.toFixed(2)}`;
        document.getElementById("totalaPagar").textContent = `$${totalSaldoAPagar.toFixed(2)}`;
        document.getElementById("fechaAlicuota").value = `${fechaInicial}`;

        console.log('Cabecera');
        console.log(cabeceraAlicuota);
        console.log('Detalle');
        console.log(detalleAlicuota);
    } else {
        mostrarAlerta('alerta_ingresar',"Falta información por ingresar.");
    }
}

// funcion para mandar a guardar la alicuota
function CrearAlicuota() {
    console.log(cabeceraAlicuota)
    fetch(`http://localhost:8000/api/crear_alicuota/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken,
        },
        body: JSON.stringify({cabecera: cabeceraAlicuota, pagos: detalleAlicuota}),
    })
        .then((response) => {
            if (!response.ok) {
                // Si la respuesta no es correcta, lanza un error con el mensaje de la respuesta
                return response.json().then(data => {
                    throw new Error(data.error || "Error desconocido");
                });
            }
            return response.json();
        })
        .then((data) => {
            GenerarAlicuotaPDF(data.AlicuotaCreada);
            console.log(data);
            window.location.href = '/alicuota_lista/'
        })
        .catch(error => {
            // Mostrar el mensaje de error que se obtiene del API
            console.error("Error al crear el objeto:", error);
            mostrarAlerta('errorAlerta', error.message); // Muestra el mensaje de error
        });
}

function GenerarAlicuotaPDF(idAlicuota) {
    // Si ambas variables tienen valores, ejecutar la solicitud fetch
    fetch(`http://localhost:8000/api/generar_pdfAlicuota/${idAlicuota}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken,
        },
        body: JSON.stringify({
            email: datosCorroPDF,
            subject: `Alicuota ${idAlicuota} - Creación de Alícuota`,
            message: `Adjunto el PDF con los detalles de la Alicuota ${idAlicuota}.`,
        }),
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error("Error en la red");
            }

            // Crear una URL de objeto para abrir el PDF en una nueva pestaña
            return response.blob(); // Obtiene el archivo binario
        })
        .then((blob) => {
            // Crear un enlace URL del blob para abrir el PDF en una nueva pestaña
            const pdfUrl = URL.createObjectURL(blob);

            // Abrir el PDF en una nueva pestaña
            window.open(pdfUrl, '_blank');
        })
        .catch((error) => {
            console.error("Error al crear el objeto:", error);
        });
}
