# axelrod_tetradic
A four-player, four-move (4p4m) generalization of the Prisoner's Dilemma, to be studied with Axelrod's (1984, 1997) tournament and evolutionary methodology.

This is a fork from the Axelrod Python repository which is designed for the standard 2-player Prisoner's Dilemma (https://github.com/Axelrod-Python/Axelrod). Although Axelrod Python can be modified to accomodate different payoffs and more than two moves, there is not much support for n > 2 player games. This repository was created as part of my Master's Thesis in Management at the University of Mannheim (Germany). 

As of July 2025: In terms of module structure, my repository differs from Axelrod Python only in two ways: 1) An independent module for calculating the payoffs and scoring dictionaries (mapping each game state to a payoff distribution) was created. In fact, the major hurdle to changing Axelrod Python to a four-player, four-move game was that scoring information as not centralized, scattered, and redundantly added in multiple places. While this is unproblematic for the limited four possible game states in a Prisoner's Dilemma, my tetradic generalization has 256 game states (similar to other higher-n games). 2) While some of the contributors to Axelrod Python implemented optimized AI methods to study tournaments in a separate repository (https://github.com/Axelrod-Python/axelrod-dojo), I re-implemented the crude, un-optimized Genetic Algorithm that Axelrod (1997) used within this module. Currently, running the Genetic Algorithm over a reasonable number of generations (100-2000) requires one night depending on the configuration. 

Because it is too tedious to display the 256 (4^4) game states of my tetradic (4p4m) generalization of the Prisoner's Dilemma, I developed a different representation and payoff logic. Similar to dictator games, every player unilaterally sets the payoffs for themselves and others but contrary to the dictator game, everyone gets to do it. This more closely resembles investment decisions by firms and managers who can choose to invest (incurring costs and providing benefits to the investees). 

Payoff matrix definition
Structure: [move][player_payoff]
- Rows (moves): W=0, X=1, Y=2, Z=3
- Columns: payoffs for (self, competitor, supply_chain1, supply_chain2)
- --> (for an n-Prisoner's Dilemma, the first column sets payoff for self, second for second player etc.)

<img width="721" height="429" alt="image" src="https://github.com/user-attachments/assets/0cbcf6b1-6afe-4bef-b6fb-db5d3841f43e" />

The title of my Master's Thesis is: "Strategies for Managing Key Accounts and Preferred Suppliers – Overcoming Cooperative Dilemmas with Evolutionary Game Theory". As it suggests, the interpretation of this generalized model is about investing in long-term cooperative supply-chain relationships despite the threat of opportunism. At request per Email, I am happy to share and discuss my thesis results. I believe that a tetradic generalization is well suited to modelling the challenge of achieving a competitive advantage. Because the interpretative framework of evolutionary game theory allows players to be e.g. sets of firms/managers, researchers arguably need no more than four players to properly represent competitive business relationships.

<img width="654" height="356" alt="image" src="https://github.com/user-attachments/assets/95193580-d030-4171-ac99-bff64c75d40f" />

