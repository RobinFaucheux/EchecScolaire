class Player:

    def __init__(self, id: int, pseudo: str, elo: int, historical: list[tuple[int, str]]):
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

    def get_historical(self) -> list[tuple[int, str]]:
        return self.historical

    def set_elo(self, new_elo: int) -> None:
        self.elo = new_elo

    def add_historical_entry(self, elo: int, date: str) -> None:
        self.historical.append((elo, date))
