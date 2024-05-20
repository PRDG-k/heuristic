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

