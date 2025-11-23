# python
import websocket
import json
import time
import os
import asyncio
import threading
import signal

# 🛑 CONFIGURACIÓN CLAVE 🛑
SERVER_IP = "10.194.222.20"
SERVER_PORT = "8080"
WS_URL = f"ws://{SERVER_IP}:{SERVER_PORT}/ws/robot/"

# --- Loop asíncrono en hilo separado para ejecutar scripts ---
_script_loop = asyncio.new_event_loop()
_thread = threading.Thread(target=_script_loop.run_forever, daemon=True)
_thread.start()

async def _run_script(script_path: str, timeout: int = 60):
    """
    Ejecuta el script con /bin/bash, imprime su salida en tiempo real.
    Si excede `timeout` segundos, envía SIGTERM y luego SIGKILL si es necesario.
    """
    try:
        proc = await asyncio.create_subprocess_exec(
            "/bin/bash", script_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT
        )

        async def _stream_output(stream):
            while True:
                line = await stream.readline()
                if not line:
                    break
                print(line.decode(errors="ignore"), end="")

        reader = asyncio.create_task(_stream_output(proc.stdout))

        try:
            await asyncio.wait_for(proc.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            print(f"⏱️ Timeout ({timeout}s) alcanzado para `{script_path}`. Enviando SIGTERM...")
            try:
                proc.send_signal(signal.SIGTERM)
                await asyncio.wait_for(proc.wait(), timeout=5)
            except asyncio.TimeoutError:
                print("SIGTERM no finalizó el proceso. Enviando SIGKILL...")
                proc.kill()
                await proc.wait()
        finally:
            # asegurar que se termine de leer la salida
            await reader
    except Exception as e:
        print(f"Error ejecutando `{script_path}`: {e}")

def start_script(script_path: str, timeout: int = 60):
    """
    Encola la ejecución asíncrona del script en el loop de fondo.
    Devuelve el Future para quien quiera vigilar el resultado.
    """
    fut = asyncio.run_coroutine_threadsafe(_run_script(script_path, timeout), _script_loop)
    def _done_cb(f):
        try:
            f.result()
        except Exception as e:
            print(f"Script `{script_path}` terminó con error: {e}")
    fut.add_done_callback(_done_cb)
    return fut

# --- Callbacks del websocket ---
def on_message(ws, message):
    try:
        data = json.loads(message)
        if data.get('type') == 'command':
            command = data.get('command')
            print(f"\n✨ ¡COMANDO RECIBIDO para el Robot! ✨")
            print(f"Comando: {command}")

            if command.startswith("PREPARAR:"):
                trago = command.split("PREPARAR:")[1].replace(':', ' ').upper()
                print(f"--- 🍹 INICIANDO PREPARACIÓN: {trago} ---")
                if trago == "COKE":
                    start_script("./coke.sh", timeout=60)
                elif trago == "WATER":
                    start_script("./water.sh", timeout=60)
                else:
                    print(f"Receta `{trago}` no encontrada.")

                print(f"--- ✅ {trago} INICIADO (controlado con timeout). ---")
            else:
                print(f"Comando desconocido: {command}")
    except json.JSONDecodeError:
        print(f"Mensaje JSON inválido: {message}")
    except Exception as e:
        print(f"Error procesando el mensaje: {e}")

def on_error(ws, error):
    print(f"### ERROR ###: {error}")

def on_close(ws, close_code, reason):
    print(f"### CONEXIÓN CERRADA ### Código: {close_code}, Razón: {reason}")
    print("Intentando reconectar en 5 segundos...")
    time.sleep(5)
    connect_websocket()

def on_open(ws):
    print(f"🚀 Conectado a Daphne en: {WS_URL}")

def connect_websocket():
    ws = websocket.WebSocketApp(WS_URL,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    while True:
        try:
            ws.run_forever()
        except Exception as e:
            print(f"Error en run_forever: {e}")
            time.sleep(5)

if __name__ == "__main__":
    connect_websocket()
