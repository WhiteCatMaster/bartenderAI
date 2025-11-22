# bartender_app/views.py

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

# =================================================================
# 1. IMPORTS DE GEMINI
# =================================================================
from google import genai
from google.genai import types
from google.genai.errors import APIError

# =================================================================
# 2. INICIALIZACIÓN GLOBAL DEL CLIENTE DE GEMINI
# El cliente busca la clave en la variable de entorno GEMINI_API_KEY
# =================================================================
client = None
model = 'gemini-2.5-flash'

try:
    client = genai.Client()
    print("Gemini Client inicializado correctamente.")

except Exception as e:
    print(f"Error al inicializar el cliente de Gemini (Revisar GEMINI_API_KEY): {e}")
    client = None


# =================================================================


# 3. Vista que renderiza la interfaz web
def bartender_interface(request):
    # Asegúrate de que el path a la plantilla sea correcto
    return render(request, 'bartender_app/bartender.html', {})


# 4. API para manejar el diálogo (recibir texto, responder texto)
@csrf_exempt
def dialogue_api(request):
    """
    Recibe el mensaje del usuario, interactúa con Gemini y envía comandos por WebSocket.
    """

    # Manejo de error si el cliente no se inicializó
    if not client:
        return JsonResponse({
            'response': "🚫 ERROR: The bartender AI system is currently unavailable. Check the GEMINI_API_KEY."
        }, status=503)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_text = data.get('message', '')

            if not user_text:
                return JsonResponse({'response': "Please say something so I can help you."}, status=400)

            # --- LÓGICA DEL BARTENDER USANDO GEMINI ---

            # Definir el contexto del sistema (¡Traducido a INGLÉS para TTS!)
            system_prompt = (
                "You are MegasBot, a robotic bartender. Your *PRIMARY and NON-NEGOTIABLE* task "
                "is to identify an order for either COKE or WATER. "
                "The only drinks you can prepare are COKE and WATER. "
                
                "*STRICT COMMAND FORMAT RULE:* When the customer orders one of these two drinks, "
                "you MUST respond with a short, friendly phrase, and then you MUST immediately and "
                "consecutively include the specific command tag at the very end. "
                
                "The command tag must use the exact format: [COMANDO:PREPARAR:NAME]. "
                "NAME must be either COKE or WATER, always in ALL CAPS. "
                
                "Example (Coke): 'Excellent choice! [COMANDO:PREPARAR:COKE]' "
                "Example (Water): 'Hydration is key. [COMANDO:PREPARAR:WATER]' "
                
                "If the customer does NOT order a drink, continue the conversation normally."
            )

            # Configurar y llamar a la API
            response = client.models.generate_content(
                model=model,
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
                print(f"!!! COMMAND DETECTED: {command_to_robot}")

                channel_layer = get_channel_layer()
                # Envía el comando al grupo de WebSockets "robot_commands"
                async_to_sync(channel_layer.group_send)(
                    "robot_commands",
                    {
                        "type": "send.command",  # Tipo de mensaje que recibirá el consumer
                        "text": command_to_robot,
                    }
                )

            # 5. Devolver la respuesta de texto al frontend (para ser leída por TTS)
            return JsonResponse({'response': bartender_response})

        except APIError as e:
            print(f"Error in Gemini API call: {e}")
            return JsonResponse(
                {'response': "Apologies, the AI service is mixing things up. Could you please repeat that?"},
                status=500)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format received.'}, status=400)
        except Exception as e:
            print(f"Unexpected error in dialogue_api: {e}")
            return JsonResponse({'response': "Oops, an unexpected server error occurred. Please try again."},
                                status=500)

    # Si no es un método POST
    return HttpResponse(status=405)