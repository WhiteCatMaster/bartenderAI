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
@csrf_exempt
def dialogue_api(request):
    if request.method == 'POST':
        if not client:
            return JsonResponse({'response': "Lo siento, el sistema del bartender (IA) no está disponible."},
                                status=503)

        try:
            data = json.loads(request.body)
            user_text = data.get('message', '')

            # --- LÓGICA DEL BARTENDER USANDO GEMINI ---

            # Definir el contexto del sistema (el "rol" del bartender)
            system_prompt = (
                "Eres Leo, un bartender robótico amable y ligeramente sarcástico. "
                "Tu trabajo es conversar, guiar al cliente a elegir una bebida y, "
                "una vez que nombren una bebida (ej. 'Mojito', 'Cerveza', 'Whisky Sour'), "
                "debes responder con un mensaje amigable, **Y solo entonces**, "
                "debes incluir la etiqueta especial [COMANDO:PREPARAR_NOMBRE_DEL_TRAGO] "
                "al final de tu respuesta, sin más texto después de ella. "
                "Ejemplo: '¡Excelente elección! Un Whisky Sour es una decisión de clase. [COMANDO:PREPARAR_WHISKY_SOUR]'"
            )

            # Configurar el chat (usamos generate_content por simplicidad de hackathon)
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[user_text],
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt
                )
            )

            llm_response = response.text
            command_to_robot = None

            # 3. Procesar la respuesta para buscar el comando de acción
            if "[COMANDO:" in llm_response:
                # Separar el mensaje visible del comando oculto
                parts = llm_response.split("[COMANDO:")
                bartender_response = parts[0].strip()

                # Extraer el comando real
                command_part = parts[1].replace("]", "").strip()
                command_to_robot = command_part
            else:
                bartender_response = llm_response

            # 4. Enviar el comando al robot si fue detectado
            if command_to_robot:
                print(f"!!! COMANDO DETECTADO: {command_to_robot}")

                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    "robot_commands",
                    {
                        "type": "send.command",
                        "text": command_to_robot,
                    }
                )

            return JsonResponse({'response': bartender_response})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            print(f"Error en la llamada a Gemini: {e}")
            return JsonResponse({'response': "Vaya, parece que la IA está mezclando ideas. ¿Puedes repetir eso?"},
                                status=500)

    return HttpResponse(status=405)