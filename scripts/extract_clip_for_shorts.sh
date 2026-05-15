#!/bin/bash
# Script para extraer clip de YouTube y formatearlo para Shorts/Reels/TikTok
# Uso: bash extract_clip_for_shorts.sh [inicio_segundos] [duracion_segundos]
# Ejemplo: bash extract_clip_for_shorts.sh 30 60

VIDEO_URL="https://youtu.be/K7LKA_kr7p8"
START=${1:-0}        # Inicio en segundos (por defecto: 0)
DURATION=${2:-60}    # Duración en segundos (por defecto: 60)
OUTPUT_DIR="./clips_output"

mkdir -p "$OUTPUT_DIR"

echo "=== Descargando video de YouTube ==="
yt-dlp --no-check-certificates \
  -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" \
  -o "$OUTPUT_DIR/original.%(ext)s" \
  "$VIDEO_URL"

# Detectar el archivo descargado
ORIGINAL=$(ls "$OUTPUT_DIR"/original.* 2>/dev/null | head -1)
if [ -z "$ORIGINAL" ]; then
  echo "Error: No se pudo descargar el video."
  exit 1
fi

echo "=== Video descargado: $ORIGINAL ==="
echo "=== Extrayendo clip desde ${START}s por ${DURATION}s ==="

# Extraer el clip con recorte vertical 9:16 centrado
# Para Shorts/Reels/TikTok (1080x1920)
ffmpeg -ss "$START" -i "$ORIGINAL" -t "$DURATION" \
  -vf "crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale=1080:1920,setsar=1" \
  -c:v libx264 -crf 23 -preset fast \
  -c:a aac -b:a 128k \
  -movflags +faststart \
  "$OUTPUT_DIR/clip_vertical_${START}s_${DURATION}s.mp4"

echo ""
echo "=== Clip listo: $OUTPUT_DIR/clip_vertical_${START}s_${DURATION}s.mp4 ==="
echo "Formatos soportados: YouTube Shorts, Instagram Reels, TikTok"
