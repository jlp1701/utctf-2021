import sys
import time


def parse_tetr(filePath):
    f = open(filePath, "rb")
    d = f.read()
    # skip first 8 bytes: TETR\00\00\00\00
    d = d[8:]

    
    def parse_frame(frames, d):
        # print(f"frame")
        assert(len(d) >= 7)
        assert(d[0] == 0xf0)
        def parse_run(runs, d):
            # get type and len
            t = int(d[0])
            type_map = {0: "I", 1: "S", 2: "Z", 3: "O", 4: "J", 5: "L", 6: "T", 7: "_", 8: "X"}
            type_descramble = {1: 0, 5: 1, 6: 2, 4: 3, 3: 4, 2: 5, 7: 6, 0: 7, 8: 8}
            # l = int(bytes(reversed(d[2:5])), 16)
            l = int.from_bytes(d[1:4], byteorder="little")
            # print(f"run: {t}, {l}")
            # append run
            runs.append({"t": type_map[type_descramble[t]], "l": l})
            if d[5] == 0xf1:
                return
            else:
                parse_run(runs, d[5:])
        runs = []
        parse_run(runs, d[1:])
        n = len(runs)
        frames.append(runs)
        # check if more runs available
        assert(d[n * 5 + 1] == 0xf1)
        if len(d) - (n * 5 + 2) > 0:
            parse_frame(frames, d[(n * 5 + 2):])
            
    frames = []
    parse_frame(frames, d)
    # print(f"frames: {frames}")
    return frames
    

def print_frame(f):
    a = []
    a.extend([m['t'] for m in f for _ in range(m['l'])])
    assert len(a) == 240
    b = []
    for r in range(24):
        b.append(a[r*10:r*10+10])
    return b


# the resulting tetris frames are inserted into https://harddrop.com/fumen/
# utflag{v115@vhIkJJBwBHtBilBGnBDcBEjBnfBAAA}

if __name__=='__main__':
    frames = parse_tetr("challenge/secret.tetr")
    #f = print_frame(frames[0])
    for f in frames:
        print("#############")
        for l in reversed(print_frame(f)):
            for c in l:
                print(c, end='')
            print("\n", end='')
        