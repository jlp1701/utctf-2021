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
Several tools and frameworks are available to build and train a classifier model. I chose to a semi-automatic approach with the ML tool [weka](http://old-www.cms.waikato.ac.nz/~ml/weka/index.html) and python. Before loading data into weka, 


1. **Inspect the dataset**:
Make sure you have added a row on top to name each column. Otherwise weka refuses to accept the dataset. To load the lab.csv into weka, open the *Explorer*, click *Open file ...*, select the csv file and click *Open*.

2. **Evaluate and select features**
Change to column *Select attributes*. Change the attribute evaluator to the desired method (I chose *InfoGainAttributeEval*). Acknowledge the ranker message with *yes*. On the left side, choose *Cross-validation* as the selection mode and in the drop-down menu below, choose the last entry as class attribute (*cat* in my case). Click *Start*. In the window on the right, we can see the output of the selection process. With this evaluation method, the attributes of column 5 and 35 have the biggest merit.

3. **Construct a classifier based on decision rules**
First we check our results by visualizing the whole data set (lab + target) with respect of the attributes 5 and 35, and its classes m, p, d:
Append the target vectors to the lab vectors and insert a `?` in the class column so signal weka an unknown class. Load the csv as described in 1. Click on the column *Visualize*. In the settings below the plot matrix, click *Select Attributes*. Select the attributes 5 and 35 and click *OK* and then *Update*. Left-click on the top-left picture in the plot matrix to open it in a separate window.
It shows a plot with attribute 5 as x-axis and attribute 35 as y-axis. `p`, `m` and `d` vectors are colorized in blue, red and green respectively. Additionally, all unclassified target vectors are indicated as gray `M` symbols. The picture perfectly visualized the the three clusters of each class. All unclassified data correlate with the clusters and both attributes are sufficient to correctly classify the data. 
Decision-rule-based classifiers means, that we have a set of relational decisions (`<`, `<=`, `>`, `>=`) in a tree structure to classify data.
In our example, we set up two rules:
  1. `v[5] >= 24.75` to check if the data point `v` is within the `d` class or not
  2. `v[35] >= 16.75` to check if `v` is in class `m` or `p`.
The advantage of such decision-based classifiers is, that they are simple and fast. On the other hand, they might fail to handle more complex data sets with mixing clusters.
The classification function is:
```
def classify_attr_5_35(dat):
    classes = []
    for v in dat:
        if v[5] >= 24.75:
            classes.append("d")
        else:
            if v[35] >= 16.75:
                classes.append("m")
            else:
                classes.append("p")
    return classes
```

4. **Classify the target data with python**
Having the determined the decision rules, we now can move on to classify the target dataset. 


I combined the `lab.csv` and `target.csv` data into one dataset with `?` as placeholders for the class in target vectors.
