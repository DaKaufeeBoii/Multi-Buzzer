import socket
import threading
import json
import time

class BuzzerServer:
    def __init__(self, host='0.0.0.0', port=12345):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = []
        self.running = False
        self.on_buzz_received = None 
        self.lock = threading.Lock()

    def start(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            threading.Thread(target=self._accept_connections, daemon=True).start()
            print(f"Server started on {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Failed to start server: {e}")
            return False

    def _accept_connections(self):
        while self.running and self.server_socket:
            try:
                client_sock, addr = self.server_socket.accept()
                with self.lock:
                    self.clients.append(client_sock)
                threading.Thread(target=self._handle_client, args=(client_sock,), daemon=True).start()
            except:
                break

    def _handle_client(self, client_sock):
        buffer = ""
        while self.running:
            try:
                data = client_sock.recv(1024).decode('utf-8')
                if not data:
                    break
                
                buffer += data
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line.strip():
                        message = json.loads(line)
                        if message.get('type') == 'buzz':
                            if self.on_buzz_received:
                                self.on_buzz_received(message['name'], message['color'])
            except:
                break
        
        with self.lock:
            if client_sock in self.clients:
                self.clients.remove(client_sock)
        try:
            client_sock.close()
        except:
            pass

    def broadcast_reset(self):
        message = (json.dumps({"type": "reset"}) + "\n").encode('utf-8')
        with self.lock:
            disconnected = []
            for client in self.clients:
                try:
                    client.sendall(message)
                except:
                    disconnected.append(client)
            
            for client in disconnected:
                if client in self.clients:
                    self.clients.remove(client)

    def stop(self):
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        self.server_socket = None

class BuzzerClient:
    def __init__(self, host, port=12345):
        self.host = host
        self.port = port
        self.client_socket = None
        self.on_reset_received = None 
        self.running = False

    def connect(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.settimeout(5.0)
            self.client_socket.connect((self.host, self.port))
            self.client_socket.settimeout(None)
            self.running = True
            threading.Thread(target=self._listen_for_messages, daemon=True).start()
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def _listen_for_messages(self):
        buffer = ""
        while self.running and self.client_socket:
            try:
                data = self.client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                
                buffer += data
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line.strip():
                        message = json.loads(line)
                        if message.get('type') == 'reset':
                            if self.on_reset_received:
                                self.on_reset_received()
            except:
                break
        self.running = False
        self.disconnect()

    def send_buzz(self, name, color):
        if self.client_socket and self.running:
            message = (json.dumps({"type": "buzz", "name": name, "color": color}) + "\n").encode('utf-8')
            try:
                self.client_socket.sendall(message)
            except:
                self.running = False

    def disconnect(self):
        self.running = False
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
        self.client_socket = None
