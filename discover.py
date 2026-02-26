import threading
import socket
import json
import time
import uuid


class Discovery:
    def __init__(self, settings, pc_name=None):
        self.settings = settings
        self.pc_name = pc_name if pc_name else socket.gethostname()
        self.device_id = str(uuid.uuid4())

        self.message = {
            "type": "hello",
            "device_id": self.device_id,
            "name": self.pc_name,
            "port": self.settings.get_transfer_port()
        }
        self.data = json.dumps(self.message).encode("utf-8")

        self.peers = {}
        self.peers_lock = threading.Lock()

        self.running = False

    def broadcast_loop(self, interval=2.0):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        while self.running:
            try:
                sock.sendto(self.data, ("255.255.255.255", self.settings.get_discovery_port()))
            except Exception:
                pass
            time.sleep(interval)
        sock.close()

    def listen_loop(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("", self.settings.get_discovery_port()))
        sock.settimeout(1.0)
        while self.running:
            try:
                data, addr = sock.recvfrom(4096)
                msg = json.loads(data)

                if msg.get("device_id") == self.device_id:
                    continue

                with self.peers_lock:
                    self.peers[msg["device_id"]] = {
                        "name": msg.get("name", ""),
                        "ip": addr[0],
                        "port": msg.get("port", 0),
                        "last_seen": time.time()
                    }

            except socket.timeout:
                pass
            except Exception:
                pass
        sock.close()

    # Start/stop service
    def start(self):
        self.running = True
        threading.Thread(target=self.broadcast_loop, daemon=True).start()
        threading.Thread(target=self.listen_loop, daemon=True).start()

    def stop(self):
        self.running = False

    def get_peers(self):
        """Return a copy of current peers list (safe for UI)."""
        with self.peers_lock:
            now = time.time()
            self.peers = {k: v for k, v in self.peers.items() if now - v["last_seen"] <= 8}
            return list(self.peers.values())
