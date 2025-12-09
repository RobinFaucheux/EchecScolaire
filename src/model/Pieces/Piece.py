from .. import Color, Case

class Piece:
    def __init__(self, color : Color, case : Case ):
        self.color =  color
        self.case = case
        self._vectors = []

    def get_color(self) -> Color:
        return self.color
    
    def set_color(self, color : Color):
        self.color = color
    
    def get_case(self) -> Case:
        return self.case

    def set_case(self, case : Case):
        self.case = case

    def move(self, case : Case) -> bool:
        self.case.remove_piece()
        case.add_piece(self)
        return True

    