# Harmonica Pentatonic Notation Editor

A desktop app for creating, displaying, and exporting pentatonic notation diagrams for 10-hole diatonic harmonica. Supports all 12 harp keys × 7 modes, custom paths, real-time note detection via microphone, and MIDI playback.

## Running from source

```bash
python app.py
```

## Building a distributable app

### Prerequisites

#### macOS
```bash
brew install fluid-synth portaudio
pip install -r requirements.txt
```

#### Windows

The easiest way to get FluidSynth and all its dependencies is via **conda**:
```bash
conda install -c conda-forge fluidsynth
pip install -r requirements.txt
```

If you don't use conda, download `libfluidsynth-3.dll` (cpp11 build) from the [FluidSynth GitHub releases](https://github.com/FluidSynth/fluidsynth/releases) and place it in the project folder. You will also need the MinGW runtime DLLs (`libgcc_s_seh-1.dll`, `libstdc++-6.dll`, `libwinpthread-1.dll`) — these can be obtained from a [WinLibs standalone GCC package](https://winlibs.com/) (extract the zip and copy those three files from `mingw64\bin\` into the project folder).

```bash
pip install -r requirements.txt
```

#### Linux (Debian/Ubuntu)
```bash
sudo apt install libfluidsynth-dev portaudio19-dev python3-tk
pip install -r requirements.txt
```

### Build

```bash
pyinstaller "Harmonica Notation.spec"
```

Output lands in `dist/`. On macOS this produces `dist/Harmonica Notation.app`; on Windows/Linux a `dist/Harmonica Notation/` folder containing the executable.

### Notes

- **Soundfont:** `Hohner_Silverstar_Harmonica.sf2` is included in the repo and bundled automatically — no separate download needed.
- **tkinter:** included with Python on macOS and Windows. On Linux install `python3-tk` if missing (see above).
- **Clipboard copy (Linux end users):** the Copy button requires `xclip` or `xsel` to be installed (`sudo apt install xclip`). All other features work without it.
- **Microphone (macOS):** on first launch macOS will prompt for microphone permission. If you previously ran a build that lacked the permission prompt, enable it manually in **System Settings → Privacy & Security → Microphone**.

## Batch export

Export all 84 canonical diagrams for a given harp key (12 keys × 7 modes):

```bash
python export_all.py C              # light background
python export_all.py C --dark       # dark background
python export_all.py C --outdir ~/Desktop/C_diagrams
```

Valid harp keys: `C Db D Eb E F Gb G Ab A Bb B`
