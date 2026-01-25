import pygame
import os
import threading
import socket
import struct

# Initialisation Pygame
pygame.init()

# Constantes
TILE_SIZE = 80
BOARD_SIZE = 8
WINDOW_SIZE = TILE_SIZE * BOARD_SIZE
INFO_PANEL_WIDTH = 200

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
HIGHLIGHT = (186, 202, 68)
SELECTED = (246, 246, 105)
POSSIBLE_MOVE = (130, 151, 105)

# Symboles Unicode pour les pièces (fallback si pas d'images)
PIECE_UNICODE = {
    'K': {'WHITE': '♔', 'BLACK': '♚'},
    'Q': {'WHITE': '♕', 'BLACK': '♛'},
    'R': {'WHITE': '♖', 'BLACK': '♜'},
    'B': {'WHITE': '♗', 'BLACK': '♝'},
    'N': {'WHITE': '♘', 'BLACK': '♞'},
    'P': {'WHITE': '♙', 'BLACK': '♟'},
}


class ChessGUI:
    def __init__(self, client=None):
        self.client = client
        self.screen = pygame.display.set_mode((WINDOW_SIZE + INFO_PANEL_WIDTH, WINDOW_SIZE))
        pygame.display.set_caption("EchecScolaire")
        
        self.font = pygame.font.SysFont('segoeuisymbol', 60)
        self.small_font = pygame.font.SysFont('arial', 20)
        self.info_font = pygame.font.SysFont('arial', 16)
        
        self.selected_square = None
        self.possible_moves = []
        self.board_state = self.init_board_state()
        self.my_color = 'WHITE'
        self.current_turn = 'WHITE'
        self.game_over = False
        self.game_message = ""
        
        # Timers
        self.white_time = 600  # 10 minutes
        self.black_time = 600
        
        self.load_images()
        
    def load_images(self):
        """Charge les images des pièces et du plateau"""
        self.piece_images = {}
        self.board_image = None
        img_path = os.path.join(os.path.dirname(__file__), '..', 'img')
        
        # Charger l'image du plateau
        board_path = os.path.join(img_path, 'board.png')
        if os.path.exists(board_path):
            try:
                board_img = pygame.image.load(board_path).convert_alpha()
                # Redimensionner à la taille de la fenêtre
                self.board_image = pygame.transform.scale(board_img, (WINDOW_SIZE, WINDOW_SIZE))
                print("Image du plateau chargée")
            except Exception as e:
                print(f"Erreur chargement board.png: {e}")
        
        # Essayer de charger pions.png comme spritesheet
        pions_path = os.path.join(img_path, 'pions.png')
        if os.path.exists(pions_path):
            try:
                sheet = pygame.image.load(pions_path).convert()
                # Remplacer le magenta par de la transparence
                arr = pygame.surfarray.pixels3d(sheet)
                alpha = pygame.surfarray.pixels_alpha(sheet)
                magenta = (255, 0, 255)
                mask = (arr[:,:,0] == 255) & (arr[:,:,1] == 0) & (arr[:,:,2] == 255)
                alpha[:,:][mask] = 0
                del arr, alpha
                sheet = sheet.convert_alpha()
                sheet_w, sheet_h = sheet.get_size()
                sprite_w = sheet_w // 6
                sprite_h = sheet_h // 2
                pieces = ['K', 'Q', 'B', 'N', 'R', 'P']
                colors = ['WHITE', 'BLACK']
                for row, color in enumerate(colors):
                    for col, piece in enumerate(pieces):
                        x = col * sprite_w
                        y = row * sprite_h
                        rect = pygame.Rect(x, y, sprite_w, sprite_h)
                        sprite = sheet.subsurface(rect).copy()
                        # Auto-crop sur le contenu non transparent
                        bbox = sprite.get_bounding_rect()
                        cropped = sprite.subsurface(bbox).copy() if bbox.width > 0 and bbox.height > 0 else sprite
                        # Redimensionner à la taille de la case
                        image = pygame.transform.scale(cropped, (TILE_SIZE - 10, TILE_SIZE - 10))
                        self.piece_images[(piece, color)] = image
                print(f"Sprites chargés: {len(self.piece_images)} pièces")
            except Exception as e:
                print(f"Erreur chargement spritesheet: {e}")
                self.piece_images = {}
    
    def init_board_state(self):
        """Initialise l'état du plateau"""
        board = [[None for _ in range(8)] for _ in range(8)]
        
        # Placement initial des pièces
        # Ligne 0 : pièces noires
        board[0] = [('R', 'BLACK'), ('N', 'BLACK'), ('B', 'BLACK'), ('Q', 'BLACK'),
                    ('K', 'BLACK'), ('B', 'BLACK'), ('N', 'BLACK'), ('R', 'BLACK')]
        board[1] = [('P', 'BLACK') for _ in range(8)]
        
        # Ligne 7 : pièces blanches
        board[7] = [('R', 'WHITE'), ('N', 'WHITE'), ('B', 'WHITE'), ('Q', 'WHITE'),
                    ('K', 'WHITE'), ('B', 'WHITE'), ('N', 'WHITE'), ('R', 'WHITE')]
        board[6] = [('P', 'WHITE') for _ in range(8)]
        
        return board
    
    def draw_board(self):
        """Dessine le plateau"""
        # Dessiner l'image du plateau si disponible
        if self.board_image:
            self.screen.blit(self.board_image, (0, 0))
        else:
            # Fallback: dessiner le plateau avec des couleurs
            for row in range(BOARD_SIZE):
                for col in range(BOARD_SIZE):
                    if (row + col) % 2 == 0:
                        color = LIGHT_SQUARE
                    else:
                        color = DARK_SQUARE
                    rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(self.screen, color, rect)
        
        # Surligner les cases spéciales (sélection et mouvements possibles)
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                
                if self.selected_square == (row, col):
                    # Case sélectionnée: overlay jaune semi-transparent
                    s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                    s.fill((246, 246, 105, 150))
                    self.screen.blit(s, rect)
                elif (row, col) in self.possible_moves:
                    # Mouvement possible: cercle vert
                    center = (col * TILE_SIZE + TILE_SIZE // 2, row * TILE_SIZE + TILE_SIZE // 2)
                    pygame.draw.circle(self.screen, POSSIBLE_MOVE, center, 15)
                
                # Dessiner la pièce
                piece = self.board_state[row][col]
                if piece:
                    self.draw_piece(piece, row, col)
        
        # Dessiner les coordonnées
        for i in range(8):
            # Lettres (a-h)
            letter = chr(ord('a') + i)
            text = self.info_font.render(letter, True, BLACK)
            self.screen.blit(text, (i * TILE_SIZE + TILE_SIZE // 2 - 5, WINDOW_SIZE - 18))
            
            # Chiffres (1-8)
            number = str(8 - i)
            text = self.info_font.render(number, True, BLACK)
            self.screen.blit(text, (5, i * TILE_SIZE + TILE_SIZE // 2 - 8))
    
    def draw_piece(self, piece, row, col):
        """Dessine une pièce sur une case"""
        piece_type, piece_color = piece
        x = col * TILE_SIZE + TILE_SIZE // 2
        y = row * TILE_SIZE + TILE_SIZE // 2
        
        if (piece_type, piece_color) in self.piece_images:
            # Utiliser l'image
            img = self.piece_images[(piece_type, piece_color)]
            rect = img.get_rect(center=(x, y))
            self.screen.blit(img, rect)
        else:
            # Utiliser les caractères Unicode
            symbol = PIECE_UNICODE.get(piece_type, {}).get(piece_color, '?')
            text_color = (50, 50, 50) if piece_color == 'WHITE' else (20, 20, 20)
            text = self.font.render(symbol, True, text_color)
            text_rect = text.get_rect(center=(x, y))
            self.screen.blit(text, text_rect)
    
    def draw_info_panel(self):
        """Dessine le panneau d'information"""
        panel_x = WINDOW_SIZE
        pygame.draw.rect(self.screen, (50, 50, 50), (panel_x, 0, INFO_PANEL_WIDTH, WINDOW_SIZE))
        
        # Titre
        title = self.small_font.render("EchecScolaire", True, WHITE)
        self.screen.blit(title, (panel_x + 50, 20))
        
        # Tour actuel
        turn_text = f"Tour: {'Blancs' if self.current_turn == 'WHITE' else 'Noirs'}"
        turn = self.small_font.render(turn_text, True, WHITE)
        self.screen.blit(turn, (panel_x + 20, 60))
        
        # Ma couleur
        my_color_text = f"Vous jouez: {'Blancs' if self.my_color == 'WHITE' else 'Noirs'}"
        my_color = self.info_font.render(my_color_text, True, (150, 150, 150))
        self.screen.blit(my_color, (panel_x + 20, 90))
        
        # Timers
        white_time_str = self.format_time(self.white_time)
        black_time_str = self.format_time(self.black_time)
        
        pygame.draw.rect(self.screen, WHITE, (panel_x + 20, 130, 160, 40))
        white_timer = self.small_font.render(f"⬜ {white_time_str}", True, BLACK)
        self.screen.blit(white_timer, (panel_x + 30, 138))
        
        pygame.draw.rect(self.screen, (30, 30, 30), (panel_x + 20, 180, 160, 40))
        black_timer = self.small_font.render(f"⬛ {black_time_str}", True, WHITE)
        self.screen.blit(black_timer, (panel_x + 30, 188))
        
        # Message de jeu
        if self.game_message:
            msg = self.info_font.render(self.game_message, True, (255, 200, 100))
            self.screen.blit(msg, (panel_x + 20, 250))
        
        # Instructions
        instructions = [
            "Clic: Sélectionner",
            "Clic: Déplacer",
            "ESC: Quitter"
        ]
        for i, inst in enumerate(instructions):
            text = self.info_font.render(inst, True, (150, 150, 150))
            self.screen.blit(text, (panel_x + 20, WINDOW_SIZE - 80 + i * 20))
    
    def format_time(self, seconds):
        """Formate le temps en MM:SS"""
        minutes = int(seconds) // 60
        secs = int(seconds) % 60
        return f"{minutes:02}:{secs:02}"
    
    def get_square_from_mouse(self, pos):
        """Retourne la case (row, col) depuis la position de la souris"""
        x, y = pos
        if x >= WINDOW_SIZE:
            return None
        col = x // TILE_SIZE
        row = y // TILE_SIZE
        if 0 <= row < 8 and 0 <= col < 8:
            return (row, col)
        return None
    
    def get_possible_moves(self, row, col):
        """Retourne les mouvements possibles pour une pièce"""
        piece = self.board_state[row][col]
        if not piece:
            return []
        
        piece_type, color = piece
        moves = []
        
        if piece_type == 'P':
            moves = self.get_pawn_moves(row, col, color)
        elif piece_type == 'R':
            moves = self.get_rook_moves(row, col, color)
        elif piece_type == 'N':
            moves = self.get_knight_moves(row, col, color)
        elif piece_type == 'B':
            moves = self.get_bishop_moves(row, col, color)
        elif piece_type == 'Q':
            moves = self.get_queen_moves(row, col, color)
        elif piece_type == 'K':
            moves = self.get_king_moves(row, col, color)
        
        return moves
    
    def is_valid_pos(self, row, col):
        """Vérifie si la position est sur le plateau"""
        return 0 <= row < 8 and 0 <= col < 8
    
    def is_empty(self, row, col):
        """Vérifie si la case est vide"""
        return self.board_state[row][col] is None
    
    def is_enemy(self, row, col, my_color):
        """Vérifie si la case contient une pièce ennemie"""
        piece = self.board_state[row][col]
        return piece is not None and piece[1] != my_color
    
    def get_pawn_moves(self, row, col, color):
        """Mouvements du pion"""
        moves = []
        direction = -1 if color == 'WHITE' else 1
        start_row = 6 if color == 'WHITE' else 1
        
        # Avancer d'une case
        new_row = row + direction
        if self.is_valid_pos(new_row, col) and self.is_empty(new_row, col):
            moves.append((new_row, col))
            
            # Avancer de deux cases (seulement si le pion n'a jamais bougé)
            if row == start_row:
                new_row2 = row + 2 * direction
                if self.is_valid_pos(new_row2, col) and self.is_empty(new_row2, col):
                    moves.append((new_row2, col))
        
        # Captures en diagonale
        for dc in [-1, 1]:
            new_col = col + dc
            if self.is_valid_pos(new_row, new_col) and self.is_enemy(new_row, new_col, color):
                moves.append((new_row, new_col))
        
        return moves
    
    def get_rook_moves(self, row, col, color):
        """Mouvements de la tour"""
        moves = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        for dr, dc in directions:
            for i in range(1, 8):
                new_row, new_col = row + dr * i, col + dc * i
                if not self.is_valid_pos(new_row, new_col):
                    break
                if self.is_empty(new_row, new_col):
                    moves.append((new_row, new_col))
                elif self.is_enemy(new_row, new_col, color):
                    moves.append((new_row, new_col))
                    break
                else:
                    break
        
        return moves
    
    def get_knight_moves(self, row, col, color):
        """Mouvements du cavalier"""
        moves = []
        offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                   (1, -2), (1, 2), (2, -1), (2, 1)]
        
        for dr, dc in offsets:
            new_row, new_col = row + dr, col + dc
            if self.is_valid_pos(new_row, new_col):
                if self.is_empty(new_row, new_col) or self.is_enemy(new_row, new_col, color):
                    moves.append((new_row, new_col))
        
        return moves
    
    def get_bishop_moves(self, row, col, color):
        """Mouvements du fou"""
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        
        for dr, dc in directions:
            for i in range(1, 8):
                new_row, new_col = row + dr * i, col + dc * i
                if not self.is_valid_pos(new_row, new_col):
                    break
                if self.is_empty(new_row, new_col):
                    moves.append((new_row, new_col))
                elif self.is_enemy(new_row, new_col, color):
                    moves.append((new_row, new_col))
                    break
                else:
                    break
        
        return moves
    
    def get_queen_moves(self, row, col, color):
        """Mouvements de la dame (tour + fou)"""
        return self.get_rook_moves(row, col, color) + self.get_bishop_moves(row, col, color)
    
    def get_king_moves(self, row, col, color):
        """Mouvements du roi"""
        moves = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                new_row, new_col = row + dr, col + dc
                if self.is_valid_pos(new_row, new_col):
                    if self.is_empty(new_row, new_col) or self.is_enemy(new_row, new_col, color):
                        moves.append((new_row, new_col))
        
        return moves
    
    def handle_click(self, pos):
        """Gère le clic de souris"""
        square = self.get_square_from_mouse(pos)
        if not square:
            return
        
        row, col = square
        
        if self.selected_square is None:
            # Sélectionner une pièce
            piece = self.board_state[row][col]
            if piece and piece[1] == self.my_color:
                self.selected_square = (row, col)
                self.possible_moves = self.get_possible_moves(row, col)
        else:
            # Déplacer la pièce
            start_row, start_col = self.selected_square
            piece = self.board_state[start_row][start_col]
            
            # Ne rien faire si on clique sur la même case
            if (row, col) == self.selected_square:
                self.selected_square = None
                self.possible_moves = []
                return
            
            # Si on clique sur une de nos pièces, la sélectionner
            target = self.board_state[row][col]
            if target and target[1] == self.my_color:
                self.selected_square = (row, col)
                self.possible_moves = self.get_possible_moves(row, col)
                return
            
            if piece:
                # Vérifier que le mouvement est valide
                if (row, col) not in self.possible_moves:
                    # Mouvement invalide, désélectionner
                    self.selected_square = None
                    self.possible_moves = []
                    return
                
                # Envoyer au serveur
                start = f"{chr(ord('a') + start_col)}{8 - start_row}"
                end = f"{chr(ord('a') + col)}{8 - row}"
                
                if self.client:
                    self.client.send(f"play {start} {end}")
                
                # Effectuer le mouvement localement
                self.board_state[row][col] = piece
                self.board_state[start_row][start_col] = None
                
                # Changer de tour
                self.current_turn = 'BLACK' if self.current_turn == 'WHITE' else 'WHITE'
            
            self.selected_square = None
            self.possible_moves = []
    
    def update_from_server(self, message):
        """Met à jour l'état depuis un message serveur"""
        parts = message.strip().split(' ')
        cmd = parts[0]
        
        if cmd == 'move' or cmd == 'play_ad':
            # Format: move e2 e4 ou play_ad e2 e4
            start, end = parts[1], parts[2]
            start_col = ord(start[0]) - ord('a')
            start_row = 8 - int(start[1])
            end_col = ord(end[0]) - ord('a')
            end_row = 8 - int(end[1])
            
            piece = self.board_state[start_row][start_col]
            self.board_state[end_row][end_col] = piece
            self.board_state[start_row][start_col] = None
            self.current_turn = 'BLACK' if self.current_turn == 'WHITE' else 'WHITE'
        
        elif cmd == 'start':
            # Format: start w ou start b
            self.my_color = 'WHITE' if parts[1] == 'w' else 'BLACK'
            self.board_state = self.init_board_state()
            self.current_turn = 'WHITE'
        
        elif cmd == 'win':
            self.game_message = "Vous avez gagné!"
            self.game_over = True
        
        elif cmd == 'loose' or cmd == 'lose':
            self.game_message = "Vous avez perdu."
            self.game_over = True
        
        elif cmd == 'draw':
            self.game_message = "Match nul!"
            self.game_over = True
    
    def run(self):
        """Boucle principale du jeu"""
        clock = pygame.time.Clock()
        running = True
        
        # Si on a un client, lancer un thread pour écouter le serveur
        if self.client and self.client.file:
            self.listening = True
            listener_thread = threading.Thread(target=self.listen_server, daemon=True)
            listener_thread.start()
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Clic gauche
                        if not self.game_over and self.current_turn == self.my_color:
                            self.handle_click(event.pos)
            
            # Dessiner
            self.screen.fill(WHITE)
            self.draw_board()
            self.draw_info_panel()
            
            pygame.display.flip()
            clock.tick(60)
        
        self.listening = False
        pygame.quit()
    
    def listen_server(self):
        """Thread pour écouter les messages du serveur"""
        while self.listening:
            try:
                if self.client and self.client.file:
                    line = self.client.file.readline()
                    if line:
                        self.update_from_server(line)
            except Exception as e:
                print(f"Erreur écoute serveur: {e}")
                break
    
    def send_move(self, start, end):
        """Envoie un mouvement au serveur"""
        if self.client:
            self.client.send(f"play {start} {end}")


def main():
    """Point d'entrée pour tester l'interface"""
    gui = ChessGUI()
    gui.run()


if __name__ == "__main__":
    main()
