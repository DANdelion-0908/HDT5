from simpy import *
import random

RANDOM_SEED = 42

def makeRAM(env, init, cap):
    RAM = Container(env, init=init, capacity=cap)
    return RAM

def newProcess():
    memorySize = random.randint(1, 10)
    instructions = random.randint(1, 10)
    att = [memorySize, instructions]
    return att

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def queue(env, name, size, instructions, ps, proc_duration):

    print("%s ha sido creado y entra a la cola en el tiempo %d" % (name, env.now))

    size = lista[0]

    with ps.request() as req:
        yield req
    

        while size > Memory.capacity:
            print("No hay suficiente espacio en la RAM para %s, por lo que debe esperar" % (name))

        print("%s entrando a la cola en el tiempo %d" % (name, env.now))
        Memory.capacity - lista[0]

        print("%s comenzando a procesarse en el tiempo %d" % (name, env.now))
        yield env.timeout(proc_duration)
            
        instructions = lista[1]
        if instructions <= 3:
            print("%s saliendo del sistema en el tiempo %d" % (name, env.now))

        else:
            print("%s saliendo de la CPU en el tiempo %d y se regresa a la cola" % (name, env.now))
            lista[1] - 1

#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////

env = Environment()

Memory = makeRAM(env, 100, 100)

ps = Resource(env, capacity=1)

for i in range(25):
    lista = newProcess()
    print(lista)
    env.process(queue(env, "Proceso %d" % i, lista[0], lista[1], ps, 3))

env.run()