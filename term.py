import os
import sys
import subprocess
from datetime import datetime

# Códigos de color ANSI
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
        
    def obtener_prompt(self):
        """Crea un prompt personalizado con colores"""
        usuario = os.getenv('USER', os.getenv('USERNAME', 'user'))
        host = os.uname()[1] if hasattr(os, 'uname') else 'localhost'
        
        prompt = f"{Colores.VERDE}{usuario}@{host}{Colores.RESET}:"
        prompt += f"{Colores.AZUL}{self.directorio_actual}{Colores.RESET}"
        
        if self.variables:
            prompt += f" {Colores.AMARILLO}({len(self.variables)} vars){Colores.RESET}"
        
        prompt += f"\n{Colores.MAGENTA}❯{Colores.RESET} "
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
            'dir': self.listar,
            'pwd': self.pwd,
            'echo': self.echo,
            'set': self.set_variable,
            'get': self.get_variable,
            'vars': self.mostrar_variables,
            'historial': self.mostrar_historial,
            'fecha': self.fecha,
            'clear': self.limpiar_pantalla,
        }
        
        if cmd in comandos:
            try:
                comandos[cmd](args)
            except Exception as e:
                print(f"{Colores.ROJO}Error: {e}{Colores.RESET}")
        else:
            # Intentar ejecutar como comando del sistema
            self.ejecutar_sistema(comando)
    
    def ejecutar_sistema(self, comando):
        """Ejecuta comandos del sistema operativo"""
        try:
            # Expandir variables de nuestra shell
            for var, valor in self.variables.items():
                comando = comando.replace(f"${var}", str(valor))
            
            resultado = subprocess.run(comando, shell=True, 
                                     capture_output=True, text=True)
            
            if resultado.stdout:
                print(resultado.stdout, end='')
            if resultado.stderr:
                print(f"{Colores.ROJO}{resultado.stderr}{Colores.RESET}", end='')
                
        except Exception as e:
            print(f"{Colores.ROJO}Error ejecutando comando: {e}{Colores.RESET}")
    
    def salir(self, args):
        """Sale de la shell"""
        print(f"{Colores.VERDE}¡Hasta luego!{Colores.RESET}")
        sys.exit(0)
    
    def ayuda(self, args):
        """Muestra ayuda de comandos"""
        ayuda_texto = f"""
{Colores.NEGRITA}{Colores.CYAN}COMANDOS DISPONIBLES:{Colores.RESET}
  {Colores.AMARILLO}salir, exit, quit{Colores.RESET}   - Salir de la shell
  {Colores.AMARILLO}ayuda, help{Colores.RESET}         - Muestra esta ayuda
  {Colores.AMARILLO}cd [directorio]{Colores.RESET}     - Cambiar directorio
  {Colores.AMARILLO}ls, dir{Colores.RESET}             - Listar archivos
  {Colores.AMARILLO}pwd{Colores.RESET}                 - Mostrar directorio actual
  {Colores.AMARILLO}echo [texto]{Colores.RESET}        - Mostrar texto
  {Colores.AMARILLO}set var=valor{Colores.RESET}       - Crear variable
  {Colores.AMARILLO}get var{Colores.RESET}             - Mostrar variable
  {Colores.AMARILLO}vars{Colores.RESET}                - Listar variables
  {Colores.AMARILLO}historial{Colores.RESET}           - Ver historial
  {Colores.AMARILLO}fecha{Colores.RESET}               - Mostrar fecha y hora
  {Colores.AMARILLO}clear{Colores.RESET}               - Limpiar pantalla

{Colores.NEGRITA}{Colores.CYAN}Cualquier otro comando se ejecuta en el sistema.{Colores.RESET}
        """
        print(ayuda_texto)
    
    def cambiar_directorio(self, args):
        """Cambia el directorio actual"""
        if not args:
            destino = os.path.expanduser('~')
        else:
            destino = args[0]
        
        try:
            os.chdir(destino)
            self.directorio_actual = os.getcwd()
        except FileNotFoundError:
            print(f"{Colores.ROJO}Directorio no encontrado: {destino}{Colores.RESET}")
        except PermissionError:
            print(f"{Colores.ROJO}Permiso denegado: {destino}{Colores.RESET}")
    
    def listar(self, args):
        """Lista archivos en el directorio actual"""
        try:
            archivos = os.listdir('.')
            for archivo in sorted(archivos):
                if os.path.isdir(archivo):
                    print(f"{Colores.AZUL}{archivo}/{Colores.RESET}")
                else:
                    print(f"  {archivo}")
        except Exception as e:
            print(f"{Colores.ROJO}Error listando archivos: {e}{Colores.RESET}")
    
    def pwd(self, args):
        """Muestra el directorio actual"""
        print(self.directorio_actual)
    
    def echo(self, args):
        """Muestra el texto proporcionado"""
        texto = ' '.join(args)
        print(texto)
    
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
        
        print(f"{Colores.CYAN}Historial de comandos:{Colores.RESET}")
        for i, cmd in enumerate(self.historial[-20:], 1):  # Últimos 20
            print(f"  {i:3d}  {cmd}")
    
    def fecha(self, args):
        """Muestra fecha y hora actual"""
        ahora = datetime.now()
        print(ahora.strftime("%A, %d de %B de %Y - %H:%M:%S"))
    
    def limpiar_pantalla(self, args):
        """Limpia la pantalla"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def iniciar(self):
        """Inicia el bucle principal de la shell"""
        self.limpiar_pantalla([])
        print(f"{Colores.NEGRITA}{Colores.VERDE}╔════════════════════════════════╗{Colores.RESET}")
        print(f"{Colores.NEGRITA}{Colores.VERDE}║   SHELL INTERACTIVA AVANZADA  ║{Colores.RESET}")
        print(f"{Colores.NEGRITA}{Colores.VERDE}╚════════════════════════════════╝{Colores.RESET}")
        print(f"{Colores.AMARILLO}Escribe 'ayuda' para ver comandos disponibles{Colores.RESET}\n")
        
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