# Bartender Robot (Django + Channels)

Descripción
- Proyecto Django que expone una interfaz web de bartender, una API REST para diálogo y un canal WebSocket para enviar comandos al robot.

Requisitos
- Python 3.11+ (recomendado)
- `pip`
- `virtualenv` (opcional)
- Dependencias listadas en `requirements.txt`
- Para WebSockets en producción se recomienda `daphne` o similar

Instalación rápida (desarrollo)
1. Clonar el repositorio:
   git clone <repo-url>
   cd <repo-folder>

2. Crear y activar entorno virtual:
   python -m venv venv
   source venv/bin/activate

3. Instalar dependencias:
   pip install -r requirements.txt

Configuración mínima
- Copiar/ajustar variables sensibles:
  - `SECRET_KEY` en `core/settings.py` (no usar el valor por defecto en producción)
  - Configurar credenciales del cliente de IA (biblioteca `google-genai` / Gemini) según la documentación oficial. Puede requerirse `GOOGLE_APPLICATION_CREDENTIALS` o variables de entorno específicas.
- Revisar `DEBUG` y `ALLOWED_HOSTS` en `core/settings.py`.

Migraciones y datos
- Ejecutar migraciones:
  python manage.py migrate

Ejecución
- Desarrollo (incluye soporte WebSocket vía ASGI dev server):
  python manage.py runserver

- Ejecución ASGI (recomendado para WebSockets en producción o pruebas avanzadas):
  daphne -b 0.0.0.0 -p 8000 core.asgi:application

Rutas y endpoints importantes
- Interfaz web (UI): `http://127.0.0.1:8000/` (ruta raíz)
- API de diálogo (POST): `http://127.0.0.1:8000/api/dialogue/`
  - Ejemplo `curl`:
    curl -X POST -H "Content-Type: application/json" -d '{"message":"Hola"}' http://127.0.0.1:8000/api/dialogue/
- WebSocket para el robot: `ws://<host>:8000/ws/robot/` (mapeado en `bartender_app/routing.py`)
- Grupo channel para comandos: `robot_commands` (usado en el backend para enviar instrucciones)

Estructura relevante
- `core/` — configuración de Django y ASGI
- `bartender_app/` — app principal (vistas, consumers, routing, templates)
- `bartender_app/templates/bartender_app/bartender.html` — plantilla de la interfaz
- `requirements.txt` — dependencias Python

Notas
- `CHANNEL_LAYERS` usa `InMemoryChannelLayer` por simplicidad; cambiar a Redis para entornos con múltiples procesos/nodos.
- Asegurarse de configurar correctamente las credenciales de la IA antes de usar la API de diálogo.
- Cambiar `SECRET_KEY` y ajustar `DEBUG` para producción.

Licencia
- Añadir la licencia adecuada al repositorio si procede (por ejemplo `LICENSE`).

Archivo objetivo
- Guardar este contenido en `README.md`.
