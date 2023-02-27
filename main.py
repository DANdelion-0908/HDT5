from simpy import *
import random
import matplotlib.pyplot as plt

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

def queue(env, name, size, instructions, ps, proc_duration, Memory):

    RAM_Required = size

    print("%s con %i instrucciones, un tamaño de %i entra a la cola en el tiempo %d" % (name, instructions, size, env.now))

    if Memory.level - RAM_Required < 0:
        print("No hay suficiente espacio de almacenamiento en la RAM")
        yield env.timeout(1)

    else:
        print("%s entrando a la RAM en el tiempo %d" % (name, env.now))

        with ps.request() as req:
            yield req
            yield Memory.get(size)
            print("%s entrando a la cola en el tiempo %d" % (name, env.now))

            print("%s comenzando a procesarse en el tiempo %d" % (name, env.now))
            yield env.timeout(proc_duration)

            print("%s ahora tiene %i instrucciones" % (name, instructions - 3))
            
            instructions = instructions - 3
            if instructions <= 3:
                yield Memory.put(size)
                print("%s saliendo del sistema en el tiempo %d" % (name, env.now))
                ps.release(req)

            else:
                print("%s saliendo de la CPU en el tiempo %d y se regresa a la cola" % (name, env.now))
                ps.release(req)
                yield Memory.put(size)

                queueBack = random.randint(1, 2)

                if queueBack == 1:
                    yield env.process(queue(env, name, size, instructions, ps, proc_duration, Memory))
                    yield env.timeout(random.expovariate(1.0/interval))

                elif queueBack == 2:
                    print("%s debe esperar 3 segundos para volver a la cola" % (name))
                    yield env.timeout(proc_duration)
                    yield env.process(queue(env, name, size, instructions, ps, proc_duration, Memory))
                    yield env.timeout(random.expovariate(1.0/interval))

#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////

random.seed(RANDOM_SEED)
env = Environment()
Memory = makeRAM(env, 100, 100)
ps = Resource(env, capacity=1)
interval = 5

def Pro_Gen(processes):
    for i in range(processes):
        lista = newProcess()
        env.process(queue(env, "Proceso %d" % i, lista[0], lista[1], ps, 3, Memory=Memory))
        yield env.timeout(random.expovariate(1.0/interval))

processNum = [25, 50, 100, 150, 200]
finalTime = []

print(finalTime)

for i in range(5):
    env.process(Pro_Gen(processNum[i]))
    env.run()
    finalTime.append(env.now)
    print("\n")

fig,ax = plt.subplots()
print(finalTime)
print(processNum)
ax.fill_between(processNum, finalTime)
plt.show()

# [Container].level | Regresa el valor
# [Container].get(x) | Saca el valor de x
# [Container].put(x) | La pone
