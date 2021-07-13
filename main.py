#!/usr/bin/env -S python3 -i
import sys
import os
import time
from Sketch import Sketch

DELAY = 10

if len(sys.argv) <= 1:
    print(f"Usage: {sys.argv[0]} json_sketch_file.json")
    sys.exit(1)

json_sketch_file = sys.argv[1]

if not os.path.isfile(json_sketch_file):
    print(f"{json_sketch_file} not found.")
    sys.exit(2)

sketch = Sketch(json_sketch_file)
print(f"Waiting {DELAY} seconds before lauching sketch...")
time.sleep(DELAY)
sketch.run()
