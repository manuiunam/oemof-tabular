from oemof.solph import EnergySystem, Model, processing, Bus
# DONT REMOVE THIS LINE!
from oemof.tabular import datapackage  # noqa
from oemof.tabular.facades import TYPEMAP, Conversion, Commodity, Excess
from oemof.tabular.postprocessing import calculations
from oemof.tabular.facades import Load, Dispatchable, MultiGrid

path_datapackage = "datapackage.json"
path_results = ""


es = EnergySystem.from_datapackage(
    path_datapackage,
    # attributemap={},
    typemap={
        "bus": Bus,
        "multi_grid": MultiGrid,
        "dispatchable": Dispatchable,
        "excess": Excess,
        "load": Load,
        "conversion": Conversion,
    },
    #infer_last_interval=False,
)

# create model from energy system (this is just oemof.solph)
m = Model(es)

"""
    # add constraints from datapackage to the model
    m.add_constraints_from_datapackage(
        os.path.join(datapackage_dir, "datapackage.json"),
        constraint_type_map=CONSTRAINT_TYPE_MAP,
    )

    # if you want dual variables / shadow prices uncomment line below
    # m.receive_duals()
"""


# select solver 'gurobi', 'cplex', 'glpk' etc
m.solve(solver="cbc",solve_kwargs={"tee": True})

es.params = processing.parameter_as_dict(es,exclude_attrs=["subnodes"], exclude_none=True)
es.results = m.results()

#results = Results(energysystem_model)
# now we use the write results method to write the results in oemof-tabular
# format
"""FutureWarning: The behavior of array concatenation with empty entries is deprecated. In a future version, this will no longer exclude empty items when determining the result dtype. To retain the old behavior, exclude the empty entries before the concat operation.
  all_scalars = pd.concat(all_scalars, axis=0)
"""

postprocessed_results = calculations.run_postprocessing(es)
postprocessed_results.to_csv("results.csv", sep=";")
