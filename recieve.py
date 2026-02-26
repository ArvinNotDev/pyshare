import socket
import threading
import os
import json



class FileReceiver:
    def __init__(self, settings, listen_port, save_dir="downloads"):
        self.listen_port = listen_port
        self.save_dir = save_dir
        self.settings = settings
        os.makedirs(save_dir, exist_ok=True)
        self.running = False

    def start(self):
        self.running = True
        threading.Thread(target=self._listen_loop, daemon=True).start()

    def stop(self):
        self.running = False

    def _listen_loop(self):
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.bind(("", self.listen_port))
        server_sock.listen(1)
        print(f"[Receiver] Listening on port {self.listen_port}...")
        while self.running:
            try:
                conn, addr = server_sock.accept()
                print(f"[Receiver] Connection from {addr}")
                threading.Thread(target=self._handle_client, args=(conn,), daemon=True).start()
            except Exception:
                continue
        server_sock.close()

    def _handle_client(self, conn):
        try:
            # receive file info first: {"filename": "example.txt", "size": 12345}
            info_len_bytes = conn.recv(4)
            if len(info_len_bytes) < 4:
                conn.close()
                return
            info_len = int.from_bytes(info_len_bytes, "big")
            info_json = conn.recv(info_len).decode("utf-8")
            info = json.loads(info_json)
            filename = info.get("filename", "received_file")
            total_size = info.get("size", 0)

            filepath = os.path.join(self.save_dir, filename)
            print(f"[Receiver] Receiving {filename} ({total_size} bytes)")

            received = 0
            with open(filepath, "wb") as f:
                while received < total_size:
                    chunk = conn.recv(self.settings.get_chunk_size())
                    if not chunk:
                        break
                    f.write(chunk)
                    received += len(chunk)
            print(f"[Receiver] File saved to {filepath}")
        except Exception as e:
            print("[Receiver] Error:", e)
        finally:
            conn.close()