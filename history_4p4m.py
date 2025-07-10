"""
History Module for Four-Player Four-Move Prisoner's Dilemma

This module implements a history tracking system for a four-player variant of the
Prisoner's Dilemma game. It maintains records of player actions, game states,
and provides statistical analysis of gameplay patterns.

Key Features:
- Tracks actions for all four players independently
- Maintains state distribution statistics
- Supports history manipulation (copying, flipping)
- Provides action counting and analysis
- Compatible with the Action_4p4m enumeration system

Classes:
    History_4p4m: Main class for tracking game history and statistics

Example:
    history = History_4p4m()
    history.append(W, X, Y, Z)  # Record one round of play
    print(f"Profiteering moves: {history.profiteering}")

Author: Max Bayer
Date: July 2025
"""

# Standard library imports
from collections import Counter

# Local imports
from action_4p4m import Action_4p4m, actions_to_str 

W, X, Y, Z = Action_4p4m.W, Action_4p4m.X, Action_4p4m.Y, Action_4p4m.Z



class History_4p4m(object):
    """
    Tracks and analyzes the history of play in a four-player game.

    This class maintains a complete record of all player actions and provides
    statistical analysis of gameplay patterns. It tracks actions for the main
    player, their competitor, and two strategic companions (SC1 and SC2).

    Attributes:
        _plays (list): Sequential actions of the main player
        _competitor_plays (list): Sequential actions of the competitor
        _SC1_plays (list): Sequential actions of strategic companion 1
        _SC2_plays (list): Sequential actions of strategic companion 2
        _actions (Counter): Count of each action type by main player
        _state_distribution (Counter): Distribution of game states

    Note:
        All actions are represented using the Action_4p4m enumeration
        (W, X, Y, Z) representing different strategic choices.
    """


    
    def __init__(self, plays=None, competitor_plays=None,SC1_plays=None, SC2_plays=None):
        """
        Parameters
        ----------
        plays:
            An ordered iterable of the actions of the player.
        (originally: "coplays" for actions of the coplayer (aka opponent).)
        
        competitor_plays
        SC1
        SC2
        
        """
        # manually adapt number_of_players
        
        self._plays = []
        # Coplays is tracked mainly for computation of the state distribution
        # when cloning or dualing.
        # 4p4m>>> ignore coplays if i can
        self._competitor_plays = []
        self._SC1_plays = []
        self._SC2_plays = []
        self._actions = Counter()
        self._state_distribution = Counter()
        if plays:
            self.extend(plays, competitor_plays, SC1_plays, SC2_plays) #i dno if i want "list" structure here

    def append(self, play, competitor_coplay, SC1_coplay, SC2_coplay): 
        """
        Records one round of play from all four players.

        Updates internal statistics including action counts and state distribution.

        Args:
            play (Action_4p4m): Main player's action
            competitor_coplay (Action_4p4m): Competitor's action
            SC1_coplay (Action_4p4m): Strategic companion 1's action
            SC2_coplay (Action_4p4m): Strategic companion 2's action
        """
        # manually adapt number_of_players
        
        self._plays.append(play)
        self._actions[play] += 1
        self._competitor_plays.append(competitor_coplay)
        self._SC1_plays.append(SC1_coplay)
        self._SC2_plays.append(SC2_coplay)
        self._state_distribution[(play, competitor_coplay,SC1_coplay,SC2_coplay)] += 1

    def copy(self):
        """Returns a new object with the same data."""
        return self.__class__(plays=self._plays, competitor_plays=self._competitor_plays, SC1_plays=self._SC1_plays, SC2_plays=self._SC2_plays)

    def flip_plays(self):
        """Creates a flipped plays history for use with DualTransformer."""
        flipped_plays = [action.flip() for action in self._plays]
        return self.__class__(plays=flipped_plays, competitor_plays=self._competitor_plays, SC1_plays=self._SC1_plays, SC2_plays=self._SC2_plays)

    def extend(self, plays, competitor_plays, SC1_plays, SC2_plays):
        """A function that emulates list.extend."""
        # axl: We could repeatedly call self.append but this is more efficient.
        # manually adapt number_of_players
        self._plays.extend(plays)
        self._actions.update(plays)
        self._competitor_plays.extend(competitor_plays)
        self._SC1_plays.extend(SC1_plays)
        self._SC2_plays.extend(SC2_plays)
        self._state_distribution.update(zip(plays, competitor_plays, SC1_plays, SC2_plays))
    
    def reset(self):
        """Clears all data in the History object."""
        self._plays.clear()
        self._competitor_plays.clear()
        self._SC1_plays.clear()
        self._SC2_plays.clear()
        self._actions.clear()
        self._state_distribution.clear()

    # manually adapt number_of_players in following

    @property
    def competitor_plays(self): 
        return self._competitor_plays
   
    @property
    def SC1_plays(self): 
        return self._SC1_plays

    @property
    def SC2_plays(self): 
        return self._SC2_plays
    
    @property
    def profiteering(self): #4p4m: to access properties, do not call with brackets >> history1.cooperations() is false
        """
        Count of profiteering moves (W) made by the main player.
        
        Returns:
            int: Number of times W was played
        """
        return self._actions[W]

    @property
    def competing(self):
        return self._actions[Z]

    @property
    def invest_SC1(self):
        return self._actions[X]

    @property
    def invest_SC2(self):
        return self._actions[Y]
    
    @property
    def state_distribution(self):
        return self._state_distribution
        
    def __getitem__(self, key):
        # Passthrough keys and slice objects
        return self._plays[key]

    def __str__(self):
        return actions_to_str(self._plays)

    def __list__(self):
        return self._plays

    def __len__(self):
        return len(self._plays)

    def __repr__(self):
        return repr(self.__list__())

