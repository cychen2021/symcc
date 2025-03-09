#!/usr/bin/env python3

import sys

if len(sys.argv) < 2:
    print("Usage: binaralize.py number1 [number2 ...]")
    sys.exit(1)

numbers = []
for arg in sys.argv[1:]:
    try:
        num = int(arg)
        numbers.append(num)
    except ValueError:
        print(f"Error: '{arg}' is not a valid integer")
        sys.exit(1)

# Write integers as binary data to stdout
for num in numbers:
    sys.stdout.buffer.write(num.to_bytes(4, byteorder='little', signed=True))


