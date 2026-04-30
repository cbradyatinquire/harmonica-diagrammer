#!/usr/bin/env python3
"""Compare harmonica soundfonts by playing C major pentatonic through each."""
import fluidsynth
import time

SF2_FILES = {
    "harmonica full soundfont": "/Users/49356183/Documents/Software/harmonica-notation/harmonica full soundfont.sf2",
    "Hohner Silverstar":         "/Users/49356183/Documents/Software/harmonica-notation/Hohner_Silverstar_Harmonica.sf2",
}

NOTES = [60, 62, 64, 67, 69, 72]   # C D E G A C
DUR   = 0.5

for name, sf2 in SF2_FILES.items():
    print(f"\n--- {name} ---")
    fs = fluidsynth.Synth(gain=0.8)
    fs.start(driver='coreaudio')
    sfid = fs.sfload(sf2)
    fs.program_select(0, sfid, 0, 0)   # program 0 = first patch in each font

    for midi in NOTES:
        fs.noteon(0, midi, 90)
        time.sleep(DUR)
        fs.noteoff(0, midi)
        time.sleep(0.05)
    time.sleep(0.6)
    fs.delete()
    time.sleep(0.5)   # gap between the two fonts

print("\nDone.")
