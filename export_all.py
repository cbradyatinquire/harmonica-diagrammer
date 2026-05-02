#!/usr/bin/env python3
"""
export_all.py — render all 84 canonical diagrams for one harp key.

Usage:
    python export_all.py C              # light background (default)
    python export_all.py C --dark       # dark background
    python export_all.py C --outdir ~/Desktop/C_harp_diagrams

Output files are named like:
    C_major.png, Db_dorian.png, D_phrygian.png, …

Valid harp keys: C Db D Eb E F Gb G Ab A Bb B
"""

import argparse
import os
import sys

# ── Bootstrap: import render() and the key/mode tables from app.py ──────────
# app.py starts the FluidSynth audio engine and creates a Tk window on import
# unless we suppress those side-effects.  We do so by patching the modules it
# needs before the import.

# Stub out tkinter so the App class is defined but nothing is displayed.
import types

_tk_stub = types.ModuleType('tkinter')
_tk_stub.Tk         = object
_tk_stub.Frame      = object
_tk_stub.Label      = object
_tk_stub.Canvas     = object
_tk_stub.Button     = object
_tk_stub.Checkbutton = object
_tk_stub.Spinbox    = object
_tk_stub.Entry      = object
_tk_stub.StringVar  = object
_tk_stub.BooleanVar = object
_tk_stub.IntVar     = object
_tk_stub.ttk        = types.ModuleType('tkinter.ttk')
_tk_stub.filedialog = types.ModuleType('tkinter.filedialog')
_tk_stub.END        = 'end'
sys.modules['tkinter']          = _tk_stub
sys.modules['tkinter.ttk']      = _tk_stub.ttk
sys.modules['tkinter.filedialog'] = _tk_stub.filedialog

# Stub out fluidsynth so the audio engine doesn't start.
_fs_stub = types.ModuleType('fluidsynth')
class _FakeSynth:
    def __init__(self, **kw): pass
    def start(self, **kw):    pass
    def sfload(self, *a):     return 0
    def program_select(self, *a): pass
    def noteon(self, *a):     pass
    def noteoff(self, *a):    pass
    def delete(self):         pass
_fs_stub.Synth = _FakeSynth
sys.modules['fluidsynth'] = _fs_stub

# Stub out sounddevice (used by NoteCapture).
_sd_stub = types.ModuleType('sounddevice')
class _FakeInputStream:
    def __init__(self, **kw): pass
    def __enter__(self): return self
    def __exit__(self, *a): pass
    def start(self): pass
    def stop(self):  pass
_sd_stub.InputStream = _FakeInputStream
sys.modules['sounddevice'] = _sd_stub

# Now it is safe to import the real module.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import app  # noqa: E402  (import after stubs)

# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Export all 84 canonical pentatonic diagrams for one harp key.')
    parser.add_argument('harp_key',
                        choices=app.NOTES,
                        metavar='HARP_KEY',
                        help='Harp key, e.g. C  Db  D  Eb  E  F  Gb  G  Ab  A  Bb  B')
    parser.add_argument('--dark', action='store_true',
                        help='Use dark background (default: light)')
    parser.add_argument('--outdir', default=None,
                        help='Output directory (default: ./<HARP_KEY>_harp)')
    args = parser.parse_args()

    harp_key = args.harp_key
    dark_bg  = args.dark
    outdir   = args.outdir or f'{harp_key}_harp'

    os.makedirs(outdir, exist_ok=True)

    total  = len(app.NOTES) * len(app.MODES)   # 84
    done   = 0
    errors = []

    print(f'Rendering {total} diagrams → {os.path.abspath(outdir)}/')
    print(f'Background: {"dark" if dark_bg else "light"}')
    print()

    for scale_key in app.NOTES:         # 12 keys
        for mode in app.MODES:          # 7 modes
            # Safe filename: replace 'b' suffix ambiguity with 'b', keep it readable
            fname = f'{scale_key.replace("/", "_")}_{mode}.png'
            fpath = os.path.join(outdir, fname)
            try:
                img = app.render(scale_key, mode, harp_key, dark_bg=dark_bg)
                img.save(fpath)
                done += 1
                print(f'  [{done:2d}/{total}]  {fname}  ({img.width}×{img.height})')
            except Exception as exc:
                errors.append((fname, exc))
                print(f'  [{done:2d}/{total}]  {fname}  ERROR: {exc}')

    print()
    print(f'Done — {done} images saved to {os.path.abspath(outdir)}/')
    if errors:
        print(f'{len(errors)} error(s):')
        for fname, exc in errors:
            print(f'  {fname}: {exc}')
        sys.exit(1)


if __name__ == '__main__':
    main()
