"""
Game Module for Four-Player Four-Strategy Prisoner's Dilemma

This module implements the game logic for a four-player variant of the Prisoner's 
Dilemma game with four possible strategies. It provides scoring functionality
and game state management.

Informally: because the game states are more complex in a tetradic game,
the scoring logic is separated and can be adjusted in the scoring_dict_4p4m.py file.
This leaves the game_4p4m.py file rather limited but conceptually it is helpful to 
distinguish games, matches, and tournaments even if calculations are done elsewhere.

Key Features:
- Four-player interactions
- Four distinct strategies (W, X, Y, Z)
- Flexible scoring system using dictionary lookup
- Type hints and input validation

Classes:
    TetradicPrisonersDilemmaGame: Main class handling game mechanics and scoring

Example:
    game = TetradicPrisonersDilemmaGame()
    scores = game.score_4p4m((W, X, Y, Z))
    # Returns tuple of scores for all four players

Author: Max Bayer
Date: July 2025
"""

# Standard library imports
#from enum import Enum
from typing import Tuple, Union

# Third-party imports
import numpy as np

# Local imports
import scoring_dict_4p4m as scD
from action_4p4m import Action_4p4m 

# Game actions
W, X, Y, Z = Action_4p4m.W, Action_4p4m.X, Action_4p4m.Y, Action_4p4m.Z

# Type aliases
Score = Union[int, float]




class TetradicPrisonersDilemmaGame(object):
    """Container for the game matrix and scoring logic.

    Attributes
    ----------
    scores: dict
        The numerical score attribute to all combinations of action pairs.
    """
    
    
    

    def __init__(self, scoring_dictionary =scD.payoff_dictionary_4p4m_WXYZ) -> None:
        self.scoring_dictionary = scoring_dictionary
                
    def score_4p4m(self, interaction: Union[Tuple[Action_4p4m, Action_4p4m, Action_4p4m, Action_4p4m], Tuple[int,int,int,int]]) -> Tuple[Score, Score, Score, Score]:
        """Returns the appropriate score for a 4-player interaction.
        
        Parameters
        ----------
        interaction: tuple(int, int, int, int) or tuple(Action, Action, Action, Action)
            The actions chosen by the four players. Can be specified either as:
            - Action_4p4m enum values (W, X, Y, Z)
            - Integers (0, 1, 2, 3) corresponding to (W, X, Y, Z)

        Returns
        -------
        tuple of int or float
            Scores for four players resulting from their actions.
        """

        # Convert integers to Action_4p4m if needed
        def to_action(x):
            if isinstance(x, int):
                return Action_4p4m(x)  # Converts 0->W, 1->X, etc.
            return x

        decisions = tuple(to_action(x) for x in interaction)
        return self.scoring_dictionary.get(decisions)
    
        


        