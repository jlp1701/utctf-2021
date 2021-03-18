#include <cstring>
#include <iostream>


using namespace std;


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

int main() {
    char flag[] = {0x54, 0x27, 0x62, 0x0b, 0x4b, 0x2b, 0x73, 0x14, 0x06, 0x32, 0x61, 0x3b, 0x78, 0x4f, 0x5c, 0x29, 0x57, 0x20, 0x30, 0x06, 0x45, 0x1d, 0x4e, 0x7b, 0x6a, 0x0f, 0x51, 0x5e, 0x00, 0x00, 0x00, 0x00};
    cout << "encoded flag: " << flag << endl;
    decode(flag);
    cout << "decoded: " << flag << endl;
    return 0;
}