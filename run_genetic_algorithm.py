"""
Genetic Algorithm Runner for Four-Player Four-Move Prisoner's Dilemma

This module executes genetic algorithm simulations for evolving strategies in
the four-player variant of the Prisoner's Dilemma game. It manages population
evolution, tournament execution, and results tracking.

Informally: This file is functional but not yet well organized (WIP) or optimized for performance.
The former will be improved shortly. This program is not concerned with performance, but rather
attempts to re-implement Axelrod's (1997) genetic algorithm faithfully and in line with the rest of 
this repository.

Key Features:
    - Population initialization and evolution
    - Tournament-based fitness evaluation
    - Strategy performance tracking
    - CSV output generation
    - Progress monitoring
    - Space-efficient file management

Settings:
    - Population size: Configurable number of strategies per generation
    - Memory depth: How many previous moves strategies consider
    - Information sets: 'complete', 'ignore_comp', 'ignore_comp_sc2'
    - Tournament parameters: turns, noise, repetitions
    - Evolution parameters: mutation rate, crossover points

Example:
    python run_genetic_algorithm.py
    Generation 1/1000
    Tournament completed in 3.1s
    Best strategy: GA_Player_3_Gen1 (Score: 82.85)

Output Files:
    - Tournament results: GA_Tournament_{settings}.csv
    - Chromosome history: GA_Chromosomes_{settings}.csv
    - Rankings history: GA_Rankings_{settings}.csv

Author: Max Bayer
Date: July 2025
"""

# Standard library imports
import csv
import os
import time
import copy
start_time = time.time() # Record the start time
from typing import List, Optional, Tuple

# Third-party library imports
import dask as da
import dask.dataframe as dd
import numpy as np

# Local imports
import genetic_algorithm as ga
import csv_handler
import strategies_4p4m as strat
from action_4p4m import Action_4p4m
from game_4p4m import TetradicPrisonersDilemmaGame
from tournament_4p4m import Tournament_4p4m

# Initialize game actions
W, X, Y, Z = Action_4p4m.W, Action_4p4m.X, Action_4p4m.Y, Action_4p4m.Z




# Configuration
information_set = "ignore_comp"  # Options: "complete", "ignore_comp"
premise_count_per_memory_slot = 3 if information_set == "ignore_comp" else 4

GA_SETTINGS = {
    'memory_depth': 3,
    'information_set': information_set,
    'population_size': 5,
    'num_generations': 3,
    'mutation_rate': 0.01,
    'num_crossovers': 10,
    'premise_count_per_memory_slot': premise_count_per_memory_slot
}

TOURNAMENT_SETTINGS = {
    'turns': 10,
    'repetitions': 1,
    'noise': 0.03,
    'edges': None,
    'match_attributes': None,
    'seed': 1,
    
}

FILE_SETTINGS = {
    'keep_every_xth_csv': GA_SETTINGS['num_generations'] // 1,
    'delete_csv_files': True,
    'output_folder': "ga_csv_outputs"
}

RANKING_SETTINGS = {
    'max_retries': 50,
    'retry_delay': 0.5,  # seconds
    'scheduler': "single-threaded",
    'score_precision': 2
}

DASK_COLUMNS = {
    'groups': ["Player index", "Competitor index", "SC1 index", "SC2 index"],
    'metrics': ["Turns", "Score"]
}

# Create output directory
if not os.path.exists(FILE_SETTINGS['output_folder']):
    os.makedirs(FILE_SETTINGS['output_folder'])
    
base_filename = (f"GA_{GA_SETTINGS['population_size']}pop_"
                f"{GA_SETTINGS['num_generations']}gen_"
                f"{GA_SETTINGS['memory_depth']}mem_"
                f"{GA_SETTINGS['information_set']}Info")

paths = {
    'tournament': os.path.join(FILE_SETTINGS['output_folder'], f"{base_filename}_Tournament.csv"),
    'chromosomes': os.path.join(FILE_SETTINGS['output_folder'], f"{base_filename}_Chromosomes.csv"),
    'rankings': os.path.join(FILE_SETTINGS['output_folder'], f"{base_filename}_Rankings.csv")
}

# Ensure all file paths are absolute, not relative
for key in paths:
    paths[key] = os.path.abspath(paths[key])

# Initialize tracking containers
best_chromosomes = []
best_fitness_history = []
population_history = {}

def read_tournament_results(filepath: str, max_retries: int, retry_delay: float) -> dd.DataFrame:
    """Read tournament results with retry mechanism for cloud storage sync."""
    for attempt in range(max_retries):
        try:
            return dd.read_csv(filepath)
        except PermissionError:
            if attempt == max_retries - 1:
                raise
            print(f"Permission denied, retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)

def process_tournament_results(df: dd.DataFrame, players: List, alternative: int = 0) -> np.ndarray:
    """Process tournament results and calculate mean payoffs."""
    groups = DASK_COLUMNS['groups']
    columns = DASK_COLUMNS['metrics']
    
    # Calculate statistics
    tasks = (
        df.groupby(groups)[columns].sum(),
        df.groupby(groups)[columns].mean(),
        df.groupby(groups)[columns].std()
    )
    sum_df, mean_df, stddev_df = da.compute(*tasks, scheduler=RANKING_SETTINGS['scheduler'])
    
    # Process mean scores
    series = mean_df["Score"]
    series_dict = series.to_dict()
    
    # Reshape results
    num_players = len(players)
    output_mean_df = csv_handler.reshape_four_dim_list(
        series_dict=series_dict,
        num_players=num_players,
        alternative=alternative
    )
    
    return output_mean_df

def write_rankings(players: List, scores: List, population: List, gen_num: int) -> None:
    """Write ranking data to CSV file."""
    row_data = []
    ranked_players_indices = []

    # Get ranking information
    ranking = csv_handler.rank_strategies(players, scores)
    
    # Process player names and indices
    for rank_info in ranking[1:]:
        player_name = rank_info[1]
        row_data.append(player_name)
        
        # Find player index
        for idx, player in enumerate(players):
            if player.name == player_name:
                ranked_players_indices.append(idx)
                break
    
    # Add scores
    for rank_info in ranking[1:]:
        row_data.append(round(float(rank_info[2]), RANKING_SETTINGS['score_precision']))
    
    # Add action frequencies
    for player_idx in ranked_players_indices:
        chromosome = population[player_idx]
        for action in [W, X, Y, Z]:
            action_count = sum(1 for gene in chromosome if gene == action)
            row_data.append(action_count)
    
    # Write to file
    if not os.path.exists(paths['rankings']):
        create_rankings_header(GA_SETTINGS['population_size'])
    
    with open(paths['rankings'], 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(row_data)

def create_rankings_header(population_size: int) -> None:
    """Create the rankings CSV file with headers."""
    headers = []
    for i in range(population_size):
        headers.extend([
            f"Rank {i+1} Player",
            f"Rank {i+1} Average Tournament Score",
            f"Rank {i+1} W count",
            f"Rank {i+1} X count",
            f"Rank {i+1} Y count",
            f"Rank {i+1} Z count"
        ])
    
    with open(paths['rankings'], 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)

               
# Main evolution loop
for generation in range(GA_SETTINGS['num_generations']):
    gen_num = generation + 1
    print(f"\nGeneration {gen_num}/{GA_SETTINGS['num_generations']}")
    
    if gen_num == 1:
        # Initialize population
        population = ga.create_random_population(
            GA_SETTINGS['memory_depth'],
            GA_SETTINGS['information_set'],
            GA_SETTINGS['population_size']
        )
        
        # Create initial players
        players = []
        for i, chromosome in enumerate(population):
            if GA_SETTINGS['information_set'] == "ignore_comp":
                player = strat.GeneticAlgorithmPlayer_ignoreCompetitor(
                    chromosome=chromosome,
                    memory_depth=GA_SETTINGS['memory_depth'],
                    information_set=GA_SETTINGS['information_set'],
                    premise_count_per_memory_slot=GA_SETTINGS['premise_count_per_memory_slot']
                )
            else:  # information_set == "complete"
                player = strat.GeneticAlgorithmPlayer(
                    chromosome=chromosome,
                    memory_depth=GA_SETTINGS['memory_depth'],
                    information_set=GA_SETTINGS['information_set'],
                    premise_count_per_memory_slot=GA_SETTINGS['premise_count_per_memory_slot']
                )
            player.name = f"GA_Player_{i+1}_Gen1"  # Set name directly
            players.append(player)

        # Store initial population
        population_history.update({(1, i): chrom for i, chrom in enumerate(population)})
        ga.write_chromosomes_to_csv(population_history, paths['chromosomes'])
    
    else:
        # Evolution step
        population = ga.crossover(
            population,
            tournament_mean_payoffs,
            mutation_rate=GA_SETTINGS['mutation_rate'],
            num_crossovers=GA_SETTINGS['num_crossovers']
        )
        
        # Update history
        population_history.update({(gen_num, i): chrom for i, chrom in enumerate(population)})
        generation_history = {(gen_num, i): chrom for i, chrom in enumerate(population)}
        ga.write_chromosomes_to_csv(generation_history, paths['chromosomes'], mode='a')
        
        # Create new generation players
        players = []
        for i, chromosome in enumerate(population):
            if GA_SETTINGS['information_set'] == "ignore_comp":
                player = strat.GeneticAlgorithmPlayer_ignoreCompetitor(
                    chromosome=chromosome,
                    memory_depth=GA_SETTINGS['memory_depth'],
                    information_set=GA_SETTINGS['information_set'],
                    premise_count_per_memory_slot=GA_SETTINGS['premise_count_per_memory_slot']
                )
            else:  # information_set == "complete"
                player = strat.GeneticAlgorithmPlayer(
                    chromosome=chromosome,
                    memory_depth=GA_SETTINGS['memory_depth'],
                    information_set=GA_SETTINGS['information_set'],
                    premise_count_per_memory_slot=GA_SETTINGS['premise_count_per_memory_slot']
                )
            player.name = f"GA_Player_{i+1}_Gen{gen_num}"  # Set name directly
            players.append(player)
                
        
    # Run tournament
    tournament = Tournament_4p4m(
        players,
        # Change the name to avoid creating the unwanted rankings file
        name=f"gen{gen_num}_{base_filename}",  # Use the same name as your tournament_filename
        **TOURNAMENT_SETTINGS
    )

    # Then explicitly pass the correct filename (without 'Rankings' in it)
    tournament_filename = f"gen{gen_num}_{base_filename}.csv"
    tournament.play(
        filename=tournament_filename,
        foldername=FILE_SETTINGS['output_folder']
    )
    
    # Process tournament results
    tournament_file = os.path.join(FILE_SETTINGS['output_folder'], tournament_filename)
    df = read_tournament_results(
        tournament_file,
        RANKING_SETTINGS['max_retries'],
        RANKING_SETTINGS['retry_delay']
    )
    
    output_mean_df = process_tournament_results(df, players)
    payoff_matrix = csv_handler.build_summary_matrix(output_mean_df, len(players))
    tournament_mean_payoffs = csv_handler.tournament_mean_payoff_summary(
        players=players,
        payoff_matrix=payoff_matrix
    )
    
    # Write rankings
    write_rankings(players, tournament_mean_payoffs, population, gen_num)
    
    # Clean up tournament files if needed
    if FILE_SETTINGS['delete_csv_files']:
        if not (gen_num == 1 or gen_num % FILE_SETTINGS['keep_every_xth_csv'] == 0):
            try:
                os.remove(tournament_file)
                print(f"Deleted tournament file: {tournament_file}")
            except OSError as e:
                print(f"Error deleting {tournament_file}: {e}")

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time:.2f} seconds")





    
    
