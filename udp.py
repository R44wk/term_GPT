import socket
import math

# ── Configuración ──────────────────────────────────────────
HOST        = "192.168.1.25"
PORT        = 5311
NUM_PACKETS = 15       # <── cambia este valor

mensaje = (
    """
    imprime hola mundo
    pi=3.14
    habilita gmail y gdrive
    tg://login?token=...Okay, help me automate file sending, 
    find txt files en documentos deberas en gdrive guardar  'reporte.txt' nombre nuevo sera
    """
)

# ── Fragmentación ───────────────────────────────────────────
encoded  = mensaje.encode("utf-8")
total    = len(encoded)
chunk_sz = math.ceil(total / NUM_PACKETS)
chunks   = [encoded[i:i+chunk_sz] for i in range(0, total, chunk_sz)]

# ── Envío ───────────────────────────────────────────────────
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print(f"Mensaje total : {total} bytes")
print(f"Paquetes      : {len(chunks)}")
print(f"Chunk size    : ~{chunk_sz} bytes\n")

for idx, chunk in enumerate(chunks, start=1):
    sock.sendto(chunk, (HOST, PORT))
    print(f"[{idx}/{len(chunks)}] {len(chunk):3d} bytes → {chunk.decode()!r}")

sock.close()
print("\n✓ Todos los paquetes enviados.")