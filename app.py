#!/usr/bin/env python3
"""Harmonica Pentatonic Notation Editor — Phase 1"""

import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageDraw, ImageFont, ImageTk
import os
import threading
import time
import numpy as np
import pygame

# ─── Audio Engine ─────────────────────────────────────────────────────────────

_SAMPLE_RATE = 44100
pygame.mixer.pre_init(_SAMPLE_RATE, -16, 2, 512)
pygame.mixer.init()

def _synth_reed(freq, duration):
    """Synthesize a harmonica reed tone: blend of harmonics with ADSR envelope."""
    n = int(_SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, endpoint=False)

    # Harmonica reed: strong fundamental + rolloff harmonics, slight odd-harmonic bias
    wave = (
        1.00 * np.sin(2 * np.pi * 1 * freq * t) +
        0.55 * np.sin(2 * np.pi * 2 * freq * t) +
        0.30 * np.sin(2 * np.pi * 3 * freq * t) +
        0.18 * np.sin(2 * np.pi * 4 * freq * t) +
        0.12 * np.sin(2 * np.pi * 5 * freq * t) +
        0.08 * np.sin(2 * np.pi * 6 * freq * t)
    )
    peak = np.max(np.abs(wave))
    if peak > 0:
        wave /= peak

    # ADSR: 15 ms attack, sustain at 0.75, 80 ms release
    attack  = min(int(0.015 * _SAMPLE_RATE), n)
    release = min(int(0.080 * _SAMPLE_RATE), n)
    env = np.full(n, 0.75)
    env[:attack]  = np.linspace(0, 1.0, attack)
    env[-release:] = np.linspace(0.75, 0.0, release)

    samples = (wave * env * 32767).astype(np.int16)
    return np.column_stack([samples, samples])   # stereo


def _midi_to_freq(midi):
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))


def _play_sequence(midi_notes, note_dur, stop_event):
    """Play MIDI notes sequentially in a background thread."""
    for midi in midi_notes:
        if stop_event.is_set():
            break
        freq = _midi_to_freq(midi)
        samples = _synth_reed(freq, note_dur)
        sound = pygame.sndarray.make_sound(np.ascontiguousarray(samples))
        sound.play()
        deadline = time.monotonic() + note_dur
        while time.monotonic() < deadline:
            if stop_event.is_set():
                pygame.mixer.stop()
                return
            time.sleep(0.01)
    pygame.mixer.stop()


# ─── Music Theory ──────────────────────────────────────────────────────────────

NOTES = ['C','Db','D','Eb','E','F','Gb','G','Ab','A','Bb','B']
MAJOR_STEPS = [0, 2, 4, 5, 7, 9, 11]
MODES = ['major','dorian','phrygian','lydian','mixolydian','minor','locrian']
MODE_DISPLAY = ['Major','Dorian','Phrygian','Lydian','Mixolydian','Minor','Locrian']

# Scale degree indices (0-based) that are in the 7-note scale but NOT in the pentatonic
ORANGE_IDX = {
    'major':      [3, 6],
    'dorian':     [3, 6],
    'phrygian':   [3, 6],
    'lydian':     [1, 5],
    'mixolydian': [1, 5],
    'minor':      [1, 5],
    'locrian':    [1, 5],
}

def mode_scale(key, mode):
    """Return the 7-note modal scale as note names, starting on key."""
    shift = MAJOR_STEPS[MODES.index(mode)]
    parent_root = (NOTES.index(key) - shift) % 12
    parent = [NOTES[(parent_root + s) % 12] for s in MAJOR_STEPS]
    r = parent.index(key)
    return parent[r:] + parent[:r]

def pentatonic_info(key, mode):
    """Return (scale_7, orange_set, pentatonic_list) as note names."""
    scale = mode_scale(key, mode)
    oi = ORANGE_IDX[mode]
    orange = {scale[i] for i in oi}
    pent = [n for i, n in enumerate(scale) if i not in oi]
    return scale, orange, pent

def relative_pair(key, mode):
    """
    For major/minor modes, return (major_key, minor_key) of the relative pair.
    Returns None for other modes.
    """
    if mode == 'major':
        minor_key = NOTES[(NOTES.index(key) + 9) % 12]
        return key, minor_key
    if mode == 'minor':
        major_key = NOTES[(NOTES.index(key) + 3) % 12]
        return major_key, key
    return None

# ─── Harp Layout ──────────────────────────────────────────────────────────────

# Semitone offsets from harp root for blow and draw notes across 10 holes
BLOW_OFF = [0,  4,  7, 12, 16, 19, 24, 28, 31, 36]
DRAW_OFF = [2,  7, 11, 14, 17, 21, 23, 26, 29, 33]

def harp_note(root, offset):
    return NOTES[(NOTES.index(root) + offset) % 12]

def harp_notes(root):
    blow = [harp_note(root, o) for o in BLOW_OFF]
    draw = [harp_note(root, o) for o in DRAW_OFF]
    return blow, draw

def draw_bends(root):
    """
    Draw bends for holes 1-6 (where draw > blow pitch).
    Returns list of 10 lists; each is [highest_bend, ..., lowest_bend].
    """
    result = []
    for i in range(10):
        d, b = DRAW_OFF[i], BLOW_OFF[i]
        if d > b:
            result.append([harp_note(root, d - j) for j in range(1, d - b)])
        else:
            result.append([])
    return result

def over_notes(root):
    """
    Overblow notes for holes 1-6 (draw + 1 semitone, shown above draw row).
    Overdraw notes for holes 7-10 (blow + 1 semitone, shown above draw row).
    Returns list of 10 note names (empty string if not applicable or same as existing).
    """
    blow, draw = harp_notes(root)
    result = []
    for i in range(10):
        d, b = DRAW_OFF[i], BLOW_OFF[i]
        if d > b:   # holes 1-6: overblow = draw + 1
            n = harp_note(root, d + 1)
        else:       # holes 7-10: overdraw = blow + 1
            n = harp_note(root, b + 1)
        # Suppress if same as an existing blow or draw note at this hole
        if n == blow[i] or n == draw[i]:
            result.append('')
        else:
            result.append(n)
    return result

def blow_bends(root):
    """
    Blow bends for holes 7-10 (where blow > draw pitch).
    Returns list of 10 lists; each is [highest_bend, ..., lowest_bend].
    """
    result = []
    for i in range(10):
        d, b = DRAW_OFF[i], BLOW_OFF[i]
        if b > d:
            result.append([harp_note(root, b - j) for j in range(1, b - d)])
        else:
            result.append([])
    return result

def _path_offset(hole, row_type):
    """MIDI offset (semitones from harp root) for any path position type."""
    if row_type == 'draw':
        return DRAW_OFF[hole]
    if row_type == 'blow':
        return BLOW_OFF[hole]
    if row_type == 'over':
        # holes 0-5: overblow = draw+1; holes 6-9: overdraw = blow+1
        return (DRAW_OFF[hole] + 1) if DRAW_OFF[hole] > BLOW_OFF[hole] else (BLOW_OFF[hole] + 1)
    if isinstance(row_type, tuple):
        kind, level = row_type
        return (DRAW_OFF[hole] if kind == 'draw_bend' else BLOW_OFF[hole]) - (level + 1)
    return 0


def _group_path(path):
    """
    Group consecutive same-pitch path entries.
    Returns list-of-lists; each inner list is a 'fork group' of same-pitch positions.
    Lines are drawn all-pairs between consecutive groups, never within a group.
    """
    if not path:
        return []
    groups, cur, cur_off = [], [path[0]], _path_offset(*path[0])
    for pos in path[1:]:
        off = _path_offset(*pos)
        if off == cur_off:
            cur.append(pos)
        else:
            groups.append(cur)
            cur, cur_off = [pos], off
    groups.append(cur)
    return groups


def _path_to_midi(path, harp_root):
    """Return one MIDI note per pitch group in the path (deduplicates fork positions).
    C harp root = C4 = MIDI 60."""
    midi_root = 60 + NOTES.index(harp_root)
    return [midi_root + _path_offset(*group[0]) for group in _group_path(path)]


def pentatonic_path(harp_root, pent_set):
    """
    All harp positions that are pentatonic notes, including bend positions,
    sorted by ascending pitch then hole index.
    row_type is 'blow' | 'draw' | ('draw_bend', level) | ('blow_bend', level).
    Returns [(hole_idx, row_type), ...].
    """
    blow, draw = harp_notes(harp_root)
    db = draw_bends(harp_root)
    bb = blow_bends(harp_root)
    ob = over_notes(harp_root)
    positions = []
    SUPPRESS_OVER = {1, 2, 7}

    for i, n in enumerate(blow):
        if n in pent_set:
            positions.append((BLOW_OFF[i], i, 'blow'))
    for i, n in enumerate(draw):
        if n in pent_set:
            positions.append((DRAW_OFF[i], i, 'draw'))
    for i, bends in enumerate(db):
        for level, n in enumerate(bends):
            if n in pent_set:
                positions.append((DRAW_OFF[i] - (level + 1), i, ('draw_bend', level)))
    for i, bends in enumerate(bb):
        for level, n in enumerate(bends):
            if n in pent_set:
                positions.append((BLOW_OFF[i] - (level + 1), i, ('blow_bend', level)))
    for i, n in enumerate(ob):
        if n and n in pent_set and i not in SUPPRESS_OVER:
            off = _path_offset(i, 'over')
            positions.append((off, i, 'over'))

    positions.sort(key=lambda x: (x[0], x[1]))
    return [(h, r) for (_, h, r) in positions]

# ─── Renderer ─────────────────────────────────────────────────────────────────

# Geometry
HOLE_W   = 84       # pixels per hole (column width)
L_MARGIN = 40       # left and right margin
CIRCLE_R = 28       # note circle radius
IMG_W    = L_MARGIN * 2 + 10 * HOLE_W   # = 920

TITLE_H      = 56   # title area height
OVER_H       = 26   # overblow/overdraw label row above draw row
ROW_H        = CIRCLE_R * 2 + 8         # = 64 (height of a note row)
DRAW_BEND_H  = 30   # height per draw-bend level (must fit small bend ellipse)
BLOW_BEND_H  = 30   # height per blow-bend level
MAX_DRAW_B   = 3    # max draw bends (hole 3 has 3)
MAX_BLOW_B   = 2    # max blow bends (hole 10 has 2)
BOT_MARGIN   = 18

# Ellipse dimensions for non-standard (bent / overblow / overdraw) notes.
# Wider than tall to suggest these notes require a technique beyond normal blow/draw,
# matching the Photoshop reference style.
BEND_RX  = 24   # horizontal radius of draw/blow bend ellipse
BEND_RY  = 13   # vertical radius  (fits inside DRAW_BEND_H = 30 px)
OVER_RX  = 20   # horizontal radius of overblow/overdraw ellipse
OVER_RY  = 11   # vertical radius  (fits inside OVER_H = 26 px)

IMG_H = (TITLE_H + OVER_H + ROW_H + MAX_DRAW_B * DRAW_BEND_H +
         ROW_H + MAX_BLOW_B * BLOW_BEND_H + BOT_MARGIN)
# = 56 + 22 + 72 + 66 + 72 + 44 + 18 = 350

# Fixed colours (same regardless of background)
PENT_C    = (255, 210, 0  )   # yellow-gold: pentatonic non-root
ROOT_C    = (0,   200, 60 )   # green: root note
ORANGE_C  = (255, 140, 0  )   # orange: in scale, not pentatonic
OUTLINE_C = (0,   0,   0  )   # black outline (always)
LINE_C    = (210, 35,  35 )   # dark red path lines
TEXT_C    = (0,   0,   0  )   # black text inside circles/boxes

# Theme colours — depend on dark_bg flag (resolved in render())
def _theme(dark_bg):
    if dark_bg:
        return dict(bg=(0,0,0), title=(255,255,255),
                    plain=(190,190,190), bend=(155,155,155),
                    outline_lw=3)
    else:
        return dict(bg=(255,255,255), title=(0,0,0),
                    plain=(0,0,0), bend=(0,0,0),
                    outline_lw=2)

# Y-positions
def _over_y():
    """Y-centre of the overblow/overdraw label row (above draw row)."""
    return TITLE_H + OVER_H // 2

def _draw_cy():
    return TITLE_H + OVER_H + CIRCLE_R + 4

def _blow_cy():
    return TITLE_H + OVER_H + ROW_H + MAX_DRAW_B * DRAW_BEND_H + CIRCLE_R + 4

def _bend_between_y(level):
    """Y-centre of draw-bend label at given level (0 = closest to draw row)."""
    return TITLE_H + OVER_H + ROW_H + level * DRAW_BEND_H + DRAW_BEND_H // 2

def _blow_bend_y(level):
    return TITLE_H + OVER_H + ROW_H + MAX_DRAW_B * DRAW_BEND_H + ROW_H + level * BLOW_BEND_H + BLOW_BEND_H // 2

def _hole_x(i):
    return L_MARGIN + i * HOLE_W + HOLE_W // 2


def _load_font(size, bold=False):
    candidates = []
    if bold:
        candidates = [
            '/System/Library/Fonts/Supplemental/Arial Bold.ttf',
            '/System/Library/Fonts/Supplemental/Trebuchet MS Bold.ttf',
            '/System/Library/Fonts/Supplemental/Verdana Bold.ttf',
        ]
    else:
        candidates = [
            '/System/Library/Fonts/Supplemental/Arial.ttf',
            '/System/Library/Fonts/Supplemental/Verdana.ttf',
            '/System/Library/Fonts/Supplemental/Trebuchet MS.ttf',
        ]
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    # Fallback to any system font
    for p in ['/System/Library/Fonts/Helvetica.ttc',
              '/Library/Fonts/Arial Unicode.ttf']:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def _center_text(dc, cx, cy, text, font, color):
    bb = dc.textbbox((0, 0), text, font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    dc.text((cx - tw // 2 - bb[0], cy - th // 2 - bb[1]), text, font=font, fill=color)


def _draw_circle(dc, cx, cy, r, fill, outline, lw=3):
    dc.ellipse([cx-r, cy-r, cx+r, cy+r], fill=fill, outline=outline, width=lw)


def _draw_ellipse(dc, cx, cy, rx, ry, fill, outline, lw=2):
    dc.ellipse([cx-rx, cy-ry, cx+rx, cy+ry], fill=fill, outline=outline, width=lw)


def _draw_rounded_rect(dc, cx, cy, w, h, fill, outline, radius=10, lw=3):
    x0, y0, x1, y1 = cx - w//2, cy - h//2, cx + w//2, cy + h//2
    dc.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill,
                          outline=outline, width=lw)


def _pos_xy(hole_idx, row_type):
    """Return (x, y) pixel centre for a path position."""
    x = _hole_x(hole_idx)
    if row_type == 'draw':
        y = _draw_cy()
    elif row_type == 'blow':
        y = _blow_cy()
    elif row_type == 'over':
        y = _over_y()
    elif isinstance(row_type, tuple) and row_type[0] == 'draw_bend':
        y = _bend_between_y(row_type[1])
    elif isinstance(row_type, tuple) and row_type[0] == 'blow_bend':
        y = _blow_bend_y(row_type[1])
    else:
        y = _draw_cy()
    return x, y


def _render_bend_note(dc, cx, cy, note, pent_set, green_notes, orange_set,
                      f_tiny, theme, rx=BEND_RX, ry=BEND_RY):
    """Draw a bend-level note as a wide ellipse (pentatonic) or rounded rect (orange) or plain text."""
    lw = theme['outline_lw']
    if note in pent_set:
        fill = ROOT_C if note in green_notes else PENT_C
        _draw_ellipse(dc, cx, cy, rx, ry, fill, LINE_C, lw=lw)
        _center_text(dc, cx, cy, note, f_tiny, TEXT_C)
    elif note in orange_set:
        _draw_rounded_rect(dc, cx, cy, rx * 2, ry * 2, ORANGE_C, OUTLINE_C, radius=4, lw=lw)
        _center_text(dc, cx, cy, note, f_tiny, TEXT_C)
    else:
        _center_text(dc, cx, cy, note, f_tiny, theme['bend'])


def _make_title(scale_key, mode, harp_key):
    pair = relative_pair(scale_key, mode)
    if pair:
        maj, minn = pair
        body = f"{maj} Major   or   {minn} Minor"
    else:
        body = f"{scale_key} {MODE_DISPLAY[MODES.index(mode)]}"
    return f"{body}   on a   {harp_key} Harp"


def render(scale_key, mode, harp_key, dark_bg=True):
    """Build and return a PIL Image of the pentatonic notation diagram."""
    t = _theme(dark_bg)   # resolve background-dependent colours

    _, orange_set, pent_list = pentatonic_info(scale_key, mode)
    pent_set = set(pent_list)

    pair = relative_pair(scale_key, mode)
    if pair:
        green_notes = {pair[0], pair[1]}
    else:
        green_notes = {scale_key}

    blow, draw = harp_notes(harp_key)
    db = draw_bends(harp_key)
    bb = blow_bends(harp_key)
    ob = over_notes(harp_key)
    path = pentatonic_path(harp_key, pent_set)

    img = Image.new('RGB', (IMG_W, IMG_H), t['bg'])
    dc  = ImageDraw.Draw(img)

    f_title = _load_font(26, bold=True)
    f_note  = _load_font(24, bold=True)
    f_small = _load_font(14)
    f_tiny  = _load_font(14, bold=True)

    # Title
    _center_text(dc, IMG_W // 2, TITLE_H // 2,
                 _make_title(scale_key, mode, harp_key), f_title, t['title'])

    draw_cy = _draw_cy()
    blow_cy = _blow_cy()
    lw = t['outline_lw']

    # Path lines (drawn behind note shapes)
    # Group consecutive path nodes by pitch offset so duplicate-pitch positions
    # (e.g. draw-2 and blow-3 both = G on a C harp) produce forked paths.
    groups = _group_path(path)
    for i in range(len(groups) - 1):
        for p1 in groups[i]:
            for p2 in groups[i + 1]:
                x1, y1 = _pos_xy(*p1)
                x2, y2 = _pos_xy(*p2)
                dc.line([x1, y1, x2, y2], fill=LINE_C, width=4)

    # Note shapes for draw and blow rows
    for _row, notes_list, cy in [('draw', draw, draw_cy),
                                   ('blow', blow, blow_cy)]:
        for i, note in enumerate(notes_list):
            cx = _hole_x(i)
            if note in pent_set:
                fill = ROOT_C if note in green_notes else PENT_C
                _draw_circle(dc, cx, cy, CIRCLE_R, fill, LINE_C, lw=lw)
                _center_text(dc, cx, cy, note, f_note, TEXT_C)
            elif note in orange_set:
                _draw_rounded_rect(dc, cx, cy,
                                   CIRCLE_R * 2 - 4, CIRCLE_R * 2 - 4,
                                   ORANGE_C, OUTLINE_C, radius=9, lw=lw)
                _center_text(dc, cx, cy, note, f_note, TEXT_C)
            else:
                _center_text(dc, cx, cy, note, f_note, t['plain'])

    # Overblow/overdraw labels above the draw row
    # Holes 2, 3, 8 (0-based 1, 2, 7) are suppressed: draw-2 and blow-3 share a
    # pitch, so the overblow there is redundant and would confuse the fork paths.
    SUPPRESS_OVER = {1, 2, 7}
    oy = _over_y()
    for i, note in enumerate(ob):
        if note and i not in SUPPRESS_OVER:
            _render_bend_note(dc, _hole_x(i), oy, note, pent_set, green_notes,
                              orange_set, f_tiny, t, rx=OVER_RX, ry=OVER_RY)

    # Draw-bend labels between the rows
    for i in range(10):
        cx = _hole_x(i)
        for level, note in enumerate(db[i]):
            y = _bend_between_y(level)
            _render_bend_note(dc, cx, y, note, pent_set, green_notes,
                              orange_set, f_tiny, t)

    # Blow-bend labels below the blow row
    for i in range(10):
        cx = _hole_x(i)
        for level, note in enumerate(bb[i]):
            y = _blow_bend_y(level)
            _render_bend_note(dc, cx, y, note, pent_set, green_notes,
                              orange_set, f_tiny, t)

    return img

# ─── GUI ──────────────────────────────────────────────────────────────────────

PREVIEW_SCALE = 0.85   # scale factor for on-screen preview

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Harmonica Pentatonic Editor")
        self.resizable(False, False)
        self.configure(bg='#1e1e1e')

        self._stop_event  = threading.Event()
        self._play_thread = None

        self._build_controls()
        self._build_preview()
        self._refresh()

    # ── Control panel ─────────────────────────────────────────────────────────

    def _build_controls(self):
        ctrl = tk.Frame(self, bg='#1e1e1e', padx=12, pady=10)
        ctrl.grid(row=0, column=0, sticky='nsw')

        lbl_opts = dict(bg='#1e1e1e', fg='#cccccc', font=('Arial', 11))
        combo_opts = dict(state='readonly', width=14, font=('Arial', 11))

        def row(label, var, choices, r):
            tk.Label(ctrl, text=label, **lbl_opts).grid(
                row=r, column=0, sticky='w', pady=3)
            cb = ttk.Combobox(ctrl, textvariable=var, values=choices, **combo_opts)
            cb.grid(row=r, column=1, sticky='w', padx=(6, 0), pady=3)
            cb.bind('<<ComboboxSelected>>', lambda _: self._refresh())
            return cb

        self.v_harp  = tk.StringVar(value='C')
        self.v_key   = tk.StringVar(value='C')
        self.v_mode  = tk.StringVar(value='major')
        self.v_dark  = tk.BooleanVar(value=True)

        row('Harp key:',    self.v_harp,  NOTES,        0)
        row('Scale key:',   self.v_key,   NOTES,        1)
        row('Mode:',        self.v_mode,  MODES,        2)

        ttk.Separator(ctrl, orient='horizontal').grid(
            row=3, columnspan=2, sticky='ew', pady=8)

        cb_dark = tk.Checkbutton(
            ctrl, text='Dark background',
            variable=self.v_dark,
            command=self._refresh,
            bg='#1e1e1e', fg='#cccccc', selectcolor='#333333',
            activebackground='#1e1e1e', activeforeground='#cccccc',
            font=('Arial', 11))
        cb_dark.grid(row=4, columnspan=2, sticky='w', pady=2)

        ttk.Separator(ctrl, orient='horizontal').grid(
            row=5, columnspan=2, sticky='ew', pady=8)

        btn_style = dict(font=('Arial', 11), padx=8, pady=4)
        tk.Button(ctrl, text='Export PNG…',
                  command=self._export, **btn_style).grid(
            row=6, columnspan=2, sticky='ew', pady=2)

        ttk.Separator(ctrl, orient='horizontal').grid(
            row=7, columnspan=2, sticky='ew', pady=8)

        # Tempo
        self.v_tempo = tk.IntVar(value=100)
        tk.Label(ctrl, text='Tempo (BPM):', **lbl_opts).grid(
            row=8, column=0, sticky='w', pady=3)
        tk.Spinbox(ctrl, from_=40, to=240, textvariable=self.v_tempo,
                   width=5, font=('Arial', 11)).grid(
            row=8, column=1, sticky='w', padx=(6, 0), pady=3)

        # Play buttons
        play_frame = tk.Frame(ctrl, bg='#1e1e1e')
        play_frame.grid(row=9, columnspan=2, sticky='ew', pady=(6, 2))
        tk.Button(play_frame, text='◀ Play',
                  command=lambda: self._play(forward=False),
                  **btn_style).pack(side='left', expand=True, fill='x', padx=(0, 2))
        tk.Button(play_frame, text='Play ▶',
                  command=lambda: self._play(forward=True),
                  **btn_style).pack(side='left', expand=True, fill='x', padx=(2, 0))

        tk.Button(ctrl, text='■ Stop', command=self._stop,
                  **btn_style).grid(row=10, columnspan=2, sticky='ew', pady=2)

        self._info = tk.Label(ctrl, text='', bg='#1e1e1e', fg='#888888',
                              font=('Arial', 9), wraplength=200, justify='left')
        self._info.grid(row=11, columnspan=2, sticky='w', pady=(8, 0))

    # ── Preview canvas ─────────────────────────────────────────────────────────

    def _build_preview(self):
        pw = int(IMG_W * PREVIEW_SCALE)
        ph = int(IMG_H * PREVIEW_SCALE)
        self._canvas = tk.Canvas(self, width=pw, height=ph,
                                  bg='black', highlightthickness=0)
        self._canvas.grid(row=0, column=1, padx=(0, 12), pady=12)
        self._tk_img = None

    # ── Refresh ────────────────────────────────────────────────────────────────

    def _refresh(self):
        harp_key = self.v_harp.get()
        key      = self.v_key.get()
        mode     = self.v_mode.get()

        try:
            img = render(key, mode, harp_key, dark_bg=self.v_dark.get())
        except Exception as e:
            self._info.config(text=f"Error: {e}")
            return

        pw = int(IMG_W * PREVIEW_SCALE)
        ph = int(IMG_H * PREVIEW_SCALE)
        preview = img.resize((pw, ph), Image.LANCZOS)
        self._tk_img = ImageTk.PhotoImage(preview)
        self._canvas.create_image(0, 0, anchor='nw', image=self._tk_img)
        self._current_img = img

        # Update info label
        _, orange, pent = pentatonic_info(key, mode)
        self._info.config(
            text=f"Scale: {' '.join(mode_scale(key, mode))}\n"
                 f"Pentatonic: {' '.join(pent)}\n"
                 f"Orange (non-pent): {' '.join(sorted(orange, key=NOTES.index))}")

    # ── Playback ───────────────────────────────────────────────────────────────

    def _play(self, forward=True):
        # Stop any current playback first
        self._stop()

        harp_key = self.v_harp.get()
        key      = self.v_key.get()
        mode     = self.v_mode.get()
        _, _, pent = pentatonic_info(key, mode)
        path = pentatonic_path(harp_key, set(pent))
        if not path:
            return

        midi_notes = _path_to_midi(path, harp_key)

        # Trim to first octave: first occurrence of the tonic to the next occurrence
        # of the same pitch class (12 semitones higher = one true octave).
        key_class = NOTES.index(key)
        root_idx = [i for i, m in enumerate(midi_notes) if m % 12 == key_class]
        if len(root_idx) >= 2:
            midi_notes = midi_notes[root_idx[0]:root_idx[1] + 1]

        if not forward:
            midi_notes = list(reversed(midi_notes))

        note_dur = 60.0 / max(self.v_tempo.get(), 1)
        self._stop_event = threading.Event()
        self._play_thread = threading.Thread(
            target=_play_sequence,
            args=(midi_notes, note_dur, self._stop_event),
            daemon=True)
        self._play_thread.start()

    def _stop(self):
        self._stop_event.set()
        if self._play_thread and self._play_thread.is_alive():
            self._play_thread.join(timeout=0.3)
        pygame.mixer.stop()

    # ── Export ─────────────────────────────────────────────────────────────────

    def _export(self):
        harp = self.v_harp.get()
        key  = self.v_key.get()
        mode = self.v_mode.get()
        default = f"{key}_{mode}_on_{harp}_harp.png"
        path = filedialog.asksaveasfilename(
            defaultextension='.png',
            filetypes=[('PNG image', '*.png')],
            initialfile=default,
            title='Export diagram')
        if path:
            # Re-render at full resolution with current settings
            img = render(self.v_key.get(), self.v_mode.get(),
                         self.v_harp.get(), dark_bg=self.v_dark.get())
            img.save(path)
            self._info.config(text=f"Saved: {os.path.basename(path)}")


if __name__ == '__main__':
    App().mainloop()
