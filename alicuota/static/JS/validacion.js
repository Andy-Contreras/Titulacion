// Obtén el elemento input
const fechaAlicuota = document.getElementById("fechaAlicuota");

// Obtén la fecha actual
const hoy = new Date();
const fechaActual = hoy.toISOString().split('T')[0]; // Formato YYYY-MM-DD

// Asigna la fecha al valor del input
fechaAlicuota.value = fechaActual;