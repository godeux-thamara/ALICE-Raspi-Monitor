#!/usr/bin/env python3
import sys
import os
import time
from dotenv import dotenv_values
from Sketch import Sketch

PARAMETERS = dotenv_values("parameters.env")
DELAY = PARAMETERS['DELAY'] if 'DELAY' in PARAMETERS else 10
if 'WORKING_DIRECTORY' in PARAMETERS:
    os.chdir(PARAMETERS['WORKING_DIRECTORY'])

if len(sys.argv) <= 1 and 'SKETCH' not in PARAMETERS:
    print(f"Usage: {sys.argv[0]} json_sketch_file.json")
    sys.exit(1)

json_sketch_file = sys.argv[1] if len(sys.argv) > 1 else PARAMETERS['SKETCH']

if not os.path.isfile(json_sketch_file):
    print(f"{json_sketch_file} not found.")
    sys.exit(2)

sketch = Sketch(json_sketch_file)
print(f"Waiting {DELAY} seconds before launching sketch...")
time.sleep(DELAY)
sketch.run()
