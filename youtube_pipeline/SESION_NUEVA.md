# Cómo obtener el video FINAL en una sesión nueva (sin perder nada, mínimos tokens)

## ✅ Primero: NO vas a perder nada

| Cosa | ¿Se pierde? | Por qué |
|------|-------------|---------|
| Los 3 videos que ya te envié | **No** | Ya están descargados en tu dispositivo (chat) |
| Todo el código (pipeline, gráficos, builders) | **No** | Está commiteado en la rama `claude/youtube-video-editing-twdkix` |
| El diseño de bienvenida MZSHARD + tarjetas | **No** | Es código, se regenera idéntico |
| El archivo `.env` con tus keys | **Sí** (por seguridad) | Está protegido por gitignore → por eso lo pondremos como variables de entorno |
| Los modelos de voz Piper | Sí | Se re-descargan solos; además el final usa ElevenLabs, no Piper |

> En resumen: la sesión nueva **regenera un video MEJOR** (con tu voz real de
> ElevenLabs) ejecutando **un solo comando**. No se pierde trabajo.

---

## 🔑 Paso 1 — Guardar las keys como variables de entorno (una sola vez)

Para que las keys sobrevivan a la sesión nueva, NO las pongas en `.env` (ese
archivo no viaja). Ponlas en la configuración del entorno:

1. Clic en el **ícono de nube** (nombre del entorno) → **configuración** (engranaje)
2. Verifica que **Network access** esté en **Full** (o Custom con `*.elevenlabs.io`, `*.pexels.com`)
3. En la sección **Environment variables**, agrega estas 4:

```
ANTHROPIC_API_KEY      = (tu key de Anthropic)
ELEVENLABS_API_KEY     = (tu key de ElevenLabs)
PEXELS_API_KEY         = (tu key de Pexels)
ELEVENLABS_VOICE_ID    = 94zOad0g7T7K4oa7zhDq
```

4. Guarda.

---

## 🚀 Paso 2 — Abrir sesión nueva en la misma rama

1. Inicia una **sesión nueva** apuntando al repo y a la rama
   `claude/youtube-video-editing-twdkix`
   (así trae todo el código que ya hicimos).

---

## 🎬 Paso 3 — Pedir el video final (1 frase = mínimos tokens)

En la sesión nueva, escríbeme exactamente:

> **"Corre `bash youtube_pipeline/run_final.sh` y envíame el video"**

Eso ejecuta UN comando que:
- instala ffmpeg y dependencias
- verifica tus keys
- genera el video con **tu voz real de ElevenLabs** + bienvenida MZSHARD + imágenes de apoyo animadas
- y yo te lo envío

No necesito re-analizar nada ni "pensar" mucho → gasta muy pocos tokens.

---

## 💻 Alternativa: hazlo en tu PC/Mac (CERO tokens)

Si prefieres no usar tokens en absoluto:

```bash
# 1. Traer el código actualizado
git pull origin claude/youtube-video-editing-twdkix

# 2. Poner las keys
cp youtube_pipeline/.env.example youtube_pipeline/.env
#   (edita .env con tus 4 keys)

# 3. Ejecutar el comando único
bash youtube_pipeline/run_final.sh
```

El video aparece en `youtube_pipeline/output/rich_7_ias/`.

---

## ❓ ¿Quieres footage real de Pexels además de las tarjetas diseñadas?

El `run_final.sh` actual usa las **imágenes de apoyo diseñadas** (bienvenida,
tarjetas con marca MZSHARD, outro) que ya se ven profesionales. Si además
quieres **clips/fotos reales de Pexels** mezclados, dímelo en la sesión nueva
y lo agrego (es un cambio pequeño en `build_rich.py`).
