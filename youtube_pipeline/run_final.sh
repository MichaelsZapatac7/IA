#!/usr/bin/env bash
#
# Script de UN SOLO COMANDO para producir el video final completo.
# Diseñado para gastar mínimos tokens: en una sesión nueva basta con ejecutarlo.
#
#   bash youtube_pipeline/run_final.sh
#
# Requisitos (deben existir como variables de entorno o en youtube_pipeline/.env):
#   ANTHROPIC_API_KEY, ELEVENLABS_API_KEY, PEXELS_API_KEY, ELEVENLABS_VOICE_ID
#
set -e

# Ir a la raíz del repo (carpeta padre de este script)
cd "$(dirname "$0")/.."
echo "== Carpeta de trabajo: $(pwd) =="

# 1) FFmpeg (motor de edición)
if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "== Instalando ffmpeg =="
  (apt-get update -qq && apt-get install -y ffmpeg) \
    || (sudo apt-get update -qq && sudo apt-get install -y ffmpeg)
fi

# 2) Dependencias de Python
echo "== Instalando dependencias de Python =="
pip3 install -q -r youtube_pipeline/requirements.txt

# 3) Verificar que las claves estén presentes
python3 - <<'PY'
from youtube_pipeline.config import cfg
import sys
faltan = [k for k,v in {
    "ANTHROPIC_API_KEY": cfg.anthropic_api_key,
    "ELEVENLABS_API_KEY": cfg.elevenlabs_api_key,
    "PEXELS_API_KEY": cfg.pexels_api_key,
}.items() if not v]
if faltan:
    print("FALTAN claves:", ", ".join(faltan))
    print("Agrega las variables de entorno o crea youtube_pipeline/.env")
    sys.exit(1)
print("Claves OK. Voz ElevenLabs:", cfg.elevenlabs_voice_id)
PY

# 4) Producir el video enriquecido (bienvenida MZSHARD + imágenes de apoyo +
#    voz: usa ElevenLabs automáticamente si hay red/keys, si no Piper)
echo "== Generando video final =="
python3 -m youtube_pipeline.examples.build_rich

echo ""
echo "== LISTO =="
echo "Video en: youtube_pipeline/output/rich_7_ias/"
ls -la youtube_pipeline/output/rich_7_ias/*FINAL.mp4 2>/dev/null || true
