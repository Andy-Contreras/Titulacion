// Definimos variables
const residente = {
    id: 0,
    descripcion: "",
};
const listaFamilia = []; // Detalles de la transacción
let contFamilia = 0;
document.getElementById("contadorMiembros").textContent = contFamilia;

function comsumirApi() {
    residente["id"] = document.getElementById("id_residente").value;
    residente["descripcion"] = document.getElementById("id_descripcion").value;
    // Verificar si los campos 'residente' y 'descripcion' están llenos
    if (!residente["id"] || !residente["descripcion"]) {
        mostrarAlerta('alerta_Cabecerafamilia',"Debe seleccionar un residente y proporcionar una descripción.");
        return;
    }

    if (listaFamilia.length === 0) {
        mostrarAlerta('alerta_miembro',"Debe ingresar al menos un miembro de la familia.");
        return;
    }

    if (residente.descripcion.length > 50) {
        // La longitud de la descripción es mayor a 50
        console.log("La descripción es demasiado larga.");
        alert("La descripción es demasiado larga.");
        return;
    } else {
        console.log("La descripción es aceptable.");
        fetch("http://localhost:8000/api/crear_familia/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken,
            },
            body: JSON.stringify({residente, listaFamilia}),
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error("Error en la red");
                }
                return response.json();
            })
            .then((data) => {
                console.log("Objeto creado:", data);
                console.log(data);
                window.location.href = '/familia_lista/'
            })
            .catch((error) => {
                console.error("Error al crear el objeto:", error);
            });
    }
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

function agregarPersona() {
    const nombre = document.getElementById("nombre").value;
    const cedula = document.getElementById("cedula").value;
    const sexo = document.getElementById("sexo").value;
    const parentesco = document.getElementById("parentesco").value;
    const fechaNacimiento = document.getElementById("fecha-nacimiento").value;

    if (nombre && cedula && sexo && parentesco && fechaNacimiento) {
        const persona = {
            nombre,
            cedula,
            sexo,
            parentesco,
            fechaNacimiento,
        };
        fetch("http://localhost:8000/api/validar_persona_familia/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken,
            },
            body: JSON.stringify({persona}),
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error("Error en la red");
                }
                return response.json();
            })
            .then((data) => {
                console.log(data.mensaje);
                if (data.mensaje === "La cedula es ecuatoriana") {
                    listaFamilia.push(persona);
                    actualizarTabla();
                    // limpiar campos
                    document.getElementById("nombre").value = "";
                    document.getElementById("cedula").value = "";
                    document.getElementById("sexo").value = "";
                    document.getElementById("parentesco").value = "";
                    document.getElementById("fecha-nacimiento").value = "";
                    contFamilia += 1;
                    document.getElementById("contadorMiembros").textContent = contFamilia;
                } else {
                    mostrarAlerta('alerta_cedula',data.mensaje);
                }
            })
            .catch((error) => {
                console.error("Error al crear el objeto:", error);
            });
    } else {
        mostrarAlerta('alerta_datos',"Debe insertar todos los datos.");
    }
}

function eliminarPersona(index) {
    listaFamilia.splice(index, 1); // elimiar la persona de la lista/ tabla
    actualizarTabla();
    contFamilia -= 1;
    document.getElementById("contadorMiembros").textContent = contFamilia;
}

function actualizarTabla() {
    console.log(listaFamilia);
    const cuerpoTabla = document
        .getElementById("familia")
        .getElementsByTagName("tbody")[0];
    cuerpoTabla.innerHTML = ""; // limpiamos el contenido de la tabla, por si contiene algo

    // agregar personas a la tabla
    listaFamilia.forEach((persona, index) => {
        const nuevaFila = cuerpoTabla.insertRow();
        nuevaFila.innerHTML = `
                <td class="p-3">${persona.nombre}</td>
                    <td class="p-3">${persona.cedula}</td>
                    <td class="p-3">${persona.sexo}</td>
                    <td class="p-3">${persona.parentesco}</td>
                    <td class="p-3">${persona.fechaNacimiento}</td>
                    <td class="p-3 flex justify-center items-center">
                        <button class="bg-red-500 px-4 py-2 rounded-lg text-white" onclick="eliminarPersona(${index})">
                        Eliminar</button>
                    </td>`;
    });
}
