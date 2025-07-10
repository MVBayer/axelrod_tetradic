# axelrod_tetradic
A four-player, four-move (4p4m) generalization of the Prisoner's Dilemma, to be studied with Axelrod's (1984, 1997) tournament and evolutionary methodology.

This is a fork from the Axelrod Python repository which is designed for the standard 2-player Prisoner's Dilemma (https://github.com/Axelrod-Python/Axelrod). Although Axelrod Python can be modified to accomodate different payoffs and more than two moves, there is not much support for n > 2 player games. This repository was created as part of my Master's Thesis in Management at the University of Mannheim (Germany). 

As of July 2025: In terms of module structure, my repository differs from Axelrod Python only in two ways: 1) An independent module for calculating the payoffs and scoring dictionaries (mapping each game state to a payoff distribution) was created. In fact, the major hurdle to changing Axelrod Python to a four-player, four-move game was that scoring information as not centralized, scattered, and redundantly added in multiple places. While this is unproblematic for the limited four possible game states in a Prisoner's Dilemma, my tetradic generalization has 256 game states (similar to other higher-n games). 2) While some of the contributors to Axelrod Python implemented optimized AI methods to study tournaments in a separate repository (https://github.com/Axelrod-Python/axelrod-dojo/tree/master/tests), I re-implemented the crude, un-optimized Genetic Algorithm that Axelrod (1997) used within this module. Currently, running the Genetic Algorithm over a reasonable number of generations (100-2000) requires one night depending on the configuration. 

Because it is too tedious to display the 256 (4^4) game states of my tetradic (4p4m) generalization of the Prisoner's Dilemma, I developed a different representation and payoff logic. Similar to dictator games, every player unilaterally sets the payoffs for themselves and others but contrary to the dictator game, everyone gets to do it. This more closely resembles investment decisions by firms and managers who can choose to invest (incurring costs and providing benefits to the investees). 

Payoff matrix definition
Structure: [move][player_payoff]
- Rows (moves): W=0, X=1, Y=2, Z=3
- Columns: payoffs for (self, competitor, supply_chain1, supply_chain2)
--> (for an n-Prisoner's Dilemma, the first column sets payoff for self, second for second player etc.)
payoff_matrix = (   ( 0, 0, 0, 0),  # Payoffs for move W
                    (-3, 0, 4, 0),  # Payoffs for move X
                    (-3, 0, 0, 4),  # Payoffs for move Y
                    (-4, 0, 3, 3)   # Payoffs for move Z
)
Player position mapping for calculating payoffs
Each tuple represents how payoffs should be distributed for each player's perspective
--> 0 = self, 1 = competitor, 2 = sc1, 3 = sc2
indices_game_4players = (   (0,1,2,3), # Player 1's perspective
                            (1,0,3,2), # Player 2's perspective
                            (2,3,0,1), # Player 3's perspective
                            (3,2,1,0)) # Player 4's perspective

The title of my Master's Thesis is: "Strategies for Managing Key Accounts and Preferred Suppliers – Overcoming Cooperative Dilemmas with Evolutionary Game Theory". As it suggests, the interpretation of this generalized model is about investing in long-term cooperative supply-chain relationships despite the threat of opportunism. At request per Email, I am happy to share and discuss my thesis results.
