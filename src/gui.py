import pygame
import os

pygame.init()

# --- CONSTANTES ---
TILE_SIZE = 80          
BOARD_SIZE = 8          
BOARD_OFFSET = 28
PIECE_OFFSET_Y = -10
WINDOW_SIZE = (TILE_SIZE * BOARD_SIZE) + (BOARD_OFFSET * 2)
INFO_PANEL_WIDTH = 200

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
POSSIBLE_MOVE = (130, 151, 105)

PIECE_UNICODE = {
    'K': {'WHITE': '♔', 'BLACK': '♚'}, 'Q': {'WHITE': '♕', 'BLACK': '♛'},
    'R': {'WHITE': '♖', 'BLACK': '♜'}, 'B': {'WHITE': '♗', 'BLACK': '♝'},
    'N': {'WHITE': '♘', 'BLACK': '♞'}, 'P': {'WHITE': '♙', 'BLACK': '♟'},
}

class ChessGUI:
    def __init__(self, my_color='WHITE'):
        self.screen = pygame.display.set_mode((WINDOW_SIZE + INFO_PANEL_WIDTH, WINDOW_SIZE))
        pygame.display.set_caption(f"EchecScolaire - {my_color}")
        
        self.font = pygame.font.SysFont('segoeuisymbol', 60)
        self.small_font = pygame.font.SysFont('arial', 20)
        self.info_font = pygame.font.SysFont('arial', 16)
        
        self.board_state = self.init_board_state()
        self.my_color = my_color 
        self.current_turn = 'WHITE'
        self.game_over = False
        self.game_message = ""
        self.running = True
        
        # Timers visuels
        self.white_time = 600
        self.black_time = 600
        
        self.load_images()
        
    def load_images(self):
        self.piece_images = {}; self.board_image = None
        base_dir = os.path.dirname(__file__)
        img_path = base_dir
        for p in [os.path.join(base_dir, 'img'), os.path.join(base_dir, '..', 'img')]:
            if os.path.exists(p) and os.path.isdir(p): img_path = p; break

        for name in ['board.jpg', 'board.png']:
            p = os.path.join(img_path, name)
            if os.path.exists(p):
                try:
                    self.board_image = pygame.transform.scale(pygame.image.load(p).convert(), (WINDOW_SIZE, WINDOW_SIZE))
                    break
                except: pass

        pieces = ['K', 'Q', 'B', 'N', 'R', 'P']
        cols = ['WHITE', 'BLACK']; pre = {'WHITE': 'white', 'BLACK': 'black'}
        nams = {'K': 'king', 'Q': 'queen', 'B': 'bishop', 'N': 'knight', 'R': 'rook', 'P': 'pawn'}
        magenta = (255, 0, 255)

        for c in cols:
            for p in pieces:
                fp = os.path.join(img_path, f"{pre[c]}_{nams[p]}.png")
                if os.path.exists(fp):
                    try:
                        src = pygame.image.load(fp).convert(); src.set_colorkey(magenta)
                        surf = pygame.Surface(src.get_size(), pygame.SRCALPHA); surf.fill((0,0,0,0)); surf.blit(src, (0,0))
                        rect = surf.get_bounding_rect()
                        if rect.w > 0: surf = surf.subsurface(rect).copy()
                        sz = int(TILE_SIZE * 0.85)
                        ratio = min(sz/surf.get_width(), sz/surf.get_height())
                        final = pygame.transform.smoothscale(surf, (int(surf.get_width()*ratio), int(surf.get_height()*ratio)))
                        self.piece_images[(p, c)] = final
                    except: pass

    def init_board_state(self):
        b = [[None]*8 for _ in range(8)]
        b[0] = [('R','BLACK'), ('N','BLACK'), ('B','BLACK'), ('Q','BLACK'), ('K','BLACK'), ('B','BLACK'), ('N','BLACK'), ('R','BLACK')]
        b[1] = [('P','BLACK') for _ in range(8)]
        b[7] = [('R','WHITE'), ('N','WHITE'), ('B','WHITE'), ('Q','WHITE'), ('K','WHITE'), ('B','WHITE'), ('N','WHITE'), ('R','WHITE')]
        b[6] = [('P','WHITE') for _ in range(8)]
        return b

    def get_view_coords(self, r, c):
        if self.my_color == 'BLACK': return 7-r, 7-c
        return r, c

    def get_screen_coords(self, row, col):
        vr, vc = self.get_view_coords(row, col)
        return BOARD_OFFSET + vc * TILE_SIZE, BOARD_OFFSET + vr * TILE_SIZE

    def draw_board(self):
        if self.board_image: self.screen.blit(self.board_image, (0, 0))
        else: self.screen.fill((50, 50, 50))
        
        for row in range(8):
            for col in range(8):
                x, y = self.get_screen_coords(row, col)
                piece = self.board_state[row][col]
                if piece:
                    cx, cy = x + TILE_SIZE//2, y + TILE_SIZE//2 + PIECE_OFFSET_Y
                    if piece in self.piece_images:
                        im = self.piece_images[piece]
                        self.screen.blit(im, im.get_rect(center=(cx, cy)))
                    else:
                        col_txt = (255,255,255) if piece[1]=='WHITE' else (0,0,0)
                        txt = self.font.render(PIECE_UNICODE[piece[0]][piece[1]], True, col_txt)
                        self.screen.blit(txt, txt.get_rect(center=(cx, cy)))
        
        for i in range(8):
            ci = i if self.my_color == 'WHITE' else 7 - i
            ni = 8 - i if self.my_color == 'WHITE' else i + 1
            self.screen.blit(self.info_font.render(chr(ord('a')+ci), True, BLACK), (BOARD_OFFSET + i*TILE_SIZE + 35, WINDOW_SIZE - 20))
            self.screen.blit(self.info_font.render(str(ni), True, BLACK), (8, BOARD_OFFSET + i*TILE_SIZE + 35))

    def draw_info_panel(self):
        px = WINDOW_SIZE
        pygame.draw.rect(self.screen, (40, 40, 40), (px, 0, INFO_PANEL_WIDTH, WINDOW_SIZE))
        self.screen.blit(self.small_font.render("EchecScolaire", True, WHITE), (px+40, 20))
        
        t = "Blancs" if self.current_turn == 'WHITE' else "Noirs"
        self.screen.blit(self.small_font.render(f"Tour: {t}", True, WHITE), (px+20, 60))
        
        m = "Blancs" if self.my_color == 'WHITE' else "Noirs"
        self.screen.blit(self.info_font.render(f"Vous: {m}", True, (200,200,200)), (px+20, 90))

        self.draw_timer(px+20, 130, self.white_time, False)
        self.draw_timer(px+20, 180, self.black_time, True)
        
        if self.game_message:
            self.screen.blit(self.info_font.render(self.game_message, True, (255,200,0)), (px+20, 250))

    def draw_timer(self, x, y, sec, is_black):
        pygame.draw.rect(self.screen, (20,20,20) if is_black else WHITE, (x, y, 160, 40))
        txt = f"{'⬛' if is_black else '⬜'} {int(sec)//60:02}:{int(sec)%60:02}"
        self.screen.blit(self.small_font.render(txt, True, WHITE if is_black else BLACK), (x+10, y+8))

    def external_move(self, s, e):
        """Met à jour le plateau graphique quand le terminal valide un coup"""
        try:
            sc, sr = ord(s[0])-ord('a'), 8-int(s[1])
            ec, er = ord(e[0])-ord('a'), 8-int(e[1])
            self.board_state[er][ec] = self.board_state[sr][sc]
            self.board_state[sr][sc] = None
            self.current_turn = 'BLACK' if self.current_turn == 'WHITE' else 'WHITE'
        except: pass

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: self.running = False
            
            self.draw_board()
            self.draw_info_panel()
            pygame.display.flip()
            clock.tick(30)
        pygame.quit()

if __name__ == "__main__": ChessGUI().run()