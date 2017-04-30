from typing import NamedTuple, Sequence
import pulp


class Shape(NamedTuple):
    events: int
    rooms: int
    slots: int


def variables(events: Sequence, rooms: Sequence, slots: Sequence):
    """Defines the required instances of pulp.LpVariable

    Parameters
    ----------
    events : List or Tuple
        of resources.Event
    rooms : List or Tuple
        of resources.Room
    slots : List or Tuple
        of resources.Slot

    Returns
    -------
    dict
        mapping a tuple of event index, room index and slot index to an
        instance of pulp.LpVariable.
    """
    variables = {
        (events.index(event), rooms.index(room), slots.index(slot)):
        pulp.LpVariable(
            f'{event.name}_{room.name}_slot_{slots.index(slot)}',
            cat='Binary'
        )
        for event in events for room in rooms for slot in slots
    }
    return variables


def _max_one_event_per_room_per_slot(variables, dimensions):
    # A room may only have a maximum of one event scheduled in any time slot
    return [
        sum(
            variables[(event_idx, room_idx, slot_idx)]
            for event_idx in range(dimensions.events)
        ) <= 1
        for room_idx in range(dimensions.rooms)
        for slot_idx in range(dimensions.slots)
    ]


def _only_once_per_event(variables, dimensions):
    # An event may only be scheduled in one combination of room and time slot
    return [
        sum(
            variables[(event_idx, room_idx, slot_idx)]
            for room_idx in range(dimensions.rooms)
            for slot_idx in range(dimensions.slots)
        ) == 1
        for event_idx in range(dimensions.events)
    ]


def _is_suitable_room(event, room):
    return event.event_type in room.suitability


def _room_suitability(variables, dimensions, events, rooms):
    # A room may only be scheduled to host an event for which it is deemed
    # suitable
    return [
        sum(
            variables[(events.index(event), rooms.index(room), slot_idx)]
            for slot_idx in range(dimensions.slots)
        ) == 0
        for room in rooms for event in events
        if not _is_suitable_room(event, room)
    ]


def constraints(variables, events, rooms, slots):
    dimensions = Shape(len(events), len(rooms), len(slots))
    constraints = []
    constraints.extend(_max_one_event_per_room_per_slot(variables, dimensions))
    constraints.extend(_only_once_per_event(variables, dimensions))
    constraints.extend(_room_suitability(variables, dimensions, events, rooms))

    return constraints
