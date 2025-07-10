"""
Action Module for a tetradic generalization of a Prisoner's Dilemma studied with Axelrod tournaments.

This module defines the Action_4p4m class which implements the possible actions
in a 4-player game: no investment (W), invest in SC1 (X), invest in SC2 (Y), and invest in both SC1 and SC2 (Z).
It provides functionality for action comparison, string conversion, and random action selection.

Author: Max Bayer
Date: July 2025    
"""

# Standard library imports
import random
from enum import Enum
from functools import total_ordering
from typing import Iterable, Tuple



class UnknownActionError(ValueError):
    """Error indicating an unknown action was used."""

    def __init__(self, *args):
        super(UnknownActionError, self).__init__(*args)


@total_ordering
class Action_4p4m(Enum):
    """Actions for 4-Player Game."""
    W = 0  # no investment
    X = 1  # invest in SC1
    Y = 2  # invest in SC2
    Z = 3  # invest in both SC1 and SC2
    
    def __lt__(self, other):
        return self.value < other.value

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    def flip(self):
        # returns a random action which is not the original action.
        random_value = random.random()
        
        #if the original action is W, one of the other three is randomly chosen.
        if self == Action_4p4m.W: 
            if random_value <= 1/3:
                return Action_4p4m.X
                random_value = 0
            elif random_value > 1/3 and random_value <= 2/3:
                return Action_4p4m.Y
                random_value = 0
            elif random_value > 2/3: 
                return Action_4p4m.Z
                random_value = 0
        
        elif self == Action_4p4m.X:
            if random_value <= 1/3:
                return Action_4p4m.Y
                random_value = 0
            elif random_value > 1/3 and random_value <= 2/3:
                return Action_4p4m.Z
                random_value = 0
            elif random_value > 2/3: 
                return Action_4p4m.W
                random_value = 0

        elif self == Action_4p4m.Y:
            if random_value <= 1/3:
                return Action_4p4m.Z
                random_value = 0
            elif random_value > 1/3 and random_value <= 2/3:
                return Action_4p4m.W
                random_value = 0
            elif random_value > 2/3: 
                return Action_4p4m.X
                random_value = 0

        elif self == Action_4p4m.Z:
            if random_value <= 1/3:
                return Action_4p4m.W
                random_value = 0
            elif random_value > 1/3 and random_value <= 2/3:
                return Action_4p4m.X
                random_value = 0
            elif random_value > 2/3: 
                return Action_4p4m.Y
                random_value = 0
    
    """
        #Cycles one step through the actions.
        #mvb: dno if i even need it but good to remember for cleaner code
    def rotate(self):
        
        
        
        rotations = {
            Action_4p4m.W: Action_4p4m.X,
            Action_4p4m.X: Action_4p4m.Y,
            Action_4p4m.Y: Action_4p4m.Z,
            Action_4p4m.Z: Action_4p4m.W
        }
        return rotations[self]
    """
    
    @classmethod
    def from_char(cls, character):
        """Converts a single character into an Action.

        Parameters
        ----------
        character: a string of length one

        Returns
        -------
        Action
            The action corresponding to the input character


        Raises
        ------
        UnknownActionError
            If the input string is not 'W's, 'X's, 'Y's, and 'Z's
        """
        if character == "W":
            return cls.W
        if character == "X":
            return cls.X
        if character == "Y":
            return cls.Y
        if character == "Z":
            return cls.Z
        raise UnknownActionError('Character must be "W", "X", "Y" or "Z".')


def str_to_actions(actions: str) -> Tuple[Action_4p4m, ...]:
    """Converts a string to a tuple of actions.

    Parameters
    ----------
    actions: A string of 'W's, 'X's, 'Y's, and 'Z's

    Returns
    -------
    tuple
        Each element corresponds to a letter from the input string.
    """
    return tuple(Action_4p4m.from_char(element) for element in actions)


def actions_to_str(actions: Iterable[Action_4p4m]) -> str:
    """Converts an iterable of actions into a string.

    Example: (W, W, X) would be converted to 'WWX'

    Parameters
    -----------
    actions: iterable of Action

    Returns
    -------
    str
        A string of 'W's, 'X's, 'Y's, and 'Z's
    """
    return "".join(map(str, actions))

    








