"""
Random Number Generation for Four-Player Four-Move Prisoner's Dilemma

This module provides random number generation functionality specifically designed
for the four-player variant of the Prisoner's Dilemma game. It ensures
reproducibility across matches and tournaments while maintaining efficiency.

Key Features:
    - Reproducible random number generation
    - Bulk generation for tournament seeding
    - Probability distribution handling
    - Action randomization with custom probabilities
    - Efficient batch processing

Classes:
    RandomGenerator_4p4m: Core random number generator
    BulkRandomGenerator_4p4m: Efficient bulk random number generation
    Pdf: Probability distribution management

Example:
     rng = RandomGenerator_4p4m(seed=42)
     action = rng.random_choice(p_w=0.5, p_x=0.2, p_y=0.2)
     print(action)
    <Action_4p4m.W: 0>

Note:
    Uses numpy.random.RandomState for core functionality to ensure
    cross-platform reproducibility.

Author: Max Bayer
Date: July 2025
"""

# Standard library imports
from typing import Optional
import random

# Third-party imports
import numpy as np
from numpy.random import RandomState

# Local imports
from action_4p4m import Action_4p4m, str_to_actions, actions_to_str

W, X, Y, Z = Action_4p4m.W, Action_4p4m.X, Action_4p4m.Y, Action_4p4m.Z



class RandomGenerator_4p4m(object):
    """
    Core random number generator for game operations.
    
    Provides reproducible random number generation for player actions,
    match outcomes, and tournament operations.
    
    Attributes:
        original_seed (Optional[int]): Initial seed value
        _random (RandomState): Internal numpy random state object
        
    Example:
         rng = RandomGenerator_4p4m(seed=42)
         print(rng.random_choice())
        <Action_4p4m.W: 0>
    """

    def __init__(self, seed: Optional[int] = None):
        # _random is the internal object that generators random values
        self._random = RandomState()
        self.original_seed = seed
        self.seed(seed)

    def seed(self, seed_: Optional[int] = None):
        """Sets a seed"""
        self._random.seed(seed_)

    def random(self, *args, **kwargs):
        return self._random.rand(*args, **kwargs)

    def randint(self, *args, **kwargs):
        return self._random.randint(*args, **kwargs)

    def random_seed_int(self) -> int:
        return self.randint(low=0, high=2**32 - 1, dtype="uint64")

    def choice(self, *args, **kwargs):
        return self._random.choice(*args, **kwargs)

    def uniform(self, *args, **kwargs):
        return self._random.uniform(*args, **kwargs)

    def random_choice(self, p_w: float = 0.25, p_x: float = 0.25, p_y: float = 0.25) -> Action_4p4m:
        """
        Return a random action based on specified probabilities.
        
        Args:
            p_w: Probability of selecting W (default: 0.25)
            p_x: Probability of selecting X (default: 0.25)
            p_y: Probability of selecting Y (default: 0.25)
            
        Returns:
            Randomly selected action based on probabilities
            
        Note:
            p_z is automatically calculated as 1 - (p_w + p_x + p_y)
        """
        if p_w == 1:
            return W
        if p_x == 1:
            return X
        if p_y == 1:
            return Y
        if p_w == 0 and  p_x == 0  and  p_y == 0:
            return Z


        random_value = self.random()
        if random_value <= p_w:
            return W
        elif random_value > p_w and random_value <= (p_w + p_x):
            return X
        elif random_value > p_x and random_value <= (p_x + p_y):
            return Y
        elif random_value > p_y:
            return Z


    
    def random_flip(self, action: Action_4p4m, threshold:float) -> Action_4p4m:
        #original comment
        """
        Return flipped action with probability `threshold`

        No random sample is carried out if threshold is 0 or 1.

        Parameters
        ----------
        action:
            The action to flip or not
        threshold : float
            The probability of flipping action

        Returns
        -------
        axelrod.Action
        """
        random_value = random.random()
        if random_value <= threshold:
            return action.flip()
        return action
        

    def randrange(self, a: int, b: int) -> int:
        """Returns a random integer uniformly between a and b: [a, b)."""
        c = b - a
        r = c * self.random()
        return a + int(r)

    def random_vector(self, size):
        """Create a random vector of values in [0, 1] that sums to 1."""
        vector = self.random(size)
        return np.array(vector) / np.sum(vector)


class Pdf(object):
    """A class for a probability distribution"""

    def __init__(self, counter, seed=None):
        """Take as an instance of collections.counter"""
        self.sample_space, self.counts = zip(*counter.items())
        self.size = len(self.sample_space)
        self.total = sum(self.counts)
        self.probability = list([v / self.total for v in self.counts])
        self._random = RandomGenerator_4p4m(seed=seed)

    def sample(self):
        """Sample from the pdf"""
        index = self._random.choice(a=range(self.size), p=self.probability)
        # Numpy cannot sample from a list of n dimensional objects for n > 1,
        # need to sample an index.
        return self.sample_space[index]


class BulkRandomGenerator_4p4m(object):
    """Bulk generator of random integers for tournament seeding and
    reproducibility. Bulk generation of random values is more efficient.
    Use this class like a generator."""

    def __init__(self, seed=None, batch_size: int = 1000):
        self._random_generator = RandomState()
        self._random_generator.seed(seed)
        self._ints = None
        self._batch_size = batch_size
        self._index = 0
        self._fill_ints()

    def _fill_ints(self):
        # Generate more random values. Store as a list since generators
        # cannot be pickled.
        self._ints = self._random_generator.randint(
            low=0, high=2**32 - 1, size=self._batch_size, dtype="uint64"
        )
        self._index = 0

    def __next__(self):
        try:
            x = self._ints[self._index]
        except IndexError:
            self._fill_ints()
            x = self._ints[self._index]
        self._index += 1
        return x
