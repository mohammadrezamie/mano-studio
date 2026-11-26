"""Native and legacy editable circuit file adapter."""
import json
from pathlib import Path
from circuit_document import CircuitDocument
from circuit_file import read_text
import mano_file


def load_circuit(path):
    if Path(path).suffix.lower() == mano_file.SUFFIX:
        kind, payload = mano_file.load(path)
        if kind != "circuit":
            raise ValueError("Expected a circuit document")
        return CircuitDocument.loads(json.dumps(payload))
    return CircuitDocument.loads(read_text(path))


def save_circuit(path, document):
    text = document.dumps()
    if Path(path).suffix.lower() == mano_file.SUFFIX:
        mano_file.save(path, "circuit", json.loads(text))
    else:
        Path(path).write_text(text, encoding="utf-8")
