import json
from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from ai.interprete import interpretar_mensaje
from models import SessionLocal, Cita 
from services.citas_service import agendar_cita, cancelar_cita

app = FastAPI()

# 1. Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. Ruta para el Dashboard
@app.get("/")
def leer_index():
    return FileResponse('static/index.html')

# 3. Ruta para Procesar Citas con IA
@app.get("/test-ia")
def probar_ia(mensaje: str = Query(...), historial: str = Query(None)):
    try:
        # 1. Procesar el historial (limpieza de seguridad)
        contexto_previo = []
        if historial and historial != "undefined":
            try:
                contexto_previo = json.loads(historial)
            except Exception as e:
                print(f"Aviso: No se pudo cargar el historial: {e}")

        # 2. Obtener interpretación de la IA
        resultado = interpretar_mensaje(mensaje, contexto_previo)
        print(f"DEBUG - IA ENTENDIÓ: {resultado}") 

        intencion = resultado.get("intencion")

        # 3. Lógica de Decisiones (Aseguramos que CADA camino tenga un return)
        if intencion == "agendar":
            respuesta = agendar_cita(resultado)
            print(f"DEBUG - RESPUESTA SERVICE (AGENDAR): {respuesta}")
            return respuesta

        elif intencion == "cancelar":
            respuesta = cancelar_cita(resultado)
            print(f"DEBUG - RESPUESTA SERVICE (CANCELAR): {respuesta}")
            return respuesta

        # 4. Caso por defecto: Si es FAQ o la IA no está segura
        # Esto evita que el navegador reciba un 'null'
        return {
            "respuesta_bot": "Entiendo tu mensaje, pero necesito más detalles para ayudarte con la cita. ¿Qué día y hora prefieres?",
            "ia_entendio": resultado
        }

    except Exception as e:
        # Esto te dirá exactamente qué falló en la terminal de VS Code
        import traceback
        print(f"ERROR CRÍTICO EN TEST-IA:\n{traceback.format_exc()}")
        return {"error_sistema": str(e)}
    
# 4. Ruta para LIMPIAR la base de datos
@app.get("/limpiar-todo-ya")
def limpiar_db():
    try:
        db = SessionLocal()
        num_borrados = db.query(Cita).delete()
        db.commit()
        db.close()
        return {"mensaje": f"Base de datos vaciada. Se eliminaron {num_borrados} citas."}
    except Exception as e:
        return {"error": str(e)}

# 5. Ruta para ver JSON de citas
@app.get("/ver-citas")
def obtener_todas_las_citas():
    db = SessionLocal()
    citas_db = db.query(Cita).all()

    resultado = [
        {
            "id": c.id,
            "paciente_nombre": c.paciente_nombre,
            "fecha": c.fecha,
            "hora": c.hora,
            "motivo": c.motivo,
            "estado": c.estado
        }
        for c in citas_db
    ]

    db.close()

    return {
        "total_citas": len(resultado),
        "agenda": resultado
    }