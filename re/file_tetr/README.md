# File.tetr

### Description: 
"I really like tetris. I made a top secret opener and encoded it with my custom encoding scheme.
I hope no one finds my opener..
Put the opener into https://harddrop.com/fumen/ to find the secret part of the flag. The flag is utflag{v115@???????????}."

Within the provided archive there is a binary file `encoder`, three times the combination of a `.gif` and `.tetr` file and a `secret.tetr` file.

### Analysis

We can execute the binary which yields a binary file `output.tetr`. Using `xxd output.tetr` reveals no flag unfortunately.

We analyze the executable with ghidra.
Basically, the program takes a string encoding Tetris game states (https://github.com/knewjade/tetris-fumen, https://harddrop.com/wiki/SRS#How_Guideline_SRS_Really_Works), parses it into internal structures. Then the game states are written into a file using a simple run-length encoding (type, len).

The following pseudo-code shows the program semantics (with simplifications):
```python
frames = []
frames = decode_str(inp_str)  # returns a list of tetris frames

write_file("TETR")  # file header
for b in frames:
    write_file("F0")  # begin of a tetris frame
    write_file(encode_frame_run_len(b))
    write_file("F1")  # end of a tetris frame

```

The structure of a run-length encoded tetris frame is ([] symbolizes one byte and is not part of the actual encoding) `[F0][t][s0][s1][s2][s3][F1]` with t indicating the tile type and s is a 4 byte-long integer (little-endian) which give the repetition count of the symbol t.

For example, a empty frame (dimensions: 10x24) would be encoded as: `F0 00 F0 00 00 00 F1`. Where the type `t` can be one of the following:
```
Tile types:
0 --> " " (emtpy)
1 --> "I" (line piece)
2 --> "L" (L piece)
3 --> "J" (J piece)
4 --> "O" (block piece)
5 --> "S" (S piece)
6 --> "Z" (Z piece)
7 --> "T" (T piece)
8 --> "X" (Gray)
```

We could reverse engineer the whole program, including `encode_frame_run_len` and `decode` functions to compute the actual flag. I could not find any good source which describes the v115 encoding so I just reversed the simpler run-length encoding in the files to recover the actual tetris frames and then stick them into the given [creation tool](https://harddrop.com/fumen/) manually.
The script [](decode_tetr.py) implements the run-length reversing and prints all tetris frames to stdout. Luckily, there are only 9 frames so manual insertion is not a big deal. The page the encodes the tetris frames into v115 encoding which is the desired flag.

