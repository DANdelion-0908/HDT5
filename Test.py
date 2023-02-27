"""
Covers:

- Resources: Resource
- Resources: Container
- Waiting for other processes

Scenario:
  A gas station has a limited number of gas pumps that share a common
  fuel reservoir. Cars randomly arrive at the gas station, request one
  of the fuel pumps and start refueling from that reservoir.

  A gas station control process observes the gas station's fuel level
  and calls a tank truck for refueling if the station's level drops
  below a threshold.

Updated my Michel R. Gibbs
Car does not make a request for gas amount unless it can get full amount.
If cannot get full amount, will wait for truck to replenish before making request
"""

import itertools
import random

import simpy


RANDOM_SEED = 42
GAS_STATION_SIZE = 200     # liters
THRESHOLD = 10             # Threshold for calling the tank truck (in %)
FUEL_TANK_SIZE = 50        # liters
FUEL_TANK_LEVEL = [5, 25]  # Min/max levels of fuel tanks (in liters)
REFUELING_SPEED = 2        # liters / second
TANK_TRUCK_TIME = 300      # Seconds it takes the tank truck to arrive
T_INTER = [30, 300]        # Create a car every [min, max] seconds
SIM_TIME = 2000            # Simulation time in seconds
REPLENISHMENT_SPEED = 20   # linters / second for tanker truck to refill gas staiion


def car(name, env, gas_station, fuel_pump, replenish_event):
    """A car arrives at the gas station for refueling.

    It requests one of the gas station's fuel pumps and tries to get the
    desired amount of gas from it. If the stations reservoir is
    depleted, the car has to wait for the tank truck to arrive.

    """
    fuel_tank_level = random.randint(*FUEL_TANK_LEVEL)
    print('%s arriving at gas station at %.1f' % (name, env.now))
    with gas_station.request() as req:
        start = env.now
        # Request one of the gas pumps
        yield req
        print('%s exit queue and started pumping gas at %.1f' % (name, env.now))
        # Get the required amount of fuel
        liters_required = FUEL_TANK_SIZE - fuel_tank_level
        
        # check if amount is available
        while liters_required > fuel_pump.level:
            # use a while in case another car uses up the replenishment

            # wait for truck
            print('%s waiting for fuel truck before starting to pump %.1f' % (name, env.now))
            yield replenish_event

        yield fuel_pump.get(liters_required)

        # The "actual" refueling process takes some time
        yield env.timeout(liters_required / REFUELING_SPEED)

        print('%s finished refueling in %.1f seconds.' % (name,
                                                          env.now - start))


def gas_station_control(env, gas_station, fuel_pump):
    """
    Periodically check the level of the *fuel_pump* and call the tank
    truck if the level falls below a threshold.
    """
    
    gas_station.replenish_event = env.event()
    while True:
        if fuel_pump.level / fuel_pump.capacity * 100 < THRESHOLD:
            # We need to call the tank truck now!
            print('Calling tank truck at %d' % env.now)
            env.process(tank_truck(env, fuel_pump, gas_station.replenish_event))

            # yield until replenishment is finished
            yield gas_station.replenish_event

            # reset event for next replenishment
            gas_station.replenish_event = env.event()

        yield env.timeout(10)  # Check every 10 seconds


def tank_truck(env, fuel_pump, replenish_event):
    """
    Arrives at the gas station after a certain delay and refuels it.
    """
    yield env.timeout(TANK_TRUCK_TIME)
    print('Tank truck arriving at time %d' % env.now)
    
    amount = fuel_pump.capacity - fuel_pump.level
    replem_time = amount / REPLENISHMENT_SPEED
    yield env.timeout(replem_time)

    print('Tank truck replenshied %.1f liters at time %.1f.' % (amount, env.now))
    yield fuel_pump.put(amount)

    # let any listeners know replenishment is done
    replenish_event.succeed()


def car_generator(env, gas_station, fuel_pump):
    """
    Generate new cars that arrive at the gas station.
    """
    for i in itertools.count():
        yield env.timeout(random.randint(*T_INTER))
        env.process(car('Car %d' % i, env, gas_station, fuel_pump, gas_station.replenish_event))


# Setup and start the simulation
print('Gas Station refuelling')
random.seed(RANDOM_SEED)

# Create environment and start processes
env = simpy.Environment()
gas_station = simpy.Resource(env, 2)
fuel_pump = simpy.Container(env, GAS_STATION_SIZE, init=GAS_STATION_SIZE)
env.process(gas_station_control(env, gas_station, fuel_pump))
env.process(car_generator(env, gas_station, fuel_pump))

# Execute!
env.run(until=SIM_TIME)