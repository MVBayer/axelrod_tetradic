"""
CSV Handler Module for Tournament Analysis

This module provides functionality for analyzing and summarizing tournament results
stored in CSV format. It includes functions for:
- Building summary matrices of tournament outcomes
- Calculating mean payoffs across all tournament matches
- Ranking strategies based on their performance

The module is specifically designed to work with the 4-player, 4-strategy game 
developed for this Master's Thesis.

Currently, this is only used for the genetic algorithm module but it will be replaced.
Originally, it was used for tournaments and ecosystem simulations because it was adapted from
the Axelrod Python repository but for the purposes of this thesis, it was better to use pd Pivot tables.

Author: Max Bayer
Date: July 2025    
"""


# Standard library imports
import csv
import itertools
import os

# Third-party imports
import numpy as np



def build_summary_matrix(attribute, num_players, func=np.mean, ):
    """
    Builds a 4-dimensional summary matrix of tournament attributes.
    
    Parameters
    ----------
    attribute : list
        The tournament attribute to summarize (e.g., payoffs, moves)
    num_players : int
        Number of players in the tournament
    func : callable, optional
        Function to apply to the utilities (default: np.mean)
        
    Returns
    -------
    list
        4D matrix containing summarized attributes for all player combinations
    """
    #create a placeholder for the output
    matrix = [] 
    for player_index in range(num_players):
        first_layer =[]
        for competitor_index in range(num_players):
            second_layer =[]
            for SC1_index in range(num_players):
                third_layer =[]
                for SC2_index in range(num_players):
                        third_layer.append(0)                
                second_layer.append(third_layer)
            first_layer.append(second_layer)
        matrix.append(first_layer) 

    #create an iterable to check for all possible cases (combinatorics)
    pairs = itertools.product(range(num_players), repeat=4)

    #iterate through all cases, check if they are in CSV-df, if yes, apply function at each step
    for player_index, competitor_index, SC1_index, SC2_index in pairs:
        utilities = attribute[player_index][competitor_index][SC1_index][SC2_index]
        if utilities:
            matrix[player_index][competitor_index][SC1_index][SC2_index] = func(utilities)
    return matrix




def tournament_mean_payoff_summary(players, payoff_matrix):
    """
    Calculates the mean payoff for each player across all possible game combinations.
    
    Parameters
    ----------
    players : list
        List of player objects
    payoff_matrix : list
        4D matrix containing payoff values
        
    Returns
    -------
    list
        Average payoff for each player
    """
    num_players = len(players)
    player_sums = [0] * num_players

    for player_index in range(num_players):
        for competitor_index in range(num_players):
            for SC1_index in range(num_players):
                for SC2_index in range(num_players):
                    player_sums[player_index] += payoff_matrix[player_index][competitor_index][SC1_index][SC2_index]
    player_avg = [player_sum / (num_players ** 3) for player_sum in player_sums]
    
    return player_avg


def rank_strategies(players, tournament_mean_payoffs):
    # Combine player names and their corresponding mean payoffs
    #player_payoffs = [(player.__class__.__name__, payoff) for player, payoff in zip(players, tournament_mean_payoffs)]
    player_payoffs = [(player.name, payoff) for player, payoff in zip(players, tournament_mean_payoffs)]
    
    # Sort the players based on their mean payoffs in descending order
    sorted_player_payoffs = sorted(player_payoffs, key=lambda x: x[1], reverse=True)
    
    # Create the ranking list with header
    ranking = [["Rank", "Strategy Name", "Average Tournament Score"]]
    ranking.extend([f"Rank {i+1}:", player_name, round(float(avg_score), 5)] for i, (player_name, avg_score) in enumerate(sorted_player_payoffs))
    
    return ranking


def reshape_four_dim_list(series_dict, num_players, alternative=None, key_order=[0, 1, 2, 3]):
    """
    Reshapes a dictionary of series into a 4-dimensional list structure.
    
    Parameters
    ----------
    series_dict : dict
        Dictionary containing series data
    num_players : int
        Number of players in the tournament
    alternative : Optional[int]
        Value to use for missing combinations (default: None)
    key_order : List[int]
        Order of indices in the dictionary keys (default: [0,1,2,3])
        
    Returns
    -------
    list
        4D list containing reshaped data
    """
    output_mean_df = []
    for player_index in range(num_players):
        first_layer = []
        for competitor_index in range(num_players):
            second_layer = []
            for SC1_index in range(num_players):
                third_layer = []
                for SC2_index in range(num_players):
                    key = (player_index, competitor_index, SC1_index, SC2_index)
                    key = tuple(key[order] for order in key_order)
                    if key in series_dict:
                        third_layer.append(series_dict[key])
                    elif alternative is not None:
                        third_layer.append(alternative)
                second_layer.append(third_layer)
            first_layer.append(second_layer)
        output_mean_df.append(first_layer)
    return output_mean_df

def write_chromosomes_to_csv(
    population_history: dict, 
    filename: str, 
    mode: str = 'w'
) -> None:
    """
    Exports chromosome data to CSV format with generational history.

    Writes or appends chromosome data to a CSV file, organizing by generation
    and player. Each row represents a gene, and columns represent different
    chromosomes across generations.

    Args:
        population_history: Dictionary mapping (generation, player_index) to chromosomes
        filename: Path to the output CSV file
        mode: File operation mode - 'w' for write/overwrite, 'a' for append

    Returns:
        None
    """
    if not population_history:
        return
        
    # Get the maximum length of chromosomes
    max_chromosome_length = max(len(chrom) for chrom in population_history.values())
    
    # If we're creating a new file
    if mode == 'w' or not os.path.exists(filename):
        # Create the header row with just the first column
        header = ['Gene_ID']
        
        # Create empty rows
        rows = []
        for gene_index in range(max_chromosome_length):
            rows.append([f"Gene_{gene_index+1}"])
            
        # Write initial file structure
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows)
    
    # Read the existing file to get current state
    with open(filename, 'r', newline='') as f:
        reader = csv.reader(f)
        existing_data = list(reader)
        
    # Add new players as columns
    for (generation, player_index) in sorted(population_history.keys()):
        # Add the column header
        column_name = f"G{generation}P{player_index+1}"
        existing_data[0].append(column_name)
        
        # Add the chromosome data
        chromosome = population_history[(generation, player_index)]
        for gene_index in range(len(chromosome)):
            if gene_index + 1 < len(existing_data):  # +1 because row 0 is the header
                existing_data[gene_index + 1].append(str(chromosome[gene_index]))
            else:
                # Add a row if needed for longer chromosomes
                new_row = [f"Gene_{gene_index+1}"] + [""] * (len(existing_data[0]) - 2) + [str(chromosome[gene_index])]
                existing_data.append(new_row)
        
        # Fill empty cells for shorter chromosomes
        for gene_index in range(len(chromosome), max_chromosome_length):
            if gene_index + 1 < len(existing_data):
                existing_data[gene_index + 1].append("")
    
    # Write the updated data back to the file
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(existing_data)