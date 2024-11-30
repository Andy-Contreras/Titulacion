// Definimos variables
const residente = {
    descripcion: ''
}
const listaFamilia = [] // Detalles de la transacción
let contFamilia = 0

document.getElementById("contadorMiembros").textContent = contFamilia
const guardarUrl = "{{ cancel_url }}";

document.addEventListener('DOMContentLoaded', function () {
    id = document.getElementById('id_residente').value
    fetch(`http://localhost:8000/api/buscar_miembros_familia/${id}/`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error en la red');
            }
            return response.json();
        })
        .then(data => {
            console.log(data);
            // Asegúrate de que data no sea un array
            if (Array.isArray(data)) {
                // Si data es un array, puedes usar spread para agregarlo a la lista
                listaFamilia.push(...data);
            } else {
                // Si es un objeto, lo añades directamente
                listaFamilia.push(data);
            }

            const cuerpoTabla = document.getElementById('familia').getElementsByTagName('tbody')[0]
            cuerpoTabla.innerHTML = '' // limpiamos el contenido de la tabla, por si contiene algo

            // agregar personas a la tabla
            listaFamilia.forEach((persona, index) => {
                const nuevaFila = cuerpoTabla.insertRow();
                nuevaFila.innerHTML = `
                <td class="p-3">${persona.nombre}</td>
                    <td class="p-3">${persona.cedula}</td>
                    <td class="p-3">${persona.sexo}</td>
                    <td class="p-3">${persona.parentesco}</td>
                    <td class="p-3">${persona.fecha_nacimiento}</td>
                    <td class="p-3 flex justify-center items-center">
                        <button class="bg-red-500 px-4 py-2 rounded-lg text-white" onclick="eliminarPersona(${index})">
                        Eliminar</button>
                    </td>`
            })
            contFamilia = listaFamilia.length
            document.getElementById("contadorMiembros").textContent = contFamilia
        })
        .catch(error => {
            console.error('Error al crear el objeto:', error);
        });
    console.log('La página se ha cargado completamente.');

});

function agregarPersona() {
    const nombre = document.getElementById("nombre").value;
    const cedula = document.getElementById("cedula").value;
    const sexo = document.getElementById("sexo").value;
    const parentesco = document.getElementById("parentesco").value;
    const fecha_nacimiento = document.getElementById("fecha-nacimiento").value;

    if (nombre && cedula && sexo && parentesco && fecha_nacimiento) {
        const persona = {
            nombre,
            cedula,
            sexo,
            parentesco,
            fecha_nacimiento
        }
        fetch('http://localhost:8000/api/validar_persona_familia/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify(
                {persona}
            )
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error en la red');
                }
                return response.json();
            })
            .then(data => {
                console.log(data.mensaje);
                if (data.mensaje === 'La cedula es ecuatoriana') {
                    listaFamilia.push(persona);
                    actualizarTabla()
                    // limpiar campos
                    document.getElementById("nombre").value = ''
                    document.getElementById("cedula").value = ''
                    document.getElementById("sexo").value = ''
                    document.getElementById("parentesco").value = ''
                    document.getElementById("fecha-nacimiento").value = ''
                    contFamilia += 1
                    document.getElementById("contadorMiembros").textContent = contFamilia
                } else {
                    alert(data.mensaje)
                }
            })
            .catch(error => {
                console.error('Error al crear el objeto:', error);
            });

    } else {
        alert('Debe insertar todos los datos.')
    }
}


function eliminarPersona(index) {
    listaFamilia.splice(index, 1) // elimiar la persona de la lista/ tabla
    actualizarTabla()
    contFamilia -= 1
    document.getElementById("contadorMiembros").textContent = contFamilia
}

function actualizarTabla() {
    console.log(listaFamilia)
    const cuerpoTabla = document.getElementById('familia').getElementsByTagName('tbody')[0]
    cuerpoTabla.innerHTML = '' // limpiamos el contenido de la tabla, por si contiene algo

    // agregar personas a la tabla
    listaFamilia.forEach((persona, index) => {
        const nuevaFila = cuerpoTabla.insertRow();
        nuevaFila.innerHTML = `
                <td class="p-3">${persona.nombre}</td>
                    <td class="p-3">${persona.cedula}</td>
                    <td class="p-3">${persona.sexo}</td>
                    <td class="p-3">${persona.parentesco}</td>
                    <td class="p-3">${persona.fecha_nacimiento}</td>
                    <td class="p-3 flex justify-center items-center">
                        <button class="bg-red-500 px-4 py-2 rounded-lg text-white" onclick="eliminarPersona(${index})">
                        Eliminar</button>
                    </td>`
    })
}


function comsumirApi() {
    residente['descripcion'] = document.getElementById('id_descripcion').value

    if (listaFamilia.length === 0) {
        alert('Debe ingresar al menos un miembro de la familia.');
        return;
    }

    if (residente.descripcion.length > 50) {
        // La longitud de la descripción es mayor a 50
        console.log('La descripción es demasiado larga.');
        alert('La descripción es demasiado larga.')
    } else {
        console.log('La descripción es aceptable.');
        id = document.getElementById('id_residente').value
        fetch(`http://localhost:8000/api/modificar_familia/${id}/`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify(
                {descripcion: residente['descripcion'], listaFamilia}
            )
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error en la red');
                }
                return response.json();
            })
            .then(data => {
                console.log('Objeto creado:', data);
                console.log(data);
            })
            .catch(error => {
                console.error('Error al crear el objeto:', error);
            });
    }

}