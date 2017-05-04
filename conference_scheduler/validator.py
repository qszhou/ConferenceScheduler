from conference_scheduler import scheduler


def constraint_violations(array, events, slots, constraints=None):
    """Take a schedule in array form and return any violated constraints

    Parameters
    ----------
        events : list or tuple
            of resources.Event instances
        slots : list or tuple
            of resources.Slot instances
        constraints : list or tuple
            of generator functions which each produce instances of
            resources.Constraint

    Returns
    -------
        Generator
            of a list of strings indicating the nature of the violated
            constraints
    """
    return (
        c.label
        for c in scheduler.all_constraints(events, slots, array, constraints)
        if not c.condition
    )


def is_valid_solution(solution, events, slots, constraints=None):
    pass


def is_valid_array(array, events, slots, constraints=None):
    """Take a schedule in array form and return whether it is a valid
    solution for the given constraints

    Parameters
    ----------
        events : list or tuple
            of resources.Event instances
        slots : list or tuple
            of resources.Slot instances
        constraints : list or tuple
            of generator functions which each produce instances of
            resources.Constraint

    Returns
    -------
        bool
            True if array represents a valid solution
    """

    if len(array) == 0:
        return False
    violations = sum(1 for c in (constraint_violations(
        array, events, slots, constraints)))
    return violations == 0


def is_valid_schedule(schedule, events, slots, constraints=None):
    """Take a schedule and return whether it is a valid solution for the
    given constraints

    Parameters
    ----------
        events : list or tuple
            of resources.Event instances
        slots : list or tuple
            of resources.Slot instances
        constraints : list or tuple
            of generator functions which each produce instances of
            resources.Constraint

    Returns
    -------
        bool
            True if schedule is a valid solution
    """
    if len(schedule) == 0:
        return False
    array = scheduler.schedule_to_array(schedule, events, slots)
    return is_valid_array(array, events, slots)


def schedule_violations(schedule, events, slots, constraints=None):
    """Take a schedule and return a list of violated constraints

    Parameters
    ----------
        events : list or tuple
            of resources.Event instances
        slots : list or tuple
            of resources.Slot instances
        constraints : list or tuple
            of generator functions which each produce instances of
            resources.Constraint

    Returns
    -------
        Generator
            of a list of strings indicating the nature of the violated
            constraints
    """
    array = scheduler.schedule_to_array(schedule, events, slots)
    return constraint_violations(array, events, slots, constraints)
