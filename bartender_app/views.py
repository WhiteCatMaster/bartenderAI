# bartender_app/views.py

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json


# bartender_app/views.py

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

    return HttpResponse(status=405)  # Método no permitido