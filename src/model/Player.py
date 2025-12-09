class Player:

    def __init__(self, id: int, pseudo: str, elo: int, historical: list[tuple[int, str]], game: object):
        self.id = id
        self.pseudo = pseudo
        self.elo = elo
        self.historical = historical
        self.game = game

    def get_id(self) -> int:
        return self.id

    def get_pseudo(self) -> str:
        return self.pseudo

    def get_elo(self) -> int:
        return self.elo

    def get_historical(self) -> list[tuple[int, str]]:
        return self.historical

    def get_game(self) -> object:
        return self.game

    def set_elo(self, new_elo: int) -> None:
        self.elo = new_elo
    
    def set_game(self, new_game: object) -> None:
        self.game = new_game

    def add_historical_entry(self, elo: int, date: str) -> None:
        self.historical.append((elo, date))

    def play_game(self) -> None:
        self.game.play_game()