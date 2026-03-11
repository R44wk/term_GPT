#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
from datetime import datetime
import readline  # Para historial y autocompletado
import atexit
import glob  # Para autocompletado de archivos

# Códigos de color ANSI (compatibles con macOS Terminal y iTerm)
class Colores:
    RESET = '\033[0m'
    ROJO = '\033[91m'
    VERDE = '\033[92m'
    AMARILLO = '\033[93m'
    AZUL = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BLANCO = '\033[97m'
    NEGRITA = '\033[1m'

class ShellAvanzada:
    def __init__(self):
        self.variables = {}
        self.historial = []
        self.directorio_actual = os.getcwd()
        self.history_file = os.path.expanduser("~/.mishell_history")
        self.configurar_historial()
        
    def configurar_historial(self):
        """Configura el historial de comandos para macOS"""
        try:
            readline.read_history_file(self.history_file)
        except FileNotFoundError:
            pass
        
        # Guardar historial al salir
        atexit.register(readline.write_history_file, self.history_file)
        
        # Configurar autocompletado para macOS
        readline.set_completer(self.autocompletar)
        readline.parse_and_bind("tab: complete")
        
        # Límite de historial
        readline.set_history_length(1000)
    
    def autocompletar(self, text, state):
        """Autocompletado mejorado para macOS"""
        # Comandos incorporados
        comandos = ['salir', 'exit', 'quit', 'ayuda', 'help', 'cd', 'ls', 
                   'pwd', 'echo', 'set', 'get', 'vars', 'historial', 
                   'fecha', 'clear', 'cat', 'mkdir', 'rm', 'cp', 'mv']
        
        # Si el texto empieza con $, autocompletar variables
        if text.startswith('$'):
            var_name = text[1:]
            opciones = [f"${var}" for var in self.variables.keys() 
                       if var.startswith(var_name)]
            try:
                return opciones[state]
            except IndexError:
                return None
        
        # Autocompletar comandos
        if not text or text.isalpha():
            opciones = [cmd for cmd in comandos if cmd.startswith(text)]
            try:
                return opciones[state]
            except IndexError:
                return None
        
        # Autocompletar archivos (para macOS)
        try:
            # Manejar rutas con ~
            if text.startswith('~'):
                text = os.path.expanduser(text)
            
            # Obtener directorio base
            if os.path.isdir(text):
                base_dir = text
                prefix = ''
            else:
                base_dir = os.path.dirname(text) or '.'
                prefix = os.path.basename(text)
            
            # Listar archivos que coincidan
            archivos = []
            try:
                for archivo in os.listdir(base_dir):
                    if archivo.startswith(prefix):
                        ruta_completa = os.path.join(base_dir, archivo)
                        if os.path.isdir(ruta_completa):
                            archivos.append(archivo + '/')
                        else:
                            archivos.append(archivo + ' ')
            except (PermissionError, FileNotFoundError):
                pass
            
            # Ordenar y devolver según state
            archivos.sort()
            try:
                return archivos[state]
            except IndexError:
                return None
                
        except Exception:
            return None
    
    def obtener_prompt(self):
        """Crea un prompt personalizado para macOS"""
        usuario = os.getenv('USER', 'user')
        
        # En macOS, obtener nombre del host
        try:
            host = subprocess.check_output(['scutil', '--get', 'ComputerName'], 
                                         text=True).strip()
        except:
            host = 'Mac'
        
        # Ruta bonita para macOS (acortar home)
        ruta = self.directorio_actual
        home = os.path.expanduser('~')
        if ruta.startswith(home):
            ruta = '~' + ruta[len(home):]
        
        # Prompt con estilo similar a terminal de macOS
        prompt = f"{Colores.VERDE}{usuario}@{host}{Colores.RESET}:"
        prompt += f"{Colores.AZUL}{ruta}{Colores.RESET}"
        
        if self.variables:
            prompt += f" {Colores.AMARILLO}[{len(self.variables)}]{Colores.RESET}"
        
        prompt += f"\n{Colores.MAGENTA}➜{Colores.RESET} "
        return prompt
    
    def ejecutar_comando(self, comando):
        """Procesa y ejecuta comandos"""
        if not comando.strip():
            return
        
        self.historial.append(comando)
        partes = comando.split()
        cmd = partes[0].lower()
        args = partes[1:] if len(partes) > 1 else []
        
        # Comandos incorporados
        comandos = {
            'salir': self.salir,
            'exit': self.salir,
            'quit': self.salir,
            'ayuda': self.ayuda,
            'help': self.ayuda,
            'cd': self.cambiar_directorio,
            'ls': self.listar,
            'pwd': self.pwd,
            'echo': self.echo,
            'set': self.set_variable,
            'get': self.get_variable,
            'vars': self.mostrar_variables,
            'historial': self.mostrar_historial,
            'fecha': self.fecha,
            'clear': self.limpiar_pantalla,
            'cat': self.ver_archivo,
            'mkdir': self.crear_directorio,
            'open': self.abrir_archivo,  # Comando específico de macOS
        }
        
        if cmd in comandos:
            try:
                comandos[cmd](args)
            except Exception as e:
                print(f"{Colores.ROJO}Error: {e}{Colores.RESET}")
        else:
            # Ejecutar comando del sistema (macOS)
            self.ejecutar_sistema(comando)
    
    def ejecutar_sistema(self, comando):
        """Ejecuta comandos del sistema en macOS"""
        try:
            # Expandir variables de nuestra shell
            for var, valor in self.variables.items():
                comando = comando.replace(f"${var}", str(valor))
            
            # Usar shell de macOS (zsh o bash)
            resultado = subprocess.run(comando, shell=True, 
                                     capture_output=True, text=True,
                                     executable='/bin/zsh')  # Usar zsh (shell por defecto en macOS)
            
            if resultado.stdout:
                print(resultado.stdout, end='')
            if resultado.stderr:
                print(f"{Colores.ROJO}{resultado.stderr}{Colores.RESET}", end='')
                
        except Exception as e:
            print(f"{Colores.ROJO}Error ejecutando comando: {e}{Colores.RESET}")
    
    # ===== COMANDOS INCORPORADOS =====
    
    def salir(self, args):
        """Sale de la shell"""
        print(f"{Colores.VERDE}¡Hasta luego!{Colores.RESET}")
        sys.exit(0)
    
    def ayuda(self, args):
        """Muestra ayuda de comandos"""
        ayuda_texto = f"""
{Colores.NEGRITA}{Colores.CYAN}╔════════════════════════════════════╗{Colores.RESET}
{Colores.NEGRITA}{Colores.CYAN}║     COMANDOS DISPONIBLES (macOS)   ║{Colores.RESET}
{Colores.NEGRITA}{Colores.CYAN}╚════════════════════════════════════╝{Colores.RESET}

{Colores.AMARILLO}COMANDOS BÁSICOS:{Colores.RESET}
  salir, exit, quit   - Salir de la shell
  ayuda, help         - Muestra esta ayuda
  clear               - Limpiar pantalla
  fecha               - Mostrar fecha y hora
  historial           - Ver historial de comandos

{Colores.AMARILLO}NAVEGACIÓN Y ARCHIVOS:{Colores.RESET}
  cd [directorio]     - Cambiar directorio
  pwd                 - Mostrar directorio actual
  ls [ruta]           - Listar archivos
  cat [archivo]       - Ver contenido de archivo
  mkdir [nombre]      - Crear directorio
  open [archivo]      - Abrir archivo con app por defecto (macOS)

{Colores.AMARILLO}VARIABLES:{Colores.RESET}
  set nombre=valor    - Crear variable
  get nombre          - Mostrar variable
  vars                - Listar todas las variables

{Colores.AMARILLO}CUALQUIER OTRO COMANDO:{Colores.RESET}
  Se ejecuta en la terminal de macOS (zsh/bash)
  Ej: grep, find, ps, top, etc.

{Colores.NEGRITA}Presiona TAB para autocompletar comandos y archivos{Colores.RESET}
        """
        print(ayuda_texto)
    
    def cambiar_directorio(self, args):
        """Cambia el directorio actual (compatible con macOS)"""
        if not args:
            destino = os.path.expanduser('~')
        else:
            # Manejar rutas con espacios
            destino = ' '.join(args)
            destino = os.path.expanduser(destino)
        
        try:
            os.chdir(destino)
            self.directorio_actual = os.getcwd()
        except FileNotFoundError:
            print(f"{Colores.ROJO}Directorio no encontrado: {destino}{Colores.RESET}")
        except PermissionError:
            print(f"{Colores.ROJO}Permiso denegado: {destino}{Colores.RESET}")
    
    def listar(self, args):
        """Lista archivos al estilo macOS (con colores y detalles)"""
        try:
            # Usar comando ls de macOS para mejor formato
            if args and args[0] == '-l':
                # Listado detallado
                resultado = subprocess.run(['ls', '-l'] + args[1:], 
                                         capture_output=True, text=True)
            elif args:
                resultado = subprocess.run(['ls'] + args, 
                                         capture_output=True, text=True)
            else:
                resultado = subprocess.run(['ls', '-G'],  # -G para colores en macOS
                                         capture_output=True, text=True)
            
            if resultado.stdout:
                print(resultado.stdout)
            if resultado.stderr:
                print(f"{Colores.ROJO}{resultado.stderr}{Colores.RESET}")
                
        except Exception as e:
            # Fallback simple si el comando ls falla
            try:
                archivos = os.listdir('.')
                for archivo in sorted(archivos):
                    if os.path.isdir(archivo):
                        print(f"{Colores.AZUL}{archivo}/{Colores.RESET}")
                    else:
                        # Mostrar tamaño para archivos
                        tamaño = os.path.getsize(archivo) if os.path.exists(archivo) else 0
                        if tamaño < 1024:
                            tamaño_str = f"{tamaño}B"
                        elif tamaño < 1024*1024:
                            tamaño_str = f"{tamaño//1024}KB"
                        else:
                            tamaño_str = f"{tamaño//(1024*1024)}MB"
                        print(f"{archivo:30} {Colores.AMARILLO}{tamaño_str:>6}{Colores.RESET}")
            except Exception:
                print(f"{Colores.ROJO}Error listando archivos{Colores.RESET}")
    
    def pwd(self, args):
        """Muestra el directorio actual"""
        print(self.directorio_actual)
    
    def echo(self, args):
        """Muestra el texto proporcionado"""
        texto = ' '.join(args)
        print(texto)
    
    def ver_archivo(self, args):
        """Muestra contenido de archivo (como cat)"""
        if not args:
            print("Uso: cat [archivo]")
            return
        
        archivo = args[0]
        try:
            with open(archivo, 'r') as f:
                print(f.read())
        except FileNotFoundError:
            print(f"{Colores.ROJO}Archivo no encontrado: {archivo}{Colores.RESET}")
        except Exception as e:
            print(f"{Colores.ROJO}Error leyendo archivo: {e}{Colores.RESET}")
    
    def crear_directorio(self, args):
        """Crea un nuevo directorio"""
        if not args:
            print("Uso: mkdir [nombre_directorio]")
            return
        
        nombre = args[0]
        try:
            os.mkdir(nombre)
            print(f"{Colores.VERDE}Directorio '{nombre}' creado{Colores.RESET}")
        except FileExistsError:
            print(f"{Colores.ROJO}El directorio '{nombre}' ya existe{Colores.RESET}")
        except Exception as e:
            print(f"{Colores.ROJO}Error: {e}{Colores.RESET}")
    
    def abrir_archivo(self, args):
        """Abre un archivo con la aplicación por defecto (comando 'open' de macOS)"""
        if not args:
            print("Uso: open [archivo_o_directorio]")
            return
        
        try:
            subprocess.run(['open'] + args)
        except Exception as e:
            print(f"{Colores.ROJO}Error abriendo: {e}{Colores.RESET}")
    
    def set_variable(self, args):
        """Establece una variable: set nombre=valor"""
        if not args:
            print("Uso: set nombre=valor")
            return
        
        try:
            var, valor = args[0].split('=', 1)
            self.variables[var] = valor
            print(f"{Colores.VERDE}Variable '{var}' = '{valor}'{Colores.RESET}")
        except ValueError:
            print(f"{Colores.ROJO}Formato incorrecto. Usa: set nombre=valor{Colores.RESET}")
    
    def get_variable(self, args):
        """Muestra el valor de una variable"""
        if not args:
            print("Uso: get nombre")
            return
        
        var = args[0]
        if var in self.variables:
            print(f"{var} = {self.variables[var]}")
        else:
            print(f"{Colores.ROJO}Variable no encontrada: {var}{Colores.RESET}")
    
    def mostrar_variables(self, args):
        """Muestra todas las variables definidas"""
        if not self.variables:
            print("No hay variables definidas")
            return
        
        print(f"{Colores.CYAN}Variables definidas:{Colores.RESET}")
        for var, valor in sorted(self.variables.items()):
            print(f"  {var} = {valor}")
    
    def mostrar_historial(self, args):
        """Muestra el historial de comandos"""
        if not self.historial:
            print("Historial vacío")
            return
        
        print(f"{Colores.CYAN}Historial de comandos (últimos 20):{Colores.RESET}")
        inicio = max(0, len(self.historial) - 20)
        for i, cmd in enumerate(self.historial[inicio:], inicio + 1):
            print(f"  {i:3d}  {cmd}")
    
    def fecha(self, args):
        """Muestra fecha y hora actual (formato macOS)"""
        ahora = datetime.now()
        print(ahora.strftime("%a %b %d %H:%M:%S %Y"))  # Formato similar a macOS
    
    def limpiar_pantalla(self, args):
        """Limpia la pantalla (compatible con macOS)"""
        os.system('clear')  # 'clear' funciona en macOS
    
    def iniciar(self):
        """Inicia el bucle principal de la shell"""
        self.limpiar_pantalla([])
        
        # Banner de inicio estilo macOS
        print(f"{Colores.NEGRITA}{Colores.CYAN}╔════════════════════════════════════════╗{Colores.RESET}")
        print(f"{Colores.NEGRITA}{Colores.CYAN}║     SHELL INTERACTIVA PARA macOS       ║{Colores.RESET}")
        print(f"{Colores.NEGRITA}{Colores.CYAN}╚════════════════════════════════════════╝{Colores.RESET}")
        print(f"{Colores.VERDE}✓ Historial habilitado")
        print(f"✓ Autocompletado con TAB")
        print(f"✓ Compatible con zsh/bash{Colores.RESET}")
        print(f"\n{Colores.AMARILLO}Escribe 'ayuda' para ver comandos disponibles{Colores.RESET}\n")
        
        while True:
            try:
                comando = input(self.obtener_prompt())
                self.ejecutar_comando(comando)
            except KeyboardInterrupt:
                print("\nUsa 'salir' para terminar")
            except EOFError:
                print("\nSaliendo...")
                break

if __name__ == "__main__":
    shell = ShellAvanzada()
    shell.iniciar()
