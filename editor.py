#!/usr/bin/python3
import argparse
import math
from pathlib import Path


def write_data(path, data):
    with open(path, "w") as f:
        data.pop(0)
        for byte in data:
            f.write(f'{byte:02x}')


def read_file(path):
    try:
        with open(path, 'r') as f:
            i = 0
            data = [0] * 513
            while True:
                chars = f.read(2)
                string = chars.strip()
                if not string:
                    break
                if not is_hex(string):
                    continue
                i = i + 1
                if i > 512:
                    break
                data[i] = int(string, 16)
        return data
    except OSError:
        return '00' * 512


def is_hex(string):
    try:
        bytes.fromhex(string)
        return True
    except ValueError:
        return False


def set_channels(data, channel_data, mod_type):
    for x in range(0, len(channel_data), 2):
        channel = math.floor(x/2) + 1
        dmx_data = channel_data[x] + channel_data[x+1]
        if (dmx_data != 'xx'):
            if mod_type == 'up':
                data[channel] += int(dmx_data, 16)
            elif mod_type == 'down':
                data[channel] -= int(dmx_data, 16)
            else:
                data[channel] = int(dmx_data, 16)
            data[channel] = min(255, data[channel])
            data[channel] = max(0, data[channel])


def main():
    parser = argparse.ArgumentParser(description='Calculate hex values for dmxpy2')
    parser.add_argument('-c', '--channel_data', type=str, default='000000000000',
                        help='Raw channel to be sent as pairs of hex, ie FFFFF \
                                would be max level for channels 1 and 2')
    parser.add_argument('-t', '--mod-type', type=str, default='set',
                        help='Specify whether channel data is set, up, or down \
                                (default: set)')
    parser.add_argument('-b', '--blackout', action='store_true', help='Turn off \
            all channels (level = 0)')
    parser.add_argument('-p', '--path', type=str, default='dmxpy2.txt',
                        help='Which file to read from/make edits to')

    args = parser.parse_args()

    path = Path.home() / args.path

    if args.blackout:
        data = [0] * 512
        write_data(path, data)
        exit()
    data = read_file(path, )
    set_channels(data, args.channel_data, args.mod_type)
    write_data(path, data)


if __name__ == '__main__':
    main()
