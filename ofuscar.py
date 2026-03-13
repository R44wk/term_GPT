# ofuscar.py
import base64, marshal, py_compile, types

with open("phone.py", "r") as f:
    source = f.read()

code = compile(source, "phone.py", "exec")
payload = base64.b64encode(marshal.dumps(code)).decode()

ofuscado = f'''import base64,marshal
exec(marshal.loads(base64.b64decode("{payload}")))
'''

with open("phone_of.py", "w") as f:
    f.write(ofuscado)

print("[+] telefono_of.py generado")