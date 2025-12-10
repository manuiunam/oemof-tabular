""" this module should give space for facade subclasses to represent areas with multiply (solph) components"""
from typing import Union, Sequence

from oemof.solph import Flow, Bus
from oemof.solph.components import Link, Source, Converter, Sink
from oemof.tabular._facade import Facade, dataclass_facade

import json


@dataclass_facade
class BusWithMetadata(Facade,Bus):
    #label: str
    carrier:str
    feedin:False


@dataclass_facade
class MultiGridConnection(Facade):
    # label

    # default attributes to exclude
    #default_exclude = [
    #    "subnodes",
    #]

    carrier_in_use: list # names of used carriers in a list [...]
    grid_buses: list # global bus names as strings in a list [...]

    _local_bus_dict = {}
    label: str


    def build_local_carrier_busses(self):
        if isinstance(self.carrier_in_use,list):
            pass
        else:
            try:
                self.carrier_in_use = json.loads(self.carrier_in_use)
            except json.JSONDecodeError:
                pass

        for carrier in self.carrier_in_use:
            bus = Bus(label=f"{self.label}_local_{carrier}_bus")
            self._local_bus_dict.update({carrier: bus})
            self.subnodes.append(bus)

    def build_grid_connections(self):
        feedin = 0
        for bus_grid in self.grid_buses:
            # name = ((n for n in self._local_bus_dict.keys() if n in bus_grid), None)
            for carrier in self._local_bus_dict.keys(): # todo change to carrier related
                if carrier in bus_grid.label:
                    bus_local = self._local_bus_dict[carrier]
                    link2grid = Link(label=f"{self.label}_linked_{carrier}",
                                     inputs={bus_grid: Flow(),bus_local: Flow()},
                                     outputs={bus_grid: Flow(),bus_local: Flow()}, # todo maybe add parameter functionality to Flow()
                                     conversion_factors={(bus_grid, bus_local): 1,
                                                         (bus_local, bus_grid): feedin}
                                     )
                    self.subnodes.append(link2grid)
                    print(f"{self.label} got Link {link2grid.label}")

    def build_solph_components(self):
        self.build_local_carrier_busses()
        self.build_grid_connections()


class Area(MultiGridConnection):

    def build_local_load(self):
        el_load = [0.1 for n in range(10)]
        heat_load = [0.1 for n in range(10)]
        el_demand = Sink(label=f"{self.label}_el_demand",
                         inputs={self._local_bus_dict["electricity"]: Flow(nominal_value=1000.0,    # todo base unit and abs or rel %?
                                                    fix=el_load
                                                    )})
        self.subnodes.append(el_demand)
        print(f"Area got component {el_demand.label}")

        heat_demand = Sink(label=f"{self.label}_heat_demand",
                         inputs={self._local_bus_dict["heat"]: Flow(nominal_value=2000,  # todo base unit and abs or rel %?
                                                      fix=heat_load)})
        self.subnodes.append(heat_demand)
        print(f"Area got component {heat_demand.label}")

    def build_local_converter(self):
        converters = [
            {
                "name": "heater1",
                "carrier_in": "electricity",
                "carrier_out": "heat",
                "power": 1000,
                "efficiency": 0.9
            },
            {
                "name": "heater2",
                "carrier_in": "electricity",
                "carrier_out": "heat",
                "power": 2000,
                "efficiency": 0.8
            },
        ]

        for converter in converters:
            if converter["carrier_in"] in self._local_bus_dict and converter["carrier_out"] in self._local_bus_dict:
                from_bus = self._local_bus_dict[converter["carrier_in"]]
                to_bus = self._local_bus_dict[converter["carrier_out"]]
                converter = Converter(
                    label=f"{self.label}_{converter['name']}",
                    inputs={from_bus: Flow()},
                    outputs={to_bus: Flow(nominal_value=converter['power'])},
                    conversion_factors={from_bus: converter['power'],
                                        to_bus: converter['efficiency']}
                )
                # todo add capacity costs
                self.subnodes.append(converter)
                print(f"Area got component {converter.label}")



    def build_solph_components(self):
        super().build_solph_components()
        self.build_local_load()
        self.build_local_converter()
