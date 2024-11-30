const url = window.location.pathname
const partesUrl = url.split('/')
const id = parseInt(partesUrl[partesUrl.length - 1])
let info_alicuota = {}
let pagos = []
let cliente = {}
let listadClientes = []
// variales para guardar la información para enviar a aguardar el pago
let cabPago = {}
let pagosActualizar = []

let datosCorroPDF

// evento que sirve para obtener la información
document.addEventListener("DOMContentLoaded", function () {

    const urlApi = `http://localhost:8000/api/info_alicuota/${id}`
    fetch(urlApi, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken,
        },
    })
        .then(response => response.ok ? response.json() : Promise.reject("Error en la red"))
        .then((data) => {
            info_alicuota = data[0]
            pagos = data[1]
            listadClientes = data[2]
            console.log('InfoAlicuotas: ', info_alicuota)
            console.log('Pagos: ', pagos)
            console.log('Clientes: ', listadClientes)
        })
        .catch(error => console.error("Error al crear el objeto:", error));
    console.log('JS Cargado correctamente')
});

// funcion para obtener el cliente
function ObtenerCliente(nombre) {
    const sugerencias = document.getElementById('sugerencias');
    sugerencias.innerHTML = '';

    if (nombre.length === 0) return;
    const coincidencias = listadClientes.filter(cliente =>
        (cliente.nombre.toLowerCase().includes(nombre.toLowerCase()) ||
            cliente.cedula.toLowerCase().includes(nombre.toLowerCase())) &&
        cliente.status === false
    );

    coincidencias.forEach(cliente => {
        const item = document.createElement('li');
        item.textContent = `${cliente.nombre} - ${cliente.cedula}`;
        item.classList.add('p-2', 'cursor-pointer', 'hover:bg-gray-100'); // Estilo para el <li>

        item.onclick = () => SeleccionCliente(cliente);
        sugerencias.appendChild(item);
    });
}

// Seleccionar cliente ya creado
function SeleccionCliente(cliente) {
    document.getElementById('nombre').value = cliente.nombre
    document.getElementById('correo').value = cliente.email
    document.getElementById('telefono').value = cliente.telefono
    document.getElementById('cedula').value = cliente.cedula

    // Fecha actual en formato ISO para la cabecera de pago
    const fechaActual = new Date();
    const fecha = fechaActual.toLocaleDateString('en-CA'); // Formato ISO (YYYY-MM-DD)

    cabPago = {
        id_cabalicuotra_id: id,
        id_residentes_id: cliente.id,
        factura: id,
        fecha_creacion: fecha,
    };
    // Asignar el correo del cliente a la variable global para el envío de correo
    datosCorroPDF = cliente.email;  // Aquí se asigna el correo del cliente

    console.log('CABECERA CLIENTE', cabPago);
    console.log('EMAIL CLIENTE', datosCorroPDF);
    // limpiamos las sugerencias despues de seleccionar la vivienda
    document.getElementById('sugerencias').innerHTML = '';
    document.getElementById('inputMonto').classList.remove('hidden');
}

// función para asignar al residente
function ObtenerResidente() {
    console.log(info_alicuota);
    document.getElementById('nombre').value = info_alicuota.nombre
    document.getElementById('correo').value = info_alicuota.email
    document.getElementById('telefono').value = info_alicuota.telefono
    document.getElementById('cedula').value = info_alicuota.cedula
    // Fecha actual en formato ISO para la cabecera de pago
    const fechaActual = new Date();
    const fecha = fechaActual.toLocaleDateString('en-CA'); // Formato ISO (YYYY-MM-DD)

    // Crear el objeto cabPago
    cabPago = {
        id_cabalicuotra_id: id,
        id_residentes_id: info_alicuota.id_residente,
        factura: id,
        fecha_creacion: fecha,
    };
    datosCorroPDF = info_alicuota.email
    console.log('CABECERA', cabPago);
    console.log('EMAIL RESIDENTE', datosCorroPDF);
    document.getElementById('inputMonto').classList.remove('hidden');
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

// funcion para agreagar un nuevo cliente, esto es en caso de que el pago no lo realice el residente
function AgregarCliente() {
    const nombreCliente = document.getElementById('nombre_cliente').value;
    const cedulaCliente = document.getElementById('cedula_cliente').value;
    const telefonoCliente = document.getElementById('telefono_cliente').value;
    const correoCliente = document.getElementById('correo_cliente').value;
    const nombreValido = /^[a-zA-Z\s]+$/.test(nombreCliente);

    const existeCedula = listadClientes.filter(cliente =>
        cliente.cedula === cedulaCliente);
    const existeTelefono = listadClientes.filter(cliente =>
        cliente.telefono === telefonoCliente);
    const existeEmail = listadClientes.filter(cliente =>
        cliente.email === correoCliente);

    // Validación del nombre
    if (!nombreCliente.trim()) {
        mostrarAlerta('alerta_nombre', "El campo Nombre no puede estar vacío.");
        return;
    } else if (!nombreValido) {
        mostrarAlerta('alerta_nombre', "El campo Nombre solo puede contener letras.");
        return;
    }

    // Validación de la cédula
    if (!cedulaCliente.trim()) {
        mostrarAlerta('alerta_cedula', "El campo Cédula no puede estar vacío.");
        return;
    } else if (existeCedula.length > 0) {
        mostrarAlerta('alerta_cedula', "Ya existe un registro con esa cédula.");
        return;
    } else if (!validarCedulaEcuatoriana(cedulaCliente)) {
        return;
    }
    // Validacion de telefono
    if (!telefonoCliente.trim()) {
        mostrarAlerta('alerta_telefono', "El campo Teléfono no puede estar vacío.");
        return; // Detenemos la ejecución si el campo está vacío
    } else if (existeTelefono.length > 0) {
        mostrarAlerta('alerta_telefono', "Ya existe un registro con ese telefono.");
        return; // Detenemos la ejecución si el cliente ya existe
    } else if (/[^\d]/.test(telefonoCliente)) {
        // Detecta si hay letras u otros caracteres que no son números
        mostrarAlerta('alerta_telefono', "El campo Teléfono no permite letras, solo números.");
        return;
    } else if (telefonoCliente.length !== 10) {
        // Verifica si no tiene exactamente 10 dígitos
        mostrarAlerta('alerta_telefono', "El campo Teléfono debe contener exactamente 10 números.");
        return;
    }
    if (!correoCliente.trim()) {
        mostrarAlerta('alerta_correo',"El campo email no puede estar vacío.");
        return; // Detenemos la ejecución si el campo está vacío
    }else if (!correoCliente.trim()) {
        mostrarAlerta('alerta_correo', "El campo email no puede estar vacío.");
        return; // Detenemos la ejecución si el campo está vacío
    } else if (existeEmail.length > 0) {
        mostrarAlerta('alerta_correo', "Ya existe un registro con ese correo.");
        return; // Detenemos la ejecución si el cliente ya existe
    } else {
        // Validar correo (formato correcto)
        const correoValido = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(correoCliente);
        if (!correoValido) {
            mostrarAlerta('alerta_correo', "El campo Email no es válido. Asegúrate de incluir un '@' y un dominio, por ejemplo, usuario@dominio.com.");
            return;
        }
    }


    cliente = {
        nombre: nombreCliente,
        cedula: cedulaCliente,
        telefono: telefonoCliente,
        correo: correoCliente
    }
    console.log(cliente)
    document.getElementById('nombre').value = cliente.nombre
    document.getElementById('correo').value = cliente.correo
    document.getElementById('telefono').value = cliente.telefono
    document.getElementById('cedula').value = cliente.cedula
    document.getElementById('modal-toggle').checked = false;

// Fecha actual en formato ISO para la cabecera de pago
    const fechaActual = new Date();
    const fecha = fechaActual.toLocaleDateString('en-CA'); // Formato ISO (YYYY-MM-DD)

// Crear el objeto cabPago
    cabPago = {
        id_cabalicuotra_id: id,
        factura: id,
        fecha_creacion: fecha,
    };
    // Asignar el correo del cliente a la variable global para el envío de correo
    datosCorroPDF = cliente.correo;  // Aquí se asigna el correo del cliente

    console.log('CABECERA CLIENTE CREADO', cabPago);
    console.log('EMAIL CLIENTE', datosCorroPDF);
    console.log('CABECERA', cabPago);
    document.getElementById('inputMonto').classList.remove('hidden');
}

// Función para validar cédula ecuatoriana y RUC
function validarCedulaEcuatoriana(cedula) {
    // Verifica que solo contenga dígitos
    if (!/^\d+$/.test(cedula)) {
        mostrarAlerta('alerta_cedula', "La identificación debe contener únicamente dígitos numéricos.");
        return false;
    }

    // Validar como cédula ecuatoriana (10 dígitos)
    if (cedula.length === 10) {
        const provincia = parseInt(cedula.substring(0, 2), 10);
        if (provincia < 1 || provincia > 24) {
            mostrarAlerta('alerta_cedula', "Los dos primeros dígitos de la cédula no corresponden a una provincia válida.");
            return false;
        }

        const digitoVerificador = parseInt(cedula[9], 10);
        let suma = 0;

        for (let i = 0; i < 9; i++) {
            let digito = parseInt(cedula[i], 10);
            if (i % 2 === 0) { // Posición par (0, 2, 4, 6, 8)
                digito *= 2;
                if (digito > 9) {
                    digito -= 9;
                }
            }
            suma += digito;
        }

        suma = suma % 10 === 0 ? 0 : 10 - (suma % 10);

        if (suma !== digitoVerificador) {
            mostrarAlerta('alerta_cedula', "La cédula no es válida.");
            return false;
        }
    }
    // Validar como RUC ecuatoriano (13 dígitos)
    else if (cedula.length === 13) {
        const cedulaBase = cedula.substring(0, 10);
        if (!validarCedulaEcuatoriana(cedulaBase)) {
            return false; // Si la cédula base no es válida, el RUC tampoco lo es
        }

        if (cedula.substring(10) !== "001") {
            mostrarAlerta('alerta_cedula', "El RUC no tiene un código válido (debe terminar en '001').");
            return false;
        }
    } else {
        mostrarAlerta('alerta_cedula', "La identificación debe tener 10 dígitos (cédula) o 13 dígitos (RUC).");
        return false;
    }
    return true; // La cédula o RUC es válida
}

// mostrar detalle del monto
function MostrarDetalle(monto) {
    // Convertir monto a número decimal
    monto = parseFloat(monto);

    // Verificar si el monto es válido
    if (isNaN(monto) || monto <= 0) {
        const tablaPagos = document.getElementById('tablaPagos');
        tablaPagos.innerHTML = '';
        return; // Si el monto no es válido, salimos de la función
    }

    // Obtener la tabla donde se mostrarán los pagos
    const tablaPagos = document.getElementById('tablaPagos');
    tablaPagos.innerHTML = '';

    // Crear los encabezados de la tabla
    tablaPagos.innerHTML += `
    <thead>
      <tr class="bg-gray-50">
        <th class="border border-gray-300 px-4 py-2 text-center">Secuencia</th>
        <th class="border border-gray-300 px-4 py-2 text-center">Fecha Vencimiento</th>
        <th class="border border-gray-300 px-4 py-2 text-center">Valor a Pagar</th>
        <th class="border border-gray-300 px-4 py-2 text-center">Recargo</th>
        <th class="border border-gray-300 px-4 py-2 text-center">Subtotal</th>
      </tr>
    </thead>
  `;

    let valor = 0;
    let pagosRealizados = 0;

    // Limpiamos el arreglo de pagosActualizar
    pagosActualizar = [];

    // Filtramos los pagos con estado "Pendiente" o "En curso"
    const pagosPendientesOEnCurso = pagos.filter(pago => pago.estado === 'Pendiente' || pago.estado === 'En curso');

    // Verificar si el monto es mayor que el pago más bajo
    const valorMinimo = Math.min(...pagosPendientesOEnCurso.map(pago => parseFloat(pago.saldo_pagar)));
    const fechaActual = new Date();

    // Calcular el total de todas las letras con recargos
    let totalLetras = 0;

    // Calcular el total incluyendo recargos
    for (let i = 0; i < pagosPendientesOEnCurso.length; i++) {
        const pago = pagosPendientesOEnCurso[i];
        const valorPagar = parseFloat(pago.saldo_pagar);
        const fechaVencimiento = new Date(pago.fecha_vencimiento);

        let recargo = 0;

        // Verificar si la fecha actual es posterior a la fecha de vencimiento
        if (fechaActual > fechaVencimiento) {
            // Si la fecha de vencimiento ha pasado, aplicar un recargo del 10%
            recargo = valorPagar * 0.10;
        }

        totalLetras += valorPagar + recargo;
    }

    // Validar que el monto sea mayor o igual al valor mínimo
    if (monto < valorMinimo) {
        mostrarAlerta('alerta_monto', `El monto ingresado ($${monto.toFixed(2)}) debe ser mayor o igual al valor de la letra ($${valorMinimo.toFixed(2)}).`);
        tablaPagos.innerHTML = ''; // Limpiar la tabla
        return; // Detener la ejecución si el monto no es suficiente
    }

    // Validar que el monto no sea mayor que el total de todas las letras con recargos
    if (monto > totalLetras) {
        mostrarAlerta('alerta_monto', `El monto ingresado ($${monto.toFixed(2)}) no puede ser mayor al total de las letras con recargos ($${totalLetras.toFixed(2)}).`);
        tablaPagos.innerHTML = ''; // Limpiar la tabla
        return; // Detener la ejecución si el monto es mayor que el total
    }

    // Iterar sobre los pagos pendientes o en curso y agregarlos a la tabla, asegurándose de no exceder el monto
    for (let i = 0; i < pagosPendientesOEnCurso.length; i++) {
        const pago = pagosPendientesOEnCurso[i];
        const valorPagar = parseFloat(pago.saldo_pagar);
        const fechaVencimiento = new Date(pago.fecha_vencimiento); // Suponiendo que la fecha de vencimiento esté en 'fecha_vencimiento'

        let recargo = 0;

        // Verificar si la fecha actual es posterior a la fecha de vencimiento
        if (fechaActual > fechaVencimiento) {
            // Si la fecha de vencimiento ha pasado, aplicar un recargo del 10%
            recargo = valorPagar * 0.10;
        }
        const totalPagar = valorPagar + recargo;

        // Si la suma acumulada más el valor a pagar excede el monto, aplicamos el sobrante y salimos del bucle
        if (valor + totalPagar > monto) {
            const sobrante = monto - valor; // Calculamos el sobrante exacto necesario para completar el monto

            tablaPagos.innerHTML += `
        <tr>
          <td class="border border-gray-300 px-4 py-2 text-center">${pago.secuencia}</td>
          <td class="border border-gray-300 px-4 py-2 text-center">${pago.fecha_vencimiento}</td>
          <td class="border border-gray-300 px-4 py-2 text-center">${(totalPagar - sobrante).toFixed(2)}</td>
          <td class="border border-gray-300 px-4 py-2 text-center">${recargo.toFixed(2)}</td>
          <td class="border border-gray-300 px-4 py-2 text-center">${sobrante.toFixed(2)}</td>
        </tr>
      `;

            // Preparar el último pago para actualizar
            const pagoEnviar = {
                id: pago.id,
                descripcion: pago.fecha,
                valor_pagar: (totalPagar - sobrante).toFixed(2),
                recargo: recargo.toFixed(2),
                subtotal: sobrante, // Solo mostrar el recargo como subtotal en el último pago
                estado: 'En curso', // Estado "En curso" ya que el pago no se ha completado totalmente
                pago: monto
            };
            pagosActualizar.push(pagoEnviar);
            break;
        } else {
            // Acumulamos el valor del pago si no excede el monto
            valor += totalPagar;

            // Añadir el pago completo a la tabla
            tablaPagos.innerHTML += `
        <tr>
          <td class="border border-gray-300 px-4 py-2 text-center">${pago.secuencia}</td>
          <td class="border border-gray-300 px-4 py-2 text-center">${pago.fecha_vencimiento}</td>
          <td class="border border-gray-300 px-4 py-2 text-center">${valorPagar.toFixed(2)}</td>
          <td class="border border-gray-300 px-4 py-2 text-center">${recargo.toFixed(2)}</td>
          <td class="border border-gray-300 px-4 py-2 text-center">${totalPagar.toFixed(2)}</td>
        </tr>
      `;

            // Preparar el pago para actualizar
            const pagoEnviar = {
                id: pago.id,
                descripcion: pago.fecha,
                valor_pagar: valorPagar.toFixed(2),
                recargo: recargo.toFixed(2),
                subtotal: totalPagar.toFixed(2),
                estado: 'Pagado', // Asignamos el estado correspondiente
                pago: monto
            };
            pagosActualizar.push(pagoEnviar);
            pagosRealizados++;
        }
    }

    // Añadir el monto total pagado a la cabecera
    cabPago['monto'] = monto;
}

function crearPago() {
    // Verificar si cabPago y pagosActualizar contienen valores válidos
    if (!pagosActualizar || pagosActualizar.length === 0) {
        console.error("Error: pagosActualizar está vacío o no contiene pagos");
        alert("Error: No se han generado los pagos.")
        return;
    }
    if (!cabPago || Object.keys(cabPago).length === 0) {
        console.error("Error: cabPago está vacío o no definido");
        alert("Error: No ha seleccionado Residente(Clientes) está vacío o no definido.")
        return;
    }
    console.log(cabPago)
    console.log(pagosActualizar)

    // Si ambas variables tienen valores, ejecutar la solicitud fetch
    fetch("http://localhost:8000/api/guardar_pago/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken,
        },
        body: JSON.stringify({detPago: pagosActualizar, cabPago, cliente}),
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error("Error en la red");
            }
            return response.json();
        })
        .then((data) => {
            GenerarPDF(data.facturaCreada);
            console.log(data); // Manejar la respuesta de la API
            window.location.href = '/alicuota_lista/'

        })
        .catch((error) => {
            console.error("Error al crear el objeto:", error);
        });
}

function GenerarPDF(idFactura) {
    // Si ambas variables tienen valores, ejecutar la solicitud fetch
    fetch(`http://localhost:8000/api/generar_pdfPago/${idFactura}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken,
        },
        body: JSON.stringify({
            email: datosCorroPDF,
            subject: `Factura ${idFactura} - Pago de Alicuota`,
            message: `Adjunto el PDF con los detalles de la factura ${idFactura}.`,
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




