"""
Scoring Dictionary Generator for 4-Player 4-Move Game

This module generates scoring dictionaries for a 4-player, 4-move game in two formats:
1. Using WXYZ notation (W,X,Y,Z representing different moves)
2. Using integer notation (0,1,2,3 representing different moves)

The module calculates payoffs for all 256 possible game state combinations (4^4)
based on a predefined payoff matrix. Each game state maps to a tuple of 4 payoff values,
one for each player.

Example output formats:
    WXYZ format: {(W,W,W,W): (2,2,2,2), ...}
    Integer format: {(0,0,0,0): (2,2,2,2), ...}

Author: Max Bayer
Date: July 2025
"""

# Third-party imports
import itertools
import pprint

# Local imports
from action_4p4m import Action_4p4m 

W, X, Y, Z = Action_4p4m.W, Action_4p4m.X, Action_4p4m.Y, Action_4p4m.Z


# Payoff matrix definition
# Structure: [move][player_payoff]
# - Rows (moves): W=0, X=1, Y=2, Z=3
# - Columns: payoffs for (self, competitor, supply_chain1, supply_chain2)
# --> (for an n-Prisoner's Dilemma, the first column sets payoff for self, second for second player etc.)
payoff_matrix = (   ( 0, 0, 0, 0),  # Payoffs for move W
                    (-3, 0, 4, 0),  # Payoffs for move X
                    (-3, 0, 0, 4),  # Payoffs for move Y
                    (-4, 0, 3, 3)   # Payoffs for move Z
)
# Player position mapping for calculating payoffs
# Each tuple represents how payoffs should be distributed for each player's perspective
# --> 0 = self, 1 = competitor, 2 = sc1, 3 = sc2
indices_game_4players = (   (0,1,2,3), # Player 1's perspective
                            (1,0,3,2), # Player 2's perspective
                            (2,3,0,1), # Player 3's perspective
                            (3,2,1,0)) # Player 4's perspective

# Game configuration constants (can be used to create repository for n-Prisoner's Dilemma)
players_per_game = len(payoff_matrix[0]) 
possible_moves_int = tuple(range(len(payoff_matrix)))

# Move notation mappings (manual input needed for higher-n games)
possible_moves_wxyz = (W,X,Y,Z)
possible_moves_dict_int_str = {0:W, 1:X, 2:Y, 3:Z}
possible_moves_dict_str_int = {W:0, X:1, Y:2, Z:3}

# Generate scoring dictionary with integer move notation (0,1,2,3)
all_game_states_int_moves = list(itertools.product(possible_moves_int, repeat = players_per_game))
payoffs_all_game_states_int_moves = []
payoff_dictionary_4p4m_asValues = {}

for game_state in all_game_states_int_moves:
    game_payoffs = [0,0,0,0]
    for player in range(players_per_game):
        for index in range(players_per_game):
            game_payoffs[indices_game_4players[player][index]] += payoff_matrix[game_state[player]][index]   
    payoffs_all_game_states_int_moves.append(game_payoffs)
    payoff_dictionary_4p4m_asValues[game_state] = tuple(game_payoffs)  # Add entry to the dictionary
    
# Generate scoring dictionary with WXYZ move notation
all_strategic_interactions_4players_WXYZ = list(itertools.product(possible_moves_wxyz, repeat = players_per_game))
payoffs_all_game_states = []
payoff_dictionary_4p4m_WXYZ = {}

for game_state in all_strategic_interactions_4players_WXYZ:
    game_payoffs = [0,0,0,0]
    for player in range(players_per_game):
        # Convert Action_4p4m to integer for payoff matrix lookup
        player_move_int = possible_moves_dict_str_int[game_state[player]]
        for index in range(players_per_game):
            game_payoffs[indices_game_4players[player][index]] += payoff_matrix[player_move_int][index]   
    payoffs_all_game_states.append(game_payoffs)
    payoff_dictionary_4p4m_WXYZ[game_state] = tuple(game_payoffs)  # Add entry to the dictionary
    
# Uncomment to print dictionaries for debugging
# pprint.pprint(payoff_dictionary_4p4m_asValues)
# pprint.pprint(payoff_dictionary_4p4m_WXYZ)


