"""
Ecosystem Module for Tournament Evolution Analysis

This module implements an evolutionary ecosystem for analyzing strategy dynamics
in a 4-player, 4-strategy Prisoner's Dilemma game. The ecosystem simulates population dynamics over
multp1_idxle generations based on tournament results.

Key Features:
- Population evolution based on tournament payoffs
- Stochastic payoff calculation using normal distribution
- Support for custom fitness functions
- CSV export of population distributions

Classes:
    Ecosystem: Main class implementing the evolutionary dynamics

Example:
    ecosystem = Ecosystem(players=strategies,
                         detailed_scores_indexed=tournament_results,
                         detailed_score_stds_indexed=score_stddevs)
    ecosystem.reproduce(turns=1000)
    ecosystem.save_distributions(output_dir="results")

Author: Max Bayer
Date: July 2025

WIP: One change to be made is that matches where at least one of the four players
is already extinct should not be evaluated at all in this simulation.
"""

# Standard library imports
import random
from typing import Callable, List
import itertools
import os

# Third-party imports
import pandas as pd


class Ecosystem(object):
    """
    Simulates evolutionary dynamics of strategies in a tournament ecosystem.
    
    This class manages the population dynamics of different strategies based on
    their performance in tournaments. It supports stochastic payoff calculations
    and custom fitness functions.

    Attributes:
        players: List of strategy players
        num_players: Number of players in the ecosystem
        tournament_payoffs: DataFrame of tournament scores
        tournament_payoff_stddevs: DataFrame of score standard deviations
        company_value: Base value added to payoffs
        population_sizes: List of population distributions over time
    """
    
    def __init__(
        self,
        players,
        detailed_scores_indexed,  # Expecting a pandas DataFrame with multi-index
        detailed_score_stds_indexed,  # Expecting a pandas DataFrame with multi-index
        company_value: float = 0.0,
        fitness: Callable[[float], float] = None,
        population: List[int] = None,
    ) -> None:
        """
        Initialize the ecosystem with tournament results and initial conditions.
        
        Args:
            players: List of strategy players
            detailed_scores_indexed: Tournament scores as multi-indexed DataFrame
            detailed_score_stds_indexed: Score standard deviations as DataFrame
            company_value: Base value added to payoffs (default: 0.0)
            fitness: Custom fitness function (default: max(p, 0))
            population: Initial population distribution (default: uniform)
        
        Raises:
            TypeError: If population vector is invalid
        """
        self.players = players
        self.num_players = len(players)
        self.tournament_payoffs = detailed_scores_indexed
        self.tournament_payoff_stddevs = detailed_score_stds_indexed
        self.company_value = float(company_value)

        self.payoff_dict = self.tournament_payoffs.to_dict()['Average Score']
        self.stddev_dict = self.tournament_payoff_stddevs.to_dict()['Score Standard Deviation']


        # Population sizes will be recorded in this nested list, with each
        # internal list containing strategy populations for a given turn. The
        # first list, representing the starting populations, will by default
        # have all equal values, and all population lists will be normalized to
        # one. An initial population vector can also be passed. This will be
        # normalised, but must be of the correct size and have all non-negative
        # values.
        if population:
            if min(population) < 0:
                raise TypeError(
                    "Minimum value of population vector must be non-negative"
                )
            elif len(population) != self.num_players:
                raise TypeError(
                    "Population vector must be same size as number of players"
                )
            else:
                norm = sum(population)
                self.population_sizes = [[p / norm for p in population]]
        else:
            self.population_sizes = [
                [1 / self.num_players for _ in range(self.num_players)]
            ]

        # Define default fitness function if none provided
        # The fitness function determines reproduction success based on payoff
        if fitness:
            self.fitness = fitness
        else:            
            # Ensure non-negative fitness values by taking maximum of payoff and zero
            self.fitness = lambda p: max(p, 0) # can fitness be negative? If yes, i should make the zero at "next_generation" not "fitness"
            # Note: Alternative approach would be to allow negative fitness and handle at population level
            # Original Axelrod Python version: self.fitness = lambda p: p

    def reproduce(self, turns: int):
        """
        Simulate population evolution over specified number of generations.
        
        Calculates new population distributions based on tournament payoffs
        and current population sizes. Stops early if one strategy reaches 100%.
        
        Args:
            turns: Number of generations to simulate
        """        
        
        iturn = 0

        while iturn < turns:
            current_population = self.population_sizes[-1]
            
             # Check if any strategy has reached 100%
            if max(current_population) == 1.0:
                # Get the winning distribution and repeat it for remaining generations
                winning_distribution = current_population
                remaining_turns = turns - iturn
                self.population_sizes.extend([winning_distribution] * remaining_turns)
                break
            
        
            # Regular evolution calculations
            player_indices = list(range(self.num_players))
            payoffs = [self.company_value for p1_idx in player_indices]
            
            # Pre-calculate all random payoffs we'll need
            random_payoffs = {}
            for p1_idx, p2_idx, p3_idx, p4_idx in itertools.product(player_indices, repeat=4):
                try:
                    avg = self.payoff_dict[(p1_idx, p2_idx, p3_idx, p4_idx)]
                    dev = self.stddev_dict[(p1_idx, p2_idx, p3_idx, p4_idx)]
                    random_payoffs[(p1_idx, p2_idx, p3_idx, p4_idx)] = random.normalvariate(avg, dev)
                except KeyError:
                    continue
            
            # Calculate weighted payoffs for each strategy combination
            for p1_idx in player_indices:
                for p2_idx in player_indices:
                    for p3_idx in player_indices:
                        for p4_idx in player_indices:
                            try:
                                # Get random payoff from pre-calculated dictionary
                                p = random_payoffs[(p1_idx, p2_idx, p3_idx, p4_idx)]
                                # Weight payoff by population proportions of other players
                                # In 4-player game, multiply by proportions of all other players
                                payoffs[p1_idx] += p * current_population[p2_idx] * current_population[p3_idx] * current_population[p4_idx]
                            except KeyError:
                                continue

            # Calculate next generation populations
            # Multiply current population proportions by their fitness values
            fitness = [self.fitness(p) for p in payoffs]
                        
            next_generation = [p * f for p, f in zip(current_population, fitness)]
 
            # Normalize population proportions to sum to 1.0
            # This ensures total population size remains constant
            norm = sum(next_generation)
            next_generation = [p / norm for p in next_generation]


            self.population_sizes.append(next_generation)
            iturn += 1


    def save_distributions(self, output_dir: str, filename: str = "population_distributions.csv"):
        """
        Save the population distributions to a CSV file.
        
        Parameters
        ----------
        output_dir : str
            Directory where the CSV file will be saved
        filename : str
            Name of the CSV file (default: 'population_distributions.csv')
        """
        # Create DataFrame with time steps as rows and players as columns
        data = {
            f"Player_{i+1}_{str(self.players[i])}": [gen[i] for gen in self.population_sizes]
            for i in range(self.num_players)
        }
        
        # Add generation/time step column
        data['Generation'] = range(len(self.population_sizes))
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Reorder columns to put Generation first
        cols = df.columns.tolist()
        cols = ['Generation'] + [col for col in cols if col != 'Generation']
        df = df[cols]
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Save to CSV
        output_path = os.path.join(output_dir, filename)
        df.to_csv(output_path, index=False)
        print(f"Population distributions saved to: {output_path}")