from transitions import Machine

from common_lib.errors import BlinkConflictError


class BaseMachine:
    TRANSITIONS = []
    STATES = []

    # Not all models use "status" all the time  as their model column name to keep track of their internal statuses.
    # Some models may have a different name. status_field exists in order to use custom status field name.
    status_field = "status"

    def after_state_change(self):
        """
        Called after each state change to update the state of the machine on the model.
        """
        setattr(self.django_model, self.status_field, self.state)

    def __init__(self, django_model):
        self.django_model = django_model
        self.machine = Machine(
            model=self,
            states=self.STATES,
            transitions=self.TRANSITIONS,
            initial=getattr(self.django_model, self.status_field, None),
            after_state_change="after_state_change",
        )

    def can_transition(self, transition):
        """
        Returns True if order in its current state can execute the given transition

        IMPORTANT, this does not check any conditions from a trigger
        """
        status = getattr(self.django_model, self.status_field, None)
        if transition in self.machine.get_triggers(status):
            return True
        return False

    def has_transitioned(self, *transitions):
        """Returns True if the order is already in the destination state of ANY of the specified transitions"""
        status = getattr(self.django_model, self.status_field, None)
        return any(self.machine.get_transitions(t, dest=status) for t in transitions)

    def validate_transition(self, *transitions, error_type: type = BlinkConflictError):
        """
        Raises an RxValidationError if NONE of the transitions are valid, otherwise returns None

        IMPORTANT, this does not check any conditions from a trigger
        :param transitions: The name(s) of the trigger(s)
        :param error_type: The type of error class raised if the trigger is invalid
        """
        if not any(self.can_transition(t) for t in transitions):
            raise error_type(f"Transition(s) '{transitions}' not valid for status '{self.status_field}'")
