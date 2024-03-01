#!/usr/bin/python3
import os
import struct
import subprocess
import tempfile
import math

BARS_NUMBER = 1
# OUTPUT_BIT_FORMAT = "8bit"
OUTPUT_BIT_FORMAT = "16bit"
# RAW_TARGET = "/tmp/cava.fifo"
RAW_TARGET = "/dev/stdout"

conpat = """
[general]
bars = %d
[output]
method = raw
raw_target = %s
bit_format = %s
[smoothing]
integral = 20
"""

config = conpat % (BARS_NUMBER, RAW_TARGET, OUTPUT_BIT_FORMAT)
bytetype, bytesize, bytenorm = ("H", 2, 65535) if OUTPUT_BIT_FORMAT == "16bit" else ("B", 1, 255)


def run():
    with tempfile.NamedTemporaryFile() as config_file:
        config_file.write(config.encode())
        config_file.flush()

        process = subprocess.Popen(["cava", "-p", config_file.name], stdout=subprocess.PIPE)
        chunk = bytesize * BARS_NUMBER
        fmt = bytetype * BARS_NUMBER

        if RAW_TARGET != "/dev/stdout":
            if not os.path.exists(RAW_TARGET):
                os.mkfifo(RAW_TARGET)
            source = open(RAW_TARGET, "rb")
        else:
            source = process.stdout
        tick = 0
        while True:
            tick += 1
            data = source.read(chunk)
            if len(data) < chunk:
                break
            # sample = [i for i in struct.unpack(fmt, data)]  # raw values without norming
            sample = [i / bytenorm for i in struct.unpack(fmt, data)]
            if tick % 5 == 0:
                # light = int((math.sqrt(1 - math.pow(sample[0], 2)) * -1 + 1) * 20)
                light = int(math.pow(sample[0], 2) * 20)
                print(light)
                os.system("echo " + str(light) + "  | sudo tee /sys/class/leds/gip*/brightness")

if __name__ == "__main__":
    run()
