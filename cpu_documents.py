"""Read an editable assembly draft or validated CPU checkpoint without UI effects."""
import mano_file


def read(path, restore_session):
    kind, payload = mano_file.load(path)
    if kind == "asm":
        # Drafts may be empty or contain unfinished/invalid assembly.
        return kind, payload
    if kind == "cpu-run":
        return kind, restore_session(payload)
    raise ValueError("Expected assembly draft or CPU checkpoint")
