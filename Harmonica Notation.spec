# -*- mode: python ; coding: utf-8 -*-

# All Homebrew dylibs that libfluidsynth and its dependencies need.
# Bundled so the .app runs on machines without Homebrew installed.
_FLUID_LIBS = [
    '/opt/homebrew/Cellar/fluid-synth/2.5.4/lib/libfluidsynth.3.5.3.dylib',
    '/opt/homebrew/Cellar/flac/1.5.0/lib/libFLAC.14.dylib',
    '/opt/homebrew/Cellar/gettext/1.0/lib/libintl.8.dylib',
    '/opt/homebrew/Cellar/glib/2.88.0/lib/libglib-2.0.0.dylib',
    '/opt/homebrew/Cellar/glib/2.88.0/lib/libgthread-2.0.0.dylib',
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
app = BUNDLE(
    coll,
    name='Harmonica Notation.app',
    icon=None,
    bundle_identifier=None,
)
