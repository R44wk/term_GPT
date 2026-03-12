#!/usr/bin/env python3
"""
telefono.py — shell interactiva bidireccional TCP
Uso:
  Receptor:  python3 telefono.py --listen  --port 4444
  Emisor:    python3 telefono.py --connect --host 192.168.1.10 --port 4444
"""

import socket
import threading
import sys
import argparse

BUFFER = 4096
ENCODING = "utf-8"

# ── Hilos de I/O ─────────────────────────────────────────────────────────────

def recibir(sock: socket.socket):
    """Lee del socket e imprime en stdout."""
    try:
        while True:
            data = sock.recv(BUFFER)
            if not data:
                print("\n[!] Conexión cerrada por el otro extremo.")
                break
            sys.stdout.write(data.decode(ENCODING, errors="replace"))
            sys.stdout.flush()
    except Exception:
        pass

def enviar(sock: socket.socket):
    """Lee stdin línea a línea y envía al socket."""
    try:
        while True:
            linea = sys.stdin.readline()
            if not linea:          # EOF (Ctrl+D)
                break
            sock.sendall(linea.encode(ENCODING))
    except Exception:
        pass

# ── Modos ─────────────────────────────────────────────────────────────────────

def modo_escucha(port: int):
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", port))
    srv.listen(1)
    print(f"[*] Escuchando en 0.0.0.0:{port} ...")
    conn, addr = srv.accept()
    print(f"[+] Conexión desde {addr[0]}:{addr[1]}\n")
    srv.close()
    _iniciar_shell(conn)

def modo_conectar(host: str, port: int):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"[*] Conectando a {host}:{port} ...")
    sock.connect((host, port))
    print(f"[+] Conectado!\n")
    _iniciar_shell(sock)

# ── Shell interactiva ─────────────────────────────────────────────────────────

def _iniciar_shell(sock: socket.socket):
    print("─" * 50)
    print("  Shell activa. Escribe mensajes y presiona Enter.")
    print("  Ctrl+C o Ctrl+D para salir.")
    print("─" * 50 + "\n")

    t_rx = threading.Thread(target=recibir, args=(sock,), daemon=True)
    t_tx = threading.Thread(target=enviar,  args=(sock,), daemon=True)

    t_rx.start()
    t_tx.start()

    try:
        t_tx.join()   # espera a que el usuario cierre stdin
    except KeyboardInterrupt:
        print("\n[*] Cerrando...")
    finally:
        sock.close()
        sys.exit(0)

# ── Entrada ───────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description="Teléfono TCP interactivo")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--listen",  action="store_true", help="Modo receptor")
    group.add_argument("--connect", action="store_true", help="Modo emisor")
    p.add_argument("--host", default="127.0.0.1", help="IP destino (solo --connect)")
    p.add_argument("--port", type=int, default=4444, help="Puerto (default: 4444)")
    args = p.parse_args()

    if args.listen:
        modo_escucha(args.port)
    else:
        modo_conectar(args.host, args.port)

if __name__ == "__main__":
    main()
