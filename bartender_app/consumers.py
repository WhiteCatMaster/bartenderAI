# bartender_app/consumers.py

from channels.generic.websocket import AsyncWebsocketConsumer
import json


class RobotConsumer(AsyncWebsocketConsumer):
    # Nombre del grupo para enviar comandos desde las Views (paso 4 de la respuesta anterior)
    ROBOT_COMMANDS_GROUP = 'robot_commands'

    async def connect(self):
        # 1. Aceptar la conexión WebSocket
        await self.accept()

        # 2. Unir este consumidor (la conexión) al grupo 'robot_commands'
        # Esto permite que la View de Django (que es síncrona) pueda enviarle mensajes a este consumidor (que es asíncrono)
        await self.channel_layer.group_add(
            self.ROBOT_COMMANDS_GROUP,
            self.channel_name
        )
        print(f"WebSocket conectado y unido al grupo: {self.channel_name}")

    async def disconnect(self, close_code):
        # Eliminar esta conexión del grupo
        await self.channel_layer.group_discard(
            self.ROBOT_COMMANDS_GROUP,
            self.channel_name
        )
        print(f"WebSocket desconectado: {self.channel_name}")

    # Este método recibe mensajes del grupo 'robot_commands' enviados desde las Views de Django
    async def send_command(self, event):
        command = event['text']

        # 3. LÓGICA DE ENVÍO DE COMANDO AL ROBOT
        # Esta es la línea crucial: envía el comando a la otra parte
        # (que puede ser el JavaScript del frontend O el servidor del robot)
        print(f"*** COMANDO RECIBIDO DE DJANGO VIEW: {command} ***")

        # Envía el comando al cliente conectado (que puede ser la interfaz web)
        await self.send(text_data=json.dumps({
            'type': 'command',
            'command': command
        }))

    # Este método recibe mensajes si el cliente (frontend o robot) le envía algo a Django
    async def receive(self, text_data):
        data = json.loads(text_data)
        # Puedes usar esto para recibir confirmaciones de estado del robot
        print(f"Mensaje del cliente: {data}")