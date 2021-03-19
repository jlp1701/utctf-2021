# peeb-boop

Description: "Computers usually go beep boop, but I found this weird computer that goes peeb poob."

---

One binary file is provided. It seems like a regular ELF and so it is but it cannot be executed on a x86-64 machine. The error `./peeb_poob: cannot execute binary file: Exec format error` is given. 
Inspecting the ELF header with `readelf peeb_poob -h` reveals that it is compiled for `Renesas / SuperH SH` architecture.

When we open it with Ghidra and have a look at the decompiled `main` function, we can see the following:
```
undefined4 main(void)
{
  size_t len;
  char usr_inp [32];
  undefined4 l;
  uint n;
  int i;
  
  l = 0;
  i = 0;
  while (i < 0x20) {
    usr_inp[i] = '\0';
    i = i + 1;
  }
  printf("Enter a string: \n");
  fgets(usr_inp,0x20,stdin);
  encode(usr_inp);
  n = 0;
  while( true ) {
    len = strlen(usr_inp);
    if (len <= n) {
      puts("Nice flag!");
      return 0;
    }
    if (usr_inp[n] != (&flag)[n]) break;
    n = n + 1;
  }
  puts("Wrong!");
                    /* WARNING: Subroutine does not return */
  exit(-1);
}
```
Basically, the user is queried for input from stdin. This input string is then transformed within the function `encode` and checked bytewise against a hardcoded string in memory (located at `0x00411010`).
Only if the encoded input is equal to the memory string, the program prompts `Nice flag!`, which indicates, that we have to reconstruct the correct input resembling the actual flag.
To achieve this, we need to semantically reverse the `encode` function and feed the hardcoded memory string into it. 
The `encode` function looks like this:
```
void encode(char *inp_str)
{
  size_t len;
  uint i;
  uint t;
  
  i = 0;
  while (len = strlen(inp_str), i < len) {
    t = (uint)((int)i < 0);
    t = ((i ^ -t) + t & 3 ^ -t) + t;
    if (t < 4) {
      switch(t) {
      case 0:
        inp_str[i] = inp_str[i] ^ 0x21;
        break;
      case 1:
        inp_str[i] = inp_str[i] ^ 7;
        break;
      case 2:
        inp_str[i] = inp_str[i] ^ 0x23;
        break;
      case 3:
        inp_str[i] = inp_str[i] ^ 5;
      }
    }
    len = strlen(inp_str);
    if (i + 1 < len) {
      inp_str[i + 1] = inp_str[i] ^ inp_str[i + 1];
    }
    i = i + 1;
  }
  return;
}
```

The function consists of one big while loop which iterates through all input chars. The loop body can be divided into three parts: 
1. Calculation of switch case
2. XOR current byte with fixed value depending on switch case
3. XOR current and next byte (if available)

The first part is an obfuscation of the switch-case integer. When inspecting carefully, we see that `i` is always greater zero, thus `t` is always `0x0`. The whole expression boils down to `t = i & 0x3`. So the lower two bits select the switch-case. Note: If the expression would be more complex, we could use SMT-Solvers to simplify the expression.

Within the second part, the current byte simply gets XOR-ed with one of the four static numbers.

The third part transforms the next byte in the string, depending on the current byte. This works similar to CBC mode of block ciphers.

The reversed `decode` function:
```
void decode(char* inp_str) {
    // iterare over all chars in reverse
    for (long i = strlen(inp_str) - 1; i >= 0; i--)
    {
        // reverse block mode
        if (i - 1 >= 0) {
            inp_str[i] = inp_str[i] ^ inp_str[i-1];
        }
        
        // decode char
        switch (i & 3)
        {
        case 0:
            inp_str[i] ^= 0x21;
            break;

        case 1:
            inp_str[i] ^= 0x7;
            break;
        
        case 2:
            inp_str[i] ^= 0x23;
            break;

        case 3:
            inp_str[i] ^= 0x5;
            break;
        default:
            cout << "error: should not be reached." << endl;
            break;
        }   
    }
}
```

Now we just have to feed it the hardcoded string in memory:
```
int main() {
    char flag[] = {0x54, 0x27, 0x62, 0x0b, 0x4b, 0x2b, 0x73, 0x14, 0x06, 0x32, 0x61, 0x3b, 0x78, 0x4f, 0x5c, 0x29, 0x57, 0x20, 0x30, 0x06, 0x45, 0x1d, 0x4e, 0x7b, 0x6a, 0x0f, 0x51, 0x5e, 0x00, 0x00, 0x00, 0x00};
    decode(flag);
    cout << "decoded: " << flag << endl;
    return 0;
}
```

And we get the desired result: `decoded: utflag{b33p_b00p_p33b_p00b}`.
