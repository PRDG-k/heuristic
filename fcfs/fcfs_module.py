## LITERAL
peak = ([i for i in range(97, 145)] + [i  for i in range(156, 265)] +
            [i + 288 for i in range(97, 145)] + [i + 288  for i in range(156, 265)] +
            [i + 288*2 for i in range(97, 145)] + [i + 288*2  for i in range(156, 265)] +
            [i + 288*3 for i in range(97, 145)] + [i + 288*3  for i in range(156, 265)] +
            [i + 288*4 for i in range(97, 145)] + [i + 288*4  for i in range(156, 265)])

bandwidth = 0.4166667
consumption = 0.25

## Variables
# list of seize n
seize_list = []

# list of required n
wait_list = []

## Template
def TEMPLATE(bus, t, soc, type):
    if type == 0:
        return {'bus': bus, 'period': t, "charge": bandwidth, "discharge": 0, "consumption": 0, "SOC": soc + bandwidth}
    if type == 1:
        return {'bus': bus, 'period': t, "charge": 0, "discharge": bandwidth, "consumption": 0, "SOC": soc - bandwidth}
    if type == 2:
        return {'bus': bus, 'period': t, "charge": 0, "discharge": 0, "consumption": consumption, "SOC": soc - consumption}
    if type == 4:
        return {'bus': bus, 'period': t, "charge": 0, "discharge": 0, "consumption": 0, "SOC": soc}

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
    
def remove_bus(bus):
    if bus in seize_list:
        seize_list.remove(bus)

# def bus_departure(charging_list, bus, t, soc):

#     remove_bus(charging_list, bus)

#     consumption = 0.25
#     sol = {'bus': bus, 'period': t, "charge": 0, "discharge": 0, "consumption": consumption, "SOC": soc - consumption}

#     return sol

# def bus_charging(charging_list, bus, t, soc):

#     bandwidth = 0.4166667
#     required = calculate_demand(bus, soc)

#     if (required > 0) & (len(charging_list) <= 30):
#         _sol = {'bus': bus, 'period': t, "charge": bandwidth, "discharge": 0, "consumption": 0, "SOC": soc + bandwidth}
#         charging_list.append(bus)
#     else:
#         _sol = {'bus': bus, 'period': t, "charge": 0, "discharge": 0, "consumption": 0, "SOC": soc}
#         remove_bus(charging_list, bus)

#     return _sol

def check_peak(row):
    if row in peak:
        return True
    else:
        return False


def in_list_decision( bus, t, soc):
    is_required = calculate_demand(bus, soc) > 0
    is_peak = check_peak(t)

    # BASE RULE #
    if (len(wait_list) != 0) & (not is_required):
        remove_bus(bus)
        _sol = TEMPLATE(bus, t, soc, 4)
        return _sol

    # Condition
    if is_required:
        _sol = TEMPLATE(bus, t, soc, 0)
    else:
        if is_peak:
            _sol = _sol = TEMPLATE(bus, t, soc, 1)
        else:
            _sol = TEMPLATE(bus, t, soc, 0)
    return _sol


def not_in_list_decision(bus, t, soc):
    is_required = calculate_demand(bus, soc) > 0
    is_peak = check_peak(t)

    if len(seize_list) >= 30:
        # Not seizable
        if is_required:
            _sol = TEMPLATE(bus, t, soc, 4)
            wait_list.append(bus)
        else:
            _sol = TEMPLATE(bus, t, soc, 4)
            pass
    else:
        # seizable
        if is_required:
            _sol = TEMPLATE(bus, t, soc, 0)
            seize_list.append(bus)
        else:
            if is_peak:
                # Discharge
                _sol = TEMPLATE(bus, t, soc, 1)
                seize_list.append(bus)
            else:
                # Charge
                _sol = TEMPLATE(bus, t, soc, 0)
                seize_list.append(bus)
    return _sol
