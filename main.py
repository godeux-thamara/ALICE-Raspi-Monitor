#!/usr/bin/env python3
import sys
import os
import time
from Sketch import Sketch
from parameters import PARAMETERS


# Setting working directory
if 'WORKING_DIRECTORY' in PARAMETERS:
    os.chdir(PARAMETERS['WORKING_DIRECTORY'])

if len(sys.argv) <= 1 and 'SKETCH' not in PARAMETERS:
    print(f"Usage: {sys.argv[0]} json_sketch_file.json")
    sys.exit(1)

# Selecting sketch file
if len(sys.argv) >= 3 and sys.argv[1] == 'scenario':
    json_sketch_file = sys.argv[2]
    first_event_id = None
elif len(sys.argv) >= 3 and sys.argv[1] == 'start':
    json_sketch_file = PARAMETERS['SKETCH']
    first_event_id = sys.argv[2]
else:
    json_sketch_file = sys.argv[1] if len(sys.argv) > 1 else PARAMETERS['SKETCH']
    first_event_id = None

# Checking that selected sketch file exists
if not os.path.isfile(json_sketch_file):
    print(f"{json_sketch_file} not found.")
    sys.exit(2)

sketch = Sketch(json_sketch_file, first_event_id)
print(f"Waiting {PARAMETERS['DELAY']} seconds before launching sketch...", end="\n\n")
time.sleep(PARAMETERS['DELAY'])
sketch.run()
