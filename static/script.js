// 1. Variable global para la memoria
let historialMensajes = [];

function cargarCitas() {
    fetch('/ver-citas')
        .then(res => res.json())
        .then(data => {
            const tabla = document.getElementById('tabla-citas');
            if (!tabla) return;
            tabla.innerHTML = '';
            data.agenda.forEach(cita => {
                const color = cita.estado === "programada" ? "bg-success" : "bg-danger";
                tabla.innerHTML += `
                    <tr>
                        <td><strong>#${cita.id}</strong></td>
                        <td>${cita.paciente_nombre}</td>
                        <td>${cita.fecha}</td>
                        <td>${cita.hora}</td>
                        <td><span class="badge ${color}">${cita.estado.toUpperCase()}</span></td>
                    </tr>`;
            });
        });
}

function enviarMensaje() {
    const input = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');
    const mensajeTexto = input.value.trim();

    if (!mensajeTexto) return;

    // 1. Mostrar mensaje del usuario
    chatBox.innerHTML += `<div class="message user-msg">${mensajeTexto}</div>`;
    input.value = '';
    chatBox.scrollTop = chatBox.scrollHeight;

    // 2. Guardar en historial para la memoria de la IA
    historialMensajes.push({ "role": "user", "content": mensajeTexto });

    const historialJSON = JSON.stringify(historialMensajes);
    const url = `/test-ia?mensaje=${encodeURIComponent(mensajeTexto)}&historial=${encodeURIComponent(historialJSON)}`;

    fetch(url)
        .then(res => res.json())
        .then(data => {
            console.log("Respuesta del servidor:", data); // Esto te ayudará a ver errores en la consola (F12)

            // 3. Determinar qué texto mostrar
            let textoAMostrar = "";

            if (data.respuesta_bot) {
                textoAMostrar = data.respuesta_bot;
            } else if (data.ia_entendio) {
                // Si la IA entendió pero el backend no agendó (faltan datos)
                const info = data.ia_entendio;
                textoAMostrar = `Entendido. Intención: ${info.intencion}. ¿Me confirmas tu nombre o fecha?`;
            } else if (data.error_sistema) {
                textoAMostrar = `⚠️ Error: ${data.error_sistema}`;
            } else {
                textoAMostrar = "Lo siento, recibí un formato inesperado del servidor.";
            }

            // 4. Mostrar respuesta en el chat
            chatBox.innerHTML += `<div class="message bot-msg">${textoAMostrar}</div>`;
            chatBox.scrollTop = chatBox.scrollHeight;

            // 5. Guardar respuesta en memoria para mantener el hilo
            historialMensajes.push({ "role": "assistant", "content": textoAMostrar });

            // Limitar historial para no saturar la API
            if (historialMensajes.length > 10) historialMensajes.splice(0, 2);
            
            cargarCitas(); // Refrescar la tabla automáticamente
        })
        .catch(err => {
            console.error("Error en Fetch:", err);
            chatBox.innerHTML += `<div class="message bot-msg text-danger">⚠️ Error de conexión con el servidor.</div>`;
        });
}
// 5. INICIALIZACIÓN (Fuera de las otras funciones)
document.addEventListener('DOMContentLoaded', () => {
    cargarCitas();
    
    const input = document.getElementById('user-input');
    if(input) {
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') enviarMensaje();
        });
    }
});