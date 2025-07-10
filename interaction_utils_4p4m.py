"""
Interaction Utilities for Four-Player Four-Move Prisoner's Dilemma

This module provides utility functions for analyzing interactions in a four-player
variant of the Prisoner's Dilemma game. It handles scoring, statistics, and data
processing for game interactions.

Informally: For convenience, functionality from a number of other modules is bundled here.

Key Features:
    - Score calculation for four-player interactions
    - Statistical analysis of game states and actions
    - Computation of normalized distributions
    - File I/O operations for interaction data
    - Support for different action encodings (WXYZ format)

Functions:
    compute_scores_4p4m: Calculate scores for a set of interactions
    compute_final_score_4p4m: Get final scores for a game
    compute_winner_index_4p4m: Determine the winning player
    compute_*: Various statistical computation functions
    read_interactions_from_file_4p4m: Load interaction data from file

Note:
    All functions support the WXYZ action format where:
    W = Profiteering (invest in neither SC)
    X = Invest in SC1
    Y = Invest in SC2
    Z = Competing (invest in both SC1 and SC2)

Author: Max Bayer
Date: July 2025
"""
# Standard library imports
from collections import Counter, defaultdict
from typing import List, Tuple, Optional, Dict, Union

# Third-party imports
import pandas as pd
import tqdm

# Local imports
from action_4p4m import Action_4p4m, str_to_actions
import scoring_dict_4p4m as scD
import game_4p4m

W, X, Y, Z = Action_4p4m.W, Action_4p4m.X, Action_4p4m.Y, Action_4p4m.Z

# Type aliases
Interaction = Tuple[Action_4p4m, Action_4p4m, Action_4p4m, Action_4p4m]
InteractionList = List[Interaction]
PlayerScores = Tuple[float, float, float, float]



def compute_scores_4p4m(interactions: InteractionList, game: Optional[game_4p4m.TetradicPrisonersDilemmaGame] = None) -> List[PlayerScores]:
    """
    Calculate scores for a sequence of four-player interactions.
    
    Args:
        interactions: List of interaction tuples, each containing four players' moves
        game: Game instance to use for scoring (creates new if None)
    
    Returns:
        List of score tuples (one per interaction)
    """
    if not game:
        game = game_4p4m.TetradicPrisonersDilemmaGame()
    return [game.score_4p4m(plays) for plays in interactions]


def compute_final_score_4p4m(
    interactions: InteractionList,
    game: Optional[game_4p4m.TetradicPrisonersDilemmaGame] = None
) -> Optional[PlayerScores]:
    """
    Calculate final cumulative scores for all players.
    
    Args:
        interactions: List of interaction tuples
        game: Game instance to use for scoring
    
    Returns:
        Tuple of final scores (p1, p2, p3, p4) or None if no interactions
    """
    scores = compute_scores_4p4m(interactions, game)
    if len(scores) == 0:
        return None

    final_score = tuple(
        sum([score[player_index] for score in scores]) for player_index in [0, 1, 2, 3]
    )
    return final_score

def compute_winner_index_4p4m(
    interactions: InteractionList,
    game: Optional[game_4p4m.TetradicPrisonersDilemmaGame] = None
) -> Optional[int]:
    """
    Determine the winner of a sequence of interactions.
    
    Args:
        interactions: List of WXYZ interaction tuples
        game: Optional game instance for scoring
    
    Returns:
        Index of winning player (0-3), False if tie, None if no interactions
    """
    scores = compute_final_score_4p4m(interactions, game)

    if scores is not None:
        if scores[0] == scores[1] == scores[2] == scores[3]:
            return False  # No winner
        return max([0, 1, 2, 3], key=lambda i: scores[i])
    return None


def compute_profiteering(interactions: InteractionList) -> Optional[Tuple[int, int, int, int]]:
    """
    Count profiteering moves (W) for each player.
    
    Args:
        interactions: List of WXYZ interaction tuples
    
    Returns:
        Tuple of W-move counts for each player (p1, p2, p3, p4),
        or None if no interactions
    """

    if len(interactions) == 0:
        return None

    profiteering = tuple(
        sum([play[player_index] == W for play in interactions])
        for player_index in [0, 1, 2, 3]
    )
    return profiteering


def compute_investSC1(interactions: InteractionList) -> Optional[Tuple[int, int, int, int]]:
    """
    Count investments in Strategic Companion 1 (X) for each player.
    
    Args:
        interactions: List of WXYZ interaction tuples
    
    Returns:
        Tuple of X-move counts for each player (p1, p2, p3, p4),
        or None if no interactions
    """
    if len(interactions) == 0:
        return None

    investSC1 = tuple(
        sum([play[player_index] == X for play in interactions])
        for player_index in [0, 1, 2, 3]
    )
    return investSC1


def compute_investSC2(interactions: InteractionList) -> Optional[Tuple[int, int, int, int]]:
    """
    Count investments in Strategic Companion 2 (Y) for each player.
    
    Args:
        interactions: List of WXYZ interaction tuples
    
    Returns:
        Tuple of Y-move counts for each player (p1, p2, p3, p4),
        or None if no interactions
    """

    if len(interactions) == 0:
        return None

    investSC2 = tuple(
        sum([play[player_index] == Y for play in interactions])
        for player_index in [0, 1, 2, 3]
    )
    return investSC2


def compute_competing(interactions: InteractionList) -> Optional[Tuple[int, int, int, int]]:
    """
    Count competing moves (Z) for each player.
    
    Args:
        interactions: List of WXYZ interaction tuples
    
    Returns:
        Tuple of Z-move counts for each player (p1, p2, p3, p4),
        or None if no interactions
    """

    if len(interactions) == 0:
        return None

    competing = tuple(
        sum([play[player_index] == Z for play in interactions])
        for player_index in [0, 1, 2, 3]
    )
    return competing


def compute_normalised_profiteering(interactions: InteractionList) -> Optional[Tuple[float, float, float, float]]:
    """
    Calculate proportion of profiteering moves (W) per player.
    
    Args:
        interactions: List of WXYZ interaction tuples
    
    Returns:
        Tuple of W-move proportions for each player (p1, p2, p3, p4),
        or None if no interactions
    """
    if len(interactions) == 0:
        return None

    num_turns = len(interactions)
    profiteering = compute_profiteering(interactions)

    normalised_profiteering = tuple([w / num_turns for w in profiteering])

    return normalised_profiteering


def compute_normalised_investSC1(interactions: InteractionList) -> Optional[Tuple[float, float, float, float]]:
    """
    Calculate proportion of SC1 investment moves (X) per player.
    
    Args:
        interactions: List of WXYZ interaction tuples
    
    Returns:
        Tuple of X-move proportions for each player (p1, p2, p3, p4),
        or None if no interactions
    """
    if len(interactions) == 0:
        return None

    num_turns = len(interactions)
    investSC1 = compute_investSC1(interactions)

    normalised_investSC1 = tuple([x / num_turns for x in investSC1])

    return normalised_investSC1


def compute_normalised_investSC2(interactions: InteractionList) -> Optional[Tuple[float, float, float, float]]:
    """
    Calculate proportion of SC2 investment moves (Y) per player.
    
    Args:
        interactions: List of WXYZ interaction tuples
    
    Returns:
        Tuple of Y-move proportions for each player (p1, p2, p3, p4),
        or None if no interactions
    """
    if len(interactions) == 0:
        return None

    num_turns = len(interactions)
    investSC2 = compute_investSC2(interactions)

    normalised_investSC2 = tuple([y / num_turns for y in investSC2])

    return normalised_investSC2


def compute_normalised_competing(interactions: InteractionList) -> Optional[Tuple[float, float, float, float]]:
    """
    Calculate proportion of competing moves (Z) per player.
    
    Args:
        interactions: List of WXYZ interaction tuples
    
    Returns:
        Tuple of Z-move proportions for each player (p1, p2, p3, p4),
        or None if no interactions
    """
    if len(interactions) == 0:
        return None

    num_turns = len(interactions)
    competing = compute_competing(interactions)
    normalised_competing = tuple([z / num_turns for z in competing])
    return normalised_competing



def compute_state_distribution(interactions: InteractionList) -> Optional[Counter]:
    """
    Calculate frequency distribution of game states.
    
    Args:
        interactions: List of WXYZ interaction tuples
    
    Returns:
        Counter object mapping states to their frequencies,
        where states are tuples of (W/X/Y/Z) moves
    """
    if not interactions:
        return None
    return Counter(interactions)


def compute_normalised_state_distribution(
    interactions: InteractionList
) -> Optional[Counter]:
    """
    Calculate normalized frequency distribution of game states.
    
    Args:
        interactions: List of WXYZ interaction tuples
    
    Returns:
        Counter mapping states to their normalized frequencies (sum = 1),
        or None if no interactions
        
    Example:
        {(W,X,Y,Z): 0.25} means this state occurred 25% of the time
    """
    if not interactions:
        return None

    interactions_count = Counter(interactions)
    total = sum(interactions_count.values(), 0)

    normalized_count = Counter(
        {key: value / total for key, value in interactions_count.items()}
    )
    return normalized_count

## to be tested and re-written
def compute_state_to_action_distribution_4p4m(interactions: InteractionList) -> Optional[List[Counter]]:
    """
    Calculate state-to-action transition frequencies for each player.
    
    For each player, tracks how they respond to each game state. A state-action
    pair has the form ((W,X,Y,Z), W) meaning "when previous state was WXYZ,
    player chose W".
    
    Args:
        interactions: List of WXYZ interaction tuples
    
    Returns:
        List of Counter objects (one per player) mapping state-action pairs
        to their frequencies
        
    Example Counter entry:
        {((W,X,Y,Z), W): 0.25} means "Player chose W 25% of the time when 
        previous state was WXYZ"
    """
    if not interactions:
        return None

    distributions = [
        Counter(
            [
                (state, outcome[j])
                for state, outcome in zip(interactions, interactions[1:])
            ]
        )
        for j in range(4)
    ]
    return distributions


def compute_normalised_state_to_action_distribution_4p4m(
    interactions: InteractionList,
    decision_combinations: List[Interaction] = scD.all_strategic_interactions_4players_WXYZ
) -> Optional[List[Counter]]:
    """
    Calculate normalized state-to-action transition probabilities.
    
    For each player, computes the probability of choosing each action
    (W,X,Y,Z) given the previous game state.
    
    Args:
        interactions: List of WXYZ interaction tuples
        decision_combinations: List of possible game states to analyze
    
    Returns:
        List of Counter objects (one per player) mapping (state, action)
        pairs to their probabilities, or None if no interactions
        
    Example Counter entry:
        {((W,X,Y,Z), W): 0.25} means "Player chose W 25% of the time
        when previous state was WXYZ"
    """
    
    if not interactions:
        return None

    distribution = compute_state_to_action_distribution_4p4m(interactions)
    normalized_distribution = []
    for player in range(4):
        counter = {}
        for state in decision_combinations:   
            W_count = distribution[player].get((state, W), 0)
            X_count = distribution[player].get((state, X), 0)
            Y_count = distribution[player].get((state, Y), 0)
            Z_count = distribution[player].get((state, Z), 0)
            total = W_count + X_count + Y_count + Z_count
            if total > 0:
                if W_count > 0:
                    counter[(state, W)] = W_count / (W_count + X_count + Y_count + Z_count)
                if X_count > 0:
                    counter[(state, X)] = X_count / (W_count + X_count + Y_count + Z_count)
                if Y_count > 0:
                    counter[(state, Y)] = Y_count / (W_count + X_count + Y_count + Z_count)
                if Z_count > 0:
                    counter[(state, Z)] = Z_count / (W_count + X_count + Y_count + Z_count)
        normalized_distribution.append(Counter(counter))
    return normalized_distribution


### to be tested
def read_interactions_from_file_4p4m(
    filename: str,
    progress_bar: bool = True
) -> Dict[Tuple[int, int, int, int], InteractionList]:
    """
    Read interaction data from CSV file.
    
    Expected CSV format:
    Interaction index, Player1 index, Player2 index, Player3 index, Player4 index, Actions
    
    Args:
        filename: Path to CSV file
        progress_bar: Whether to show progress bar
        
    Returns:
        Dictionary mapping player indices (p1,p2,p3,p4) to their interactions
    """


def string_to_interactions(string: str) -> InteractionList:
    """
    Convert string representation to interaction tuples.
    
    Args:
        string: String of WXYZ characters representing moves
               (e.g. 'WXYZWXYZ' for two rounds)
    
    Returns:
        List of interaction tuples [(W,X,Y,Z), (W,X,Y,Z), ...]
        
    Example:
        'WXYZWXYZ' -> [(W,X,Y,Z), (W,X,Y,Z)]
    """
    interactions = []
    interactions_list = list(string)
    while interactions_list:
        p1action = Action_4p4m.from_char(interactions_list.pop(0)) #i think pop(0) doesnt change for 4 players
        p2action = Action_4p4m.from_char(interactions_list.pop(0)) #Note: The pop() method returns removed value.
        p3action = Action_4p4m.from_char(interactions_list.pop(0))
        p4action = Action_4p4m.from_char(interactions_list.pop(0))
        interactions.append((p1action, p2action, p3action, p4action))
    return interactions