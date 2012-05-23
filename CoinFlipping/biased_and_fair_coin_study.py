#!/usr/bin/env python
#
# Experiment and learning from question: implement a biased_coin function using a known_coin function
# known_coin() returns True for Heads, False for Tails
# write biased_coin(heads_prob)

import random
import math
import bisect

# decorator for experiment, a fancy global
class countcalls(object):
    '''Decorator that keeps track of the number of times a function is called.
       Added reset() to example from http://wiki.python.org/moin/PythonDecoratorLibrary#Counting_function_calls'''
   
    __instances = {}
   
    def __init__(self, f): 
       self.__f = f 
       self.__numcalls = 0 
       countcalls.__instances[f] = self
  
    def __call__(self, *args, **kwargs):
       self.__numcalls += 1
       return self.__f(*args, **kwargs)
  
    def count(self):
       "Return the number of times the function f was called."
       return countcalls.__instances[self.__f].__numcalls

    def reset(self):
        "Reset the number of times the function f was called to 0."
        countcalls.__instances[self.__f].__numcalls = 0
  
    @staticmethod
    def counts():
       "Return a dict of {function: # of calls} for all registered functions."
       return dict([(f.__name__, countcalls.__instances[f].__numcalls) for f in countcalls.__instances])

@countcalls
def known_coin(heads_prob=0.5):
    if random.random() > heads_prob:
        return False
    return True

# heads_prob is like a vertical line across the horizontal line between 0 and 1
# any number to the left of heads_prob is Heads, Tails otherwise
# biased_coin(heads_prob) is essentially a binary search that terminates early
# min and max are the current range boundary of remaining possible outcomes
def biased_coin(heads_prob):
    min = 0
    max = 1
    while(True):
        if known_coin():
            max = (min + max) / 2.0
        else:
            min = (min + max) / 2.0
        if max <= heads_prob:
            return True
        if min >= heads_prob:
            return False

# aveage is E(x), which is sum(x*p(x))
# (x,p) = (1, 0.5),(2, 0.25),(3, 0.125),...
# this is a converging series by the ratio test: 
#     p(x) = pow(2, -x), p(x+1) = pow(2, -x-1) 
#     p(x+1) / pow(2, -x) = 1/2 < 1
def expected_num_trials():
    s = 0
    limit = math.pow(10, -10)
    for i in range(1, 5000):
        incr = i * math.pow(2, -i)
        if incr < limit:
            print "converging series with each term's limit approaching 0 got a term of %s after %s steps" % (limit, i)
            break
        s += incr
    return s

def chisquare(observed_frequencies, expected_frequencies):
    for e in expected_frequencies:
        if e == 0:
            return 0
    return sum([pow(o-e, 2) / e for (o, e) in zip(observed_frequencies, expected_frequencies)])

def chisquare_to_pvalue(cs, chi_steps = [0.004, 0.02, 0.06, 0.15, 0.46, 1.07, 1.64, 2.71, 3.84, 6.64, 10.83], probs=[1, 0.95, 0.90, 0.80, 0.70, 0.50, 0.30, 0.20, 0.10, 0.05, 0.01, 0.001]):
    ''' 1 degree of freedom - http://en.wikipedia.org/wiki/Chi-squared_distribution '''
    i = bisect.bisect(chi_steps, cs)
    return probs[i]

def test(heads_prob, num_trials=1000):
    num_heads = 0
    for i in range(num_trials):
        if biased_coin(heads_prob):
            num_heads += 1
    cs = chisquare([num_heads, num_trials-num_heads], [heads_prob * num_trials, (1-heads_prob) * num_trials])
    pv = chisquare_to_pvalue(cs)

    if pv < 0.05  :
        print "result unlikely",
    else:
        print "test passed", 
    observed_prob = 1.0 * num_heads / num_trials
    print "for heads_prob %s, got chi-square of %0.4f, probability this happens is no more than %.04f. average observed prob of %.04f in %s trials" % (heads_prob, cs, pv, observed_prob, num_trials)

print "expected number of coin tosses: %0.4f"  % expected_num_trials()

num_trials = 50000
total_times_called = 0
for i in range(num_trials):
    biased_coin(random.random())
    total_times_called += known_coin.count()
    known_coin.reset()

print "avg number of times in %s trials is %0.4f" % (num_trials, 1.0 * total_times_called / num_trials)

test(0)
test(1)
test(0.1)
test(0.9)
test(0.6)
test(pow(2,-1))
for i in range(5):
    test(random.random())
