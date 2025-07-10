"""
Genetic Algorithm Implementation for Four-Player Four-Move Prisoner's Dilemma

This module implements a genetic algorithm to evolve strategies for a four-player
prisoner's dilemma game. It includes functionality for population management,
crossover operations, mutation, and fitness evaluation.

Informally: This is a very inefficient, un-optimized re-implementation of 
Axelrod's (1997) implementation of the then recently developed GA for the
dyadic (2-player) Prisoner's Dilemma with Axelrod tournaments (Axelrod, 1984).
With a limited information set, 1000-1500 generations can be evaluated
over night with 8 individuals per generation. With a complete information set,
only around a tenth can be generated in the same time frame.

Key Features:
- Population initialization with configurable memory depth
- Multi-point crossover with customizable crossover points
- Mutation with adjustable rates
- Tournament-based selection
- Support for different information sets ('complete' or 'ignore_comp')
- CSV export functionality for population history

Classes:
    None (functional implementation)

Functions:
    write_chromosomes_to_csv: Exports population history to CSV
    crossover: Creates new generation through selection and breeding
    selection_tournament: Implements tournament selection
    multi_point_crossover: Performs genetic crossover between parents
    mutate: Applies random mutations to chromosomes
    create_random_population: Initializes random population
    calculate_chromosome_length: Determines required chromosome length

Author: Max Bayer
Date: July 2025
"""

# Python standard library
import csv
import itertools
import os
import random 
import time
import copy
from typing import List, Dict, Tuple, Union
start_time = time.time() # Record the start time

# Third-party imports
import numpy as np

# Local imports
from action_4p4m import Action_4p4m

# Initialize game actions
W, X, Y, Z = Action_4p4m.W, Action_4p4m.X, Action_4p4m.Y, Action_4p4m.Z



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



def crossover(
    population: List[List[Action_4p4m]],
    tournament_mean_payoffs: Union[List[float], np.ndarray],
    mutation_rate: float,
    num_crossovers: int
) -> List[List[Action_4p4m]]:
    """
    Creates a new generation through selection, crossover, and mutation.

    Implements a fitness-based selection process where individuals with higher
    tournament payoffs have better chances of reproduction. Uses multi-point
    crossover and mutation to generate offspring.

    Args:
        population: List of current generation chromosomes
        tournament_mean_payoffs: Average payoff for each player from tournaments
        mutation_rate: Probability (0-1) of gene mutation
        num_crossovers: Number of crossing points for genetic recombination

    Returns:
        List of chromosomes forming the next generation
    """
    if hasattr(tournament_mean_payoffs, 'tolist'):
        scores_list = tournament_mean_payoffs
    else:
        scores_list = tournament_mean_payoffs

    
    
    # Create a fitness dictionary mapping chromosomes to their performance
    fitness_dict = {i: score for i, score in enumerate(scores_list)}
    #print("fitness_dict: ", fitness_dict)

    # Create new population
    new_population_expanded = []
    new_population = []
    
       # Calculate mean and standard deviation of payoffs
    mean_payoff = np.mean(scores_list)
    std_payoff = np.std(scores_list)
    
    # Create mating chances list based on standard deviation
    mating_chances = []
    for idx, score in fitness_dict.items():
        if score >= mean_payoff + std_payoff:
            mating_chances.extend([idx] * 2)  # Two chances for above 1 SD
        elif score > mean_payoff - std_payoff:
            mating_chances.append(idx)         # One chance for within 1 SD
        # No chances for below 1 SD
    
    # uncomment for debugging
    #print(f"Mean payoff: {mean_payoff:.2f}, SD: {std_payoff:.2f}")
    print("Mating chances distribution:", mating_chances)
    
    
    # Create remaining population through crossover
    while len(new_population_expanded) < len(population)*2:
        # Selecting parents based on mating chances
        parent1_idx = random.choice(mating_chances)
        parent2_idx = random.choice(mating_chances)
        
        # Ensure different parents
        while parent2_idx == parent1_idx and len(mating_chances) > 1:
            parent2_idx = random.choice(mating_chances)
        
        parent1 = population[parent1_idx]
        parent2 = population[parent2_idx]
        
        # Perform crossover
        child1, child2 = multi_point_crossover(parent1, parent2, num_crossovers)

        # Perform mutation  
        child1 = mutate(child1, mutation_rate)
        child2 = mutate(child2, mutation_rate)
        
        new_population_expanded.append(child1)
        new_population_expanded.append(child2)
    print("completed crossover")
    random.shuffle(new_population_expanded)
    new_population = new_population_expanded[:len(population)]  # Keep the size of the population constant 
    #for i in range(len(new_population)):
        #print(f"new_population[{i}]: ", new_population[i][:10])
        #print(f"length of new_population[{i}]: ", len(new_population[i]))
    return new_population



def selection_tournament(
    fitness_dict: Dict[int, float],
    tournament_size: int = 5
) -> int:
    """
    Implements tournament selection for parent choice.

    Randomly selects tournament_size individuals and returns the one
    with highest fitness. This provides selection pressure while
    maintaining population diversity.

    Args:
        fitness_dict: Dictionary mapping individual indices to their fitness scores
        tournament_size: Number of individuals to compete in each tournament

    Returns:
        Index of the tournament winner
    """
    candidates = random.sample(list(fitness_dict.keys()), min(tournament_size, len(fitness_dict)))
    print("selection_tournament_candidates function, returns: ", max(candidates, key=lambda idx: fitness_dict[idx]))
    return max(candidates, key=lambda idx: fitness_dict[idx])



def single_point_crossover(parent1, parent2):
    """
    Single-point crossover between two parents.
    (No longer used.)
    """
    # Keep premise state genes separate from reaction genes
    crossover_point = 8 + random.randint(0, len(parent1) - 8 - 1)
    
    child1 = parent1[:crossover_point] + parent2[crossover_point:]
    child2 = parent2[:crossover_point] + parent1[crossover_point:]

    print("crossover point: ", crossover_point)

    return child1, child2



def multi_point_crossover(
    parent1: List[Action_4p4m],
    parent2: List[Action_4p4m],
    num_crossovers: int
) -> Tuple[List[Action_4p4m], List[Action_4p4m]]:
    """
    Performs multi-point crossover between two parent chromosomes.

    Preserves the first 8 premise state genes and performs crossovers only
    in the reaction genes section. This maintains strategy structure while
    allowing for genetic diversity.

    Args:
        parent1: First parent's chromosome
        parent2: Second parent's chromosome
        num_crossovers: Number of crossing points to use

    Returns:
        Tuple containing two child chromosomes
    """
    # Create copies of parents to modify
    child1 = copy.deepcopy(parent1)
    child2 = copy.deepcopy(parent2)
    
    # Keep premise state genes (first 8 genes) separate from reaction genes
    chromosome_length = len(parent1)
    
    # Generate num_crossovers points (without duplicates)
    # Limiting the range to only the reaction genes (after index 8)
    possible_points = list(range(9, chromosome_length))
    
    # Ensure we don't try more crossovers than possible
    num_crossovers = min(num_crossovers, len(possible_points))
    
    # Randomly select crossover points
    crossover_points = sorted(random.sample(possible_points, num_crossovers))
    
    # Perform crossovers
    current_source = 1  # Start with parent1 genes
    
    # Start after premise genes (index 8)
    start_idx = 8
    
    for point in crossover_points:
        # Swap segments between children based on current source
        if current_source == 1:
            # Take genes from parent1
            child1[start_idx:point] = parent1[start_idx:point]
            child2[start_idx:point] = parent2[start_idx:point]
        else:
            # Take genes from parent2
            child1[start_idx:point] = parent2[start_idx:point]
            child2[start_idx:point] = parent1[start_idx:point]
            
        # Toggle source for next segment
        current_source = 3 - current_source  # Toggles between 1 and 2
        
        # Update start index for next segment
        start_idx = point
    
    # Handle the final segment
    if current_source == 1:
        child1[start_idx:] = parent1[start_idx:]
        child2[start_idx:] = parent2[start_idx:]
    else:
        child1[start_idx:] = parent2[start_idx:]
        child2[start_idx:] = parent1[start_idx:]
    
    #print(f"{len(crossover_points)} crossover points used, samples: [{crossover_points[:3]}...{crossover_points[-3:]}]")
    
    return child1, child2



def mutate(
    chromosome: List[Action_4p4m],
    mutation_rate: float
) -> List[Action_4p4m]:
    """
    Applies random mutations to a chromosome.

    Each gene has a mutation_rate probability of being randomly changed
    to any other possible move (W, X, Y, Z).

    Args:
        chromosome: List of genes (moves) to potentially mutate
        mutation_rate: Probability (0-1) of each gene mutating

    Returns:
        Mutated chromosome
    """
    all_available_moves = [W, X, Y, Z]
    mutated = copy.deepcopy(chromosome)
    
    for i in range(len(mutated)):
        if random.random() < mutation_rate:
            mutated[i] = random.choice(all_available_moves)
    
    return mutated


def create_random_population(
    memory_depth: int,
    information_set: str,
    population_size: int
) -> List[List[Action_4p4m]]:
    """
    Initializes a random population of strategy chromosomes.

    Creates chromosomes based on specified memory depth and information set.
    Supports two information set types: 'complete' and 'ignore_comp'.

    Args:
        memory_depth: Number of previous moves to consider
        information_set: Type of information available ('complete' or 'ignore_comp')
        population_size: Number of chromosomes to generate

    Returns:
        List of randomly generated chromosomes
    
    Raises:
        ValueError: If information_set is not 'complete' or 'ignore_comp'
    """
    all_available_moves = [W, X, Y, Z]
    move_count = len(all_available_moves)


    # Determine all possible interactions based on the information set    
    if information_set == "complete":
        all_possible_interactions = [p for p in itertools.product(all_available_moves, repeat=4)]
        premise_count_per_memory_slot = 4
        possible_states_count = len(all_possible_interactions)
    elif information_set == "ignore_comp":
        premise_count_per_memory_slot = 3 # What did I do? What did SC1 do? What did SC2 do?
        possible_states_count = 4*3*3 # 4 = number of self moves, 3 = did SC1/SC2 do a lot for me (X/Y) a little for me (Z) or nothing for me (Y/X, W).
    else:
        raise ValueError("Invalid information set. Choose 'complete' or 'ignore_comp'.")
    
    # Calculate the number of premise states and total states based on memory depth

    
    # Create random array for entire population
    total_length = calculate_chromosome_length(memory_depth, premise_count_per_memory_slot, possible_states_count)
    random_array = np.random.randint(0, move_count, size=(population_size, total_length))
    
    # Convert numpy array to list of chromosomes with proper action objects
    chromosomes = []
    for i in range(population_size):
        chromosome = [all_available_moves[idx] for idx in random_array[i]]
        chromosomes.append(chromosome)
    
    return chromosomes



def calculate_chromosome_length(
    memory_depth: int,
    premise_count_per_memory_slot: int,
    possible_states_count: int
) -> int:
    """
    Calculates required length of a chromosome based on game parameters.

    The total length includes both premise state genes and reaction genes,
    calculated based on memory depth and possible states.

    Args:
        memory_depth: Number of previous moves to consider
        premise_count_per_memory_slot: Number of premises per memory slot
        possible_states_count: Number of possible game states

    Returns:
        Total required length of chromosome
    """
    premise_count = premise_count_per_memory_slot * memory_depth
    states_count = possible_states_count ** memory_depth
    
    return premise_count + states_count





    
    
    
