#!/bin/bash
# =====================================================================
#  RETO · User data para una instancia lanzada DESDE TU AMI
#  La AMI ya trae la aplicación instalada: solo cambiamos la configuración.
# =====================================================================
set -euxo pipefail

F=/etc/webapp.env
sed -i 's/^COLOR_TEMA=.*/COLOR_TEMA=naranja/' "$F"
sed -i 's/^VERSION_DESPLIEGUE=.*/VERSION_DESPLIEGUE=v3-desde-AMI/' "$F"
systemctl restart webapp
