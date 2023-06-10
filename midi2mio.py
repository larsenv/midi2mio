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
octaves = {
    "21": "14",
    "22": "15",
    "23": "16",
    "24": "17",
    "25": "18",
    "26": "19",
    "27": "20",
    "28": "21",
    "29": "22",
    "30": "23",
    "31": "0",
    "32": "1",
    "33": "2",
    "34": "3",
    "35": "4",
    "36": "5",
    "37": "6",
    "38": "7",
    "39": "8",
    "40": "9",
    "41": "10",
    "42": "11",
    "43": "12",
    "44": "13",
    "45": "14",
    "46": "15",
    "47": "16",
    "48": "17",
    "49": "18",
    "50": "19",
    "51": "20",
    "52": "21",
    "53": "22",
    "54": "23",
    "55": "0",
    "56": "1",
    "57": "2",
    "58": "3",
    "59": "4",
    "60": "5",
    "61": "6",
    "62": "7",
    "63": "8",
    "64": "9",
    "65": "10",
    "66": "11",
    "67": "12",
    "68": "13",
    "69": "14",
    "70": "15",
    "71": "16",
    "72": "17",
    "73": "18",
    "74": "19",
    "75": "20",
    "76": "21",
    "77": "22",
    "78": "23",
    "79": "24",
    "80": "1",
    "81": "2",
    "82": "3",
    "83": "4",
    "84": "5",
    "85": "6",
    "86": "7",
    "87": "8",
    "88": "9",
    "89": "10",
    "90": "11",
    "91": "12",
    "92": "13",
    "93": "14",
    "94": "15",
    "95": "16",
    "96": "17",
    "97": "18",
    "98": "19",
    "99": "20",
    "100": "21",
    "101": "22",
    "102": "23",
    "103": "24",
    "104": "1",
    "105": "2",
    "106": "3",
    "107": "4",
    "108": "5",
}
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

for i, track in enumerate(mid2.tracks):
    i = 0
    l = 0
    n = 0
    end_index = 0
    for msg in track:
        if msg.type == "note_on":
            if j > 3:
                break
            if notes[j][i] != 255:
                note = int(octaves[str(msg.note)])
                """if start not in note_dex_start[j]:
                    note_dex_start[j].append(i)
                else:
                    m = j
                    while notes[m][i] != 0:
                        m += 1
                        notes[m][i] = u8(note)
                    continue
                if end not in note_dex_end[j]:
                    note_dex_end[j].append(i)
                else:
                    m = j
                    while notes[m][i] != 0:
                        m += 1
                        notes[m][i] = u8(note)
                    continue"""
                notes[j][i] = u8(note)
                if midi.tick_to_time(msg.time) > 0:
                    for k in range(1, int(midi.tick_to_time(msg.time) * 4) + 1):
                        notes[j][i + k] = u8(255)
                    i += int(midi.tick_to_time(msg.time) * 4) + 1
                l += 1
            else:
                continue
            i += 1
            n += 1
    if n > 0:
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
        track_num += 1
    track_num = 0
    for instrument in instruments:
        for block_num in range(1, 25):
            offset = 0x107 + 0x114 * block_num + 0x10A + track_num
            if instrument != 0:
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
