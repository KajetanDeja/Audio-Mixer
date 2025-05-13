import logging, sys


def setup_logging(level: str = "INFO") -> logging.Logger:
    fmt = "[%(asctime)s] %(levelname)s %(name)s: %(message)s"
    handler = logging.StreamHandler(sys.stdout)
    logging.basicConfig(level=level, format=fmt, handlers=[handler])
    return logging.getLogger("AudioStemMixer")
