"""
Four-Player Four-Move Tournament Module

This module implements a tournament framework for running multiple matches between
different strategies in a four-player, four-move variant of the Prisoner's Dilemma game.

Key Features:
    - Supports multiple players and repetitions
    - Handles noisy environments
    - Provides CSV output of tournament results
    - Supports custom game variations
    - Progress tracking with tqdm
    - Flexible match generation

Tournament Structure:
    1. Initialize players and game parameters
    2. Generate match combinations
    3. Run matches (serial execution)
    4. Record and analyze results

Output Format:
    CSV files containing:
    - Interaction details
    - Player moves and scores
    - Tournament statistics
    - Winner information

Example Usage:
    tournament = Tournament_4p4m(
        players=[player1, player2, player3, player4],
        turns=100,
        noise=0.05,
        repetitions=10
    )
    tournament.play(filename="tournament_results.csv")

Author: Max Bayer
Date: July 2025
"""

# Standard library imports
import csv
import logging
import os
import warnings
from collections import defaultdict
from tempfile import mkstemp
from typing import List, Optional, Tuple


# Third-party imports
import tqdm #for progress bar


# Local imports
from action_4p4m import Action_4p4m, actions_to_str
from game_4p4m import TetradicPrisonersDilemmaGame
import interaction_utils_4p4m as iu_4p4m
from match_4p4m import Match_4p4m
import match_generator_4p4m as mg
import player_4p4m as pl 

# Initialize game constants
W, X, Y, Z = Action_4p4m.W, Action_4p4m.X, Action_4p4m.Y, Action_4p4m.Z
DEFAULT_TURNS = 100



class Tournament_4p4m(object):
    """
    Tournament manager for four-player, four-move Prisoner's Dilemma games.
    
    This class handles the execution of a complete tournament, including match
    generation, execution, and result recording. It supports various tournament
    configurations and can output results to CSV files.
    
    Attributes:
        players (List[Player_4p4m]): List of participating players
        name (str): Tournament identifier
        game (Game): Game instance (defaults to TetradicPrisonersDilemmaGame)
        turns (int): Number of turns per match
        prob_end (float): Probability of game ending each turn
        repetitions (int): Number of times to repeat each match
        noise (float): Probability of moves being corrupted
        edges (List[Tuple]): Specific matchups to run
        match_attributes (dict): Additional match parameters
        seed (int): Random seed for reproducibility
    
    Properties:
        filename (str): Output file path
        foldername (str): Output directory path
        use_progress_bar (bool): Whether to show progress bar
    """
    def __init__(
        self,
        players: List[pl.Player_4p4m],
        name: str = "kam_axelrod_tournament",
        game = None,
        turns: int = None,
        prob_end: float = None,
        repetitions: int = 1,
        noise: float = 0,
        edges: List[Tuple] = None,
        match_attributes: dict = None,
        seed: int = None,
    ) -> None:

        """
        Initialize a new tournament instance.

        Args:
            players: List of participating player instances
            name: Identifier for the tournament
            game: Game instance (defaults to TetradicPrisonersDilemmaGame)
            turns: Number of turns per match (defaults to DEFAULT_TURNS if prob_end is None)
            prob_end: Probability of game ending each turn
            repetitions: Number of times to repeat each match
            noise: Probability of moves being corrupted
            edges: Specific matchups to run (if None, all combinations are played)
            match_attributes: Additional match parameters
            seed: Random seed for reproducibility
        """

        # allow other games to be used by this class
        if game is None:
            self.game = TetradicPrisonersDilemmaGame()
        else:
            self.game = game
        
        self.name = name
        self.noise = noise
        self.num_interactions = 0
        self.players = players
        self.repetitions = repetitions
        self.edges = edges
        self.seed = seed

        if turns is None and prob_end is None:
            turns = DEFAULT_TURNS
        self.turns = turns

        self.prob_end = prob_end
        self.match_generator = mg.MatchGenerator_4p4m(
            players=players,
            turns=turns,
            game=self.game,
            repetitions=self.repetitions,
            prob_end=prob_end,
            noise=self.noise,
            edges=edges,
            match_attributes=match_attributes,
            seed=self.seed,
        )
        self._logger = logging.getLogger(__name__)

        self.use_progress_bar = True

        self.filename = None  # type: Optional[str]
        self.foldername = "csv_outputs"  # type: Optional[str]
        self._temp_file_descriptor = None  # type: Optional[int]



    def setup_output(self, filename=None, foldername = None):
        """
        Configure output settings for tournament results.

        Args:
            filename: Name of output file (if None, creates temporary file)
            foldername: Directory for output files (creates if doesn't exist)

        Note:
            If filename is None, creates a temporary file that will be deleted
            after tournament completion.
        """
        temp_file_descriptor = None
        if filename is None:
            temp_file_descriptor, filename = mkstemp()

        self._temp_file_descriptor = temp_file_descriptor
        
        # Set up output folder and give output CSV filename
        output_dir = foldername
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        self.filename = os.path.join(output_dir,filename)


    def play(
        self,
        filename: str = None,
        foldername: str = None,
        progress_bar: bool = False,
    ):
        """
        Execute the tournament and save results.

        Args:
            filename: Name of output file
            foldername: Directory for output files
            progress_bar: Whether to display progress bar

        Returns:
            bool: True if tournament completed successfully

        Warns:
            UserWarning: If no filename is provided for results storage
        """
        self.num_interactions = 0
        self.use_progress_bar = progress_bar

        self.setup_output(filename, foldername)

        if not filename:
            warnings.warn(
                "Tournament results will not be accessible since no filename was supplied."
            )

        self._run_serial()

        return True # originally resultSet
    


    def _run_serial(self) -> bool:
        """
        Run all tournament matches in serial execution mode.

        Returns:
            bool: True if all matches completed successfully

        Note:
            This is the main tournament execution loop that processes all match chunks
            and writes results to file.
        """

        chunks = self.match_generator.build_match_chunks()

        out_file, writer = self._get_file_objects()
        progress_bar = self._get_progress_bar()

        for chunk in chunks:
            results = self._play_matches(chunk)
            self._write_interactions_to_file(results, writer=writer)
            if self.use_progress_bar:
                progress_bar.update(1)

        _close_objects(out_file)#, progress_bar)

        return True

    def _get_file_objects(self):
        """
        Initialize progress bar for tournament execution.

        Returns:
            tqdm.tqdm: Progress bar object if enabled, None otherwise
        """
        file_obj = None
        writer = None
        if self.filename is not None:
            file_obj = open(self.filename, "w")
            writer = csv.writer(file_obj, lineterminator="\n")

            header = [
                "Interaction index",
                "Player index",
                "Competitor index",
                "SC1 index",
                "SC2 index",
                "Repetition",
                "Player name",
                "Competitor name",
                "SC1 name",
                "SC2 name",
                "Actions",
                "Score",
                "Turns",
                "Winner",
            ]
            writer.writerow(header)
        return file_obj, writer
    
    
    def _get_progress_bar(self):
        if self.use_progress_bar:
            return tqdm.tqdm(
                total=self.match_generator.size, desc="Playing matches"
            )
        return None
    
    
    def _write_interactions_to_file(self, results, writer):
        """
        Write match interactions to CSV file.

        Args:
            results: Dictionary mapping player indices to match results
            writer: CSV writer object

        Note:
            Formats and writes detailed match data including player indices,
            moves, scores, and winner information.
        """
        for player_index_tuple, interactions in results.items():
            repetition = 0
            for interaction, results in interactions:

                if results is not None:
                    (
                        scores,
                        turns,
                        winner_index,
                    ) = results
                for index, player_index in enumerate(player_index_tuple):
                    
                    #set to 999 for debugging. Only valid indices in CSV later.
                    competitor_index = 999 
                    SC1_index = 999
                    SC2_index = 999
                    
                    if index == 0:
                        competitor_index = player_index_tuple[index - 3]
                        SC1_index = player_index_tuple[index - 2]
                        SC2_index = player_index_tuple[index - 1]
                        
                    if index == 1:
                        competitor_index = player_index_tuple[index - 1]
                        SC1_index = player_index_tuple[index - 2]
                        SC2_index = player_index_tuple[index - 3]
                        
                    if index == 2:
                        competitor_index = player_index_tuple[index - 3]
                        SC1_index = player_index_tuple[index - 2]
                        SC2_index = player_index_tuple[index - 1]

                    if index == 3:
                        competitor_index = player_index_tuple[index - 1]
                        SC1_index = player_index_tuple[index - 2]
                        SC2_index = player_index_tuple[index - 3]
                            
                    
                    
                    row = [
                        self.num_interactions,
                        player_index,
                        competitor_index,
                        SC1_index,
                        SC2_index,
                        repetition,
                        str(self.players[player_index]),
                        str(self.players[competitor_index]),
                        str(self.players[SC1_index]),
                        str(self.players[SC2_index]),
                    ]
                    history = actions_to_str([i[index] for i in interaction])
                    row.append(history)

                    if results is not None:
                        row.append(scores[index])
                        row.append(turns)
                        row.append(int(winner_index is index))

                    writer.writerow(row)
                repetition += 1
                self.num_interactions += 1


    def _play_matches(self, chunk):
        """
        Execute matches for a given chunk of player combinations.

        Args:
            chunk: Tuple containing (player_indices, match_params, repetitions, seed)

        Returns:
            dict: Mapping of player indices to match results and interactions

        Note:
            Handles player cloning, match setup, and result collection for each
            match in the chunk.
        """
        interactions = defaultdict(list)
        player_index_tuple, match_params, repetitions, seed = chunk
        p1_index, p2_index, p3_index, p4_index = player_index_tuple

        player1 = self.players[p1_index].clone()
        player2 = self.players[p2_index].clone()
        player3 = self.players[p3_index].clone()
        player4 = self.players[p4_index].clone()

        match_params["players"] = (player1, player2, player3, player4)
        match_params["seed"] = seed
        match = Match_4p4m(**match_params)
        for _ in range(repetitions):
            match.play()
            results = self._calculate_results(match.result)
            interactions[player_index_tuple].append([match.result, results])
        return interactions

    def _calculate_results(self, interactions):
        """
        Calculate final results for a completed match.

        Args:
            interactions: List of moves and outcomes from the match

        Returns:
            list: [scores, number_of_turns, winner_index]

        Note:
            Processes raw interaction data to compute final scores, match length,
            and determine the winner.
        """
        results = []

        scores = iu_4p4m.compute_final_score_4p4m(interactions, self.game)
        results.append(scores)

        turns = len(interactions)
        results.append(turns)

        winner_index = iu_4p4m.compute_winner_index_4p4m(interactions, self.game)
        results.append(winner_index)

        return results


def _close_objects(*objs):
    """
    Safely close multiple file or progress bar objects.

    Args:
        *objs: Variable number of objects with potential close() methods

    Note:
        Helper function to ensure proper cleanup of resources.
    """
    for obj in objs:
        if hasattr(obj, "close"):
            obj.close()



