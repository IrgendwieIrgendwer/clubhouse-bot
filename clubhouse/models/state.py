import enum


class State(enum.Enum):
    INITIAL = 0
    QUEUED = 1
    MATCHED = 2
    DONE = 3
    ABORTED = 4

    @staticmethod
    def completed(user):
        return user.state in [State.DONE, State.ABORTED]
