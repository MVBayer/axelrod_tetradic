"""
Match Generator for Four-Player Four-Move Prisoner's Dilemma

This module provides functionality for generating and managing match configurations
in a four-player variant of the Prisoner's Dilemma game. It handles tournament
pairings, match parameter management, and random seed distribution.

Key Features:
    - Round-robin tournament pairing generation
    - Complete and partial graph tournament structures
    - Match parameter management
    - Bulk random number generation for reproducibility
    - Support for match repetitions and noise

Classes:
    MatchGenerator_4p4m: Main class for generating tournament matches

Functions:
    complete_graph_4p4m: Generates all possible player combinations
    partial_graph_4p4m: Generates reduced set of combinations using symmetries

Example:
     players = [Player1(), Player2(), Player3(), Player4()]
     generator = MatchGenerator_4p4m(
         players=players,
         repetitions=3,
         turns=100,
         noise=0.1
     )
     for indices, params, reps, seed in generator.build_match_chunks():
         # Create and run match with these parameters
         pass

Author: Max Bayer
Date: July 2025
"""
# Standard library imports
import itertools
from typing import List, Dict, Tuple, Generator, Optional

# Local imports
from random_4p4m import BulkRandomGenerator_4p4m



class MatchGenerator_4p4m(object):
    """
    Generates match configurations for four-player tournament execution.
    
    Handles the creation of player combinations, match parameters, and random
    seed distribution for tournament matches.

    Attributes:
        players (List[Player]): List of players in the tournament
        repetitions (int): Number of times each match should be repeated
        turns (Optional[int]): Number of turns per match
        game (Optional[Game]): Game instance for scoring
        noise (float): Probability of move mutation
        prob_end (Optional[float]): Probability of early match termination
        edges (Optional[List[Tuple]]): Specific player combinations to use
        match_attributes (Optional[Dict]): Additional attributes for matches
        size (int): Total number of matches to be generated
    """
        
    def __init__(
        self,
        players,
        repetitions,
        turns=None,
        game=None,
        noise=0,
        prob_end=None,
        edges=None,
        match_attributes=None,
        seed=None,
    ):

        self.players = players
        self.turns = turns
        self.game = game
        self.repetitions = repetitions
        self.noise = noise
        self.competitors = players #originally "opponents"
        self.SC1 = players
        self.SC2 =players
        self.prob_end = prob_end
        self.match_attributes = match_attributes
        self.random_generator = BulkRandomGenerator_4p4m(seed)

        self.edges = edges #4p4m: i always play round-robin tournaments.
        
        n = len(self.players)
        self.size = int(n * (n - 1) // 2 + n) #4p4m: this should be fine with more players. test

    def __len__(self):
        return self.size

    def build_match_chunks(self) -> Generator[Tuple, None, None]:
        """
        Generate player combinations and match parameters for tournament.

        Yields tuples containing:
            - Player indices tuple (p1, p2, p3, p4)
            - Match parameters dictionary
            - Number of repetitions
            - Random seed for the match

        Note:
            Uses complete_graph_4p4m by default, or specified edges if provided
        """
        if self.edges is None:
            edges = complete_graph_4p4m(self.players)
        else:
            edges = self.edges
        
        for index_tuple in edges:
            match_params = self.build_single_match_params()
            r = next(self.random_generator)
            yield (index_tuple, match_params, self.repetitions, r)

    def build_single_match_params(self):
        """
        Creates a single set of match parameters.
        """
        return {
            "turns": self.turns,
            "game": self.game,
            "noise": self.noise,
            "prob_end": self.prob_end,
            "match_attributes": self.match_attributes,
        }


def complete_graph_4p4m(players):
    """
    Generate all possible four-player combinations.

    Args:
        players: List of available players

    Yields:
        Tuples of four player indices representing unique combinations
        
    Note:
        Generates n^4 combinations for n players (full Cartesian product)
    """
    player_indices_rr =[]
    player_indices_rr = complete_graph_edges_4p4m(players)
    for i in player_indices_rr:
        yield(i)
        
    

def complete_graph_edges_4p4m(players):
    player_index_iterable = list(range(len(players)))
    player_indices = [p for p in itertools.product(player_index_iterable, repeat=4)]

    return player_indices



def partial_graph_4p4m(players: List) -> Generator[Tuple[int, int, int, int], None, None]:
    """
    Generate reduced set of player combinations using game symmetries.

    Args:
        players: List of available players

    Yields:
        Tuples of four player indices representing unique combinations
        
    Note:
        Reduces computation by exploiting game symmetries
        For 15 players: 14,400 matches vs 50,625 in complete graph
    """
    player_indices_rr =[]
    player_indices_rr = partial_graph_edges(players)
    for i in player_indices_rr:
        yield(i)
        
    

def partial_graph_edges(players):
    """
    Partial graph exploiting symmetries in order to not compute redundant matches. 
    Works for my purposes if I want to save computation time here. 
    Would need to adapt analytics to this, though.

    e.g. for 15 players, complete graph would generate 15^4 = 50,625 matches
    for partial graph it is only 14400. I do not currently have the formula present.
    """
    
    player_index_iterable = list(range(len(players)))
    combinations_2players = [list(p) for p in itertools.combinations_with_replacement(player_index_iterable, 2)]

    player_indices = []
    for i in combinations_2players:
        for j in combinations_2players:
            player_indices.append(tuple(i+j))
    return player_indices