from typing import NamedTuple, Callable, List, Dict


def variables(events, rooms, slots):
    """Defines the required instances of pulp.LpVariable

    Parameters
    ----------

    Returns
    -------
    dict
        mapping an instance of resource.ScheduledItem to an instance of
        pulp.LpVariable
    """
    variables = {}
    return variables


class Constraint(NamedTuple):
    function: Callable
    args: List
    kwargs: Dict
    operator: Callable
    value: int
