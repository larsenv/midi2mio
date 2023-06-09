import binascii
import mido
import pretty_midi
import struct
import sys

if len(sys.argv) != 2:
    print("Usage: midi2mio.py <midi>")
    sys.exit(1)

midi = pretty_midi.PrettyMIDI(sys.argv[1])
# midi = mido.MidiFile("happierz.mid")
mio = open("z.mio", "rb").read()

time = 0

octaves = [
    0,
    0,
    0,
    0,
    24,
    0,
    0,
    12,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    12,
    12,
    24,
    -12,
    0,
    36,
    24,
    -12,
]
volumes = []
notes = [[0] * 50000, [0] * 50000, [0] * 50000, [0] * 50000]
note_dex_start = [[], [], [], []]
note_dex_end = [[], [], [], []]
instruments = []
instrument_lookup = [
    0,
    19,
    6,
    21,
    73,
    56,
    66,
    75,
    24,
    29,
    105,
    32,
    40,
    12,
    11,
    47,
    111,
    78,
    36,
    87,
    53,
    38,
    80,
    13,
    82,
    127,
    122,
    108,
    55,
    123,
    53,
    54,
    30,
    53,
    85,
    121,
    57,
    126,
    91,
    80,
    80,
    80,
    80,
    80,
    80,
    80,
    80,
    80,
]
times = [0, 0, 0, 0]
mid2 = mido.MidiFile(sys.argv[1])
for i, track in enumerate(mid2.tracks):
    for msg in track:
        if msg.type == "set_tempo":
            tempo = mido.tempo2bpm(msg.tempo)


def u8(data):
    return struct.pack(">B", data)


# Iterate over tracks in the MIDI file
for i, track in enumerate(mid2.tracks):
    # Iterate over messages in the current track
    for msg in track:
        if msg.type == "control_change" and msg.control == 7:
            # Control Change message with control number 7 represents volume
            if int(msg.value / 20) > 4:
                volumes.append(u8(4))
            else:
                volumes.append(u8(int(msg.value / 20)))
            break


i = 0
last = 0
beat = 60 / tempo

i = 0
j = 0

for track in midi.instruments[:4]:
    i = 0
    l = 0
    for note in track.notes:
        start = note.start.item()
        end = note.end.item()
        if notes[j][i] != 255:
            note = int(note.pitch - 43)
            if note < 0 or note > 24:
                print(
                    "AAAAA", note, "missing I'm replacing it with", int(note % 12 + 12)
                )
                note = int(note % 12 + 12)
            if start not in note_dex_start[j]:
                note_dex_start[j].append(i)
            else:
                m = j
                while notes[m][i] != 0:
                    notes[m][i] = u8(note)
                    m += 1
                continue
            if end not in note_dex_end[j]:
                note_dex_end[j].append(i)
            else:
                m = j
                while notes[m][i] != 0:
                    notes[m][i] = u8(note)
                    m += 1
                continue
            if l == 0:
                if int((start) / beat * 3) + 1 > 0:
                    for k in range(1, int((start) / beat * 4) + 1):
                        notes[j][i + k] = u8(255)
                    i += int((start) / beat * 4)
            notes[j][i] = u8(note)
            if int((end - start) / beat * 3) + 1 > 0:
                for k in range(1, int((end - start) / beat * 3) + 1):
                    notes[j][i + k] = u8(255)
                i += int((end - start) / beat * 3)
            l += 1
        else:
            continue
        i += 1
    j += 1

for instrument in midi.instruments:
    try:
        instruments.append(u8(instrument_lookup.index(instrument.program)))
    except:
        instruments.append(u8(0))


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


with open(sys.argv[1].replace(".mid", "") + ".mio", "wb") as f:
    f.write(mio)
    track_num = 0
    k = 0
    for track in notes:
        blocks = chunks(track, 32)
        block_num = 0
        for block in blocks:
            if block_num < 24:
                position_num = 0
                for note in block:
                    offset = 0x107 + 0x114 * block_num + track_num * 0x20 + position_num
                    if note != 0:
                        f.seek(offset)
                        f.write(note)
                    position_num += 1
                block_num += 1
                k += 1
        track_num += 1
    track_num = 0
    for volume in volumes[:5]:
        for block_num in range(1, 25):
            offset = 0x107 + 0x114 * block_num + 0x100 + track_num
            f.seek(offset)
            f.write(volume)
            print(volume)
            print(offset, volume)
        track_num += 1
    track_num = 0
    for instrument in instruments:
        for block_num in range(1, 25):
            offset = 0x107 + 0x114 * block_num + 0x10A + track_num
            if instrument != 0:
                print(instrument)
                f.seek(offset)
                f.write(instrument)
        track_num += 1
    f.seek(0)
    f.write(
        binascii.unhexlify(
            "110011000000000044534D494F5F530031250000E6E21400654D1FA5000000000000000000000000000000000000000000000000006D696469326D696F00000000000000000000006D696469326D696F00000000000000000000006D696469326D696F00000000000000"
        )
    )
    f.seek(28)
    f.write(sys.argv[1].replace(".mid", "")[:12].encode("utf-8"))
    f.seek(207)
    f.write(b"midi\x00\x00\x00")
    f.seek(257)
    print(tempo)
    tempo = int((tempo - 60) / 10)

    if tempo > 10:
        tempo = 10
    f.write(u8(tempo))


with open(sys.argv[1].replace(".mid", "") + ".mio", "rb") as f:
    read = f.read()

with open(sys.argv[1].replace(".mid", "") + ".mio", "wb") as f:
    checkSumOne = 0
    checkSumTwo = 0

    f.write(read)

    for i in range(16, 23):
        f.seek(i)
        f.write(u8(0))

with open(sys.argv[1].replace(".mid", "") + ".mio", "rb") as f:
    read = f.read()

with open(sys.argv[1].replace(".mid", "") + ".mio", "wb") as f:
    checkSumOne = 0
    checkSumTwo = 0

    f.write(read[:8192])

    for i in range(16, 23):
        f.seek(i)
        f.write(u8(0))

    for i in range(0, 256):
        checkSumOne += read[i] & 0xFF
    for i in range(256, len(read)):
        checkSumTwo += read[i] & 0xFF
    f.seek(19)
    f.write(u8((checkSumOne >> 24) & 0xFF))
    f.seek(18)
    f.write(u8((checkSumOne >> 16) & 0xFF))
    f.seek(17)
    f.write(u8((checkSumOne >> 8) & 0xFF))
    f.seek(16)
    f.write(u8((checkSumOne) & 0xFF))
    f.seek(23)
    f.write(u8((checkSumTwo >> 24) & 0xFF))
    f.seek(22)
    f.write(u8((checkSumTwo >> 16) & 0xFF))
    f.seek(21)
    f.write(u8((checkSumTwo >> 8) & 0xFF))
    f.seek(20)
    f.write(u8((checkSumTwo) & 0xFF))
