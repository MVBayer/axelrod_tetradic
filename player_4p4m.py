"""
Player Base Class for Four-Player Four-Move Prisoner's Dilemma

This module implements the base player class and metaclass functionality for
the four-player variant of the Prisoner's Dilemma game. It provides core
player functionality including move history tracking, strategy execution,
and player state management.

Key Features:
    - Abstract base player class implementation
    - Move history tracking and analysis
    - Strategy execution framework
    - Player state management and cloning
    - Match attribute handling
    - Random seed management

Classes:
    PostInitCaller: Metaclass for handling post-initialization tasks
    Player_4p4m: Abstract base class for all player strategies

Example:
     class MyStrategy(Player_4p4m):
         name = "MyStrategy"
         def strategy(self, competitor, SC1, SC2):
             return W  # Always profiteer
     player = MyStrategy()
     player.strategy(None, None, None)
    <Action_4p4m.W: 0>

Note:
    All concrete strategy implementations should inherit from Player_4p4m
    and implement the strategy() method.

Author: Max Bayer
Date: July 2025
"""

# Standard library imports
import copy
import inspect
import itertools
import types
import warnings
from typing import Any, Dict
import random as random

# Third-party imports
import numpy as np

# Local imports
from action_4p4m import Action_4p4m 
from game_4p4m import TetradicPrisonersDilemmaGame
from history_4p4m import History_4p4m
import interaction_utils_4p4m as iu
import random_4p4m as random_4p4m


W, X, Y, Z = Action_4p4m.W, Action_4p4m.X, Action_4p4m.Y, Action_4p4m.Z



class PostInitCaller(type):
    """Metaclass to be able to handle post __init__ tasks.
    If there is a DerivedPlayer class of Player that overrides
    _post_init, as follows:

    class Player(object, metaclass=PostInitCaller):
        def __new__(cls, *args, **kwargs):
            print("Player.__new__")
            obj = super().__new__(cls)
            return obj

        def __init__(self):
            print("Player.__init__")

        def _post_init(self):
            print("Player._post_init")

        def _post_transform(self):
            print("Player._post_transform")


    class DerivedPlayer(Player):
        def __init__(self):
            print("DerivedPlayer.__init__")
            super().__init__()

        def _post_init(self):
            print("DerivedPlayer._post_init")
            super()._post_init()


    dp = DerivedPlayer()

    Then the call order is:
        * PostInitCaller.__call__
        * Player.__new__
        * DerivedPlayer.__init__
        * Player.__init__
        * DerivedPlayer._post_init
        * Player._post_init
        * Player._post_transform

    See here to learn more: https://blog.ionelmc.ro/2015/02/09/understanding-python-metaclasses/
    """

    def __call__(cls, *args, **kwargs):
        # This calls cls.__new__ and cls.__init__
        obj = type.__call__(cls, *args, **kwargs)
        # Next we do any post init or post transform tasks, like recomputing
        # classifiers
        # Note that subclasses inherit the metaclass, and subclasses my override
        # or extend __init__ so it's necessary to do these tasks after all the
        # __init__'s have run in the case of a post-transform reclassification.
        obj._post_init()
        obj._post_transform()
        return obj


class Player_4p4m(object, metaclass=PostInitCaller):
    """A class for a player in the tournament.

    This is an abstract base class, not intended to be used directly.
    """

    name = "Player"
    classifier = {}  # type: Dict[str, Any]
    _reclassifiers = []

    def __new__(cls, *args, **kwargs):
        """Caches arguments for Player cloning."""
        obj = super().__new__(cls)
        obj.init_kwargs = cls.init_params(*args, **kwargs)
        return obj

    @classmethod
    def init_params(cls, *args, **kwargs):
        """
        Return a dictionary containing the init parameters of a strategy
        (without 'self').
        Use *args and **kwargs as value if specified
        and complete the rest with the default values.
        """
        sig = inspect.signature(cls.__init__)
        # The 'self' parameter needs to be removed or the first *args will be
        # assigned to it
        self_param = sig.parameters.get("self")
        new_params = list(sig.parameters.values())
        new_params.remove(self_param)
        sig = sig.replace(parameters=new_params)
        boundargs = sig.bind_partial(*args, **kwargs)
        boundargs.apply_defaults()
        return boundargs.arguments

    def __init__(self):
        """Initial class setup."""
        self._history = History_4p4m()
        self.classifier = copy.deepcopy(self.classifier)
        self.set_match_attributes()

    def _post_init(self):
        """Post initialization tasks such as reclassifying the strategy."""
        pass

    def _post_transform(self):
        """Handles post transform tasks such as further reclassifying."""
        # Reclassify strategy post __init__, if needed.
        for reclassifier, args, kwargs in self._reclassifiers:
            self.classifier = reclassifier(self.classifier, *args, **kwargs)

    def __eq__(self, other):
        """
        Test if two players are equal, ignoring random seed and RNG state.
        """
        if self.__repr__() != other.__repr__():
            return False

        for attribute in set(
            list(self.__dict__.keys()) + list(other.__dict__.keys())
        ):

            value = getattr(self, attribute, None)
            other_value = getattr(other, attribute, None)

            if attribute in ["_random", "_seed"]:
                # Don't compare the random generators.
                continue

            if isinstance(value, np.ndarray):
                if not (np.array_equal(value, other_value)):
                    return False

            elif isinstance(value, types.GeneratorType) or isinstance(
                value, itertools.cycle
            ):
                # Split the original generator so it is not touched
                generator, original_value = itertools.tee(value)
                other_generator, original_other_value = itertools.tee(
                    other_value
                )

                if isinstance(value, types.GeneratorType):
                    setattr(self, attribute, (ele for ele in original_value))
                    setattr(
                        other, attribute, (ele for ele in original_other_value)
                    )
                else:
                    setattr(self, attribute, itertools.cycle(original_value))
                    setattr(
                        other, attribute, itertools.cycle(original_other_value)
                    )

                for _ in range(200):
                    try:
                        if next(generator) != next(other_generator):
                            return False
                    except StopIteration:
                        break

            # Code for a strange edge case where each strategy points at each
            # other
            elif value is other and other_value is self:
                pass
            else:
                if value != other_value:
                    return False
        return True

    def receive_match_attributes(self):
        # Overwrite this function if your strategy needs
        # to make use of match_attributes such as
        # the game matrix, the number of rounds or the noise
        pass

    def set_match_attributes(self, length=-1, game=None, noise=0):
        if not game:
            game = TetradicPrisonersDilemmaGame()
        self.match_attributes = {"length": length, "game": game, "noise": noise}
        self.receive_match_attributes()

    def set_seed(self, seed):
        """Set a random seed for the player's random number generator."""
        if seed is None:
            warnings.warn(
                "Initializing player with seed from Axelrod module random number generator. "
                "Results may not be seed reproducible."
            )
            self._seed = random_4p4m.random_seed_int()
        else:
            self._seed = seed
        self._random = random_4p4m.RandomGenerator_4p4m(seed=self._seed)

    def __repr__(self):
        """The string method for the strategy.
        Appends the `__init__` parameters to the strategy's name."""
        name = self.name
        
        """ 
        prefix = ": "
        gen = (
            value for value in self.init_kwargs.values() if value is not None
        )
        for value in gen:
            try:
                if issubclass(value, Player_4p4m):
                    value = value.name
            except TypeError:
                pass
            name = "".join([name, prefix, str(value)])
            prefix = ", "
        """
        return name

    def __getstate__(self):
        """Used for pickling. Override if Player contains unpickleable attributes."""
        return self.__dict__

    def strategy(self, competitor, SC1, SC2):
        """This is a placeholder strategy."""
        raise NotImplementedError()

    def clone(self):
        """Clones the player without history, reapplying configuration
        parameters as necessary."""

        # You may be tempted to re-implement using the `copy` module
        # Note that this would require a deepcopy in some cases and there may
        # be significant changes required throughout the library.
        # Consider overriding in special cases only if necessary
        cls = self.__class__
        new_player = cls(**self.init_kwargs)
        new_player.match_attributes = copy.copy(self.match_attributes)
        return new_player

    def reset(self):
        """Resets a player to its initial state

        This method is called at the beginning of each match (between a pair
        of players) to reset a player's state to its initial starting point.
        It ensures that no 'memory' of previous matches is carried forward.
        """
        # This also resets the history.
        self.__init__(**self.init_kwargs)

    def update_history(self, play, competitor_plays, SC1_plays, SC2_plays):
        self.history.append(play, competitor_plays, SC1_plays, SC2_plays)

    @property
    def history(self):
        return self._history

    # Properties maintained for legacy API, can refactor to self.history.X
    # in 5.0.0 to reduce function call overhead.
    @property
    def invest_none(self):
        return self._history.profiteering

    @property
    def invest_both_sc(self):
        return self._history.competing

    @property
    def invest_SC1(self):
        return self._history.invest_SC1

    @property
    def invest_SC2(self):
        return self._history.invest_SC2
        
    @property
    def state_distribution(self):
        return self._history.state_distribution


