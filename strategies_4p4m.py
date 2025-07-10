"""
Four-Player Four-Move Game Strategies Collection

This module implements various strategies for a four-player, four-move variant 
of the Prisoner's Dilemma game. Each strategy defines how a player responds to 
the moves of other players based on different information sets and memory depths.

Available Strategy Categories:
    - Simple Test Strategies: Cycler, Exploiter, Copy variants
    - Unconditional Strategies: Always-W/X/Y/Z, Random
    - Tit-for-Tat Variations: 
        * 2-player (dyadic) versions
        * 3-player (triadic) versions
        * 4-player (tetradic) versions
        * Start-small (ss) and start-big (sb) variants
    - Forgiving Strategies: Various forgiving TFT implementations
    - Contrite Strategies: Error-handling variations
    - Pavlov Strategies: Win-stay, lose-shift implementations
    - Nasty Strategies: Grudger, Tester, Extortion variants
    - Experimental Strategies: Various test implementations
    - Genetic Algorithm Players: Evolution-based strategies

Move Notation:
    W: No investment/cooperation
    X: Invest in/cooperate with SC1
    Y: Invest in/cooperate with SC2
    Z: Invest in/cooperate with both SC1 and SC2

Information Sets:
    2p: Considers only SC1
    3p: Considers SC1 and SC2
    4p: Considers SC1, SC2, and competitor
    
Start small or start big?:
    ss: Start small (establish X or Y before Z)
    sb: Start big (try Z before falling back to X or Y)

Author: Max Bayer
Date: July 2025
"""

# Standard library imports
import itertools
from typing import Any, Dict
import random as random

# Local imports
from action_4p4m import Action_4p4m 
import game_4p4m as game_4p4m #care: from axelrod.game import DefaultGame
import player_4p4m as pl

# Initializing the action constants from Action_4p4m
W, X, Y, Z = Action_4p4m.W, Action_4p4m.X, Action_4p4m.Y, Action_4p4m.Z



#------------------------------------------------------------------------------
# TEST STRATEGIES
#------------------------------------------------------------------------------

class Cycler(pl.Player_4p4m):
    """
    A simple cyclic strategy that rotates through moves in a fixed pattern.

    This strategy cycles through moves in the sequence W -> X -> Y -> Z -> W,
    regardless of other players' actions. Useful as a baseline strategy and
    for testing purposes.

    Parameters:
        starting_move (Action_4p4m): The first move in the cycle (default: W)

    Attributes:
        name (str): "Cycler"
        memory_depth (int): 1 - only needs to remember its last move
        stochastic (bool): False - behavior is deterministic
    """
    
    name = "Cycler"
    classifier = {
        "memory_depth": 1,
        "stochastic": False,
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }

    def __init__(self, starting_move=W):
        self.starting_move = starting_move
        super().__init__()

    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:
        """Actual strategy definition that determines player's action."""
        # manually adapt number_of_players

        if not self.history:
            return self.starting_move
        elif self.history[-1] ==W:
            return X
        elif self.history[-1] ==X:
            return Y
        elif self.history[-1] ==Y:
            return Z
        elif self.history[-1] ==Z:
            return W



class Exploiter_2p(pl.Player_4p4m):
 
    name = "Cycle-X-W"
    classifier = {
        "memory_depth": 2,
        "stochastic": False,
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }

    def __init__(self):
        super().__init__()
    
    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:
        """Actual strategy definition that determines player's action."""
        
        if len(self.history) < 1:
            return X
        else:
            if (len(self.history) +1) % 2 == 0:
                return W
            else:
                return X
            
            

class CopyCompetitor(pl.Player_4p4m):
    name = "Copy Competitor"
    classifier = {
        "memory_depth": 1,
        "stochastic": False,
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }

    def __init__(self, starting_move=W):
        self.starting_move = starting_move
        super().__init__()

    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:
        """Actual strategy definition that determines player's action."""
        # manually adapt number_of_players

        if not self.history:
            return self.starting_move
        else:
            return competitor.history[-1]



class CopySc1(pl.Player_4p4m):
    name = "Copy SC1"
    classifier = {
        "memory_depth": 1,
        "stochastic": False,
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }

    def __init__(self, starting_move=W):
        self.starting_move = starting_move
        super().__init__()

    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:
        """Actual strategy definition that determines player's action."""
        # manually adapt number_of_players

        if not self.history:
            return self.starting_move
        else:
            return SC1.history[-1]



class CopySc2(pl.Player_4p4m):
    name = "Copy SC2"
    classifier = {
        "memory_depth": 1,
        "stochastic": False,
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }

    def __init__(self, starting_move=W):
        self.starting_move = starting_move
        super().__init__()

    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:
        """Actual strategy definition that determines player's action."""
        # manually adapt number_of_players

        if not self.history:
            return self.starting_move
        else:
            return SC2.history[-1]






#------------------------------------------------------------------------------
# UNCONDITIONAL STRATEGIES
#------------------------------------------------------------------------------
    """
    A strategy that always plays the same move regardless of other players' actions.
    
    These strategies serve as important baseline implementations and control groups
    in tournaments. They can also be used to test how other strategies respond to
    consistent behavior.
    
    Attributes:
        name (str): Name of the strategy (e.g., "Always W", "Always X", etc.)
        memory_depth (int): 0 - strategy doesn't consider history
        stochastic (bool): False - behavior is deterministic
        
    Version Variations:
        - Always-W: Never cooperates with any player
        - Always-X: Always cooperates with SC1 only
        - Always-Y: Always cooperates with SC2 only
        - Always-Z: Always cooperates with both SC1 and SC2
        - Always-Random: Randomly chooses one of the four actions
    """
    
class AlwaysRandom(pl.Player_4p4m):
    name = "Random"
    classifier = {
        "memory_depth": 1,
        "stochastic": False,
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }

    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:
        """Actual strategy definition that determines player's action."""
        # manually adapt number_of_players
        random_value = random.random()
        if random_value <= 0.25:
            return W
            random_value = 0
        elif random_value > 0.25 and random_value <= 0.5:
            return X
            random_value = 0
        elif random_value > 0.5 and random_value <= 0.75:
            return Y
            random_value = 0
        elif random_value > 0.75:
            return Z
            random_value = 0
      
        

class AlwaysW(pl.Player_4p4m):
    name = "Always W"
    classifier = {
        "memory_depth": 2,
        "stochastic": False,
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }

    def __init__(self):
        super().__init__()

    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:
        """Actual strategy definition that determines player's action."""
        # manually adapt number_of_players
        return W



class AlwaysX(pl.Player_4p4m):
    name = "Always X"
    classifier = {
        "memory_depth": 2,
        "stochastic": False,
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }

    def __init__(self):
        super().__init__()

    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:
        return X



class AlwaysY(pl.Player_4p4m):
    name = "Always Y"
    classifier = {
        "memory_depth": 2,
        "stochastic": False,
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }

    def __init__(self):
        super().__init__()

    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:
        return Y



class AlwaysZ(pl.Player_4p4m):
    name = "Always Z"
    classifier = {
        "memory_depth": 2,
        "stochastic": False,
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }

    def __init__(self):
        super().__init__()
    
    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:
        """Actual strategy definition that determines player's action."""
        return Z





#------------------------------------------------------------------------------
# TIT-FOR-TAT VARIATIONS
#------------------------------------------------------------------------------
    """
    A family of reciprocal strategies that cooperate on the first move and then 
    mirror their opponents' previous actions.
    
    These strategies implement various forms of reciprocity based on different
    information sets (2p/3p/4p) and different initial cooperation approaches
    (start small/start big).
    
    Attributes:
        memory_depth (int): Number of previous moves considered
        stochastic (bool): False - behavior is deterministic
        cooperative_sc1 (bool): Tracks SC1's cooperation status
        cooperative_sc2 (bool): Tracks SC2's cooperation status
        cooperative_comp (bool): Tracks competitor's cooperation status
        
    Information Sets:
        - 2p: Considers only SC1's moves
        - 3p: Considers both SC1 and SC2's moves
        - 4p: Considers all players' moves
        
    Starting Approaches:
        - ss (Start Small): Begins with X, builds to Z if conditions are favorable
        - sb (Start Big): Begins with Z, falls back to X/Y if necessary
        
    Common Variations:
        - Simple TFT: Basic reciprocal behavior
        - Forgiving TFT: More tolerant of defections
        - Contrite TFT: Can recover from accidental defections
    """
    
class TFT_2p(pl.Player_4p4m):
 
    name = "Simple TFT (2p)"
    classifier = {
        "memory_depth": 1,
        "stochastic": False,
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }

    def __init__(self):
        super().__init__()
    
    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:
        """Actual strategy definition that determines player's action."""
        if len(self.history) < 1:
            return X
        else:
            if SC1.history[-1] == X or SC1.history[-1] == Z:
                return X
            else:
                return W


        
class TFT_3p_sb(pl.Player_4p4m):
 
    name = "Simple TFT (3p_sb)"
    classifier = {
        "memory_depth": 1,
        "stochastic": False,
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }

    def __init__(self):
        super().__init__()
    
    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:
        
        #strategy
        if len(self.history) < 1:
            return Z
        else:
            if (SC1.history[-1] == X or SC1.history[-1] == Z) and (SC2.history[-1] == Y or SC2.history[-1] == Z):
                return Z #service both if both invest in me with XY
            elif SC1.history[-1] == X:
                return X # in a tie between SC1's X and SC2's Y, always stay with "incumbent" SC1 -> deterministic
            elif SC2.history[-1] == Y:
                return Y
            elif SC1.history[-1] == Z:
                return X
            elif SC2.history[-1] == Z:
                return Y
            else:
                return W



class TFT_3p_ss(pl.Player_4p4m):
 
    name = "Simple TFT (3p_ss)"
    classifier = {
        "memory_depth": 1,
        "stochastic": False,
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }

    def __init__(self):
        super().__init__()
        self.cooperative_sc1 = True
        self.cooperative_sc2 = False
    
    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:
        
        #strategy
        if len(self.history) < 1:
            return X
        else:
            if SC1.history[-1] == W:
                self.cooperative_sc1 = False
            else:
                self.cooperative_sc1 = True
            if SC2.history[-1] == W:
                self.cooperative_sc2 = False
            else:
                self.cooperative_sc2 = True
            
            if self.cooperative_sc1 and self.cooperative_sc2: # if SC1 and SC2 are cooperative
                if self.history[-1] != Z:
                    return Z # try to establish triadic cooperation if both are cooperative
                
            if (SC1.history[-1] == X or SC1.history[-1] == Z) and (SC2.history[-1] == Y or SC2.history[-1] == Z):
                return Z #service both if both invest in me with XY or ZZ or XZ or ZY
            elif SC1.history[-1] == X:
                return X # in a tie between SC1's X and SC2's Y, always stay with "incumbent" SC1 -> deterministic
            elif SC2.history[-1] == Y:
                return Y
            elif SC1.history[-1] == Z:
                return X
            elif SC2.history[-1] == Z:
                return Y
            else:
                return W



class TFT_4p_sb(pl.Player_4p4m):
    name = "Simple TFT (4p_sb)"
    classifier = {
        "memory_depth": 1,
        "stochastic": False,
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }
    
    def __init__(self) -> None:
        super().__init__()

    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:
                        
        if len(self.history) < 1:
            return Z 
        elif SC1.history[-1] == Z and SC2.history[-1] == Z and competitor.history[-1] == Z:
            return Z #support optimal outcome
        elif SC1.history[-1] == X and SC2.history[-1] == Y:
            return Z #service both if both invest in me with XY
        elif competitor.history[-1] == W and SC1.history[-1] != W and SC2.history[-1] != W:
            return Z # try to capture the market against uncooperative competitor
        elif SC1.history[-1] == X:
            return X # in a tie between SC1's X and SC2's Y, always stay with "incumbent" SC1 -> deterministic
        elif SC2.history[-1] == Y:
            return Y
        elif SC1.history[-1] == Z:
            return X
        elif SC2.history[-1] == Z:
            return Y
        else:
            return W
        



class TFT_4p_ss(pl.Player_4p4m):
    """
    Four-player Tit-for-Tat with 'start small' behavior.

    A sophisticated strategy that starts with simple dyadic cooperation (X)
    and gradually builds up to triadic cooperation (Z) if conditions are favorable.
    Monitors and responds to the behavior of all players, including the competitor.

    Features:
        - Starts with X (cooperation with SC1)
        - Tracks cooperation levels of all players
        - Can establish triadic cooperation (Z) when both SCs are cooperative
        - Maintains separate cooperation flags for each player
        - Falls back to simpler cooperation forms if triadic fails

    Attributes:
        name (str): "Simple TFT (4p_ss)"
        memory_depth (int): 2
        cooperative_sc1 (bool): Tracks SC1's cooperative status
        cooperative_sc2 (bool): Tracks SC2's cooperative status
        cooperative_comp (bool): Tracks competitor's cooperative status
    """
    
    name = "Simple TFT (4p_ss)"
    classifier = {
        "memory_depth": 2,
        "stochastic": False,
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }
    
    def __init__(self) -> None:
        super().__init__()
        self.cooperative_sc1 = True
        self.cooperative_sc2 = False
        self.cooperative_comp = False

    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:
                        
        if len(self.history) < 2:
            return X 
        
        else:
            if SC1.history[-1] == W and (competitor.history[-2] != W or competitor.history[-2] != X):
                self.cooperative_sc1 = False
            else:
                self.cooperative_sc1 = True
            if SC2.history[-1] == W and (competitor.history[-2] != W or competitor.history[-2] != Y):
                self.cooperative_sc2 = False
            else:
                self.cooperative_sc2 = True
            if competitor.history[-1] == W:
                self.cooperative_comp = False
            else:
                self.cooperative_comp = True  
            
            if self.cooperative_sc1 and self.cooperative_sc2: # if SC1 and SC2 are cooperative
                if self.history[-1] != Z:
                    return Z # try to establish triadic cooperation if both are cooperative
        
            if SC1.history[-1] == Z and SC2.history[-1] == Z and competitor.history[-1] == Z:
                return Z #support optimal outcome
            elif SC1.history[-1] == X and SC2.history[-1] == Y:
                return Z #service both if both invest in me with XY
            elif competitor.history[-1] == W and SC1.history[-1] != W and SC2.history[-1] != W:
                return Z # try to capture the market against uncooperative competitor
            elif SC1.history[-1] == X:
                return X # in a tie between SC1's X and SC2's Y, always stay with "incumbent" SC1 -> deterministic
            elif SC2.history[-1] == Y:
                return Y
            elif SC1.history[-1] == Z:
                return X
            elif SC2.history[-1] == Z:
                return Y
            else:
                return W



        
        
#------------------------------------------------------------------------------
# Forgiving TFT variations (defects once after two consecutive defections...
# ...to better handle noise in the game)
#------------------------------------------------------------------------------

class ForgivingTFT_2p(pl.Player_4p4m):
 
    name = "Forgiving TFT (2p)"
    classifier = {
        "memory_depth": 2,
        "stochastic": False,
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }

    def __init__(self):
        super().__init__()
    
    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:
        """Actual strategy definition that determines player's action."""
        
        if len(self.history) < 2:
            return X
        else:
            if (SC1.history[-1] == W or SC1.history[-1] == Y) and (SC1.history[-2] == W or SC1.history[-2] == Y):
                return W
            else:
                return X



class ForgivingTFT_3p_sb(pl.Player_4p4m):
 
    name = "Forgiving TFT (3p_sb)"
    classifier = {
        "memory_depth": 2,
        "stochastic": False,
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }

    def __init__(self):
        super().__init__()
    
    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:
        """Actual strategy definition that determines player's action."""
        
        if len(self.history) < 2:
            return Z
        else:
            # if both SC1 and SC2 did not cooperate with me for two rounds, then I avoid all investments (by playing W)
            if (SC1.history[-1] == W or SC1.history[-1] == Y) and (SC1.history[-2] == W or SC1.history[-2] == Y):
                if (SC2.history[-1] == W or SC2.history[-1] == X) and (SC2.history[-2] == W or SC2.history[-2] == X):
                    return W
            if (SC1.history[-1] == W or SC1.history[-1] == Y) and (SC1.history[-2] == W or SC1.history[-2] == Y):
                return Y
            elif (SC2.history[-1] == W or SC2.history[-1] == X) and (SC2.history[-2] == W or SC2.history[-2] == X):
                return X
            else:
                return Z



class ForgivingTFT_3p_ss(pl.Player_4p4m):
 
    name = "Forgiving TFT (3p_ss)"
    classifier = {
        "memory_depth": 2,
        "stochastic": False,
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }

    def __init__(self):
        super().__init__()
    
    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:
        """Actual strategy definition that determines player's action."""
        
        if len(self.history) < 2:
            return X
        else:
            # if both SC1 and SC2 did not cooperate with me for two rounds, then I avoid all investments (by playing W)
            if (SC1.history[-1] == W or SC1.history[-1] == Y) and (SC1.history[-2] == W or SC1.history[-2] == Y):
                if (SC2.history[-1] == W or SC2.history[-1] == X) and (SC2.history[-2] == W or SC2.history[-2] == X):
                    return W
            if (SC1.history[-1] == W or SC1.history[-1] == Y) and (SC1.history[-2] == W or SC1.history[-2] == Y):
                return Y
            elif (SC2.history[-1] == W or SC2.history[-1] == X) and (SC2.history[-2] == W or SC2.history[-2] == X):
                return X
            else:
                return Z
            
            

class ForgivingTFT_4p_sb(pl.Player_4p4m):
 
    name = "Forgiving TFT (4p_sb)"
    classifier = {
        "memory_depth": 2,
        "stochastic": False,
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }

    def __init__(self):
        super().__init__()
        self.cooperative_sc1 = True
        self.cooperative_sc2 = True
        self.cooperative_comp = True
    
    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:
        """Actual strategy definition that determines player's action."""
        
        if len(self.history) < 2:
            return Z
        
        else:
            if self.cooperative_sc1 and self.cooperative_sc2 and self.cooperative_comp: # if SC1, SC2, and competitor are cooperative
                if SC1.history[-1] == W and SC1.history[-2] == W:
                    self.cooperative_sc1 = False
                if SC2.history[-1] == W and SC2.history[-2] == W:
                    self.cooperative_sc2 = False
                if competitor.history[-1] == W and competitor.history[-2] == W:
                    self.cooperative_comp = False
            # if everyone is cooperative, try to establish ZZZZ
            if self.cooperative_sc1 and self.cooperative_sc2 and self.cooperative_comp:
                return Z
            # if SC2 is not cooperative, perhaps because competitor is not cooperative, try to establish ZWXY or even ZWZZ
            elif self.cooperative_sc1 and not self.cooperative_comp:
                # reset good will. Will be re-evaluated above
                self.cooperative_sc1 = True
                self.cooperative_sc2 = True
                self.cooperative_comp = True
                return Z
            elif self.cooperative_sc1:
                self.cooperative_sc1 = True
                self.cooperative_sc2 = True
                self.cooperative_comp = True
                return X
            elif self.cooperative_sc2:
                self.cooperative_sc1 = True
                self.cooperative_sc2 = True
                self.cooperative_comp = True
                return Y
            else:
                return W



class ForgivingTFT_4p_ss(pl.Player_4p4m):
 
    name = "Forgiving TFT (4p_ss)"
    classifier = {
        "memory_depth": 2,
        "stochastic": False,
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }

    def __init__(self):
        super().__init__()
        self.good_sc1 = True
        self.good_sc2 = True
        self.good_comp = True
    
    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:
        """Actual strategy definition that determines player's action."""
        
        if len(self.history) < 2:
            if len(self.history) < 1:
                return X
            else:
                return SC1.history[-1] # if only one round, play what SC1 played
        
        else:
            if self.good_sc1 and self.good_sc2 and self.good_comp: # if SC1, SC2, and competitor are cooperative
                if SC1.history[-1] == W and SC1.history[-2] == W:
                    self.good_sc1 = False
                if SC2.history[-1] == W and SC2.history[-2] == W:
                    self.good_sc2 = False
                if competitor.history[-1] == W and competitor.history[-2] == W:
                    self.good_comp = False
            # if everyone is cooperative, try to establish ZZZZ
            if self.good_sc1 and self.good_sc2 and self.good_comp:
                return Z
            # if SC2 is not cooperative, perhaps because competitor is not cooperative, try to establish ZWXY or even ZWZZ
            elif self.good_sc1 and not self.good_comp:
                # reset good will. Will be re-evaluated above
                self.good_sc1 = True
                self.good_sc2 = True
                self.good_comp = True
                return Z
            elif self.good_sc1:
                self.good_sc1 = True
                self.good_sc2 = True
                self.good_comp = True
                return X
            elif self.good_sc2:
                self.good_sc1 = True
                self.good_sc2 = True
                self.good_comp = True
                return Y
            else:
                return W
            
            
            
                    
                

#------------------------------------------------------------------------------
# CONTRITE TIT-FOR-TAT VARIATIONS (simple TFT with the ability to apologize...
# ... for its own unwanted defection)
#------------------------------------------------------------------------------

class ContriteTFT_2p(pl.Player_4p4m):
    """
    A player that corresponds to Tit For Tat if there is no noise. In the case
    of a noisy match: if the opponent defects as a result of a noisy defection
    then ContriteTitForTat will become 'contrite' until it successfully
    cooperates.
    Contrite Tit For Tat: [Axelrod 1995, 1997 reprint]
    """
    
    name = "Contrite TFT (2p)"
    classifier = {
        "memory_depth": 1,
        "stochastic": False,
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }

    def __init__(self):
        super().__init__()
        self.contrite = False
        self.last_move = X

    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:

        if len(self.history) < 1:
            self.last_move = X
            return X

        # If contrite but managed to cooperate: apologise.
        if self.contrite and self.history[-1] == X:
            self.contrite = False
            self.last_move = X
            return X

        # Check if noise provoked opponent
        if self.last_move != self.history[-1]:  # Check if noise
            if self.history[-1] == W and SC1.history[-1] == X:
                self.contrite = True
        
        # Do not copy Y or Z because these moves do not apply to dyadic information sets
        if SC1.history[-1] == Y:
            self.last_move = W
            return W
        elif SC1.history[-1] == Z:
            self.last_move = X
            return X
        else:
            self.last_move = SC1.history[-1]
            return SC1.history[-1]



class ContriteTFT_3p_sb(pl.Player_4p4m):
    """
    A player that corresponds to Tit For Tat if there is no noise. In the case
    of a noisy match: if the opponent defects as a result of a noisy defection
    then ContriteTitForTat will become 'contrite' until it successfully
    cooperates.
    Contrite Tit For Tat: [Axelrod 1995, 1997 reprint]
    """

    name = "Contrite TFT (3p_sb)"
    classifier = {
        "memory_depth": 1,
        "stochastic": False,
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }

    def __init__(self):
        super().__init__()
        self.contrite_sc1 = False
        self.contrite_sc2 = False
        self.last_move = Z

    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:

        if len(self.history) < 1:
            self.last_move = Z
            return Z

        # If contrite with both SC1 and SC2 but managed to cooperate: apologise.
        if self.contrite_sc1 and self.contrite_sc2 and self.history[-1] == Z:
            self.contrite_sc1 = False
            self.contrite_sc2 = False
            self.last_move = Z
            return Z

        # If contrite with SC1 but managed to cooperate: apologise.
        if self.contrite_sc1 and self.history[-1] == X:
            self.contrite_sc1 = False
            self.last_move = X
            return X
        
        # If contrite with SC2 but managed to cooperate: apologise.
        if self.contrite_sc2 and self.history[-1] == Y:
            self.contrite_sc2 = False
            self.last_move = Y
            return Y

        # Check if noise provoked anyone
        if self.last_move != self.history[-1]:  # Check if noise
            if (self.history[-1] != X or self.history[-1] != Z) and (SC1.history[-1] == X or SC1.history[-1] == Z):
                self.contrite_sc1 = True
            if (self.history[-1] != Y or self.history[-1] != Z) and (SC2.history[-1] == Y or SC1.history[-1] == Z):
                self.contrite_sc2 = True
        
        # else play normal TFT (3p)
        if (SC1.history[-1] == X or SC1.history[-1] == Z) and (SC2.history[-1] == Y or SC2.history[-1] == Z):
            self.last_move = Z
            return Z #service both if both invest in me with XY
        elif SC1.history[-1] == X:
            self.last_move = X
            return X # in a tie between SC1's X and SC2's Y, always stay with "incumbent" SC1 -> deterministic
        elif SC2.history[-1] == Y:
            self.last_move = Y
            return Y
        elif SC1.history[-1] == Z:
            self.last_move = X
            return X
        elif SC2.history[-1] == Z:
            self.last_move = Y
            return Y
        else:
            self.last_move = W
            return W



class ContriteTFT_3p_ss(pl.Player_4p4m):
    """
    A player that corresponds to Tit For Tat if there is no noise. In the case
    of a noisy match: if the opponent defects as a result of a noisy defection
    then ContriteTitForTat will become 'contrite' until it successfully
    cooperates.
    Contrite Tit For Tat: [Axelrod 1995, 1997 reprint]
    """

    name = "Contrite TFT (3p_ss)"
    classifier = {
        "memory_depth": 1,
        "stochastic": False,
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }

    def __init__(self):
        super().__init__()
        self.contrite_sc1 = False
        self.contrite_sc2 = False
        self.last_move = X

    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:

        if len(self.history) < 1:
            self.last_move = X
            return X

        # If contrite with both SC1 and SC2 but managed to cooperate: apologise.
        if self.contrite_sc1 and self.contrite_sc2 and self.history[-1] == Z:
            self.contrite_sc1 = False
            self.contrite_sc2 = False
            self.last_move = Z
            return Z

        # If contrite with SC1 but managed to cooperate: apologise.
        if self.contrite_sc1 and self.history[-1] == X:
            self.contrite_sc1 = False
            self.last_move = X
            return X
        
        # If contrite with SC2 but managed to cooperate: apologise.
        if self.contrite_sc2 and self.history[-1] == Y:
            self.contrite_sc2 = False
            self.last_move = Y
            return Y

        # Check if noise provoked anyone
        if self.last_move != self.history[-1]:  # Check if noise
            if (self.history[-1] != X or self.history[-1] != Z) and (SC1.history[-1] == X or SC1.history[-1] == Z):
                self.contrite_sc1 = True
            if (self.history[-1] != Y or self.history[-1] != Z) and (SC2.history[-1] == Y or SC1.history[-1] == Z):
                self.contrite_sc2 = True
        
        # else play normal TFT (3p)
        if (SC1.history[-1] == X or SC1.history[-1] == Z) and (SC2.history[-1] == Y or SC2.history[-1] == Z):
            self.last_move = Z
            return Z #service both if both invest in me with XY
        elif SC1.history[-1] == X:
            self.last_move = X
            return X # in a tie between SC1's X and SC2's Y, always stay with "incumbent" SC1 -> deterministic
        elif SC2.history[-1] == Y:
            self.last_move = Y
            return Y
        elif SC1.history[-1] == Z:
            self.last_move = X
            return X
        elif SC2.history[-1] == Z:
            self.last_move = Y
            return Y
        else:
            self.last_move = W
            return W
      



class ContriteTFT_4p_sb(pl.Player_4p4m):
    """
    A player that corresponds to Tit For Tat if there is no noise. In the case
    of a noisy match: if the opponent defects as a result of a noisy defection
    then ContriteTitForTat will become 'contrite' until it successfully
    cooperates.
    Contrite Tit For Tat: [Axelrod 1995, 1997 reprint]
    """

    name = "Contrite TFT (4p_sb)"
    classifier = {
        "memory_depth": 1,
        "stochastic": False,
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }

    def __init__(self):
        super().__init__()
        self.contrite_sc1 = False
        self.contrite_sc2 = False
        self.last_move = Z

    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:

        if len(self.history) < 1:
            self.last_move = Z
            return Z

        # If contrite with both SC1 and SC2 but managed to cooperate: apologise.
        if self.contrite_sc1 and self.contrite_sc2 and self.history[-1] == Z:
            self.contrite_sc1 = False
            self.contrite_sc2 = False
            self.last_move = Z
            return Z

        # If contrite with SC1 but managed to cooperate: apologise.
        if self.contrite_sc1 and self.history[-1] == X:
            self.contrite_sc1 = False
            self.last_move = X
            return X
        
        # If contrite with SC2 but managed to cooperate: apologise.
        if self.contrite_sc2 and self.history[-1] == Y:
            self.contrite_sc2 = False
            self.last_move = Y
            return Y

        # Check if noise provoked anyone
        if self.last_move != self.history[-1]:  # Check if noise
            if (self.history[-1] != X or self.history[-1] != Z) and (SC1.history[-1] == X or SC1.history[-1] == Z):
                self.contrite_sc1 = True
            if (self.history[-1] != Y or self.history[-1] != Z) and (SC2.history[-1] == Y or SC1.history[-1] == Z):
                self.contrite_sc2 = True

        # else play normal TFT (4p_sb)
        if SC1.history[-1] == Z and SC2.history[-1] == Z and competitor.history[-1] == Z:
            self.last_move = Z
            return Z #support optimal outcome
        elif SC1.history[-1] == X and SC2.history[-1] == Y:
            self.last_move = Z
            return Z #service both if both invest in me with XY
        elif competitor.history[-1] == W and SC1.history[-1] != W and SC2.history[-1] != W:
            self.last_move = Z
            return Z # try to capture the market against uncooperative competitor
        elif SC1.history[-1] == X:
            self.last_move = X
            return X # in a tie between SC1's X and SC2's Y, always stay with "incumbent" SC1 -> deterministic
        elif SC2.history[-1] == Y:
            self.last_move = Y
            return Y
        elif SC1.history[-1] == Z:
            self.last_move = X
            return X
        elif SC2.history[-1] == Z:
            self.last_move = Y
            return Y
        else:
            self.last_move = W
            return W



class ContriteTFT_4p_ss(pl.Player_4p4m):
    """
    Four-player Contrite Tit-for-Tat with 'start small' approach.

    An error-tolerant strategy that can recover from noise-induced defections.
    Becomes 'contrite' after accidentally defecting and attempts to restore
    cooperation through apology moves.

    Key Features:
        - Tracks contrition state for both supply chain partners
        - Implements noise handling through last_move tracking
        - Starts with X and builds toward Z cooperation
        - Maintains cooperation flags for all players
        - Can recover from accidental defections

    References:
        Axelrod, R. (1995). The Evolution of Cooperation
        Wu, J. & Axelrod, R. (1995). How to Cope with Noise in the IPD

    Attributes:
        contrite_sc1 (bool): Contrition state for SC1
        contrite_sc2 (bool): Contrition state for SC2
        last_move (Action_4p4m): Tracks intended last move for noise detection
    """

    name = "Contrite TFT (4p_ss)"
    classifier = {
        "memory_depth": 2,
        "stochastic": False,
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }

    def __init__(self):
        super().__init__()
        self.contrite_sc1 = False
        self.contrite_sc2 = False
        self.last_move = X
        self.cooperative_sc1 = True
        self.cooperative_sc2 = False
        self.cooperative_comp = False

    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:

        if len(self.history) < 2:
            self.last_move = X
            return X
        else:
            # If contrite with both SC1 and SC2 but managed to cooperate: apologise.
            if self.contrite_sc1 and self.contrite_sc2 and self.history[-1] == Z:
                self.contrite_sc1 = False
                self.contrite_sc2 = False
                self.last_move = Z
                return Z

            # If contrite with SC1 but managed to cooperate: apologise.
            if self.contrite_sc1 and self.history[-1] == X:
                self.contrite_sc1 = False
                self.last_move = X
                return X
            
            # If contrite with SC2 but managed to cooperate: apologise.
            if self.contrite_sc2 and self.history[-1] == Y:
                self.contrite_sc2 = False
                self.last_move = Y
                return Y

            # Check if noise provoked anyone
            if self.last_move != self.history[-1]:  # Check if noise
                if (self.history[-1] != X or self.history[-1] != Z) and (SC1.history[-1] == X or SC1.history[-1] == Z):
                    self.contrite_sc1 = True
                if (self.history[-1] != Y or self.history[-1] != Z) and (SC2.history[-1] == Y or SC1.history[-1] == Z):
                    self.contrite_sc2 = True

            # else play normal TFT (4p_ss)       
            if SC1.history[-1] == W and (competitor.history[-2] != W or competitor.history[-2] != X):
                self.cooperative_sc1 = False
            else:
                self.cooperative_sc1 = True
            if SC2.history[-1] == W and (competitor.history[-2] != W or competitor.history[-2] != Y):
                self.cooperative_sc2 = False
            else:
                self.cooperative_sc2 = True
            if competitor.history[-1] == W:
                self.cooperative_comp = False
            else:
                self.cooperative_comp = True  
            
            if self.cooperative_sc1 and self.cooperative_sc2: # if SC1 and SC2 are cooperative
                if self.history[-1] != Z:
                    self.last_move = Z
                    return Z # try to establish triadic cooperation if both are cooperative
        
            if SC1.history[-1] == Z and SC2.history[-1] == Z and competitor.history[-1] == Z:
                self.last_move = Z
                return Z #support optimal outcome
            elif SC1.history[-1] == X and SC2.history[-1] == Y:
                self.last_move = Z
                return Z #service both if both invest in me with XY
            elif competitor.history[-1] == W and SC1.history[-1] != W and SC2.history[-1] != W:
                self.last_move = Z
                return Z # try to capture the market against uncooperative competitor
            elif SC1.history[-1] == X:
                self.last_move = X
                return X # in a tie between SC1's X and SC2's Y, always stay with "incumbent" SC1 -> deterministic
            elif SC2.history[-1] == Y:
                self.last_move = Y
                return Y
            elif SC1.history[-1] == Z:
                self.last_move = X
                return X
            elif SC2.history[-1] == Z:
                self.last_move = Y
                return Y
            else:
                self.last_move = W
                return W
            
        
        
        
        
        
#------------------------------------------------------------------------------
# PAVLOV VARIATIONS ("Win-stay, lose-shift" strategies)
#------------------------------------------------------------------------------
"""
A strategy family implementing "win-stay, lose-shift" behavior patterns.

These strategies repeat their previous move if it led to a good outcome
and change their move if the outcome was poor. The definition of "good"
and "poor" outcomes varies by information set.

Attributes:
    memory_depth (int): 1 - needs only previous round's outcome
    stochastic (bool): False - behavior is deterministic
    
Win Conditions:
    - 2p: Mutual cooperation or mutual defection with SC1
    - 3p: Successful cooperation with either/both SCs
    - 4p: Achieving optimal outcome or outperforming competitor
    
Shift Patterns:
    - On mutual defection: Try cooperation
    - On unilateral defection: Switch to defection
    - On partial cooperation: Try simpler cooperation form
"""
    
class Pavlov_2p(pl.Player_4p4m):
 
    name = "Win-stay, lose-shift (2p)"
    classifier = {
        "memory_depth": 2,
        "stochastic": False,
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }

    def __init__(self):
        super().__init__()
    
    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:
        """Actual strategy definition that determines player's action."""
        
        if len(self.history) < 1:
            return X

        last_round = (self.history[-1], SC1.history[-1])
        if last_round == (X, X) or last_round == (W,W):
            return X
        else:
            return W
        
        
class Pavlov_3p_sb(pl.Player_4p4m):
 
    name = "Win-stay, lose-shift (3p_sb)"
    classifier = {
        "memory_depth": 1,
        "stochastic": False,
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }

    def __init__(self):
        super().__init__()
    
    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:
        
        if len(self.history) < 1:
            return Z

        #last_round = (self.history[-1], competitor.history[-1], SC1.history[-1], SC2.history[-1])
        # Win-stay
        if self.history[-1] == Z and (SC1.history[-1] == Z or SC1.history[-1] == X) and (SC2.history[-1] == Z or SC2.history[-1] == Y):
                return Z
        elif self.history[-1] == X and (SC1.history[-1] == X or SC1.history[-1] == Z):
            return X
        elif self.history[-1] == Y and (SC2.history[-1] == Y or SC2.history[-1] == Z):
            return Y
        elif self.history[-1] == W and (SC1.history[-1] == Z or SC1.history[-1] == X) and (SC2.history[-1] == Z or SC2.history[-1] == Y):
            return W
        
        # Lose-shift
        elif self.history[-1] != W and not (SC1.history[-1] == Z or SC1.history[-1] == X) and not (SC2.history[-1] == Z or SC2.history[-1] == Y):
            return W
        elif (self.history[-1] != W and self.history[-1] != X) and (SC1.history[-1] == Z or SC1.history[-1] == X):
            return X
        elif (self.history[-1] != W and self.history[-1] != Y) and (SC2.history[-1] == Z or SC2.history[-1] == Y):
            return Y
        elif self.history[-1] == W and (SC1.history[-1] == W or SC1.history[-1] == Y) and (SC2.history[-1] == W or SC2.history[-1] == X):
            return Z
        elif self.history[-1] == X and not (SC1.history[-1] == X or SC1.history[-1] == Z):
            return W
        elif self.history[-1] == Y and not (SC2.history[-1] == Y or SC2.history[-1] == Z):
            return W
        else:
            return W



class Pavlov_3p_ss(pl.Player_4p4m):
    """
    Four-player Win-Stay, Lose-Shift strategy with 'start small' behavior.

    Implements the Pavlov principle in a four-player context: repeats previous
    move if it led to a good outcome, changes move if outcome was poor.
    Starts with simpler cooperation forms before attempting complex ones.

    Strategy Logic:
        - Stays with move if it resulted in mutual cooperation
        - Shifts to alternative move after mutual defection
        - Handles asymmetric outcomes by shifting to appropriate response
        - Builds trust gradually starting from dyadic cooperation

    Game Theory Principles:
        - Reinforcement learning inspired
        - Can recover from bad states
        - Performs well in noisy environments
        - Forms stable cooperative relationships

    Attributes:
        memory_depth (int): 1 - needs only previous round's outcome
        stochastic (bool): False - deterministic decision making
    """
    
    name = "Win-stay, lose-shift (3p_ss)"
    classifier = {
        "memory_depth": 1,
        "stochastic": False,
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }

    def __init__(self):
        super().__init__()
    
    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:
        
        if len(self.history) < 1:
            return X

        #last_round = (self.history[-1], competitor.history[-1], SC1.history[-1], SC2.history[-1])
        # Win-stay
        if self.history[-1] == Z and (SC1.history[-1] == Z or SC1.history[-1] == X) and (SC2.history[-1] == Z or SC2.history[-1] == Y):
                return Z
        elif self.history[-1] == X and (SC1.history[-1] == X or SC1.history[-1] == Z):
            return X
        elif self.history[-1] == Y and (SC2.history[-1] == Y or SC2.history[-1] == Z):
            return Y
        elif self.history[-1] == W and (SC1.history[-1] == Z or SC1.history[-1] == X) and (SC2.history[-1] == Z or SC2.history[-1] == Y):
            return W
        
        # Lose-shift
        elif self.history[-1] != W and not (SC1.history[-1] == Z or SC1.history[-1] == X) and not (SC2.history[-1] == Z or SC2.history[-1] == Y):
            return W
        elif (self.history[-1] != W and self.history[-1] != X) and (SC1.history[-1] == Z or SC1.history[-1] == X):
            return X
        elif (self.history[-1] != W and self.history[-1] != Y) and (SC2.history[-1] == Z or SC2.history[-1] == Y):
            return Y
        elif self.history[-1] == W and (SC1.history[-1] == W or SC1.history[-1] == Y) and (SC2.history[-1] == W or SC2.history[-1] == X):
            return Z
        elif self.history[-1] == X and not (SC1.history[-1] == X or SC1.history[-1] == Z):
            return W
        elif self.history[-1] == Y and not (SC2.history[-1] == Y or SC2.history[-1] == Z):
            return W
        else:
            return W




   
        

#------------------------------------------------------------------------------
# NASTY STRATEGIES (uncooperative start and/or unprovoked defection)
#------------------------------------------------------------------------------
"""
A family of unforgiving strategies that attempt to exploit or punish other players.

These strategies typically start uncooperatively or quickly switch to 
uncooperative behavior based on strict criteria. They often maintain
long memories of defections.

Attributes:
    memory_depth (float): inf - keeps permanent grudges
    stochastic (bool): Strategy dependent
    
Common Variations:
    - Grudger: Never forgets a defection
    - Tester: Probes for exploitable behavior
    - ZD Extortion: Uses probability to enforce unfair payoff ratios
    
Key Behaviors:
    - Permanent retaliation after defection
    - Initial defection to test response
    - Probabilistic exploitation
"""

class SimpleGrudger_2p(pl.Player_4p4m):
 
    name = "Simple Grudger (2p)"
    classifier = {
        "memory_depth": 2,
        "stochastic": False,
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }

    def __init__(self):
        super().__init__()
    
    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:
        """Actual strategy definition that determines player's action."""
        
        if len(self.history) < 1:
            return X
        
        else:
            if SC1.invest_none or SC1.invest_SC2:
                return W
            else:
                return X
        
        
            
class SimpleGrudger_3p_sb(pl.Player_4p4m):
 
    name = "Simple Grudger (3p_sb)"
    classifier = {
        "memory_depth": 2,
        "stochastic": False,
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }

    def __init__(self):
        super().__init__()
    
    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:
        """Actual strategy definition that determines player's action."""
        
        if len(self.history) < 1:
            return Z
        
        else:
            if (SC1.invest_none or SC1.invest_SC2) and (SC2.invest_none or SC2.invest_SC1):
                return W
            elif SC2.invest_none or SC2.invest_SC1:
                return X
            elif SC1.invest_none or SC1.invest_SC2:
                return Y
            else:
                return Z
            
            

class Tester_2p(pl.Player_4p4m):
    name = "Tester by Gladstein (2p)"
    classifier = {
        "memory_depth": float("inf"),
        "stochastic": False,
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }

    def __init__(self) -> None:
        super().__init__()
        # This strategy assumes the opponent is a patsy
        self.patsy_sc1 = True
        
        
    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:
        """Actual strategy definition that determines player's action."""
        # manually adapt number_of_players
        if not self.history:
            return W
        
        # Is the opponent a patsy?
        if self.patsy_sc1:
            # If the opponent defects, apologize and play TFT.
            if SC1.history[-1] != X or SC1.history[-1] != Z:
                self.patsy_sc1 = False
                return X
            cooperation_ratio = self.invest_SC1/len(self.history)
            if cooperation_ratio > 0.5:
                return W
            else:
                return X
        else:
            # Play TFT (but do not copy Y's and Z's)
            if SC1.history[-1] == Z:
                return X
            if SC1.history[-1] == Y:
                return W
            return SC1.history[-1]  


class Tester_3p(pl.Player_4p4m):
    name = "Tester by Gladstein (3p)"
    classifier = {
        "memory_depth": float("inf"),
        "stochastic": False,
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }

    def __init__(self) -> None:
        super().__init__()
        # This strategy assumes the opponent is a patsy
        self.patsy_sc1 = True
        self.patsy_sc2 = True
        
        
    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:
        """Actual strategy definition that determines player's action."""
        # manually adapt number_of_players
        if not self.history:
            return W
        else: 
            return W
        
            
            
class Tester_4p(pl.Player_4p4m):
    name = "Tester by Gladstein (4p)"
    classifier = {
        "memory_depth": float("inf"),
        "stochastic": False,
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }

    def __init__(self) -> None:
        super().__init__()
        # This strategy assumes the opponent is a patsy
        self.nasty_sc1 = False
        self.nasty_sc2 = False
        self.nasty_comp = False
        self.cooperative_sc1 = True
        self.cooperative_sc2 = True
        self.cooperative_comp = True
        
        
    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:
        """Actual strategy definition that determines player's action."""
        # manually adapt number_of_players
        if len(self.history) < 3:
            if len(self.history) < 2:
                return W
            else:
                return Z

        else: # learn from actions of competitor and others
            if len(self.history) == 3:
                # What if competitor is also nasty?
                if competitor.history[-3] == W:
                    self.nasty_comp = True
                    self.cooperative_comp = False
                    # SC1 cooperates even though my competitor and I did not
                    if SC1.history[-2] != W:
                        self.cooperative_sc1 = True
                        self.nasty_sc1 = False
                    # SC2 cooperates even though my competitor and I did not
                    if SC2.history[-2] != W:
                        self.cooperative_sc2 = True
                        self.nasty_sc2 = False
                
                # What if competitor is not nasty?
                if competitor.history[-3] == Z:
                    if SC1.history[-2] != Y and SC1.history[-2] != Z:
                        self.cooperative_sc1 = False
                        self.nasty_sc1 = True
                    if SC2.history[-2] != X and SC2.history[-2] != Z:
                        self.cooperative_sc2 = False
                        self.nasty_sc2 = True    
                    
                if competitor.history[-3] == X:
                    if SC2.history[-2] != X and SC2.history[-2] != Z:
                        self.cooperative_sc2 = False
                        self.nasty_sc2 = True
                    if SC1.history[-3] != W and SC1.history[-2] == W:
                        self.cooperative_sc1 = True
                        self.nasty_sc1 = True
                
                if competitor.history[-3] == Y:
                    if SC1.history[-2] != Y and SC1.history[-2] != Z:
                        self.cooperative_sc1 = False
                        self.nasty_sc1 = True
                    if SC2.history[-3] != W and SC2.history[-2] == W:
                        self.cooperative_sc2 = True
                        self.nasty_sc2 = True
                
                # thieves recognize each other
                if SC1.history[-3] == W and SC1.history[-2] == W and SC1.history[-1] == Z:
                    self.nasty_sc1 = True
                    self.cooperative_sc1 = True
                if SC2.history[-3] == W and SC2.history[-2] == W and SC2.history[-1] == Z:
                    self.nasty_sc2 = True
                    self.cooperative_sc2 = True
            
            if len(self.history) >= 3:
                
                if self.cooperative_sc1 and self.nasty_sc1 and self.cooperative_sc2 and self.nasty_sc2:
                    return Z
                elif self.cooperative_sc1 and not self.nasty_sc1 and self.cooperative_sc2 and not self.nasty_sc2:
                    return W
                elif self.cooperative_sc1 and self.nasty_sc1:
                    return X
                elif self.cooperative_sc2 and self.nasty_sc2:
                    return Y
                else: 
                    return W
                


class ZD_Extortion_2p(pl.Player_4p4m):
    name = "ZD Extorsion (2p)"
    classifier = {
        "memory_depth": 1,
        "stochastic": True,
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }

    def __init__(self) -> None:
        super().__init__()
        # This strategy assumes the opponent is a patsy

        
        
    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:
        """Actual strategy definition that determines player's action."""
        # manually adapt number_of_players
        if not self.history:
            return X
        else:
            random_prob = random.random() 
            # To verify that a new random_prob is generated each turn, uncomment the next line
            # print(f"Turn {len(self.history)}, Random probability: {random_prob}")  # Debug line
            if self.history[-1] == X and (SC1.history[-1] == X or SC1.history[-1] == Z):
                if random_prob < round(float(8/9), 5):
                    return X
                else:
                    return W
            if self.history[-1] == X and (SC1.history[-1] != X and SC1.history[-1] != Z):
                if random_prob < 0.5:
                    return X
                else:
                    return W
            if self.history[-1] != X and (SC1.history[-1] == X or SC1.history[-1] == Z):
                if random_prob < round(float(1/3), 5):
                    return X
                else:
                    return W
            else:         
                return W                
                      
                
                
                
class ZD_Extortion_4p(pl.Player_4p4m):
    name = "ZD Extorsion (4p)"
    classifier = {
        "memory_depth": 1,
        "stochastic": True,
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }

    def __init__(self) -> None:
        super().__init__()
        # This strategy assumes the opponent is a patsy

        
        
    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:
        """Actual strategy definition that determines player's action."""
        # manually adapt number_of_players
        if not self.history:
            return Z
        else:
            random_prob: float = 0.0 #the random number will be generated for each condition separately
            
            # To verify that a new random_prob is generated each turn, uncomment the next line
            # print(f"Turn {len(self.history)}, Random probability: {random_prob}")  # Debug line
            
            # The intuitive rule for this strategy is to: 
            # # Reciprocate optimal outcomes (ZZZZ, XuXu, YuuY) only with p = 8/9, 
            # # Apologize with p = 1/3 (cooperate after getting temptation), 
            # # Cooperate despite getting a sucker payoff with p = 1/2
            # # Cooperate after mutual defection with p = 0
            
            # Consider Z-cases first
            if SC1.history[-1] == X and SC2.history[-1] == Y:
                return Z
            
            elif self.history[-1] == Z and SC1.history[-1] == Z and SC2.history[-1] == Z and competitor.history[-1] == Z:
                random_prob = random.random()
                if random_prob < round(float(8/9), 5):
                    return Z
                else:
                    pass # evaluate X and Y in conditions below 
            
            elif self.history[-1] == Z and SC1.history[-1] == Z and SC2.history[-1] == Z and competitor.history[-1] != Z:
                random_prob = random.random()
                if random_prob < round(float(1/3), 5):
                    return Z
                else:
                    pass # evaluate X and Y in conditions below
            
            elif self.history[-1] != Z and SC1.history[-1] == Z and SC2.history[-1] == Z and competitor.history[-1] == Z:
                random_prob = random.random()
                if random_prob < 0.5:
                    return Z
                else:
                    pass
        
            # Consider X cases
            if self.history[-1] == X and (SC1.history[-1] == X or SC1.history[-1] == Z):
                random_prob = random.random()
                if random_prob < round(float(8/9), 5):
                    return X
                else:
                    pass
            elif self.history[-1] == X and (SC1.history[-1] != X and SC1.history[-1] != Z):
                random_prob = random.random()
                if random_prob < 0.5:
                    return X
                else:
                    pass
            elif self.history[-1] != X and (SC1.history[-1] == X or SC1.history[-1] == Z):
                random_prob = random.random()
                if random_prob < round(float(1/3), 5):
                    return X
                else:
                    pass
            
            # Consider Y cases
            if self.history[-1] == Y and (SC2.history[-1] == Y or SC2.history[-1] == Z):
                random_prob = random.random()
                if random_prob < round(float(8/9), 5):
                    return Y
                else:
                    pass
            elif self.history[-1] == Y and (SC2.history[-1] != Y and SC2.history[-1] != Z):
                random_prob = random.random()
                if random_prob < 0.5:
                    return Y
                else:
                    pass
            elif self.history[-1] != Y and (SC2.history[-1] == Y or SC2.history[-1] == Z):
                random_prob = random.random()
                if random_prob < round(float(1/3), 5):
                    return Y
                else:
                    pass            
            
            return W                     

            
          
          
            

#------------------------------------------------------------------------------
# Experimental strategies (business interpretation, focus on competitor)
#------------------------------------------------------------------------------

class TFT_2p_comp_avoid(pl.Player_4p4m):
    name = "Avoidant Competitive TFT (2p)"
    classifier = {
        "memory_depth": 2,
        "stochastic": False,
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }

    def __init__(self, starting_move=X):
        self.starting_move = starting_move
        super().__init__()
    
    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:
        """Actual strategy definition that determines player's action."""
        if not self.history:
            return self.starting_move
        elif competitor.history[-1] == Z:
            return Z
        elif competitor.history[-1] == X:
            return X
        elif competitor.history[-1] == Y:
            return Y
        else:
            return W



class TFT_2p_comp_contest(pl.Player_4p4m):
    name = "Contesting Competitive TFT (2p)"
    classifier = {
        "memory_depth": 2,
        "stochastic": False,
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }

    def __init__(self):
        super().__init__()
    
    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:
        """Actual strategy definition that determines player's action."""
        if len(self.history) < 1:
            return X
        elif competitor.history[-1] == Z:
            return X #poach from samaritan
        elif competitor.history[-1] == Y:
            return X
        elif competitor.history[-1] == X:
            return Y
        else:
            return W                


class TFT_switching_3p(pl.Player_4p4m):
 
    name = "Switching TFT (3p)"
    classifier = {
        "memory_depth": 2,
        "stochastic": False,
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }

    def __init__(self):
        super().__init__()
    
    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:
        
        #strategy
        if len(self.history) < 1:
            return Z
        elif (SC1.history[-1] == X or SC1.history[-1] == Z) and (SC2.history[-1] == Y or SC2.history[-1] == Z):
            return Z #service both if both invest in me with XY
        elif self.history[-1] == X and SC1.history[-1] != X and SC1.history[-1] != Z:
            return Y #try cooperation with SC2 every third turn if SC1 didnt work
        elif SC1.history[-1] == X:
            return X # in a tie between SC1's X and SC2's Y, always stay with "incumbent" SC1 -> deterministic
        elif SC2.history[-1] == Y:
            return Y
        elif SC1.history[-1] == Z:
            return X
        elif SC2.history[-1] == Z:
            return Y
        else:
            return W
        
        
                
class SwitchingGrudger_3p(pl.Player_4p4m):
 
    name = "Switching Grudger TFT (3p)"
    classifier = {
        "memory_depth": 2,
        "stochastic": False,
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }

    def __init__(self):
        super().__init__()
    
    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:
        """Actual strategy definition that determines player's action."""
        
        #auxiliary parameters
        turns = len(self.history)
        third_turn_cond = False
        fourth_turn_cond = False
        grudge_SC1 = False
        grudge_SC2 = False
        grudge_memory_SC1 = 0 #up to 5 rounds
        grudge_memory_SC2 = 0 #up to 5 rounds

        #strategy
            #first 4 moves are deterministic: try XX (generously wait to sway SC1 from non-cooperative starting move ...
            #if SC1 wont cooperate, go to SC2. If either SC-partner doesnt cooperate, hold grudge for 5 rounds.

        #turns 1-4
        if turns <= 1: #starting 2 moves, see if SC1 reacts to cooperation.
            return X
        elif turns == 2: # third turn
            third_turn_cond == True
        elif third_turn_cond:
            if self.history[-2] == X and (SC1.history[-1] == Z and SC2.history[-1] == Z):
                return Z #support optimal outcome immediately
            elif self.history[-2] == X and (SC1.history[-1] == X and SC2.history[-1] == Y):
                return Z #exploitable if competitor is not also taken into consideration -> allrounder-TFT
            elif self.history[-2] == X and (SC1.history[-1] != X or SC1.history[-1] != Z):
                return Y #check immediatly in the second turn, whether SC2 is more cooperative than SC1
                grudge_SC1 = True
                grudge_memory_SC2 = 1 
        elif turns == 3: #fourth turn
            fourth_turn_cond = True
        elif fourth_turn_cond == True:
            if self.history[-2] == Y and (SC2.history[-1] != Y and SC2.history[-1] != Z):
                return W #support optimal outcome immediately
                grudge_SC2 = True
                grudge_memory_SC2 = 1
            else: 
                return Y

        #after four turns, act according to grudges
        elif turns > 3: 
            if grudge_memory_SC1 == 0 and grudge_memory_SC2 == 0: #without grudges, enact normal TFT  
                if SC1.history[-1] == Z and SC2.history[-1] == Z:
                    return Z #support optimal outcome
                elif SC1.history[-1] == X:
                    return X # in a tie between SC1's X and SC2's Y, always stay with "incumbent" SC1 -> deterministic
                elif SC2.history[-1] == Y:
                    return Y
                elif SC1.history[-1] == Z:
                    return X
                elif SC2.history[-1] == Z:
                    return Y
                else:
                    return W
                    
            elif grudge_memory_SC1 > 0 and grudge_memory_SC2 > 0:
                while grudge_memory_SC1 <= 6 and grudge_memory_SC2 <= 6:
                    return W
                    grudge_memory_SC1 += 1 
                    grudge_memory_SC2 += 1
                    # grudge only updates, if no one cooperates. 
                    # if i grudge SC1 but SC2 cooperates, i dont betray SC2 after 5 turns, so grudge stays.
                    
            elif grudge_memory_SC1 > 0 and grudge_memory_SC2 == 0:
                return Y
            elif grudge_memory_SC1 == 0 and grudge_memory_SC2 > 0:
                return X
            else:
                return W



class ForgivingGrudger_2p(pl.Player_4p4m):
 
    name = "Forgiving Grudger (2p)"
    classifier = {
        "memory_depth": 2,
        "stochastic": False,
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }

    def __init__(self):
        super().__init__()
        self.mem_length = 10
        self.grudged = False
        self.grudge_memory = 0        
    
    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:
        """Actual strategy definition that determines player's action."""
        if self.grudge_memory == self.mem_length:
            self.grudge_memory = 0
            self.grudged = False

        if W in SC1.history[-1:]:
            self.grudged = True

        if self.grudged:
            self.grudge_memory += 1
            return W
        return X
                
                
                
class TFT_aon_4p(pl.Player_4p4m):
    name = "All-or-nothing TFT (WZ only, 4p)"
    classifier = {
        "memory_depth": 1,
        "stochastic": False,
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }
    
    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:  
        if len(self.history) < 1:
            return Z
        elif SC1.history[-1] == Z and SC2.history[-1] == Z and competitor.history[-1] == Z:
            return Z #optimal collaborative outcome
        else:
            return W               



class Handshaker(pl.Player_4p4m):
    name = "Handshake Short-Memory"
    classifier = {
        "memory_depth": 6,
        "stochastic": False,
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }
    
    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:  
        if len(self.history) < 2:
            return X
        if len(self.history) < 4:
            return Y
        if len(self.history) < 6:
            return W
        if len(self.history) < 7:
            return Z

        array_SC1 = SC1.history[-6:]
        array_SC2 = SC2.history[-6:]
        array_competitor = competitor.history[-6:]

        X_SC1_counts = array_SC1.count(X)
        Y_SC2_counts = array_SC2.count(Y)
        W_competitor_counts = array_competitor.count(W)

        if W_competitor_counts > 2:
            return W #build cartel
        if X_SC1_counts-Y_SC2_counts > 0:
            return X
        if X_SC1_counts-Y_SC2_counts < 0:
            return Y
        if X_SC1_counts-Y_SC2_counts == 0:
            return W              
            
        
class IntensityDecisionRule1(pl.Player_4p4m):
    name = "Full-intensity TFT"
    classifier = {
        "memory_depth": 2,
        "stochastic": False,
        "long_run_time": False,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }

    def __init__(self):
        super().__init__()

    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:
        """Actual strategy definition that determines player's action."""
        # manually adapt number_of_players
        turn_10_intervals = 0
        if len(self.history) < 10:
            return X
        elif len(self.history) >= 10:
            while turn_10_intervals < 10:
                if SC1.history.count(SC1.invest_SC1) > 7:
                    return X
                turn_10_intervals +=1
        else:
            return W        
        
 
            
        

#------------------------------------------------------------------------------
# GENETIC ALGORITHM STRATEGIES (for completely randomly initialized chromosomes)
# ... (to be added: a GA strategy that reads chromosomes from csv files and ...
# ... competes against other strategies like TFT)
#------------------------------------------------------------------------------

class GeneticAlgorithmPlayer(pl.Player_4p4m):
    """
    A strategy that evolves its behavior through genetic algorithms.
    
    These strategies use chromosomes to encode decision rules for all possible
    game states. The chromosome structure and interpretation depend on the
    information set and memory depth.
    
    Attributes:
        chromosome (list): Encoded strategy rules
        memory_depth (int): Number of previous moves considered
        information_set (str): Type of information used ('complete'/'ignore_comp')
        premise_count_per_memory_slot (int): Number of premises per memory slot
        
    Chromosome Structure:
        - Premises: Initial conditions for start of game
        - State mappings: Responses to all possible game states
        - Memory depth determines the size of state space
        
    Information Sets:
        - complete: Uses all player moves
        - ignore_comp: Simplifies competitor moves
    """
    
    name = "Genetic Algo Player"
    classifier = {
        "memory_depth": 2,
        "stochastic": False,
        "long_run_time": True,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }
    def __init__(self, chromosome, memory_depth, information_set, premise_count_per_memory_slot =4):
        super().__init__()
        self.memory_depth = memory_depth
        self.information_set = information_set
        self.chromosome = chromosome
        self.premise_count_per_memory_slot = premise_count_per_memory_slot

            
         # Create mapping dictionaries once during initialization
        self.all_available_moves = [W, X, Y, Z]
        self.all_possible_interactions = [p for p in itertools.product(self.all_available_moves, repeat=4)]
        self.state_to_index_map = {state: index for index, state in enumerate(self.all_possible_interactions)}
        
        if self.memory_depth == 2:
            # Pre-compute the chunked indices for 2-memory states
            self.indexing_all_2memory_states = [i for i in range(len(self.all_possible_interactions)*len(self.all_possible_interactions))]
            # The random chromosome will be interpreted in the following way: the first 256 genes code for all possible states (last turn) 
            # following the first possible states (2nd to last turn)
            self.chunk_indexing_all_2memory_states = [self.indexing_all_2memory_states[i:i+len(self.all_possible_interactions)] 
                                                for i in range(0, len(self.indexing_all_2memory_states), len(self.all_possible_interactions))]
            
        
    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:
        if self.memory_depth == 2:
            premise_state1 = (self.chromosome[0], self.chromosome[1], self.chromosome[2], self.chromosome[3])
            premise_state2 = (self.chromosome[4], self.chromosome[5], self.chromosome[6], self.chromosome[7])
            
            
            
            if not self.history:
                # Map the premise states to the index in the chromosome
                index = self.map_states_to_indices(premise_state1, premise_state2)
                return self.chromosome[index]  # 8 is the offset for the premises
            
            elif len(self.history) < 2:
                last_state = (self.history[-1], competitor.history[-1], SC1.history[-1], SC2.history[-1])
                index = self.map_states_to_indices(premise_state2, last_state)
                return self.chromosome[index]
                
            elif len(self.history) >= 2:
                second_to_last_state = (self.history[-2], competitor.history[-2], SC1.history[-2], SC2.history[-2])
                last_state = (self.history[-1], competitor.history[-1], SC1.history[-1], SC2.history[-1])
                index = self.map_states_to_indices(second_to_last_state, last_state)
                return self.chromosome[index]
            
            
        elif self.memory_depth == 1:
            premise_last_state = (self.chromosome[0], self.chromosome[1], self.chromosome[2], self.chromosome[3])
        
            if not self.history:
                # Map the premise states to the index in the chromosome
                index = self.map_states_to_indices(second_to_last_state= None, last_state = premise_last_state)
                return self.chromosome[index]  # 8 is the offset for the premises
            
            else:
                last_state = (self.history[-1], competitor.history[-1], SC1.history[-1], SC2.history[-1])
                index = self.map_states_to_indices(second_to_last_state= None, last_state = premise_last_state)
                return self.chromosome[index]
            
        
    def map_states_to_indices(self, second_to_last_state, last_state):
        if self.memory_depth == 2:
            # "+8" to account for the premises
            return 8 + self.chunk_indexing_all_2memory_states[self.state_to_index_map[second_to_last_state]][self.state_to_index_map[last_state]]
        elif self.memory_depth == 1:
            # "+4" to account for the premises
            return 4 + self.state_to_index_map[last_state]

class GeneticAlgorithmPlayer_ignoreCompetitor(pl.Player_4p4m):
    """
    A strategy that evolves its behavior through genetic algorithms.
    
    These strategies use chromosomes to encode decision rules for all possible
    game states. The chromosome structure and interpretation depend on the
    information set and memory depth.
    
    Attributes:
        chromosome (list): Encoded strategy rules
        memory_depth (int): Number of previous moves considered
        information_set (str): Type of information used ('complete'/'ignore_comp')
        premise_count_per_memory_slot (int): Number of premises per memory slot
        
    Chromosome Structure:
        - Premises: Initial conditions for start of game
        - State mappings: Responses to all possible game states
        - Memory depth determines the size of state space
        
    Information Sets:
        - complete: Uses all player moves
        - ignore_comp: Simplifies competitor moves
    """
    
    name = "GeneticAlgoPlayer (ignoreComp)"
    classifier = {
        "memory_depth": 3,
        "stochastic": False,
        "long_run_time": True,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }
    def __init__(self, chromosome, memory_depth, information_set, premise_count_per_memory_slot = 3):
        super().__init__()
        self.memory_depth = memory_depth
        self.chromosome = chromosome
        self.information_set = information_set

            
         # Create mapping dictionaries once during initialization
        self.premise_count_per_memory_slot = premise_count_per_memory_slot
        self.premise_length = self.memory_depth * self.premise_count_per_memory_slot  # 3 premises per memory slot
        self.chromosome_indices = list(range(self.premise_length, len(self.chromosome)))

        self.self_available_moves = [W, X, Y, Z]
        self.sc1_available_moves = [X, Z, W] # where W is either Y or W
        self.sc2_available_moves = [Y, Z, W] # where W is either X or W
        self.all_states_per_turn = []
        state_list = []
        for self_move in self.self_available_moves:
            for sc1_move in self.sc1_available_moves: 
                for sc2_move in self.sc2_available_moves:
                    state_list.append(self_move)
                    state_list.append(sc1_move)
                    state_list.append(sc2_move)
                    self.all_states_per_turn.append(tuple(state_list))
                    state_list = []
        self.length_of_states = len(self.all_states_per_turn)
        
        self.state_to_index_map = {state: index for index, state in enumerate(self.all_states_per_turn)}
        self.chunked_indexed_chromosome = self.create_n_memory_state_indexing(self.length_of_states, self.memory_depth)
    
    
    
    def strategy(self, competitor: pl.Player_4p4m, SC1: pl.Player_4p4m, SC2: pl.Player_4p4m) -> Action_4p4m:
        #print("\n=== New Turn ===")
        #print(f"Current history length: {len(self.history)}")
    
        
        # Create premise states
        premise_states = []
        for i in range(self.memory_depth):
            start_idx = i * self.premise_count_per_memory_slot  
            sc1_move = self.chromosome[start_idx + 1]
            if sc1_move == Y:  # Convert Y to W for SC1
                sc1_move = W
            sc2_move = self.chromosome[start_idx + 1]
            if sc2_move == X:  # Convert X to W for SC2
                sc2_move = W
            state = (
                self.chromosome[start_idx],
                sc1_move,
                sc2_move,
                #self.chromosome[start_idx + 1],
                #self.chromosome[start_idx + 2]
            )
            premise_states.append(state)
        
        #print(f"Premise states created: {premise_states}")

        # Initialize state_history with fixed length of memory_depth
        state_history = [None] * self.memory_depth
        history_length = len(self.history)

        if not self.history:
            # First turn - use all premise states
            state_history = premise_states.copy()
            #print("First turn: Using all premise states")
        else:
            #print("\nBuilding state history from game history:")
            # Fill from newest to oldest
            for i in range(min(history_length, self.memory_depth)):
                idx = history_length - 1 - i  # Start from most recent
                
                # Convert SC1 and SC2 moves according to simplified rules
                sc1_move = SC1.history[idx]
                if sc1_move == Y:  # Convert Y to W for SC1
                    sc1_move = W
                    
                sc2_move = SC2.history[idx]
                if sc2_move == X:  # Convert X to W for SC2
                    sc2_move = W
                
                state = (
                    self.history[idx],  # Keep all self moves
                    sc1_move,           # Simplified SC1 move
                    sc2_move            # Simplified SC2 move
                )
                state_history[self.memory_depth - 1 - i] = state
                #print(f"Added game state at position {self.memory_depth - 1 - i}: {state}")
            # Fill remaining slots with premise states if needed
            remaining_slots = self.memory_depth - min(history_length, self.memory_depth)
            #print(f"\nFilling {remaining_slots} remaining slots with premise states:")
            if remaining_slots > 0:
                for i in range(remaining_slots):
                    remainder_idx = -(remaining_slots - i)
                    state_history[i] = premise_states[remainder_idx]
                    #print(f"Added premise state at position {i}: {premise_states[remainder_idx]}")
        
        #print(f"\nFinal state_history: {state_history}")
        index = self.get_chromosome_index(state_history)
        action = self.chromosome[index]
        #print(f"Chromosome index: {index}, Chosen action: {action}")

        return action
    
    
    def create_n_memory_state_indexing(self, possible_states_count, memory_depth):
        """
        Creates nested indexing for n-memory states.
        
        Args:
            possible_states_count: Number of possible states per turn (e.g., 36)
            memory_depth: Number of previous turns to consider (e.g., 3)
            
        Returns:
            Nested structure mapping state combinations to chromosome indices
        """
        total_states = possible_states_count ** memory_depth
        base_indices = list(range(total_states))
        
        # Helper function to chunk indices recursively
        def chunk_indices(indices, depth):
            if depth == 1:
                return indices
            chunk_size = len(indices) // possible_states_count
            chunks = [indices[i:i + chunk_size] for i in range(0, len(indices), chunk_size)]
            return [chunk_indices(chunk, depth - 1) for chunk in chunks]
        
        return chunk_indices(base_indices, memory_depth)
     
    def get_chromosome_index(self, state_history):
        """
        Maps a sequence of states to the corresponding chromosome index.
        
        Args:
            state_history: List of states, ordered from oldest to newest
        """
        current_level = self.chunked_indexed_chromosome
        for state in state_history:
            state_idx = self.state_to_index_map[state]
            current_level = current_level[state_idx]
        return current_level + self.premise_length