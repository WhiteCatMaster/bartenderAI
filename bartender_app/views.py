# bartender_app/views.py

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync # <-- ¡Añadir esta línea
import json
from django.shortcuts import render
# ...

# 1. Vista que renderiza la interfaz web (el bartender)
def bartender_interface(request):
    # Asegúrate de que el path a la plantilla sea correcto
    return render(request, 'bartender_app/bartender.html', {})

# 2. API para manejar el diálogo (recibir texto, responder texto)
@csrf_exempt  # NECESARIO para aceptar POST sin un token CSRF si lo pruebas rápido
def dialogue_api(request):
    if request.method == 'POST':
        try:
            # Aquí iría tu lógica de LLM/chatbot
            data = json.loads(request.body)
            user_text = data.get('message', '')

            # SIMULACIÓN de respuesta del bartender
            bartender_response = f"Me dijiste: '{user_text}'. ¿Qué te sirvo?"

            return JsonResponse({'response': bartender_response})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return HttpResponse(status=405)  # Metodo no permitido


@csrf_exempt
def dialogue_api(request):
    # ... (código existente)

    # Dentro del bloque 'if "mojito" in user_text.lower() or "trago" in user_text.lower():'

    # ... (código de detección de comando)

    # ENVIAR COMANDO AL ROBOT VÍA DJANGO CHANNELS
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(  # <-- Usar async_to_sync para llamar a group_send
        "robot_commands",  # Nombre del grupo
        {
            "type": "send.command",
            "text": command_to_robot,
        }
    )