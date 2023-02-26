from simpy import *
import random

def makeRAM(env, init, cap):
    RAM = Container(env, init=init, capacity=cap)
    return RAM

def newProcess():
    memorySize = random.randint(1, 10)
    instructions = random.randint(1, 10)
    att = [memorySize, instructions]
    return att

env = Environment()
random.seed("equiposuperdupercool")

Memory = makeRAM(env, 100, 100)