import pulp
import itertools as it
from conference_scheduler.resources import Shape, Constraint
from conference_scheduler.lp_problem import utils as lpu


# According to David MacIver, using this function is more efficient than
# using sum()
# This code is taken from his gist at:
# https://gist.github.com/DRMacIver/4b6561c8e4776597bf7568ccac52742f
def lpsum(variables):
    result = pulp.LpAffineExpression()
    for v in variables:
        result.addInPlace(v)
    return result


summation_functions = {
    'lpsum': lpsum,
    None: sum
}


def _schedule_all_events(events, slots, X, summation_type=None):

    shape = Shape(len(events), len(slots))
    summation = summation_functions[summation_type]

    label = 'Event either not scheduled or scheduled multiple times'
    for event in range(shape.events):
        yield Constraint(
            f'{label} - event: {event}',
            summation(X[event, slot] for slot in range(shape.slots)) == 1
        )


def _max_one_event_per_slot(events, slots, X, summation_type=None):

    shape = Shape(len(events), len(slots))
    summation = summation_functions[summation_type]

    label = 'Slot with multiple events scheduled'
    for slot in range(shape.slots):
        yield Constraint(
            f'{label} - slot: {slot}',
            summation(X[(event, slot)] for event in range(shape.events)) <= 1
        )


def _events_in_session_share_a_tag(events, slots, X):
    """
    Constraint that ensures that if an event has a tag and
    is in a given session then it must
    share at least one tag with all other event in that session.
    """

    session_array, tag_array = lpu.session_array(slots), lpu.tag_array(events)

    label = 'Dissimilar events schedule in same session'
    event_indices = range(len(tag_array))
    session_indices = range(len(session_array))
    for session in session_indices:
        slots = lpu._slots_in_session(session, session_array)
        for slot, event in it.product(slots, event_indices):
            if events[event].tags != []:
                other_events = lpu._events_with_diff_tag(event, tag_array)
                for other_slot, other_event in it.product(slots, other_events):
                    if other_slot != slot and other_event != event:
                        # If they have different tags they cannot be scheduled
                        # together
                        yield Constraint(
                           f'{label} - event: {event}, slot: {slot}',
                           X[(event, slot)] + X[(other_event, other_slot)] <= 1
                        )


def _events_available_in_scheduled_slot(events, slots, X):
    """
    Constraint that ensures that an event is scheduled in slots for which it is
    available
    """
    slot_availability_array = lpu.slot_availability_array(slots=slots,
                                                          events=events)

    label = 'Event scheduled when not available'
    for row, event in enumerate(slot_availability_array):
        for col, availability in enumerate(event):
            if availability == 0:
                yield Constraint(
                    f'{label} - event: {row}, slot: {col}',
                    X[row, col] <= availability
                )


def _events_available_during_other_events(events, slots, X):
    """
    Constraint that ensures that an event is not scheduled at the same time as
    another event for which it is unavailable.
    """
    event_availability_array = lpu.event_availability_array(events)

    label = 'Event clashes with another event'
    for slot1, slot2 in lpu.concurrent_slots(slots):
        for row, event in enumerate(event_availability_array):
            if events[row].unavailability:
                for col, availability in enumerate(event):
                    if availability == 0:
                        yield Constraint(
                            f'{label} - event: {row} and event: {col}',
                            X[row, slot1] + X[col, slot2] <= 1 + availability
                        )


def all_constraints(events, slots, X, summation_type=None):
    kwargs = {
        'events': events,
        'slots': slots,
        'X': X
    }
    summation = {'summation_type': summation_type}
    generators = {
        _schedule_all_events: {**kwargs, **summation},
        _max_one_event_per_slot: {**kwargs, **summation},
        _events_in_session_share_a_tag: kwargs,
        _events_available_in_scheduled_slot: kwargs,
        _events_available_during_other_events: kwargs,
    }

    for generator, kwargs in generators.items():
        for constraint in generator(**kwargs):
            yield constraint
