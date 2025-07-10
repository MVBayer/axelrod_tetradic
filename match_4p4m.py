"""
Four-Player Four-Move Prisoner's Dilemma Match Implementation

This module implements the match mechanics for a four-player variant of the
Prisoner's Dilemma game. It handles player interactions, move processing,
scoring, and statistical analysis of game outcomes.

Key Features:
    - Supports four-player simultaneous moves
    - Handles both deterministic and stochastic strategies
    - Provides noise implementation
    - Calculates various statistics (scores, move distributions)
    - Supports finite and infinite length matches
    - Implements random seed management for reproducibility

Classes:
    Match_4p4m: Main class for conducting matches between four players

Example:
    match = Match_4p4m([player1, player2, player3, player4], turns=10)
    match.play()
    print(f"Final scores: {match.final_score()}")

Note:
    This is an extension of the original Axelrod library's Match class,
    modified to support four-player interactions with WXYZ moves instead
    of the traditional two-player CD format.

Author: Max Bayer
Date: July 2025
"""

# Standard library imports
from math import ceil, log
from typing import List, Tuple, Optional, Union, Counter

# Third-party imports


# Local imports
from action_4p4m import Action_4p4m 
import interaction_utils_4p4m as iu_4p4m
from game_4p4m import TetradicPrisonersDilemmaGame
from random_4p4m import RandomGenerator_4p4m

W, X, Y, Z = Action_4p4m.W, Action_4p4m.X, Action_4p4m.Y, Action_4p4m.Z
DEFAULT_TURNS = 100  # Default number of turns in a match



class Match_4p4m(object):
    """
    Manages a match between four players in a four-move Prisoner's Dilemma game.

    This class handles the execution of a multi-player game where each player can choose
    from four possible moves (W, X, Y, Z). It supports both deterministic and stochastic
    strategies, implements noise, and tracks game statistics.

    Attributes:
        players (List[Player]): List of four player objects
        turns (int): Number of turns in the match (default: 100)
        prob_end (float): Probability of game ending after each turn
        game (TetradicPrisonersDilemmaGame): Game instance for scoring
        noise (float): Probability of random move changes (0-1)
        result (List[Tuple]): History of all plays in the match
        seed (Optional[int]): Random seed for reproducibility

    Example:
         from action_4p4m import Action_4p4m
         p1, p2, p3, p4 = Player(), Player(), Player(), Player()
         match = Match_4p4m(
             players=[p1, p2, p3, p4],
             turns=10,
             noise=0.1
         )
         match.play()
         print(match.final_score())
        (320, 280, 290, 310)

    Note:
        - Players must implement strategy() and update_history() methods
        - Noise affects all players independently
        - Setting prob_end creates matches of variable length
    """
    def __init__(
        self,
        players,
        turns=None,
        prob_end=None,
        game=None,
        #deterministic_cache=None,
        noise=0,
        match_attributes=None,
        reset=True,
        seed=None,
    ):
    
        defaults = {
            (True, True): (DEFAULT_TURNS, 0),
            (True, False): (float("inf"), prob_end),
            (False, True): (turns, 0),
            (False, False): (turns, prob_end),
        }
        self.turns, self.prob_end = defaults[(turns is None, prob_end is None)]

        self.result = []
        self.noise = noise

        self.set_seed(seed)

        if game is None:
            self.game = TetradicPrisonersDilemmaGame()
        else:
            self.game = game

        ### 4p4m: first do it easier without Chache
        #if deterministic_cache is None:
        #    self._cache = DeterministicCache()
        #else:
        #    self._cache = deterministic_cache

        if match_attributes is None:
            known_turns = self.turns if prob_end is None else float("inf")
            self.match_attributes = {
                "length": known_turns,
                "game": self.game,
                "noise": self.noise,
            }
        else:
            self.match_attributes = match_attributes

        self.players = list(players)
        self.reset = reset

    def set_seed(self, seed):
        """Sets a random seed for the Match, for reproducibility. Initializes
        a match-wide RNG instance which is used to propagate seeds to the Players
        and to generate random values for noise. Seeds are only set for stochastic players.
        Any seeds set on Players before being passed to Match will be overwritten.
        However, Evolvable Players may have already used their seeds to initialize
        their parameters, if underspecified.
        """
        self.seed = seed
        self._random = RandomGenerator_4p4m(seed=self.seed)

    @property
    def players(self):
        return self._players

    @players.setter
    def players(self, players):
        """Ensure that players are passed the match attributes"""
        newplayers = []
        for player in players:
            player.set_match_attributes(**self.match_attributes)
            newplayers.append(player)
        self._players = newplayers

    def simultaneous_play(self, player, competitor, SC1, SC2, noise=0):
        """
        Execute one turn of simultaneous play between four players.
        
        Gets moves from all players, applies noise if specified, and updates
        player histories with the moves made.
        
        Args:
            player: First player object
            competitor: Second player object
            SC1: First strategic companion
            SC2: Second strategic companion
            noise: Probability of random move changes
            
        Returns:
            Tuple of four moves (player, competitor, SC1, SC2)
        """        
        s1, s2  = player.strategy(competitor, SC1, SC2), competitor.strategy(player, SC2, SC1) 
        s3, s4 = SC1.strategy(SC2, player, competitor), SC2.strategy(SC1, competitor, player)
        if noise:
            # Note this uses the Match classes random generator, not either
            # player's random generator. A player shouldn't be able to
            # predict the outcome of this noise flip.
            s1 = self._random.random_flip(s1, noise)
            s2 = self._random.random_flip(s2, noise)
            s3 = self._random.random_flip(s3, noise)
            s4 = self._random.random_flip(s4, noise)
        player.update_history(s1, s2, s3, s4)
        competitor.update_history(s2, s1, s4, s3)
        SC1.update_history(s3, s4, s1, s2)
        SC2.update_history(s4, s3, s2, s1)
        return s1, s2, s3, s4

    def play(self):
        """
        Execute a complete match between four players.

        Handles the execution of all turns in the match, including:
        - Determining match length (fixed or probabilistic)
        - Resetting players if specified
        - Setting match attributes for all players
        - Managing simultaneous moves
        - Recording game history

        Returns:
            List[Tuple[Action_4p4m, Action_4p4m, Action_4p4m, Action_4p4m]]:
                Complete history of all plays in the match, where each tuple contains
                the moves made by all four players in one turn.

        Example:
             match = Match_4p4m([p1, p2, p3, p4], turns=5)
             result = match.play()
             print(len(result))  # Number of turns played
             5
             print(result[0])  # First turn's moves
            (W, X, Y, Z)  # Example moves from each player

        Note:
            - If prob_end is set, match length is determined probabilistically
            - Players are reset before the match if reset=True
            - Noise is applied independently to each player's moves
            - Match history is stored in self.result
        """        
        if self.prob_end:
            r = self._random.random()
            turns = min(sample_length(self.prob_end, r), self.turns)
        else:
            turns = self.turns
       
        for p in self.players:
            if self.reset:
                p.reset()
            p.set_match_attributes(**self.match_attributes)
            # WIP: tbd
            # Generate a random seed for the player, if stochastic
            #if Classifiers["stochastic"](p):
            #    p.set_seed(self._random.random_seed_int())
        
        result = []
        for _ in range(turns):
            plays = self.simultaneous_play(
                self.players[0], self.players[1], self.players[2], self.players[3], self.noise
            )
            result.append(plays)
            
        self.result = result
        return result

    def scores(self):
        """Returns the scores of the previous Match plays."""
        return iu_4p4m.compute_scores_4p4m(self.result, self.game)

    def final_score(self):
        """Returns the final score for a Match."""
        return iu_4p4m.compute_final_score_4p4m(self.result, self.game)

    def final_score_per_turn(self):
        """Returns the mean score per round for a Match."""
        return iu_4p4m.compute_final_score_per_turn_4p4m(self.result, self.game)

    def winner(self):
        """Returns the winner of the Match."""
        winner_index = iu_4p4m.compute_winner_index_4p4m(self.result, self.game)
        if winner_index is False:  # No winner
            return False
        if winner_index is None:  # No plays
            return None
        return self.players[winner_index]

    def profiteering(self) -> Optional[Tuple[int, int, int, int]]:
        """
        Returns the count of profiteering moves (W) for each player.

        Returns:
            Tuple of W-move counts for each player (p1, p2, p3, p4),
            or None if no plays have occurred
        """
        return iu_4p4m.compute_profiteering(self.result)

    def invest_SC1(self) -> Optional[Tuple[int, int, int, int]]:
        """
        Returns the count of investments in Strategic Companion 1 (X) for each player.

        Returns:
            Tuple of X-move counts for each player (p1, p2, p3, p4),
            or None if no plays have occurred
        """
        return iu_4p4m.compute_investSC1(self.result)

    def invest_SC2(self) -> Optional[Tuple[int, int, int, int]]:
        """
        Returns the count of investments in Strategic Companion 2 (Y) for each player.

        Returns:
            Tuple of Y-move counts for each player (p1, p2, p3, p4),
            or None if no plays have occurred
        """
        return iu_4p4m.compute_investSC2(self.result)

    def competing(self) -> Optional[Tuple[int, int, int, int]]:
        """
        Returns the count of competing moves (Z) for each player.

        Returns:
            Tuple of Z-move counts for each player (p1, p2, p3, p4),
            or None if no plays have occurred
        """
        return iu_4p4m.compute_competing(self.result)

    
    def normalised_profiteering(self) -> Optional[Tuple[float, float, float, float]]:
        """
        Returns the proportion of profiteering moves (W) for each player.

        Returns:
            Tuple of W-move proportions for each player (p1, p2, p3, p4),
            or None if no plays have occurred
        """
        return iu_4p4m.compute_normalised_profiteering(self.result)

    def normalised_invest_SC1(self) -> Optional[Tuple[float, float, float, float]]:
        """
        Returns the proportion of SC1 investment moves (X) for each player.

        Returns:
            Tuple of X-move proportions for each player (p1, p2, p3, p4),
            or None if no plays have occurred
        """
        return iu_4p4m.compute_normalised_investSC1(self.result)

    def normalised_invest_SC2(self) -> Optional[Tuple[float, float, float, float]]:
        """
        Returns the proportion of SC2 investment moves (Y) for each player.

        Returns:
            Tuple of Y-move proportions for each player (p1, p2, p3, p4),
            or None if no plays have occurred
        """
        return iu_4p4m.compute_normalised_investSC2(self.result)

    def normalised_competing(self) -> Optional[Tuple[float, float, float, float]]:
        """
        Returns the proportion of competing moves (Z) for each player.

        Returns:
            Tuple of Z-move proportions for each player (p1, p2, p3, p4),
            or None if no plays have occurred
        """
        return iu_4p4m.compute_normalised_competing(self.result)
    
    
    def state_distribution(self) -> Optional[Counter]:
        """
        Returns the frequency distribution of game states.

        Returns:
            Counter object mapping states to their frequencies,
            where states are tuples of (W/X/Y/Z) moves,
            or None if no plays have occurred

        Example:
            {(W,X,Y,Z): 5} means this state occurred 5 times
        """
        return iu_4p4m.compute_state_distribution(self.result)

    def normalised_state_distribution(self) -> Optional[Counter]:
        """
        Returns the normalized frequency distribution of game states.

        Returns:
            Counter mapping states to their normalized frequencies (sum = 1),
            or None if no plays have occurred

        Example:
            {(W,X,Y,Z): 0.25} means this state occurred 25% of the time
        """
        return iu_4p4m.compute_normalised_state_distribution(self.result)
    
    def __len__(self):
        return self.turns


def sample_length(prob_end: float, random_value: float) -> Union[float, int]:
    """
    Sample length of a game using inverse transform sampling.

    Args:
        prob_end: Probability of the game ending after each turn (0 to 1)
        random_value: Random value for sampling (0 to 1)

    Returns:
        Number of turns to play (float('inf') if prob_end is 0)

    Note:
        Uses probability density function f(n) = p_end * (1 - p_end)^(n-1)
        See full documentation in code comments.
    """
    if prob_end == 0:
        return float("inf")
    if prob_end == 1:
        return 1
    return int(ceil(log(1 - random_value) / log(1 - prob_end)))