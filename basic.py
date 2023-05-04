import pygame
import sys, os
import socket
import pickle

import random
import time

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


BALL_COLOR = WHITE
BALL_SIZE = 30
FPS = 120
DELTA = 30

SIDES = ["left", "right"]

class Player():
    def __init__(self, side):
        self.side = side
        if side == LEFT_PLAYER: #posición inicial del mono de la izq
            self.pos=[random.randint(0,480),random.randint(0,648)]

        else:
            self.pos=[random.randint(660,960),random.randint(0,648)] #posición inicial del mono de la derecha

    def get_pos(self): #acceder a la posición
        return self.pos

    def get_side(self): #acceder al mono correspondiente 
        return self.side

    def moveDown(self): #para moverse hacia abajo 
        self.pos[Y] += DELTA
        if self.pos[Y] > SIZE[Y]: #no podemos exceder el tamaño de la pantalla
            self.pos[Y] = SIZE[Y]

    def moveUp(self): #equivalente hacia arriba
        self.pos[Y] -= DELTA
        if self.pos[Y] < 0:
            self.pos[Y] = 0
            
    def moveRight(self): #equivalente derecha
        self.pos[X] += DELTA
        if self.pos[X] < 0:
            self.pos[X] = 0
            
    def moveLeft(self): #equivalente izquierda
        self.pos[X] -= DELTA
        if self.pos[X] > SIZE[X]:
            self.pos[X] = SIZE[X]
            
    def __str__(self):
        return f"P<{SIDES[self.side], self.pos}>"

class Ball1():
    def __init__(self, velocity):
        self.pos=[ SIZE[X]-300, SIZE[Y]//2 ] #posición inicial del coco 
        self.velocity = velocity

    def get_pos(self): #acceder a la posición
        return self.pos

    def update(self): #actualizar con las velocidades
        self.pos[X] += self.velocity[X]
        self.pos[Y] += self.velocity[Y]

    def bounce(self, AXIS): #rebotar
        self.velocity[AXIS] = -self.velocity[AXIS]

    def collide_player(self): #matar a un jugador 
        self.bounce(X)
        for i in range(3):
            self.update()

    def __str__(self):
        return f"B<{self.pos}>"

class Ball2(): #funciones equivalentes paar el segundo coco 
    def __init__(self, velocity):
        self.pos=[ SIZE[X]//2, SIZE[Y]//4 ]
        self.velocity = velocity

    def get_pos(self):
        return self.pos

    def update(self):
        self.pos[X] += self.velocity[X]
        self.pos[Y] += self.velocity[Y]

    def bounce(self, AXIS):
        self.velocity[AXIS] = -self.velocity[AXIS]

    def collide_player(self):
        self.bounce(X)
        for i in range(3):
            self.update()

    def __str__(self):
        return f"B<{self.pos}>"

class Game():
    def __init__(self):
        self.players = [Player(i) for i in range(2)]
        self.ball1 = Ball1([-2,2]) 
        self.ball2 = Ball2([-1.5,1.5])
        self.game_over = False 

    def get_player(self, side): #acceder al jugador 
        return self.players[side]

    def get_ball1(self): #acceder al coco 
        return self.ball1
    
    def get_ball2(self):
        return self.ball2

    def stop(self): #fin del juego
        self.running = False

    def moveUp(self, player): #moverse arriba un jugador concreto
        self.players[player].moveUp()

    def moveDown(self, player): #abajo 
        self.players[player].moveDown()
    
    def moveRight(self,player): #derecha
        self.players[player].moveRight()
    
    def moveLeft(self,player): #izquierda
        self.players[player].moveLeft()
    
    def movements(self):
        self.ball1.update()  #actualizamos los cocos 
        self.ball2.update()
        pos1 = self.ball1.get_pos()  #accedemos a la posición 
        pos2 = self.ball2.get_pos()
        if pos1[Y]<0 or pos1[Y]>SIZE[Y]: #rebotes 
            self.ball1.bounce(Y)
            
        if pos1[X]>SIZE[X] or pos1[X]<0:
            self.ball1.bounce(X)
            
        if pos2[Y]<0 or pos2[Y]>SIZE[Y]:
            self.ball2.bounce(Y)
            
        if pos2[X]>SIZE[X] or pos2[X]<0:
            self.ball2.bounce(X)

            
    def game_over(self): 
        self.game_over = True

    def __str__(self):
        return f"G<{self.players[RIGHT_PLAYER]}:{self.players[LEFT_PLAYER]}:{self.ball1}:{self.ball2}>"


class Cuadrado(pygame.sprite.Sprite):
    def __init__(self, player):
      super().__init__()
      self.image = pygame.image.load("mono.png") #cargamos la imagen
      self.image = pygame.transform.scale(self.image,(100,100)) #cargamos el tamaño 
      #self.image.set_colorkey(WHITE) #quitamos los bordes 
      self.player = player 
      #color = PLAYER_COLOR[self.player.get_side()]
      #pygame.draw.rect(self.image, color, [0,0,0,0])
      self.rect = self.image.get_rect(center=(110,110))
      self.update()

    def update(self): #actualizamos 
        pos = self.player.get_pos()
        self.rect.centerx, self.rect.centery = pos

    def __str__(self):
        return f"S<{self.player}>"


class BallSprite(pygame.sprite.Sprite): #equivalente
    def __init__(self, ball):
        super().__init__()
        self.ball = ball
        self.image = pygame.image.load("coco.png")
        self.image = pygame.transform.scale(self.image,(85,85))
        self.rect = self.image.get_rect(center=(85,85))
        self.update()

    def update(self): 
        pos = self.ball.get_pos()
        self.rect.centerx, self.rect.centery = pos


class Display():
    def __init__(self, game):
        self.game = game
        self.cuadrados = [Cuadrado(self.game.get_player(i)) for i in range(2)] #generamos los monos
        self.ball1 = BallSprite(self.game.get_ball1()) #generamos cada bola
        self.ball2 = BallSprite(self.game.get_ball2())
        self.all_sprites = pygame.sprite.Group()
        self.cuadrado_group = pygame.sprite.Group()
        for cuadrado  in self.cuadrados:
            self.all_sprites.add(cuadrado)
            self.cuadrado_group.add(cuadrado)
        self.all_sprites.add(self.ball1) 
        self.all_sprites.add(self.ball2)
        self.screen = pygame.display.set_mode(SIZE)
        self.background = pygame.image.load('background.png')
        self.game_over = pygame.image.load('gameover.png')
        self.clock =  pygame.time.Clock()  #FPS
        self.time = 0
        pygame.init()
     
    def game_over_pantalla(self):
        texto_segundos = str(round(self.time-1.0,2)) 
        if float(texto_segundos)<0: 
            texto_segundos='0'
        mensaje_final='¡Oh no! No has conseguido sobrevivir,' #mensaje final 
        mensaje_final2= 'enhorabuena por esos '+texto_segundos+' segundos.'
        font = pygame.font.Font(None, 70) 
        text = font.render(texto_segundos, 1, BLACK) #textos 
        text2 = font.render(mensaje_final, 1, BLACK)
        text3 = font.render(mensaje_final2,1, BLACK)
        self.screen.blit(self.game_over, (0, 0)) #cargamos la imagen
        self.screen.blit(text, (410, 10)) #ponemos los textos
        self.screen.blit(text2,(10,530))
        self.screen.blit(text3,(10,580))
        self.all_sprites.draw(self.screen)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN: #exit
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
        pygame.init()
    def analyze_events(self):
        for event in pygame.event.get(): #asignamos las teclas a los movimientos
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.stop()
                elif event.key == pygame.K_w:#s
                    self.game.moveUp(LEFT_PLAYER)
                elif event.key == pygame.K_s:#x
                    self.game.moveDown(LEFT_PLAYER)
                elif event.key == pygame.K_d:
                    self.game.moveRight(LEFT_PLAYER)
                elif event.key == pygame.K_a:
                    self.game.moveLeft(LEFT_PLAYER)
                elif event.key == pygame.K_i:#k
                    self.game.moveUp(RIGHT_PLAYER)
                elif event.key == pygame.K_k:#m
                    self.game.moveDown(RIGHT_PLAYER)
                elif event.key == pygame.K_l:
                    self.game.moveRight(RIGHT_PLAYER)
                elif event.key == pygame.K_j:
                    self.game.moveLeft(RIGHT_PLAYER)
                
        if pygame.sprite.spritecollide(self.ball1, self.cuadrado_group, False): #choque
            self.game.get_ball1().collide_player()
            self.game.game_over = True
        if pygame.sprite.spritecollide(self.ball2, self.cuadrado_group, False):
            self.game.get_ball2().collide_player()
            self.game.game_over = True
        self.all_sprites.update()



    def refresh(self): #actualizamos todo
        self.screen.blit(self.background, (0, 0))
        font = pygame.font.Font(None, 74)
        self.time = pygame.time.get_ticks()/1000
        segundos = str(self.time)
        text = font.render(segundos, 1, WHITE)
        self.screen.blit(text, (410, 10))
        self.all_sprites.draw(self.screen)
        pygame.display.flip()

    def tick(self):
        self.clock.tick(FPS)

    @staticmethod
    def quit():
        pygame.quit()

class Network:
    def __init__(self): ##this will connect to the server initially
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = '127.0.0.1' #server ip #<---
        self.port = 5555   #server port #<---
        self.addr = (self.server, self.port)
        self.p = self.connect()
    def getP(self):
        return self.p
    def connect(self):
        try:
            self.client.connect(self.addr)
            return pickle.loads(self.client.recv(2048))
        except:
            pass
    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(2048))
        except socket.error as e:
            print(e)


def main():
    try:
        game = Game()
        display = Display(game)
        i=1
        while game.game_over == False:
            game.movements()
            display.analyze_events()
            display.refresh()
            if i==1: #dejamos que se muestre el juego 1 segundo anets de comenzar para no morir directamente 
                time.sleep(1)
                i=0
            display.tick()
        while game.game_over == True:
           display.game_over_pantalla()
           
    finally:
        pygame.quit()

if __name__=="__main__":
    main()

