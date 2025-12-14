from math import ceil
from .constant import *
from typing import List, Dict, Union

class Player:
    """
    Represents a chess player with an ELO rating and historical game records.

    Attributes:
        id (int): The unique ID of the player.
        pseudo (str): The player's pseudonym.
        elo (float): The player's current ELO rating.
        historical (List[Dict[str, Union[int, str]]]): A list of historical games with details.
    """

    def __init__(self, id: int, pseudo: str, elo: float, historical: List[Dict[str, Union[int, str]]] = []):
        self.id = id
        self.pseudo = pseudo
        self.elo = elo
        self.historical = historical


    def get_id(self) -> int:
        """
        Returns the player's unique ID.

        Returns:
            int: The player's ID.
        """
        return self.id


    def get_pseudo(self) -> str:
        """
        Returns the player's pseudonym.

        Returns:
            str: The player's pseudo.
        """
        return self.pseudo


    def get_elo(self) -> int:
        """
        Returns the player's current ELO rating.

        Returns:
            int: The player's ELO.
        """
        return self.elo


    def get_historical(self) -> List[Dict[str, Union[int, str]]] :
        """
        Returns the player's historical game records.

        Returns:
            List[Dict[str, Union[int, str]]]: A list of game dictionaries.
        """
        return self.historical


    def set_historical(self, historical: List[Dict[str, Union[int, str]]]) -> None:
        """
        Updates the player's historical game records.

        Args:
            historical (List[Dict[str, Union[int, str]]]): The new historical records.
        """
        self.historical = historical


    def set_elo(self, new_elo: int) -> None:
        """
        Sets the player's ELO to a new value.

        Args:
            new_elo (int): The new ELO rating.
        """
        self.elo = new_elo


    def calculate_elo(self, elo_other_player: int, won: str) -> None:
        """
        Updates the player's ELO after a game against another player.

        Args:
            elo_other_player (int): The ELO of the opponent.
            won (str): The game result: "won", "equality", or "loose".
        """
        k = COEFF_SENSIBILITE_ELO
        expected_score = 1 / (1 + 10**((self.elo - elo_other_player)/400))
        if won == "won":
            real_score = 1 
        elif won == "equality":
            real_score = 0.5
        elif won == "loose":
            real_score = 0
        self.elo = ceil(self.elo + k * (real_score - expected_score))