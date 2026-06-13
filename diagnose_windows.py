#!/usr/bin/env python3
"""
Windows diagnostics for Harmonica Notation.
Run with:  python diagnose_windows.py
"""
import sys, os, time

print("=" * 55)
print("Harmonica Notation — Windows Diagnostics")
print("=" * 55)

# ── Architecture + DLLs in current directory ──────────────
print("\n--- Architecture ---")
import ctypes, os, struct
print(f"  Python: {struct.calcsize('P')*8}-bit")

def _dll_bits(path):
    """Return 32 or 64 for a PE DLL, or None if unreadable."""
    try:
        with open(path, 'rb') as f:
            if f.read(2) != b'MZ':
                return None
            f.seek(60); pe_offset = struct.unpack('<I', f.read(4))[0]
            f.seek(pe_offset + 4)
            machine = struct.unpack('<H', f.read(2))[0]
            return 64 if machine == 0x8664 else 32
    except Exception:
        return None

print("\n--- MinGW / MSVC runtime DLLs (FluidSynth dependencies) ---")
_runtime_dlls = [
    # MinGW C++ runtime (needed by MinGW-compiled FluidSynth)
    'libgcc_s_seh-1.dll',
    'libstdc++-6.dll',
    'libwinpthread-1.dll',
    # MSVC runtime (needed by MSVC-compiled FluidSynth)
    'VCRUNTIME140.dll',
    'MSVCP140.dll',
]
for dll in _runtime_dlls:
    try:
        ctypes.WinDLL(dll)
        print(f"  {dll}: found OK")
    except OSError:
        print(f"  {dll}: NOT FOUND")

print("\n--- DLLs in current directory ---")
# Use os.listdir to avoid case-insensitive duplicate matches on Windows
_local_dlls = sorted(
    f for f in os.listdir('.') if f.lower().endswith('.dll'))
if _local_dlls:
    for dll in _local_dlls:
        bits = _dll_bits(dll)
        bits_str = f"{bits}-bit" if bits else "?"
        try:
            ctypes.WinDLL(os.path.abspath(dll))
            print(f"  {dll} ({bits_str}): loads OK")
        except OSError as e:
            print(f"  {dll} ({bits_str}): FAILED — {e}")
else:
    print("  (none — DLLs must be on PATH)")

# ── FluidSynth audio drivers ──────────────────────────────
print("\n--- FluidSynth audio drivers ---")
try:
    import fluidsynth
    print("pyfluidsynth imported OK")
except Exception as e:
    print(f"FAILED to import fluidsynth: {e}")
    sys.exit(1)

sf2 = 'Hohner_Silverstar_Harmonica.sf2'
if not os.path.exists(sf2):
    print(f"WARNING: {sf2} not found in current directory — skipping playback test")
    sf2 = None

for drv in ('dsound', 'wasapi', 'waveout', 'winmm'):
    try:
        fs = fluidsynth.Synth(gain=0.8)
        fs.start(driver=drv)
        # Check the internal handle — pyfluidsynth doesn't raise on NULL driver
        if not getattr(fs, 'audio_driver', None):
            print(f"  {drv}: started without error but driver handle is NULL (silent fail)")
            fs.delete()
            continue
        if sf2:
            sfid = fs.sfload(sf2)
            fs.program_select(0, sfid, 0, 0)
            fs.noteon(0, 60, 90)
            time.sleep(0.6)
            fs.noteoff(0, 60)
            time.sleep(0.1)
            print(f"  {drv}: OK  (you should have heard a note)")
        else:
            print(f"  {drv}: driver handle valid (no SF2 to play)")
        fs.delete()
    except Exception as e:
        print(f"  {drv}: FAILED — {e}")

# ── sounddevice / microphone ──────────────────────────────
print("\n--- sounddevice / microphone ---")
try:
    import sounddevice as sd
    devs = sd.query_devices()
    print(f"sounddevice imported OK, {len(devs)} audio device(s) found")
    try:
        inp = sd.query_devices(kind='input')
        print(f"  Default input : {inp['name']}  ({inp['max_input_channels']} ch)")
    except Exception as e:
        print(f"  Default input : ERROR — {e}")
    try:
        out = sd.query_devices(kind='output')
        print(f"  Default output: {out['name']}  ({out['max_output_channels']} ch)")
    except Exception as e:
        print(f"  Default output: ERROR — {e}")
except Exception as e:
    print(f"FAILED: {e}")

# ── clipboard ─────────────────────────────────────────────
print("\n--- Clipboard (ctypes / CF_DIB) ---")
try:
    import ctypes, ctypes.wintypes, io
    from PIL import Image
    # Explicit 64-bit-safe declarations (avoids pointer truncation on 64-bit Python)
    k32 = ctypes.WinDLL('kernel32')
    k32.GlobalAlloc.restype  = ctypes.c_void_p
    k32.GlobalAlloc.argtypes = [ctypes.wintypes.UINT, ctypes.c_size_t]
    k32.GlobalLock.restype   = ctypes.c_void_p
    k32.GlobalLock.argtypes  = [ctypes.c_void_p]
    k32.GlobalUnlock.argtypes = [ctypes.c_void_p]
    u32 = ctypes.WinDLL('user32')
    u32.OpenClipboard.argtypes  = [ctypes.c_void_p]
    u32.SetClipboardData.restype  = ctypes.c_void_p
    u32.SetClipboardData.argtypes = [ctypes.wintypes.UINT, ctypes.c_void_p]
    img = Image.new('RGB', (200, 100), color=(255, 210, 0))
    bmp_io = io.BytesIO()
    img.convert('RGB').save(bmp_io, format='BMP')
    dib = bmp_io.getvalue()[14:]
    u32.OpenClipboard(None)
    u32.EmptyClipboard()
    h = k32.GlobalAlloc(0x0002, len(dib))
    ptr = k32.GlobalLock(h)
    ctypes.memmove(ptr, dib, len(dib))
    k32.GlobalUnlock(h)
    u32.SetClipboardData(8, h)
    u32.CloseClipboard()
    print("  OK — try pasting into Paint or Word to verify")
except Exception as e:
    print(f"  FAILED — {e}")

print("\n" + "=" * 55)
print("Done. Paste the output above when reporting issues.")
print("=" * 55)
