import argparse
import os
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent / "app"


def load_app():
    sys.path.insert(0, str(APP_DIR))
    from app import app
    return app


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Запуск портала «Конференции.РФ»")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 5000)))
    args = parser.parse_args()
    load_app().run(host=args.host, port=args.port, debug=False)
