import socket
import json


class FileSender:
    def __init__(self, settings, target_ip):
        self.settings = settings
        self.target_ip = target_ip
        self.target_port = self.settings.get_transfer_port()

    def send_file(self, filepath):
        import os
        if not os.path.isfile(filepath):
            print("[Sender] File does not exist")
            return

        filesize = os.path.getsize(filepath)
        filename = os.path.basename(filepath)

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.target_ip, self.target_port))
            print(f"[Sender] Connected to {self.target_ip}:{self.target_port}")

            # send file info first
            info = {"filename": filename, "size": filesize}
            info_json = json.dumps(info).encode("utf-8")
            info_len = len(info_json)
            sock.sendall(info_len.to_bytes(4, "big"))
            sock.sendall(info_json)

            # send file in chunks
            sent = 0
            with open(filepath, "rb") as f:
                while True:
                    chunk = f.read(self.settings.get_chunk_size())
                    if not chunk:
                        break
                    sock.sendall(chunk)
                    sent += len(chunk)
                    print(f"[Sender] Sent {sent}/{filesize} bytes", end="\r")
            print(f"\n[Sender] File {filename} sent successfully")
        except Exception as e:
            print("[Sender] Error:", e)
        finally:
            sock.close()