"""
Web de la práctica EC2 · IES Albarregas · DAM
------------------------------------------------
Pequeña aplicación Flask que muestra:
  1) La configuración del despliegue (la que inyecta el user data v2
     a través del fichero /etc/webapp.env).
  2) Los datos de la máquina EC2 que sirve la página, leídos en tiempo
     real del servicio de metadatos de la instancia (IMDSv2).

Rutas:
  /           -> página principal
  /api/info   -> los mismos datos en JSON (útil para comprobar con curl)
  /salud      -> comprobación de estado (health check)
"""

import os
import platform
import socket
import urllib.request
from datetime import datetime

from flask import Flask, jsonify, render_template

app = Flask(__name__)
app.json.ensure_ascii = False  # que curl muestre las tildes tal cual

# ---------------------------------------------------------------------------
# Temas de color que se pueden elegir con la variable COLOR_TEMA
# ---------------------------------------------------------------------------
TEMAS = {
    "azul": "#1565c0",
    "verde": "#2e7d32",
    "morado": "#6a1b9a",
    "naranja": "#e65100",
    "rojo": "#c62828",
    "gris": "#455a64",
}
TEMA_POR_DEFECTO = "gris"

# ---------------------------------------------------------------------------
# Metadatos de la instancia (IMDSv2)
# ---------------------------------------------------------------------------
IMDS = "http://169.254.169.254/latest"
CAMPOS_METADATOS = {
    "instance_id": "instance-id",
    "ami_id": "ami-id",
    "tipo_instancia": "instance-type",
    "zona_disponibilidad": "placement/availability-zone",
    "ip_privada": "local-ipv4",
    "ip_publica": "public-ipv4",
}
NO_DISPONIBLE = "no disponible"

# El servicio de metadatos nunca debe pasar por un proxy
_sin_proxy = urllib.request.build_opener(urllib.request.ProxyHandler({}))
_cache_metadatos = {}


def _pedir(url, cabeceras, metodo="GET"):
    peticion = urllib.request.Request(url, headers=cabeceras, method=metodo)
    with _sin_proxy.open(peticion, timeout=1) as respuesta:
        return respuesta.read().decode()


def leer_metadatos():
    """Devuelve los metadatos de la instancia. Se consultan una vez por
    proceso: si la máquina es nueva (por ejemplo, lanzada desde una AMI),
    el proceso también es nuevo y los datos se vuelven a leer."""
    if _cache_metadatos:
        return _cache_metadatos

    datos = {clave: NO_DISPONIBLE for clave in CAMPOS_METADATOS}
    try:
        # Paso 1 de IMDSv2: pedir un token de sesión (PUT)
        token = _pedir(
            f"{IMDS}/api/token",
            {"X-aws-ec2-metadata-token-ttl-seconds": "300"},
            metodo="PUT",
        )
        # Paso 2: usar el token en cada consulta (GET)
        for clave, ruta in CAMPOS_METADATOS.items():
            try:
                datos[clave] = _pedir(
                    f"{IMDS}/meta-data/{ruta}",
                    {"X-aws-ec2-metadata-token": token},
                )
            except Exception:
                pass  # p. ej. la instancia no tiene IP pública
        _cache_metadatos.update(datos)
    except Exception:
        pass  # No estamos en EC2 (por ejemplo, ejecutando en local)
    return datos


# ---------------------------------------------------------------------------
# Configuración del despliegue (variables de entorno)
# ---------------------------------------------------------------------------
def leer_configuracion():
    alumno = os.environ.get("ALUMNO", "").strip()
    nombre_tema = os.environ.get("COLOR_TEMA", "").strip().lower()
    if nombre_tema not in TEMAS:
        nombre_tema = TEMA_POR_DEFECTO
    ahora = datetime.now().astimezone()
    return {
        "configurada": bool(alumno),
        "alumno": alumno or "sin configurar",
        "version": os.environ.get("VERSION_DESPLIEGUE", "").strip() or "v1",
        "tema": nombre_tema,
        "color": TEMAS[nombre_tema],
        "hora_servidor": ahora.strftime("%d/%m/%Y %H:%M:%S"),
        "zona_horaria": ahora.strftime("%Z (UTC%z)"),
        "hostname": socket.gethostname(),
        "python": platform.python_version(),
    }


# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------
@app.route("/")
def inicio():
    return render_template(
        "index.html", cfg=leer_configuracion(), md=leer_metadatos()
    )


@app.route("/api/info")
def info():
    return jsonify(configuracion=leer_configuracion(), instancia=leer_metadatos())


@app.route("/salud")
def salud():
    return jsonify(estado="ok")


if __name__ == "__main__":
    # Solo para pruebas en local:  python app.py  ->  http://localhost:5000
    app.run(host="0.0.0.0", port=5000, debug=True)
