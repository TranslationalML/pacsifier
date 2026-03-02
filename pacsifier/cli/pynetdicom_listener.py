"""CLI entrypoint to run a standalone pynetdicom listener."""

import argparse
import signal
import time

from pacsifier.core.pynetdicom_listener import PynetdicomListener


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run pacsifier pynetdicom listener.")
    parser.add_argument("--address", required=True, help="Listener bind address")
    parser.add_argument("--port", required=True, type=int, help="Listener bind port")
    parser.add_argument("--aet", required=True, help="Listener AE title")
    parser.add_argument("--output_dir", required=True, help="Directory to store received DICOMs")
    return parser


def main() -> None:
    parser = get_parser()
    args = parser.parse_args()

    listener = PynetdicomListener(
        address=args.address,
        port=args.port,
        aet=args.aet,
        output_dir=args.output_dir,
    )

    should_run = {"value": True}

    def _shutdown(*_):
        should_run["value"] = False

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    listener.start()
    try:
        while should_run["value"]:
            time.sleep(0.5)
    finally:
        listener.stop()


if __name__ == "__main__":
    main()
