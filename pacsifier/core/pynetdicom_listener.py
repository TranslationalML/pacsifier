"""Helpers to run a lightweight pynetdicom C-STORE listener."""

from __future__ import annotations

import os
import time

from pydicom.uid import generate_uid

try:
    from pynetdicom import AE, AllStoragePresentationContexts, evt
except ImportError as exc:  # pragma: no cover - surfaced at runtime entrypoints
    raise ImportError(
        "pynetdicom is required for Karnak forwarding. "
        "Install dependencies including pynetdicom==2.0."
    ) from exc


class PynetdicomListener:
    """Manage a background pynetdicom storage SCP."""

    def __init__(self, address: str, port: int, aet: str, output_dir: str):
        self.address = address
        self.port = int(port)
        self.aet = aet
        self.output_dir = output_dir
        self._scp = None
        self._thread = None

    def _on_c_store(self, event):
        os.makedirs(self.output_dir, exist_ok=True)

        ds = event.dataset
        ds.file_meta = event.file_meta
        sop_uid = getattr(ds, "SOPInstanceUID", "") or generate_uid()
        output_path = os.path.join(self.output_dir, f"{sop_uid}.dcm")
        ds.save_as(output_path, write_like_original=False)
        return 0x0000

    def start(self, wait_timeout: float = 5.0) -> None:
        ae = AE(ae_title=self.aet)
        for context in AllStoragePresentationContexts:
            ae.add_supported_context(context.abstract_syntax, context.transfer_syntax)

        handlers = [(evt.EVT_C_STORE, self._on_c_store)]
        self._scp = ae.start_server(
            (self.address, self.port),
            block=False,
            evt_handlers=handlers,
        )
        self._thread = self._scp.thread

        start = time.time()
        while self._thread is None:
            if (time.time() - start) > wait_timeout:
                raise RuntimeError("Timed out while starting pynetdicom listener thread.")
            time.sleep(0.05)

    def stop(self) -> None:
        if self._scp is not None:
            self._scp.shutdown()
            self._scp = None
            self._thread = None
