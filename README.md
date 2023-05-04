# monos-vs-cocos
Este repositorio contiene la práctica número 3 realizada por Gabriela Ballesteros Gómez y Cesar De Diego Morales
El juego consiste en dos monos cuyo objetivo es sobrevivir al atque de los cocos. Intenta sobrevivir el máximo tiempo posible.
El archivo basic.py contiene una versión del juego ejecutable en un solo ordenador. En este caso tenemos el control de ambos monos que controlaremos con las teclas wsda para mono1 de la izquierda, e iklj para mono2 de la derecha. La posición inicial de los monos será aleatoria, por lo que al aparecer la pantalla de juego hay un intervalo de 1 segundo para que te situes donde está el mono, y no pierdas a la primera de cambio. 
El archivo player_juego conecta hasta dos jugadores cada uno en su ordernador conectados a traves de la misma red cableada. En concreto contiene todas las funciones de movimiento de los monos y sus teclas asociadas, que en este caso será para ambos jugadores las flechas del teclado.
En el archivo sala_juego creamos la sala del juego, donde son enviados todos los comandos de los movimientos, de forma que funcionen de manera simultanea. Además generamois los cocos que debemos esquivar.
Cabe mencionar que las imagenes background, coco, gameover, mono, mono2 nos aportan la imagen gráfica de nuestros elementos en el juego.
Para ejecutar el juego desde la terminal de dos ordenadores:
    -ordenador1 : en una pestaña escribimos el comando $python3 sala_juego.py ip_ordenador1
    -ordenador1 y 2 : en otra pestaña ejecutamos $python3 plkayer_juego.py ip_ordenador1 
    
    
    
¡ MUCHA SUERTE ! 
