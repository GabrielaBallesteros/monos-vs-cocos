from multiprocessing.connection import Listener
from multiprocessing import Process, Manager, Value, Lock
import traceback
import sys

LEFT_PLAYER = 0
RIGHT_PLAYER = 1
SIDESSTR = ["left", "right"]
SIZE = (960, 648)

X=0
Y=1
DELTA = 30

class Player():
    def __init__(self, side):
        self.side = side
        if side == LEFT_PLAYER: #accedemos a la posición del jugador 
            self.pos = [10, SIZE[Y]//2]
        else:
            self.pos = [SIZE[X] - 10, SIZE[Y]//2]

    def get_pos(self): #posición del jugador 
        return self.pos 

    def get_side(self): #mono de la derecha o de la izquierda 
        return self.side

    def moveDown(self): #nos movemos hacia abajo
        self.pos[Y] += DELTA
        if self.pos[Y] > SIZE[Y]: #no me salgo del cuadrado
            self.pos[Y] = SIZE[Y]

    def moveUp(self): #nos movemos hacia arriba 
        self.pos[Y] -= DELTA
        if self.pos[Y] < 0: #no me salgo del cuadrado
            self.pos[Y] = 0
            
    def moveRight(self): #nos movemos a la derecha 
        self.pos[X] += DELTA
        if self.pos[X] < 0: #no me salgo del cuadrado 
            self.pos[X] = 0
            
    def moveLeft(self): #nos movemos a la izquierda 
        self.pos[X] -= DELTA
        if self.pos[X] > SIZE[X]: #no me salgo del cuadrado
            self.pos[X] = SIZE[X]
            
    def __str__(self):
        return f"P<{SIDESSTR[self.side]}, {self.pos}>"
    
class Ball1(): #definimos los cocos por separado para evitar movimientos simétricos 
    def __init__(self, velocity):
        self.pos=[ SIZE[X]-300, SIZE[Y]//2 ] #posición inicial del coco
        self.velocity = velocity

    def get_pos(self): #accedemos a la posición del coco 
        return self.pos

    def update(self): #actualizamos dónde está el coco según la velocidad 
        self.pos[X] += self.velocity[X]
        self.pos[Y] += self.velocity[Y]

    def bounce(self, AXIS): #el coco rebota 
        self.velocity[AXIS] = -self.velocity[AXIS]

    def collide_player(self): #el coco mata al mono
        self.bounce(X)
        for i in range(3):
            self.update()

    def __str__(self):
        return f"B<{self.pos,self.velocity}>"

class Ball2(): #funciones equivalentes 
    def __init__(self, velocity):
        self.pos=[ SIZE[X]//2, SIZE[Y]//4 ] #posición inicial coco 2 
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
        return f"B<{self.pos,self.velocity}>"

class Game():
    def __init__(self,manager):
        self.players = manager.list( [Player(LEFT_PLAYER),Player(RIGHT_PLAYER)] ) #meetmos en una lista a ambos monos 
        self.ball1 = manager.list([Ball1([-3,3])]) #iniciamos la velocidad del primer coco
        self.ball2 = manager.list([Ball2([-2.5,2.5])]) #inciciamos la velocidad del segundo coco 
        self.running = Value('i', 1) # 1 = running para acceder a si el juego está activo
        self.lock = Lock()
        self.game_over = False #bool que cambiará cuando colapsen un coco y un mono => fin de la partida

    def get_player(self, side): #accedemos a uno de los jugadores 
        return self.players[side]

    def get_ball1(self):
        return self.ball1
    
    def get_ball2(self):
        return self.ball2

    def is_running(self): 
        return self.running

    def stop(self):
        self.running.value =0  #cuando acaba el juego, cambiamos el valor de la variable compartida running 

    def moveUp(self, player): # moverse hacia arriba 
        self.lock.acquire()
        p = self.players[player] #accedo al jugador
        p.moveUp() #uso la función de la clase jugador para moverme hacia arriba 
        self.players[player] = p #actualizo el movimiento 
        self.lock.release()

    def moveDown(self, player): #equivalente hacia abajo 
        self.lock.acquire()
        p = self.players[player]
        p.moveDown()
        self.players[player] = p
        self.lock.release()
    
    def moveRight(self,player): #equivalente hacia la derecha 
        self.lock.acquire()
        p = self.players[player]
        p.moveRight()
        self.players[player] = p
        self.lock.release()
    
    def moveLeft(self,player): #equivalente hacia la izquierda 
        self.lock.acquire()
        p = self.players[player]
        p.moveLeft()
        self.players[player] = p
        self.lock.release()
    
    def movements(self):
        self.lock.acquire()
        ball1 = self.ball1[0] #ball1 es un Manager así que accedemos a la posición 0 para poder usar todas las propiedades del coco
        ball2 = self.ball2[0] #equivalente con el 2 
        ball1.update() #actualizamos 
        ball2.update()
        pos1 = ball1.get_pos() #accedo a la posición 
        pos2 = ball2.get_pos()
        if pos1[Y]<0 or pos1[Y]>SIZE[Y]: #tengo que rebotar si el coco está en el límite de la pantalla 
            ball1.bounce(Y)
            
        if pos1[X]>SIZE[X] or pos1[X]<0: #equivalente 
            ball1.bounce(X)
            
        if pos2[Y]<0 or pos2[Y]>SIZE[Y]: # "
            ball2.bounce(Y)
            
        if pos2[X]>SIZE[X] or pos2[X]<0: # "
            ball2.bounce(X)

        self.ball1[0]=ball1 #actualizo 
        self.ball2[0]=ball2 #actualizo 
        self.lock.release() 
        
    def ball_collide(self, player): #función para cuando algún coco choca con algún mono
        self.lock.acquire()
        ball1 = self.ball1[0] #igual que en movements
        ball2 = self.ball2[0]
        ball1.collide_player() #choca con el coco 1 
        ball2.collide_player() #choca con el coco 2 
        self.ball1[0] = ball1 #actualizo 
        self.ball2[0] = ball2 #actualizo 
        self.lock.release()
        
    def get_info(self): #metemos en un diccionario toda la información actualizada para que los monos se ubiquen 
        info = {
            'pos_left_player': self.players[LEFT_PLAYER].get_pos(),
            'pos_right_player': self.players[RIGHT_PLAYER].get_pos(),
            'pos_ball1': self.ball1[0].get_pos(),
            'pos_ball2': self.ball2[0].get_pos(),
            'is_running': self.running.value == 1
        }
        return info
    
    def __str__(self):
        return f"G<{self.players[RIGHT_PLAYER]}:{self.players[LEFT_PLAYER]}:{self.ball1[0]}:{self.ball2[0]}:{self.running}>"

def player(side, conn, game):
    try:
        print(f"starting player {SIDESSTR[side]}:{game.get_info()}")
        conn.send( (side, game.get_info()) )
        while game.is_running():
            command = "" #cuando el jugador pulsa una de las teclas, se ejecutan estas palabras (definido en analyze_events de la clase display)
            while command != "next":
                command = conn.recv()
                if command == "up":
                    game.moveUp(side)
                elif command == "down":
                    game.moveDown(side)
                elif command == "right":
                    game.moveRight(side)
                elif command == "left":
                    game.moveLeft(side)
                elif command == "collide":
                    game.ball_collide(side)
                elif command == "quit":
                    game.stop()
            if side == 1:
                game.movements()
            conn.send(game.get_info())
    except:
        traceback.print_exc()
        conn.close()
    finally:
        print(f"Game ended {game}") #finaliza el juego
        
def main(ip_address): #necesitamos la ip del ordenador que inicie la sala 
    manager = Manager()
    try:
        with Listener((ip_address, 6000),
                      authkey=b'secret password') as listener:
            n_player = 0 #esperando jugadores
            players = [None, None]
            game = Game(manager)
            while True:
                print(f"accepting connection {n_player}")
                conn = listener.accept()
                players[n_player] = Process(target=player,
                                            args=(n_player, conn, game))
                n_player += 1
                if n_player == 2: #cuando tenemos dos jugadores 
                    players[0].start() #inicio el mono 1 
                    players[1].start() #inicio el mono 2 
                    n_player = 0 
                    players = [None, None]
                    game = Game(manager)

    except Exception as e:#por is hay errores de conexión 
        traceback.print_exc()

if __name__=='__main__':
    ip_address = "127.0.0.1"
    if len(sys.argv)>1:
        ip_address = sys.argv[1]

    main(ip_address)