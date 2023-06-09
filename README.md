# midi2mio
Convert MIDIs to records in WarioWare DIY

This script will convert MIDIs to the MIO format used for WarioWare DIY records. To use, just install Python, install pretty_midi and mido which you can do by running `pip install -r requirements.txt`, after that you can run run `python midi2mio.py <path to midi>`. This script works best on simple MIDIs, I recommend starting using one track. Some notes will be scaled in the script because WarioWare DIY only uses less notes than you can find on a MIDI file.