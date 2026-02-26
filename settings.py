from pathlib import Path
import configparser


class Settings:
    def __init__(self, path="config/settings.conf"):
        self.path = Path(path)
        self.config = configparser.ConfigParser()

        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)

            self.config["network"] = {
                "discovery_port": "50000",
                "discovery_broadcast_interval": "2.0",
                "transfer_port": "50010",
                "chunk_size": "65536",
            }

            self.config["device"] = {
                "downloads_dir": "downloads",
            }

            self.save()

        self.config.read(self.path)

    # ---------- helpers ----------

    def _ensure(self, section: str):
        if not self.config.has_section(section):
            self.config.add_section(section)

    # ---------- network ----------

    def get_discovery_port(self) -> int:
        return self.config.getint(
            "network", "discovery_port", fallback=50000
        )

    def set_discovery_port(self, port: int):
        self._ensure("network")
        self.config.set("network", "discovery_port", str(int(port)))

    def get_discovery_broadcast_interval(self) -> float:
        return self.config.getfloat(
            "network", "discovery_broadcast_interval", fallback=2.0
        )

    def set_discovery_broadcast_interval(self, interval: float):
        self._ensure("network")
        self.config.set(
            "network",
            "discovery_broadcast_interval",
            str(float(interval)),
        )

    def get_transfer_port(self) -> int:
        return self.config.getint(
            "network", "transfer_port", fallback=50010
        )

    def set_transfer_port(self, port: int):
        self._ensure("network")
        self.config.set("network", "transfer_port", str(int(port)))

    def get_chunk_size(self) -> int:
        return self.config.getint(
            "network", "chunk_size", fallback=65536
        )

    def set_chunk_size(self, size: int):
        self._ensure("network")
        self.config.set("network", "chunk_size", str(int(size)))

    # ---------- device ----------

    def get_downloads_dir(self) -> Path:
        value = self.config.get(
            "device", "downloads_dir", fallback="downloads"
        )
        path = Path(value).resolve()
        path.mkdir(parents=True, exist_ok=True)
        return path

    def set_downloads_dir(self, path: str | Path):
        self._ensure("device")
        self.config.set("device", "downloads_dir", str(path))

    # ---------- persistence ----------

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as f:
            self.config.write(f)