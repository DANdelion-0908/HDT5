from simpy import *
import random
import matplotlib.pyplot as plt
import statistics

RANDOM_SEED = 42
START = []

def DProceso():
    duration = input("Unidades que desea para la duracion del proceso, deben ser valores enteros mayores o iguales que 1. (Recordatorio 1 unidad de tiempo = 3 procesos): ")
    if(duration.isdigit() and int(duration)>= 1):
        duration = int(duration) * 3
        return duration
    else:
        print("Ingresa un número válido")
    DProceso()
    
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

    print("%s con %i instrucciones, un tamaño de %i entra a la cola en el tiempo %d" % (name, instructions, size, env.now))
    START.append(env.now)

    if Memory.level - size < 0:
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
            
            instructions = instructions - proc_duration
            if instructions <= proc_duration:
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
                    print("%s debe esperar %i segundos para volver a la cola" % (name, proc_duration))
                    yield env.timeout(proc_duration)
                    yield env.process(queue(env, name, size, instructions, ps, proc_duration, Memory))
                    yield env.timeout(random.expovariate(1.0/interval))

#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////

random.seed(RANDOM_SEED)
env = Environment()
Memory = makeRAM(env, 100, 100)
ps = Resource(env, capacity=1)
interval = 1

def Pro_Gen(processes, duration):
    for i in range(processes):
        lista = newProcess()
        env.process(queue(env, "Proceso %d" % i, lista[0], lista[1], ps, duration, Memory=Memory))
        yield env.timeout(random.expovariate(1.0/interval))

processNum = [25, 50, 100, 150, 200]
finalTime = []

print(finalTime)

duration = DProceso()

for i in range(5):
    env.process(Pro_Gen(processNum[i], duration))
    env.run()
    finalTime.append(env.now)
    print("\n")

mean = statistics.mean(START)
print("El promedio es: ", mean, "\n")

desv = statistics.pstdev(START)
print("La desviación estándar es: ", desv, "\n")

fig,ax = plt.subplots()
print(finalTime)
print(processNum)
ax.fill_between(processNum, finalTime)
#plt.title("Grafico Numero de procesos vs Tiempo de EJecucion")
plt.show()


# [Container].level | Regresa el valor
# [Container].get(x) | Saca el valor de x
# [Container].put(x) | La pone