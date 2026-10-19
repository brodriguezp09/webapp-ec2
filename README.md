# webapp-ec2 · Práctica EC2 (IES Albarregas · DAM)

Pequeña web en **Python (Flask + Gunicorn)** para la práctica guiada de Amazon EC2 en AWS Academy Learner Lab.

La página muestra dos cosas:

1. **La configuración del despliegue** (alumno, versión, color, zona horaria), que llega a través del fichero `/etc/webapp.env` creado por el *user data*.
2. **Qué máquina la está sirviendo** (ID de instancia, AMI, zona de disponibilidad, IPs), leído en tiempo real del servicio de metadatos **IMDSv2**.

## Estructura

```
webapp-ec2/
├── app.py                  # aplicación Flask
├── requirements.txt        # dependencias (Flask y Gunicorn)
├── templates/index.html    # página principal
├── static/style.css        # estilos (el color sale de COLOR_TEMA)
└── userdata/
    ├── userdata-v1.sh      # user data inicial
    ├── userdata-v2.sh      # user data modificado (v1 + bloque nuevo)
    └── userdata-reto-ami.sh# reto opcional: user data para una instancia lanzada desde la AMI
```

## Rutas

| Ruta        | Qué devuelve                                  |
|-------------|-----------------------------------------------|
| `/`         | Página principal                              |
| `/api/info` | Los mismos datos en JSON                      |
| `/salud`    | `{"estado": "ok"}` (comprobación de estado)   |

## Variables de configuración

| Variable             | Ejemplo               | Valor por defecto |
|----------------------|-----------------------|-------------------|
| `ALUMNO`             | `María López Pérez`   | `sin configurar`  |
| `COLOR_TEMA`         | `azul`, `verde`, `morado`, `naranja`, `rojo`, `gris` | `gris` |
| `VERSION_DESPLIEGUE` | `v2`                  | `v1`              |

## Probar en local

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
ALUMNO="Prueba Local" COLOR_TEMA=morado python app.py
# Abre http://localhost:5000
```

En local los datos de la instancia aparecen como «no disponible», porque no hay servicio de metadatos de EC2.

## Copiar el user data sin errores

Copia los scripts desde GitHub con el botón **Raw** (o **Copy raw file**), no desde un documento de Word: Word cambia las comillas y los guiones y el script deja de funcionar.
