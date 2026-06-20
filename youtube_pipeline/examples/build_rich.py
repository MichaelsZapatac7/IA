"""
Construye el video ENRIQUECIDO:
  - Bienvenida hablada del canal MZSHARD (intro con branding)
  - Imágenes de APOYO diseñadas (Pillow) por cada IA, animadas con Ken Burns
  - Outro de suscripción
  - Voz: ElevenLabs si hay red/keys; si no, Piper TTS local (fallback)

Ejecutar desde la raíz del repo:
  python -m youtube_pipeline.examples.build_rich
"""

import sys
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from youtube_pipeline.config import cfg
from youtube_pipeline.examples.script_7_ias import SCRIPT
from youtube_pipeline.generators.graphics import (
    make_support_image, make_welcome_image, make_outro_image,
)
from youtube_pipeline.editors.video_editor import ken_burns, get_video_info
from youtube_pipeline.editors.assembler import assemble_video

# Narración de bienvenida del canal (se antepone al guión)
WELCOME_TEXT = (
    "¡Bienvenido a MZSHARD! Tu canal de inteligencia artificial y tecnología. "
    "Hoy te traigo un ranking que tienes que ver: las siete inteligencias "
    "artificiales más poderosas del momento. Vamos con ello."
)

# tagline + tipo de imagen por etiqueta del segmento
TAGLINES = {
    "LAS 7 IA MÁS PODEROSAS": ("RANKING 2026", "topic"),
    "1. FABLE 5": ("El modelo más potente — con límites de uso", "ai"),
    "2. CLAUDE OPUS 4.8": ("Rey de la programación y los agentes", "ai"),
    "3. GPT-5": ("El todoterreno que todos conocen", "ai"),
    "4. GEMINI": ("Contexto gigante y multimodal", "ai"),
    "5. VIDEO IA: VEO & SORA": ("Texto a video cinematográfico", "ai"),
    "6. HIGGSFIELD": ("Tu director de cine con IA", "ai"),
    "7. ELEVENLABS": ("La voz más realista del mundo", "ai"),
    "SUSCRÍBETE": ("", "outro"),
}


def _audio_dur(path: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 6.0


def _gen_voice(text: str, out: Path):
    """ElevenLabs si está disponible; si no, Piper local."""
    try:
        from youtube_pipeline.generators.voiceover import text_to_speech
        if cfg.elevenlabs_api_key:
            return text_to_speech(text, out.with_suffix(".mp3"), voice_id=cfg.elevenlabs_voice_id)
    except Exception as e:
        print(f"    [voz] ElevenLabs no disponible ({str(e)[:50]}), uso Piper")
    from youtube_pipeline.generators.demo_assets import piper_voiceover, demo_voiceover, _piper_available
    return piper_voiceover(text, out) if _piper_available() else demo_voiceover(text, out)


def main():
    print("=" * 60)
    print("  VIDEO ENRIQUECIDO — MZSHARD")
    print("=" * 60)

    job = cfg.output_dir / "rich_7_ias"
    (job / "audio").mkdir(parents=True, exist_ok=True)
    (job / "img").mkdir(parents=True, exist_ok=True)
    (job / "clips").mkdir(parents=True, exist_ok=True)

    W, H, FPS = cfg.video_width, cfg.video_height, cfg.video_fps

    # Construir secuencia: bienvenida + segmentos del guión
    segments = [{"text": WELCOME_TEXT, "label": "WELCOME"}] + SCRIPT.segments

    audio_paths, footage_paths, used_segments = [], [], []

    for i, seg in enumerate(segments):
        text = seg.get("text", "").strip()
        label = seg.get("label", "")
        print(f"\n[{i+1}/{len(segments)}] {label or text[:30]}")

        # 1) voz
        audio = _gen_voice(text, job / "audio" / f"seg_{i:03d}")
        dur = _audio_dur(audio)
        print(f"    voz {dur:.1f}s -> {audio.name}")

        # 2) imagen de apoyo según tipo
        img_path = job / "img" / f"img_{i:03d}.png"
        if label == "WELCOME":
            make_welcome_image(img_path, channel="MZSHARD",
                               tagline="Inteligencia Artificial y Tecnología")
        else:
            tagline, kind = TAGLINES.get(label, ("", "ai"))
            if kind == "outro":
                make_outro_image(img_path, channel="MZSHARD")
            elif kind == "topic":
                make_support_image("7", "LAS 7 IA", tagline, img_path, index=i)
            else:
                num = label.split(".")[0].strip() if "." in label else str(i)
                name = label.split(".", 1)[1].strip() if "." in label else label
                make_support_image(num.zfill(2), name, tagline, img_path, index=i)

        # 3) Ken Burns (alterna zoom in/out para variar)
        clip = job / "clips" / f"clip_{i:03d}.mp4"
        ken_burns(img_path, clip, duration=dur + 0.5, width=W, height=H, fps=FPS,
                  direction="in" if i % 2 == 0 else "out")

        audio_paths.append(audio)
        footage_paths.append(clip)
        used_segments.append({**seg, "duration_seconds": dur})

    # Ensamblar con un guión que incluye la bienvenida
    rich_script = type(SCRIPT)(
        title=SCRIPT.title, description=SCRIPT.description, tags=SCRIPT.tags,
        hook=SCRIPT.hook, segments=used_segments,
        call_to_action=SCRIPT.call_to_action, thumbnail_text=SCRIPT.thumbnail_text,
        total_estimated_seconds=int(sum(s["duration_seconds"] for s in used_segments)),
        is_shorts=False,
    )

    print("\n[ensamblando] ...")
    final = assemble_video(
        script=rich_script, footage_paths=footage_paths, audio_paths=audio_paths,
        output_dir=job, is_shorts=False, burn_captions=True,
    )
    print(f"\n  LISTO -> {final}")
    return final


if __name__ == "__main__":
    main()
