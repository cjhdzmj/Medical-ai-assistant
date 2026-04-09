import os
import json
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime, timedelta

# 1. Forzamos la recarga del archivo .env
load_dotenv(override=True)

def interpretar_mensaje(texto_usuario: str, historial_previo: list = None):
    # 2. Obtenemos la clave y le quitamos espacios/saltos de línea con .strip()
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        raise Exception("No se encontró la clave GROQ_API_KEY en el archivo .env")

    client = Groq(api_key=api_key.strip())
    
    if not api_key:
        raise Exception("No se encontró la GROQ_API_KEY. Revisa tu archivo .env")
        
    client = Groq(api_key=api_key.strip())

    ahora = datetime.now()
    fecha_hoy = ahora.strftime("%Y-%m-%d")
    manana = (ahora + timedelta(days=1)).strftime("%Y-%m-%d")

    historial_previo = historial_previo or []

    historial_texto = "\n".join(
        [f"{m['role']}: {m['content']}" for m in historial_previo]
    )

    prompt_sistema = f"""
Eres un asistente médico que extrae información estructurada de citas.

Fecha hoy: {fecha_hoy}
Mañana: {manana}

========================
REGLA DE ORO: MEMORIA ACUMULATIVA
========================
- Analiza TODO el historial.
- Si el usuario ya dijo su nombre, fecha u hora, CONSÉRVALO.
- Nunca borres datos previos válidos.
- El JSON final debe representar el estado completo actual.

========================
JSON OBLIGATORIO
========================
{{
  "intencion": "agendar" | "cancelar" | "faq",
  "paciente_nombre": "string o null",
  "fecha": "YYYY-MM-DD o null",
  "hora": "HH:00 o null",
  "motivo": "string"
}}

========================
REGLAS DE MEMORIA Y FALTANTES:
========================
- Revisa el HISTORIAL PREVIO para rellenar campos que el usuario no repitió.
- Si falta la HORA: pon "null" (el backend sugerirá una).
- Si el usuario solo da su nombre pero no pide cita: pon intencion "faq".
- El JSON debe ser siempre completo.

========================
HISTORIAL PREVIO
========================
{historial_texto}

Solo responde JSON puro.
"""
# 3. Construcción de Mensajes
    messages = [{"role": "system", "content": prompt_sistema}]
    
    # Añadimos historial para que Llama tenga contexto real
    if historial_previo:
        messages.extend(historial_previo)
        
    # Añadimos el último mensaje del usuario
    messages.append({"role": "user", "content": texto_usuario})

    try:
        # 4. Llamada a la API de Groq
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            response_format={"type": "json_object"}
        )

        contenido = completion.choices[0].message.content
        respuesta_ia = json.loads(contenido)

        # 5. Lógica de Respaldo para el Nombre (Solo si la IA falla)
        if not respuesta_ia.get("paciente_nombre") or respuesta_ia.get("paciente_nombre") == "null":
            for msg in reversed(historial_previo):
                cont = msg["content"].lower()
                if "soy " in cont or "me llamo " in cont:
                    # Intento de extracción rápida
                    nombre_extraido = cont.replace("soy ", "").replace("me llamo ", "").split()[0]
                    respuesta_ia["paciente_nombre"] = nombre_extraido.capitalize()
                    break

        print(f"DEBUG IA -> {respuesta_ia}")
        return respuesta_ia

    except Exception as e:
        print(f"Error en Interprete: {e}")
        return {
            "intencion": "faq",
            "paciente_nombre": None,
            "fecha": None,
            "hora": None,
            "motivo": "Error de procesamiento"
        }