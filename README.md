# term_GPT
# 📞 telefono.py

> Herramienta ligera de soporte técnico remoto por línea de comandos — sin agentes, sin instalaciones, solo Python.

---

## ¿Qué es?

`telefono.py` es una utilidad de soporte técnico remoto que permite a un técnico conectarse a la máquina de un usuario y ejecutar comandos de diagnóstico directamente desde la terminal. No requiere instalar software adicional en el equipo del usuario — solo Python 3, que viene preinstalado en macOS y la mayoría de distribuciones Linux.

Está pensado para escenarios donde herramientas gráficas como TeamViewer o AnyDesk no están disponibles, el acceso es por SSH pero sin credenciales configuradas, o simplemente se necesita una sesión rápida de diagnóstico sin fricción.

---

## Características

- ✅ Sin dependencias externas — solo stdlib de Python 3
- ✅ Funciona en macOS, Linux y Windows (WSL)
- ✅ Historial de comandos persistente (`↑` / `↓`)
- ✅ Autocompletado con `Tab` (comandos del sistema y rutas)
- ✅ Seguimiento del directorio de trabajo remoto
- ✅ Interfaz limpia con colores ANSI
- ✅ Un solo archivo, fácil de transferir

---

## Requisitos

- Python 3.6 o superior


---

## Uso rápido

### 1. En la máquina del usuario (modo escucha)

El usuario ejecuta este comando en su terminal y comparte su IP al técnico:

```bash
python3 telefono.py -l 4444
```

```
[*] Escuchando en 0.0.0.0:4444 ...
```

### 2. En la máquina del técnico (modo conexión)

```bash
python3 telefono.py -c <IP-del-usuario> 4444
```

```
[+] Conectado!
──────────────────────────────────────────────────────────────
  Shell Remota Interactiva
  Host : 192.168.1.20:4444
  Tab  : autocompletar   ↑/↓ : historial   exit : cerrar
──────────────────────────────────────────────────────────────

[/Users/usuario]$
```

A partir de aquí el técnico puede ejecutar comandos de diagnóstico directamente en la máquina remota.

---

## Ejemplos de uso en soporte técnico

```bash
# Ver información del sistema
uname -a
sw_vers                  # versión de macOS

# Revisar procesos que consumen recursos
top -l 1 -n 10
ps aux | grep <proceso>

# Verificar conectividad
ping -c 4 8.8.8.8
networksetup -listallhardwareports

# Revisar espacio en disco
df -h

# Ver logs del sistema
tail -50 /var/log/system.log

# Listar aplicaciones instaladas (macOS)
ls /Applications

# Cambiar directorio y explorar archivos
cd /var/log
ls -lh
```

---

## Referencia de argumentos

| Argumento | Descripción | Ejemplo |
|---|---|---|
| `-l <puerto>` | Modo escucha — equipo del usuario | `python3 telefono.py -l 4444` |
| `-c <host> <puerto>` | Modo conexión — equipo del técnico | `python3 telefono.py -c 192.168.1.5 4444` |

---

## Flujo de una sesión de soporte

```
Usuario                          Técnico
   │                                │
   │  python3 telefono.py -l 4444   │
   │  [*] Escuchando...             │
   │                                │  python3 telefono.py -c 192.168.1.20 4444
   │ ◄────── TCP connect ─────────  │
   │                                │
   │  [+] Conexión establecida      │  [+] Conectado!
   │                                │
   │ ◄────── "df -h" ─────────────  │  (técnico escribe comando)
   │                                │
   │  ejecuta df -h                 │
   │  ──────── output ──────────►   │  (técnico ve el resultado)
   │                                │
```

---

## Seguridad y buenas prácticas

- Usar **solo en redes de confianza** (red local, VPN corporativa)
- Cerrar la sesión con `exit` una vez terminado el soporte
- No exponer el puerto a Internet sin tunelización (SSH tunnel, VPN)
- El usuario tiene control total: él inicia y puede interrumpir la sesión con `Ctrl+C`

---

## Distribución sin código fuente visible

Si necesitas distribuir la herramienta sin exponer el código fuente:

```bash
# Compilar a binario nativo (macOS)
pip3 install pyinstaller
pyinstaller --onefile telefono.py

# El ejecutable queda en:
./dist/telefono
```

---

## Licencia

MIT — libre para uso personal y corporativo.
