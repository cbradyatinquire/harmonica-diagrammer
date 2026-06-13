# -*- mode: python ; coding: utf-8 -*-
import platform as _platform

# ── Bundle FluidSynth and its dependencies for each platform.
# PyInstaller doesn't trace ctypes.util.find_library() calls, so we locate
# the FluidSynth library explicitly and add it to binaries.  PyInstaller then
# analyses that binary and pulls in its transitive dependencies automatically.

_FLUID_LIBS = []
if _platform.system() == 'Darwin':
    _FLUID_LIBS = [
        '/opt/homebrew/Cellar/fluid-synth/2.5.4/lib/libfluidsynth.3.5.3.dylib',
        '/opt/homebrew/Cellar/flac/1.5.0/lib/libFLAC.14.dylib',
        '/opt/homebrew/Cellar/gettext/1.0/lib/libintl.8.dylib',
        '/opt/homebrew/Cellar/glib/2.88.1/lib/libglib-2.0.0.dylib',
        '/opt/homebrew/Cellar/glib/2.88.1/lib/libgthread-2.0.0.dylib',
        '/opt/homebrew/Cellar/lame/3.100/lib/libmp3lame.0.dylib',
        '/opt/homebrew/Cellar/libogg/1.3.6/lib/libogg.0.8.6.dylib',
        '/opt/homebrew/Cellar/libsndfile/1.2.2_1/lib/libsndfile.1.0.37.dylib',
        '/opt/homebrew/Cellar/libvorbis/1.3.7/lib/libvorbis.0.dylib',
        '/opt/homebrew/Cellar/libvorbis/1.3.7/lib/libvorbisenc.2.dylib',
        '/opt/homebrew/Cellar/mpg123/1.33.5/lib/libmpg123.0.dylib',
        '/opt/homebrew/Cellar/opus/1.6.1/lib/libopus.0.dylib',
        '/opt/homebrew/Cellar/pcre2/10.47_1/lib/libpcre2-8.0.dylib',
        '/opt/homebrew/Cellar/portaudio/19.7.0/lib/libportaudio.2.dylib',
        '/opt/homebrew/Cellar/readline/8.3.3/lib/libreadline.8.3.dylib',
    ]
elif _platform.system() == 'Windows':
    import os as _os
    def _find_dll(dll_name):
        # shutil.which won't find .dll files on Windows (not in PATHEXT).
        # Check: project dir, PATH directories, conda env.
        _search_dirs = [
            SPECPATH,        # directory containing the spec file (PyInstaller built-in)
            _os.getcwd(),
        ] + [_d.strip() for _d in _os.environ.get('PATH', '').split(';')]
        _conda = _os.environ.get('CONDA_PREFIX', '')
        if _conda:
            _search_dirs.append(_os.path.join(_conda, 'Library', 'bin'))
        for _dir in _search_dirs:
            if not _dir:
                continue
            _p = _os.path.join(_dir, dll_name)
            if _os.path.isfile(_p):
                return _p
        return None
    # Find FluidSynth DLL. PyInstaller will analyse it and pull in its
    # transitive dependencies (MinGW runtime, libsndfile, etc.) automatically.
    for _dll_name in ('libfluidsynth-3.dll', 'libfluidsynth.dll', 'fluidsynth.dll'):
        _dll_path = _find_dll(_dll_name)
        if _dll_path:
            _FLUID_LIBS.append((_dll_path, '.'))
            break

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[(lib, '.') for lib in _FLUID_LIBS],
    datas=[('Hohner_Silverstar_Harmonica.sf2', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Harmonica Notation',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Harmonica Notation',
)

# macOS only: wrap in a .app bundle with required Info.plist keys.
if _platform.system() == 'Darwin':
    app = BUNDLE(
        coll,
        name='Harmonica Notation.app',
        icon=None,
        bundle_identifier=None,
        info_plist={
            'NSMicrophoneUsageDescription':
                'Harmonica Notation listens to your harmonica to detect notes for the '
                'Record and Listen features.',
        },
    )
