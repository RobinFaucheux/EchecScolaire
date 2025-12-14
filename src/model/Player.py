from math import ceil
from .constant import *
from typing import List, Dict, Union

class Player:

    def __init__(self, id: int, pseudo: str, elo: float, historical: List[Dict[str, Union[int, str]]] = []):
        self.id = id
        self.pseudo = pseudo
        self.elo = elo
        self.historical = historical

    def get_id(self) -> int:
        return self.id

    def get_pseudo(self) -> str:
        return self.pseudo

    def get_elo(self) -> int:
        return self.elo

    def get_historical(self) -> List[Dict[str, Union[int, str]]]:
        return self.historical
    
    def set_historical(self, historical: List[Dict[str, Union[int, str]]]):
        self.historical = historical

    def set_elo(self, new_elo: int) -> None:
        self.elo = new_elo

    # def add_historical_entry(self, elo: int, date: str) -> None:
    #     self.historical.append(elo, date)

    def calculate_elo(self, elo_other_player: int, won: str) -> None:
        k = COEFF_SENSIBILITE_ELO
        expected_score = 1 / (1 + 10**((self.elo - elo_other_player)/400))
        if won == "won":
            real_score = 1 
        elif won == "equality":
            real_score = 0.5
        elif won == "loose":
            real_score = 0
        self.elo = ceil(self.elo + k * (real_score - expected_score))