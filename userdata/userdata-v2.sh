#!/bin/bash
# =====================================================================
#  USER DATA v2 · Práctica EC2 · IES Albarregas · DAM
#  Es el v1 SIN CAMBIOS + el bloque "NUEVO EN v2" del final.
# =====================================================================
set -euxo pipefail   # para si hay un error y escribe cada orden en el log

# 1) Variables (cambia TU_USUARIO por el usuario de GitHub del repositorio)
REPO_URL="https://github.com/TU_USUARIO/webapp-ec2.git"
APP_DIR="/opt/webapp"

# 2) Paquetes del sistema (Amazon Linux 2023 usa dnf)
dnf install -y git python3-pip

# 3) Descargar la aplicación desde GitHub
git clone "$REPO_URL" "$APP_DIR"

# 4) Entorno virtual de Python e instalación de dependencias
python3 -m venv "$APP_DIR/venv"
"$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt"

# 5) Servicio systemd: la web arranca sola, también tras cada reinicio
cat > /etc/systemd/system/webapp.service <<'EOF'
[Unit]
Description=Web de la practica EC2 (Flask + Gunicorn)
After=network-online.target
Wants=network-online.target

[Service]
User=ec2-user
WorkingDirectory=/opt/webapp
EnvironmentFile=-/etc/webapp.env
ExecStart=/opt/webapp/venv/bin/gunicorn --workers 2 --bind 0.0.0.0:80 app:app
AmbientCapabilities=CAP_NET_BIND_SERVICE
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now webapp

# =====================================================================
#  NUEVO EN v2
# =====================================================================
# 6) Zona horaria de España peninsular
timedatectl set-timezone Europe/Madrid

# 7) Configuración de la web (systemd la lee gracias a EnvironmentFile)
#    Escribe TU nombre y elige color: azul, verde, morado, naranja, rojo o gris
cat > /etc/webapp.env <<'EOF'
ALUMNO=Nombre Apellido1 Apellido2
COLOR_TEMA=verde
VERSION_DESPLIEGUE=v2
EOF

# 8) Reiniciar el servicio para que lea la nueva configuración
systemctl restart webapp
