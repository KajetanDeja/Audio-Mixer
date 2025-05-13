import os
import shutil
import sys
import tempfile

import ffmpeg
from demucs.separate import main as demucs_main

from config import settings
from logger import setup_logging

logger = setup_logging(settings.log_level)


def configure_ffmpeg():
    base = getattr(sys, "_MEIPASS", os.path.dirname(__file__))
    ffm_dir = os.path.join(base, "resources", "ffmpeg")
    ffm = os.path.join(ffm_dir, "ffmpeg.exe")
    if not os.path.isfile(ffm):
        ffm = shutil.which("ffmpeg") or ffm
    if not os.path.isfile(ffm):
        raise RuntimeError(f"ffmpeg.exe nie znaleziony w {ffm_dir} ani w PATH")
    os.environ["PATH"] = ffm_dir + os.pathsep + os.environ.get("PATH", "")
configure_ffmpeg()


def extract_audio(input_video: str, audio_wav: str) -> None:
    logger.info(f"🔊 Extracting audio from {input_video}")
    (
        ffmpeg
        .input(input_video)
        .output(audio_wav, vn=None, acodec="pcm_s16le")
        .overwrite_output()
        .run(quiet=True)
    )
    logger.info("✅ Audio extracted")


def separate_tracks(input_wav: str, out_dir: str) -> tuple[str, str]:
    logger.info(f"🎚️ Separating tracks with model '{settings.demucs_model}'")
    args = [
        "--two-stems", "vocals",
        "-d", "cpu",
        "-n", settings.demucs_model,
        "-o", out_dir,
        input_wav
    ]
    demucs_main(args)

    base = os.path.splitext(os.path.basename(input_wav))[0]
    demucs_out = os.path.join(out_dir, settings.demucs_model, base)

    vocals = os.path.join(demucs_out, "vocals.wav")
    candidates = ["other.wav", "accompaniment.wav"]
    instr = None
    for name in candidates:
        p = os.path.join(demucs_out, name)
        if os.path.exists(p):
            instr = p
            break

    if not os.path.exists(vocals) or instr is None:
        logger.error("❌ Demucs wypakował w katalogu:")
        for fn in sorted(os.listdir(demucs_out)):
            logger.error(f"   • {fn}")
        raise RuntimeError(
            f"Demucs did not produce expected stems: "
            f"vocals={vocals!r}, instr={instr!r}"
        )

    logger.info("✅ Tracks separated:")
    logger.info(f"   vocals -> {vocals}")
    logger.info(f"   instr  -> {instr}")
    return vocals, instr


def mix_tracks(vocals: str, instr: str, mixed_wav: str, vol: float) -> None:
    logger.info(f"🎛️ Mixing tracks (volume={vol})")
    v_stream = ffmpeg.input(vocals)
    i_stream = ffmpeg.input(instr).filter("volume", vol)
    merged = ffmpeg.filter([v_stream, i_stream], "amerge", inputs=2)
    (
        ffmpeg
        .output(merged, mixed_wav, ac=2)
        .overwrite_output()
        .run(quiet=True)
    )
    logger.info("✅ Tracks mixed")


def remix_video(input_vid: str, mixed_wav: str, output_vid: str) -> None:
    logger.info("🎬 Remixing video + new audio")
    vs = ffmpeg.input(input_vid)
    as_ = ffmpeg.input(mixed_wav)
    (
        ffmpeg
        .output(vs, as_, output_vid,
                vcodec="copy", acodec="aac",
                audio_bitrate=settings.audio_bitrate)
        .global_args("-map", "0:v:0", "-map", "1:a:0")
        .overwrite_output()
        .run(quiet=True)
    )
    logger.info("✅ Remix complete")


def full_pipeline(
        input_video: str,
        output_video: str,
        volume: float,
        logger_signal: callable,
        progress_signal: callable
) -> None:
    tmp = tempfile.mkdtemp()
    try:
        audio_wav = os.path.join(tmp, "audio.wav")
        tracks_dir = os.path.join(tmp, "tracks");
        os.makedirs(tracks_dir)
        mixed_wav = os.path.join(tmp, "mixed.wav")

        logger_signal(f"🔧 Temp dir: {tmp}")
        progress_signal(0)

        logger_signal("🔊 Extracting audio")
        extract_audio(input_video, audio_wav)
        progress_signal(25)

        logger_signal("🎚️ Separating tracks")
        vocals, instr = separate_tracks(audio_wav, tracks_dir)
        progress_signal(50)

        logger_signal("🎛️ Mixing tracks")
        mix_tracks(vocals, instr, mixed_wav, volume)
        progress_signal(75)

        logger_signal("🎬 Remixing video + new audio")
        remix_video(input_video, mixed_wav, output_video)
        progress_signal(100)

        logger_signal("✅ Done")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
