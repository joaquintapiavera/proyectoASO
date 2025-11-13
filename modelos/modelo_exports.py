from dataclasses import dataclass, field
from typing import List, Optional
import re
import shutil
import os

@dataclass
class HostEntry:
    host: str
    options: str = ""

@dataclass
class ExportEntry:
    path: str
    hosts: List[HostEntry] = field(default_factory=list)
    raw_comment: str = ""

class ModeloExports:
    def __init__(self, path: str = "/etc/exports"):
        self.path = path
        self.exports: List[ExportEntry] = []
        try:
            self.load_from_file(self.path)
        except FileNotFoundError:
            self.exports = []
        except Exception:
            self.exports = []

    @staticmethod
    def _tokenize_rest(rest: str):
        return re.findall(r'\S+\([^)]*\)|\S+', rest)

    @staticmethod
    def parse_exports_text(text: str) -> List[ExportEntry]:
        lines = text.splitlines()
        out: List[ExportEntry] = []
        for raw in lines:
            s = raw.strip()
            if not s or s.startswith("#"):
                out.append(ExportEntry(path="", hosts=[], raw_comment=raw))
                continue
            m = re.match(r'^(?P<path>\S+)\s+(?P<rest>.+)$', raw)
            if not m:
                out.append(ExportEntry(path="", hosts=[], raw_comment=raw))
                continue
            path = m.group("path")
            rest = m.group("rest").strip()
            tokens = ModeloExports._tokenize_rest(rest)
            hosts = []
            for tok in tokens:
                if "(" in tok and tok.endswith(")"):
                    host_part, opts = tok.split("(", 1)
                    opts = opts[:-1]
                    hosts.append(HostEntry(host=host_part.strip(), options=opts.strip()))
                else:
                    hosts.append(HostEntry(host=tok.strip(), options=""))
            out.append(ExportEntry(path=path, hosts=hosts))
        return out

    @staticmethod
    def format_exports_text(exports: List[ExportEntry]) -> str:
        lines = []
        for e in exports:
            if e.raw_comment and not e.path:
                lines.append(e.raw_comment)
                continue
            if not e.path:
                continue
            parts = []
            for h in e.hosts:
                if h.options:
                    parts.append(f"{h.host}({h.options})")
                else:
                    parts.append(h.host)
            lines.append(f"{e.path} {' '.join(parts)}")
        return "\n".join(lines) + ("\n" if lines else "")

    def load_from_string(self, text: str):
        self.exports = self.parse_exports_text(text)

    def load_from_file(self, path: Optional[str] = None):
        p = path or self.path
        with open(p, "r", encoding="utf-8") as f:
            txt = f.read()
        self.load_from_string(txt)

    def backup(self, path: Optional[str] = None) -> str:
        p = path or self.path
        dst = f"{p}.bak"
        shutil.copy2(p, dst)
        return dst

    def save_to_file(self, path: Optional[str] = None, overwrite: bool = False) -> str:
        text = self.format_exports_text(self.exports)
        p = path or self.path
        if not overwrite:
            raise PermissionError("overwrite must be True to write to file")
        if os.path.exists(p):
            self.backup(p)
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
        return text

    def get_exports_paths(self) -> List[str]:
        return [e.path for e in self.exports if e.path]

    def get_export_by_path(self, path: str) -> Optional[ExportEntry]:
        for e in self.exports:
            if e.path == path:
                return e
        return None

    def add_export(self, path: str) -> ExportEntry:
        e = ExportEntry(path=path, hosts=[])
        self.exports.append(e)
        return e

    def remove_export(self, path: str) -> bool:
        for i, e in enumerate(self.exports):
            if e.path == path:
                del self.exports[i]
                return True
        return False

    def add_host(self, export_path: str, host: str, options: str = "") -> bool:
        e = self.get_export_by_path(export_path)
        if not e:
            return False
        e.hosts.append(HostEntry(host=host, options=options))
        return True

    def remove_host(self, export_path: str, host_index: int) -> bool:
        e = self.get_export_by_path(export_path)
        if not e or host_index < 0 or host_index >= len(e.hosts):
            return False
        del e.hosts[host_index]
        return True

    def edit_host(self, export_path: str, host_index: int, new_host: str, new_options: str) -> bool:
        e = self.get_export_by_path(export_path)
        if not e or host_index < 0 or host_index >= len(e.hosts):
            return False
        e.hosts[host_index].host = new_host
        e.hosts[host_index].options = new_options
        return True

    @staticmethod
    def verificar_directorio(path: str) -> bool:
        return os.path.isdir(path)

    @staticmethod
    def crear_directorio(path: str, exist_ok: bool = True) -> tuple[bool, str]:
        try:
            os.makedirs(path, exist_ok=exist_ok)
            return True, f"Directorio {path} creado o ya existe."
        except PermissionError:
            return False, "Error de permisos: no se pudo crear el directorio."
        except Exception as e:
            return False, f"Error inesperado: {e}"

    def to_config_dict(self) -> dict:
        out = {}
        for e in self.exports:
            if not e.path:
                continue
            lst = []
            for h in e.hosts:
                lst.append({"host": h.host, "options": h.options})
            out[e.path] = lst
        return out
