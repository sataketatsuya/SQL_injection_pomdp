from typing import Mapping, Any


class Agent:
    """ Interface for any agent playing TextWorld games. """
    def act(self, obs: str, score: int, done: bool, infos: Mapping[str, Any]) -> str:
        """
        Acts upon the current list of observations.

        One text command must be returned for each observation.

        Arguments:
            obs: Previous command's feedback (game's narrative).
            score: The score obtained so far.
            done: Whether the game is finished.
            infos: Additional information requested.

        Returns:
            Text command to be performed.
            If episode has ended (i.e. `done` is `True`), the returned
            value is expected to be ignored.
        """
        raise NotImplementedError()
