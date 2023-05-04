from multiprocessing.connection import Client
import traceback
import pygame
import sys, os
Monos = ["mono.png","mono2.png"]
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255,255,0)
GREEN = (0,255,0)
X = 0
Y = 1
SIZE = (960, 648)

LEFT_PLAYER = 0
RIGHT_PLAYER = 1
PLAYER_COLOR = [GREEN, YELLOW]
PLAYER_HEIGHT = 60
PLAYER_WIDTH = 10

BALL_COLOR = WHITE
BALL_SIZE = 10
FPS = 60


SIDES = ["left", "right"]
SIDESSTR = ["left", "right"]

class Player():
    def __init__(self, side):
        self.side = side #definimos el lado
        self.pos = [None, None] #una tupla con la posición 

    def get_pos(self): #acceder a la posición 
        return self.pos

    def get_side(self): #acceder al lado, es decir, el mono que se inicia en el lado izquiero o en el derecho
        return self.side

    def set_pos(self, pos): #modificar la posición
        self.pos = pos

    def __str__(self):
        return f"P<{SIDES[self.side], self.pos}>"

class Ball1(): #funciones equivalentes 
    def __init__(self): 
        self.pos=[ None, None ]

    def get_pos(self): 
        return self.pos

    def set_pos(self, pos): 
        self.pos = pos

    def __str__(self):
        return f"B<{self.pos}>"
class Ball2(): #funciones equivalentes 
    def __init__(self):
        self.pos=[ None, None ]

    def get_pos(self):
        return self.pos

    def set_pos(self, pos):
        self.pos = pos

    def __str__(self):
        return f"B<{self.pos}>"
class Game():
    def __init__(self):
        self.players = [Player(i) for i in range(2)] #inicializamos dos jugadores
        self.ball1 = Ball1() #iniciamos los cocos 
        self.ball2 = Ball2()
        self.running = True #para comprobar si el juego está en curso

    def get_player(self, side): #acceder al jugador del lado concreto
        return self.players[side]

    def set_pos_player(self, side, pos): #modiicar la posición
        self.players[side].set_pos(pos)


    def get_ball1(self): #acceder a la información del coco
        return self.ball1

    def set_ball_pos1(self, pos): #modificar la posición 
        self.ball1.set_pos(pos)
    
    def get_ball2(self): #análoga 
        return self.ball2
    
    def set_ball_pos2(self, pos):#análoga
        self.ball2.set_pos(pos)
    


    def update(self, gameinfo): #actualizar el juego
        self.set_pos_player(LEFT_PLAYER, gameinfo['pos_left_player']) #modificamos las posiciones de los monos y las bolas 
        self.set_pos_player(RIGHT_PLAYER, gameinfo['pos_right_player'])
        self.set_ball_pos1(gameinfo['pos_ball1']) 
        self.set_ball_pos2(gameinfo['pos_ball2'])
        self.running = gameinfo['is_running'] #comprobamos que el juego no ha acabado 

    def is_running(self): #devuelve si el juego sigue funcionando
        return self.running

    def stop(self):#detener el juego
        self.running = False

    def __str__(self):
        return f"G<{self.players[RIGHT_PLAYER]}:{self.players[LEFT_PLAYER]}:{self.ball}>"

class Cuadrado(pygame.sprite.Sprite):
    def __init__(self, player): #definimos la parte gráfica de los monos, equivalente a la versión basic
      super().__init__()
      self.player = player
      self.image = pygame.image.load(Monos[self.player.get_side()])
      self.image = pygame.transform.scale(self.image,(120,120))
      self.image.set_colorkey(WHITE)
      color = PLAYER_COLOR[self.player.get_side()]
      pygame.draw.rect(self.image, color, [0,0,0,0])
      self.rect = self.image.get_rect()
      self.update()

    def update(self):
        pos = self.player.get_pos()
        self.rect.centerx, self.rect.centery = pos

class BallSprite(pygame.sprite.Sprite): #expresión gráfica de los cocos, equivalente al basic 
    def __init__(self, ball):
        super().__init__()
        self.ball = ball
        self.image = pygame.image.load("coco.png")
        self.image = pygame.transform.scale(self.image,(85,85))
        self.image.set_colorkey(WHITE)
        pygame.draw.rect(self.image, BALL_COLOR, [0, 0, 0, 0])
        self.rect = self.image.get_rect()
        self.update()

    def update(self): 
        pos = self.ball.get_pos()
        self.rect.centerx, self.rect.centery = pos

class Display(): 
    def __init__(self, game): #inicio del juego
        self.game = game
        self.cuadrados = [Cuadrado(self.game.get_player(i)) for i in range(2)] #definimos las figuras 
        self.ball1 = BallSprite(self.game.get_ball1())
        self.ball2 = BallSprite(self.game.get_ball2())
        self.all_sprites = pygame.sprite.Group()
        self.cuadrado_group = pygame.sprite.Group()
        for cuadrado  in self.cuadrados:
            self.all_sprites.add(cuadrado)
            self.cuadrado_group.add(cuadrado)
        self.all_sprites.add(self.ball1)
        self.all_sprites.add(self.ball2)
        self.screen = pygame.display.set_mode(SIZE)
        self.clock =  pygame.time.Clock()  #FPS 
        self.background = pygame.image.load('background.png')
        self.time=0 #iniciamos el tiempo
        pygame.init()
     

    def analyze_events(self,side): #asociamos pulsar una tecla con el movimiento correspondiente
        events = []
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    events.append("quit")
                elif event.key == pygame.K_UP:
                    events.append("up")
                elif event.key == pygame.K_DOWN:
                    events.append("down")
                elif event.key == pygame.K_RIGHT:
                    events.append("right")
                elif event.key == pygame.K_LEFT:
                    events.append("left")
                elif event.type == pygame.QUIT:
                    events.append("quit")
                
        if pygame.sprite.spritecollide(self.ball1, self.cuadrado_group, False): #si uno de los jugadores muere
            #self.game.get_ball1().collide_player()
            #self.game.game_over = True
            #self.game_over_pantalla()
            events.append('quit')
        if pygame.sprite.spritecollide(self.ball2, self.cuadrado_group, False):
            #self.game.get_ball2().collide_player()
            #self.game.game_over = True
            #self.game_over_pantalla()
            events.append('quit')
            
        return events
        

    def refresh(self): #actualizamos la información
        self.all_sprites.update()
        self.screen.blit(self.background, (0, 0))
        font = pygame.font.Font(None, 74)
        self.time = pygame.time.get_ticks()/1000 #para que el tiempo se mida en segundos 
        segundos = str(self.time)
        text = font.render(segundos, 1, WHITE) 
        self.screen.blit(text, (350, 10)) #colocamos el contador en la pantalla para que se siga actualizando
        self.all_sprites.draw(self.screen)
        pygame.display.flip()

    def tick(self):
        self.clock.tick(FPS)

    @staticmethod
    def quit():
        pygame.quit()
        
def main(ip_address):
    try:
        with Client((ip_address, 6000), authkey=b'secret password') as conn:
            game = Game()
            side,gameinfo = conn.recv()
            print(f"I am playing {SIDESSTR[side]}") 
            game.update(gameinfo)
            display = Display(game)
            while game.is_running(): #iniciamos el juego cuando hayamos conectado con el otro jugador 
                events = display.analyze_events(side)
                for ev in events:
                    conn.send(ev)
                    if ev == 'quit': #detenemos el juego
                        game.stop()
                conn.send("next")
                gameinfo = conn.recv()
                game.update(gameinfo)
                display.refresh()
                display.tick()
            print('Habéis sobrevivido: ', int(display.time), 'segundos.')
    except:
        traceback.print_exc()
    finally:
        pygame.quit()


if __name__=="__main__":
    ip_address = "127.0.0.1"
    if len(sys.argv)>1:
        ip_address = sys.argv[1]
    main(ip_address)

