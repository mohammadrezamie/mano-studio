"""Record the actual runtime loaded by a frozen Windows application."""
import ctypes
import json
from pathlib import Path
import sys


def verify_paths(root, modules, required):
    root = Path(root).resolve()
    if not required or not set(required).issubset(modules):
        raise ValueError("Missing required private runtime module")
    result = {}
    for name, value in modules.items():
        path = Path(value).resolve()
        if not path.is_file() or not path.is_relative_to(root):
            raise ValueError("Runtime module outside application: " + name)
        result[name] = path.relative_to(root).as_posix()
    return result


def loaded_path(name):
    from ctypes import wintypes
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    handle = kernel.GetModuleHandleW
    handle.argtypes = [wintypes.LPCWSTR]
    handle.restype = wintypes.HMODULE
    filename = kernel.GetModuleFileNameW
    filename.argtypes = [wintypes.HMODULE, wintypes.LPWSTR, wintypes.DWORD]
    filename.restype = wintypes.DWORD
    loaded = handle(name)
    if not loaded:
        return None
    buffer = ctypes.create_unicode_buffer(32768)
    length = filename(loaded, buffer, len(buffer))
    if not length or length >= len(buffer):
        raise OSError("Cannot locate loaded module: " + name)
    return buffer.value


def write_report(path):
    if sys.platform != "win32" or not getattr(sys, "frozen", False):
        raise ValueError("Expected frozen Windows application")
    import ssl
    import _ssl
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([sys.argv[0]])
    ssl.create_default_context()  # Local TLS context, no connection.
    required = (f"python{sys.version_info.major}{sys.version_info.minor}.dll",
                "Qt6Core.dll", "Qt6Gui.dll", "Qt6Widgets.dll", Path(_ssl.__file__).name)
    optional = ("libcrypto-3.dll", "libssl-3.dll", "libcrypto-3-x64.dll", "libssl-3-x64.dll")
    modules = {name: value for name in required + optional if (value := loaded_path(name))}
    if not any(n.startswith("libcrypto-") for n in modules) or not any(n.startswith("libssl-") for n in modules):
        raise ValueError("Missing loaded TLS module evidence")
    private = verify_paths(Path(sys.executable).parent, modules, required)
    # Compatible OS/shared C runtimes may legitimately be used; record, don't modify.
    shared = {name: value for name in ("vcruntime140.dll", "vcruntime140_1.dll", "msvcp140.dll")
              if (value := loaded_path(name))}
    Path(path).write_text(json.dumps({"kind": "standalone-runtime-probe", "private": private,
        "shared_runtime_paths": shared, "python": sys.version.split()[0], "ssl": ssl.OPENSSL_VERSION,
        "clean_vm_verified": False, "public_release_approved": False}, indent=2) + "\n", encoding="utf-8")
    return 0
