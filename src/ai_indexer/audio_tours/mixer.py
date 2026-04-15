# ai_indexer/audio_tours/mixer.py
import logging
import shutil
from pathlib import Path
from typing import Optional

log = logging.getLogger("ai-indexer.mixer")


def finalize_audio(wav_path: Path, output_path: Path, bg_music: Optional[Path] = None) -> None:
    """Converte para MP3 (requer ffmpeg) ou WAV puro via módulo wave nativo.

    Se ffmpeg não estiver no PATH:
      - background music é ignorada
      - o WAV sintetizado é renomeado/copiado para *output_path* com sufixo .wav
    """

    if not wav_path.exists():
        return

    has_ffmpeg = shutil.which("ffmpeg") is not None

    if has_ffmpeg:
        # Caminho completo: pydub + ffmpeg (MP3 + opcional bg music)
        from pydub import AudioSegment  # importação tardia — requer ffmpeg

        narrative = AudioSegment.from_wav(str(wav_path))
        narrative = narrative + 3  # +3 dB para encorpar voz sintética

        if bg_music and bg_music.exists():
            bg = AudioSegment.from_file(str(bg_music))
            bg = bg - 20
            combined = narrative.overlay(bg, loop=True)
        else:
            combined = narrative

        combined.export(str(output_path), format="mp3", bitrate="128k")
        wav_path.unlink()
    else:
        # Caminho leve: copia o WAV diretamente (sem pydub/ffmpeg)
        wav_output = output_path.with_suffix(".wav")
        shutil.move(str(wav_path), str(wav_output))
        log.warning(
            "ffmpeg não encontrado — áudio salvo como WAV: %s. "
            "Instale ffmpeg para gerar MP3: brew install ffmpeg",
            wav_output,
        )