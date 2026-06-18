#!/usr/bin/env bash
# Regenera el feed desde Tiendanube y lo sube a GitHub.
# Programar con Task Scheduler de Windows cada 6 horas.
cd "$(dirname "$0")" || exit 1
python generar_feed.py || exit 1
git add fb_catalog.xml
git diff --cached --quiet && { echo "Sin cambios"; exit 0; }
git commit -m "chore: actualizar feed $(date +%Y-%m-%d_%H:%M)"
git push origin main
echo "Feed actualizado y publicado"
