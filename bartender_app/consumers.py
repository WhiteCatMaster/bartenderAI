#bartender_app/consumers.py

import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

class RobotConsumer(WebsocketConsumer):

    def connect(self):
        # 1. Unir al grupo de comandos
        self.group_name = 'robot_commands'

        # Añadir este canal (esta conexión de navegador) al grupo 'robot_commands'
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )
        self.accept()
        print(f"✅ WebSocket conectado y unido al grupo: {self.group_name}")

    def disconnect(self, close_code):
        # Dejar el grupo de comandos
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )
        print(f"❌ WebSocket desconectado.")


    # 💡 ESTE MÉTODO RECIBE EL COMANDO DESDE LA VISTA (via group_send)
    def send_command(self, event):
        """
        Recibe un mensaje de tipo 'send.command' del Channel Layer.
        El nombre del método debe coincidir con 'send_command' (reemplazando el punto por guion bajo).
        """
        
        command_text = event['text']
        print(f"⚙ Consumer recibió comando: {command_text}")

        # 2. Enviar el comando al WebSocket del navegador (máquina cliente)
        self.send(text_data=json.dumps({
            'type': 'command',
            'command': command_text
        }))
        
    
    # Este método recibe mensajes directamente del navegador, aunque puede que no lo uses ahora:
    def receive(self, text_data):
        pass # Dejar vacío si el navegador no envía datos