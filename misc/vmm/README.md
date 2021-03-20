# Virtual Machine Monitor UWU

### Description
Virtual Machine Monitor UWU
998

A botnet has infected your computer. By examining the URL of its command and control server, you've discovered that your backup server is co-resident with the command and control server. You decided to prime and probe the instruction set cache of the VM to determine the botnets secret key and shut it down. You now have a collection of cache vectors representing the response time of the shared instruction cache. Your goal is to determine the key. Luckily, your hosting provider is antiquated and the botnet VM doesn't alternate between cores so you could continuously monitor it. You also know that the victim VM uses the exponent by squaring algorithm in cryptographic operations with the key.

```
int mult(int x, int y) { return x * y; }

int div(int x, int y) { return x / y; }

int exp_by_squaring(int x, int n) {
  if (n == 0) {
    return 1;
  }
  int y = 1;
  while (n > 1) {
    if (n % 2 == 1) {
      x = pow(x, 2);
      n = div(n, 2);
    } else {
      y = mult(x, y);
      x = pow(x, 2);
      n = div((n - 1), 2);
    }
  }
  return x * y;
}
```

In your lab, you ran the same hardware as the target VM with a similar software stack. You used the same prime and probe technique to label cache vectors P, D, M referring to when the functions pow, div, mult were running. Below are the datasets from the machines.

target.csv

lab.csv

The flag is the n parameter of exp_by_squaring used by the victim VM in binary.

-- a1c3

### Analysis

The descriptions tells us about a botnet C&C server which runs on the same server as our machine. So, it was possible to acquire two datasets which resemble instruction cache data:
1. **lab.csv**: Recorded vectors of own machine. Each row has 64 floating point features and one class feature, which can be `m`, `p` or `d`.
2. **target.csv**: Recorded vectors of C&C machine. Has the same set of features but lacks the classification column.
In this scenario, the classes resemble the specific arithmetic operations **m**ultiply, **d**ivision and **p**ower which are used in the `exp_by_squaring` function. 

The goal is to find the value of `n` used in the `exp_by_squaring` function. Each operation has its own unique response time fingerprint. If we can acquire the sequence of operations from **target.csv**, then we can use this set to reverse the bits of `n`, one-by-one. A sequence of `m p d` operations indicate a 0 bit and `p d` tells us that the bit was 1.

This setting is a classical data science scenario: We have a training dataset with feature vectors and classification and a test dataset with the same amount of features per entry but without classification. Our goal is to use the training set to train a classifier model and apply it on the test set to assign classes to it.

#### Classify the data of target.csv

