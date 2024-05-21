peak = ([i for i in range(97, 145)] + [i  for i in range(156, 265)] +
            [i + 288 for i in range(97, 145)] + [i + 288  for i in range(156, 265)] +
            [i + 288*2 for i in range(97, 145)] + [i + 288*2  for i in range(156, 265)] +
            [i + 288*3 for i in range(97, 145)] + [i + 288*3  for i in range(156, 265)] +
            [i + 288*4 for i in range(97, 145)] + [i + 288*4  for i in range(156, 265)])

def on_station_list(schedules, nt):
    T = set(range(1,nt + 1))
    
    station_list = {}
    for bus, sch in schedules.items():
        _list = list(map(int, sch))
        on = T - set(_list)

        station_list[bus] = sorted(list(on))
    
    return station_list

def calculate_demand(bus, soc):
    capa = {'day_bus' : 250,
            'n_bus' : 350}
    
    if bus[0] == '1':
        return capa['day_bus'] * 0.7 - soc
    else:
        return capa['n_bus'] * 0.7 - soc
    
def remove_bus(charging_list, bus):
    if bus in charging_list:
        charging_list.remove(bus)

def bus_departure(charging_list, bus, t, soc):

    remove_bus(charging_list, bus)

    consumption = 0.25
    sol = {'bus': bus, 'period': t, "charge": 0, "discharge": 0, "consumption": consumption, "SOC": soc - consumption}

    return sol

def bus_charging(charging_list, bus, t, soc):

    bandwidth = 0.4166667
    required = calculate_demand(bus, soc)

    if (required > 0) & (len(charging_list) <= 30):
        _sol = {'bus': bus, 'period': t, "charge": bandwidth, "discharge": 0, "consumption": 0, "SOC": soc + bandwidth}
        charging_list.append(bus)
    else:
        _sol = {'bus': bus, 'period': t, "charge": 0, "discharge": 0, "consumption": 0, "SOC": soc}
        remove_bus(charging_list, bus)

    return _sol

def check_peak(row):
    # peak = ([i for i in range(97, 145)] + [i  for i in range(156, 265)] +
    #         [i + 288 for i in range(97, 145)] + [i + 288  for i in range(156, 265)] +
    #         [i + 288*2 for i in range(97, 145)] + [i + 288*2  for i in range(156, 265)] +
    #         [i + 288*3 for i in range(97, 145)] + [i + 288*3  for i in range(156, 265)] +
    #         [i + 288*4 for i in range(97, 145)] + [i + 288*4  for i in range(156, 265)])
    if row in peak:
        return True
    else:
        return False

def seize_charger(charging_list, bus, t, soc):
    bandwidth = 0.4166667
    required = calculate_demand(bus, soc)

    if bus in charging_list:
        if len(charging_list) == 30:
            remove_bus(charging_list, bus)
            _sol = {'bus': bus, 'period': t, "charge": 0, "discharge": 0, "consumption": 0, "SOC": soc}
    if len(charging_list) > 30:
        _sol = {'bus': bus, 'period': t, "charge": 0, "discharge": 0, "consumption": 0, "SOC": soc}
        remove_bus(charging_list, bus)


    if (required > 0) & (len(charging_list) <= 30) & (not check_peak(t)):
        _sol = {'bus': bus, 'period': t, "charge": bandwidth, "discharge": 0, "consumption": 0, "SOC": soc + bandwidth}
        charging_list.append(bus)
    elif (required < 0) & (len(charging_list) <= 30) & ():

    else:
        _sol = {'bus': bus, 'period': t, "charge": 0, "discharge": 0, "consumption": 0, "SOC": soc}
        remove_bus(charging_list, bus)

    return _sol

