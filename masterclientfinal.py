import pygame
from pygame import *
import os
import random
from os import path
import socket
from _thread import *
from queue import Queue
import ast
import subprocess

WIDTH = 900
HEIGHT = 500
FPS = 30

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BUTTONBLUE = (174,234,255)
BUTTONHIGHLIGHTEDBLUE = (66,134,244)
OUTLINEREMOVE = (160,212,255)

# Default mode:
mode = 'intro'

# Connect to client/ testing lobby 
serverCounter = 0

# Initialize pygame and create window
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PAYDAY 2D")
clock = pygame.time.Clock()

# Path for loading files
img_dir = path.join(path.dirname(__file__), 'img')

# Load game graphics for master client
background = pygame.image.load(path.join(img_dir, "lobbybackground.png")).convert()
background_rect = background.get_rect()
help1 = pygame.image.load(path.join(img_dir, 'help1.png')).convert()
help2 = pygame.image.load(path.join(img_dir, 'help2.png')).convert()
help3 = pygame.image.load(path.join(img_dir, 'help3.png')).convert()

# Sounds for master client
background_music = pygame.mixer.music.load('lobbymusic.mp3')
select_sound = pygame.mixer.Sound('click.wav')

pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1,0.0)

# Animation Variables- used to create scrolling animation
lobbyBlit = 500
helpBlit = 0
direc = 1

# User input variables
startInput = ''
connectInput = ''
ipadd = ' '

# Function to draw rounded rectangles
# This function was taken from an online pygame function library
def AAfilledRoundedRect(surface,rect,color,radius=0.4):

    rect = Rect(rect)
    color = Color(*color)
    alpha = color.a
    color.a = 0
    pos = rect.topleft
    rect.topleft = 0,0
    rectangle = Surface(rect.size,SRCALPHA)

    circle = Surface([min(rect.size)*3]*2,SRCALPHA)
    draw.ellipse(circle,(0,0,0),circle.get_rect(),0)
    circle = transform.smoothscale(circle,[int(min(rect.size)*radius)]*2)

    radius = rectangle.blit(circle,(0,0))
    radius.bottomright = rect.bottomright
    rectangle.blit(circle,radius)
    radius.topright = rect.topright
    rectangle.blit(circle,radius)
    radius.bottomleft = rect.bottomleft
    rectangle.blit(circle,radius)

    rectangle.fill((0,0,0),rect.inflate(-radius.w,0))
    rectangle.fill((0,0,0),rect.inflate(0,-radius.h))

    rectangle.fill(color,special_flags=BLEND_RGBA_MAX)
    rectangle.fill((255,255,255,alpha),special_flags=BLEND_RGBA_MIN)

    return surface.blit(rectangle,pos)

fontTitle = pygame.font.SysFont('Subway Ticker', 90)
fontButton = pygame.font.SysFont('Subway Ticker', 45)

#- Code to run role of seeker-------------------------------------------------------------------------------------------------------------------------#
def runSeeker(IPadd):
    # Attempt to connect to the server
    HOST = IPadd
    PORT = 50020

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

    server.connect((HOST,PORT))
    print("connected to server")

    def handleServerMsg(server, serverMsg):
        server.setblocking(1)
        msg = ""
        command = ""
        while True:
            msg += server.recv(10).decode("UTF-8")
            command = msg.split("\n")
            while (len(command) > 1):
                readyMsg = command[0]
                msg = "\n".join(command[1:])
                serverMsg.put(readyMsg)
                command = msg.split("\n")

    def serverTimer():
        if (serverMsg.qsize() > 0):
            msg = serverMsg.get(False)
            try:
                # Retrieving if a new player connected
                if msg.startswith("newPlayer"):
                    msg = msg.split()
                    newPID = int(msg[1])
                    x = int(msg[2])
                    y = int(msg[3])
                    otherPlayer.append([x, y, newPID])
                # Retrieving the player moving
                elif msg.startswith("playerMoved"):
                    msg = msg.split()
                    PID = int(msg[1])
                    dx = int(msg[2])
                    dy = int(msg[3])
                    for player in otherPlayer: # must update the othe rplayer
                        if player[2] == PID:
                            creeper[0] += dx * 10
                            creeper[1] += dy * 10
                            break
                            
                # Retrieving the counter
                elif msg.startswith('counter'):
                    msg = msg.split()
                    counter = int(msg[2])
                    listCounter.pop()
                    listCounter.append(counter)

                # Retrieving AI location
                elif msg.startswith('AILocation ='):
                    # Strips the 'AILocation ='
                    msg = msg[13:]

                    # Check if counter was included in the message and remove it
                    if not msg.endswith("]"):
                        msg = msg[:len(msg)-13]

                    # Update our global variable to have our list of bot coordinates
                    listMsg = ast.literal_eval(msg)
                    for lists in listMsg:
                        botCoords.append(lists)

                elif msg.startswith('otherLocation ='):
                    # Strips 'otherLocation ='
                    msg = msg[16:]
                    listPlayerMsg = ast.literal_eval(msg)
                    for coord in listPlayerMsg:
                        otherPlayer.append(coord)

                # If we've lost the game
                elif msg.startswith('You Lose'):
                    winText.pop()
                    winText.append(msg)

                elif msg.startswith('You Win'):
                    winText.pop()
                    winText.append(msg)

                # Indicates that the camera is to be blacked out    
                elif msg.startswith('blackout'):
                    blackScreen.pop()
                    blackScreen.append(True)
            except:
                print("failed")
            serverMsg.task_done()

    # Initialize our serverMsg and thread
    serverMsg = Queue(100)
    start_new_thread(handleServerMsg, (server, serverMsg))

    # ------------------------------------------------------------------------------------# 

    ## GLOBAL VARIABLES
    otherPlayer = []
    # These are lists specific to the seeker
    # They include a list of received coordinates of bot and a list to save the list

    botCoords = []
    checkBlankList = []
    checkPlayerBlankList = []
    selectedLocationToSend = []
    selectedPlayerLocationToSend = []
    blackScreen = [False] # This is the variable to draw a black screen over everything to simulate a blind

    # Define some base variables and parameters
    img_dir = path.join(path.dirname(__file__), 'img')

    # Size of the actual game map
    MAP_XSIZE = 2000
    MAP_YSIZE = 900

    WIDTH = 900
    HEIGHT = 500
    FPS = 30
    PLAYER_MOVE = 10

    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)

    #  Initialize pygame and create window
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("PAYDAY 2-D")
    clock = pygame.time.Clock()

    # Initialize the timer
    listCounter = [240]
    counter, text = 240, '240'
    alarmCounter = 0
    pygame.time.set_timer(pygame.USEREVENT, 1000)
    font = pygame.font.SysFont('Subway Ticker', 90)

    #  Load seeker game graphics
    background = pygame.image.load(path.join(img_dir, "background.png")).convert()
    background_rect = background.get_rect()
    other_player_img = pygame.image.load(os.path.join(img_dir, 'main_standing.png')).convert()
    player_img = pygame.image.load(os.path.join(img_dir, 'seeker_Animation 1_0.png')).convert()
    player_img_selected = pygame.image.load(path.join(img_dir, "main_selected_walk_Animation 1_0.png")).convert()
    player_selected_walkf1 = pygame.image.load(path.join(img_dir, "main_selected_walk_Animation 1_0.png")).convert() 
    player_selected_walkf2 = pygame.image.load(path.join(img_dir, "main_selected_walk_Animation 1_1.png")).convert()
    player_walkf1 = pygame.image.load(path.join(img_dir, "main_walking_Animation 1_0.png")).convert()
    player_walkf2 = pygame.image.load(path.join(img_dir, "main_walking_Animation 1_1.png")).convert()
    AI_img = pygame.image.load(os.path.join(img_dir, 'main_standing.png')).convert()

    #  Sounds
    alarm = pygame.mixer.Sound('alarm1.wav')
    background_music = pygame.mixer.music.load('thegauntlet.mp3')
    pygame.mixer.music.set_volume(0.1)
    pygame.mixer.music.play(-1,0.0)

    # Winning condition
    winText = [' ']
    selectedRobot = False

    # Class to use for our scrolling mechanism 
    class Camera(object):
        def __init__(self,width,height):
            self.camera = pygame.Rect(0,0, width, height)
            self.width = width
            self.height = height
            self.cameraX = 0
            self.cameraY = 0

        def apply(self, entity):
            return entity.rect.move(self.camera.topleft)

        def update(self, target):
            x = -target.rect.x + int(WIDTH/2 - 100)
            y = -target.rect.y + int(HEIGHT/2 - 100)

            # Limit scrolling to map size
            x = min(0, x+50)# Left
            y = min(0, y+50)# Top
            x = max(-(self.width - WIDTH), x) # right
            y = max(-(self.height - HEIGHT), y) # bot

            self.cameraX -= x
            self.cameraY -= y
            self.camera = pygame.Rect(x,y,self.width,self.height)

    class Player(pygame.sprite.Sprite):
        def __init__(self):
            # Initializing the image
            pygame.sprite.Sprite.__init__(self)
            self.image = player_img
            self.image.set_colorkey(BLACK)
            self.rect = self.image.get_rect()
            self.rect.x = 800
            self.rect.y = 450
            self.speedx = 0
            self.speedy = 0
            self.absoluteX = self.rect.x
            self.absoluteY = self.rect.y

        def __repr__(self):
            return str(self.rect.x) + ',' + str(self.rect.y)

        def update(self):
            self.speedx = 0

            keystate = pygame.key.get_pressed()

            # If left key pressed
            if keystate[pygame.K_LEFT]:
                # check if too far left 
                if (self.rect.x - PLAYER_MOVE < 100):
                    self.rect.x = self.rect.x
                else:
                    self.rect.x += -PLAYER_MOVE

            # If right key pressed
            if keystate[pygame.K_RIGHT]:

                if (self.rect.x + PLAYER_MOVE > 1400):
                    self.rect.x = self.rect.x
                else:
                    self.rect.x += PLAYER_MOVE

            # If up key pressed
            if keystate[pygame.K_UP]:
                self.walking = True
                if (self.rect.y - PLAYER_MOVE < 200):
                    self.rect.y = self.rect.y
                else:
                    self.rect.y += -PLAYER_MOVE

            # If down key pressed
            if keystate[pygame.K_DOWN]:
                self.walking = True
                if (self.rect.y + PLAYER_MOVE > 700):
                    self.rect.y = self.rect.y
                else:
                    self.rect.y += PLAYER_MOVE

    class robotPlayer(pygame.sprite.Sprite):
        def __init__(self,x,y,AIvariant,selected,walking,counter,framesleft,newDeterminant):
            pygame.sprite.Sprite.__init__(self)
            self.image = AI_img
            self.image.set_colorkey(BLACK)
            self.rect = self.image.get_rect()
            self.rect.left = x
            self.rect.top = y
            self.speedx = 0
            self.speedy = 0

            # Properties to initialize walking
            self.walking = walking
            self.counter = counter
            self.player_walk = [player_walkf1,player_walkf2]
            self.player_selected_walk = [player_selected_walkf1,player_selected_walkf2]

            self.selected = selected

            self.framesleft = framesleft
            self.determinant = newDeterminant
            self.AInumber = AIvariant

        def update(self):
            self.walking = self.walking

            # Changes the animation to walking
            if self.selected == True:
                if self.walking == True:
                    self.image = self.player_selected_walk[self.counter]
                    self.image.set_colorkey(BLACK)
                    self.counter = (self.counter + 1) % len(self.player_walk)
                else:
                    self.image = self.player_selected_walk[self.counter]
                    self.image.set_colorkey(BLACK)
            else:
                if self.walking == True: 
                    self.image = self.player_walk[self.counter]
                    self.image.set_colorkey(BLACK)
                    self.counter = (self.counter + 1) % len(self.player_walk)
                else:
                    self.image = self.player_walk[self.counter]
                    self.image.set_colorkey(BLACK)


    class opponentPlayer(robotPlayer):
        def __init__(self,x,y,selected,walking,counter):
            pygame.sprite.Sprite.__init__(self)
            self.image = other_player_img
            self.image.set_colorkey(BLACK)
            self.rect = self.image.get_rect()
            self.rect.left = x
            self.rect.top = y
            self.speedx = 0
            self.speedy = 0

            # properties to initialize walking
            self.walking = walking
            self.counter = counter
            self.player_walk = [player_walkf1,player_walkf2]
            self.player_selected_walk = [player_selected_walkf1,player_selected_walkf2]

            self.selected = selected


        def update(self):
            self.walking = self.walking

            #changes the animation to walking
            if self.selected == True:
                if self.walking == True:
                    self.image = self.player_selected_walk[self.counter]
                    self.image.set_colorkey(BLACK)
                    self.counter = (self.counter + 1) % len(self.player_walk)
                else:
                    self.image = self.player_selected_walk[self.counter]
                    self.image.set_colorkey(BLACK)
            else:
                if self.walking == True: 
                    self.image = self.player_walk[self.counter]
                    self.image.set_colorkey(BLACK)
                    self.counter = (self.counter + 1) % len(self.player_walk)
                else:
                    self.image = self.player_walk[self.counter]
                    self.image.set_colorkey(BLACK)



    class BackGroundClass(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image = background
            self.rect = self.image.get_rect()


    # keeps container of all sprites
    player_sprites = pygame.sprite.Group()
    bot_sprites = pygame.sprite.Group()
    opponent_sprite = pygame.sprite.Group()

    player = Player() # this version is just a blank character
    player_sprites.add(player)

    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)

    # bg as sprite
    backgroundSprite = BackGroundClass()

    #  Game loop
    running = True
    while running == True:
        #  Keep loop running at the right speed
        clock.tick(FPS)
        # handle our server
        serverTimer()

        gameCamera = Camera(MAP_XSIZE,MAP_YSIZE)

        gameCamera.update(player)
        # Create new bots
        # Check if we accidentally created a blank list
        # If we did, change our list to our previous list that was saved in checkBlankList
        if len(botCoords) == 0:
            for coords in checkBlankList:
                newBot = robotPlayer(coords[0],coords[1],coords[2],coords[3],
                    coords[4],coords[5],coords[6],coords[7])
                bot_sprites.add(newBot)
                all_sprites.add(newBot)
            botCoords = checkBlankList
        else:
            for coords in botCoords:
                newBot = robotPlayer(coords[0],coords[1],coords[2],coords[3],
                    coords[4],coords[5],coords[6],coords[7])
                bot_sprites.add(newBot)
                all_sprites.add(newBot)

        # Create the other player
        if (len(otherPlayer) == 0 or len(otherPlayer) == 1):
            for coords in checkPlayerBlankList:
                opponent = opponentPlayer(checkPlayerBlankList[0],checkPlayerBlankList[1],
                    checkPlayerBlankList[2],checkPlayerBlankList[3],checkPlayerBlankList[4])
                opponent_sprite.add(opponent)
                all_sprites.add(opponent)
            otherPlayer = checkPlayerBlankList
        else:
            opponent = opponentPlayer(otherPlayer[0],otherPlayer[1],
                otherPlayer[2],otherPlayer[3],otherPlayer[4])
            opponent_sprite.add(opponent)
            all_sprites.add(opponent)

        #  Process input (events)
        for event in pygame.event.get():
            keystate = pygame.key.get_pressed()
            if event.type == pygame.USEREVENT:
                if len(listCounter) > 0:
                    counter = listCounter[0]
                text = str(counter).rjust(3)
                # if counter is negative, you win
                if counter <= 0:
                    counter = 0
                    if (alarmCounter < 1 and winText[0] == 'You Win'):
                        alarm.play()
                    else:
                        pass
                    alarmCounter += 1
                    running = True
                    running = True

            # checking collisions with cursor
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # check for collision with players or robots
                mousePos = pygame.mouse.get_pos()
                # must convert to list to update for camera offset, then change back to tuple
                mousePos = list(mousePos)
                mousePos[0] += gameCamera.cameraX
                mousePos[1] += gameCamera.cameraY
                mousePos = tuple(mousePos)

                for sprite in all_sprites:
                    if sprite.rect.collidepoint(mousePos):
                        sprite.selected = True
                        all_sprites.remove(sprite)
                        if sprite in bot_sprites:
                            selectedRobot = True
                            opponent.selected = False
                            bot_sprites.remove(sprite)
                        elif sprite in opponent_sprite:
                            opponent.selected = True
                            selectedRobot = False
                            opponent_sprite.remove(sprite)
                        for othersprites in all_sprites:
                            othersprites.selected = False
                        if selectedRobot == True:
                            bot_sprites.add(sprite)
                        else:
                            opponent_sprite.add(sprite)
                        all_sprites.add(sprite)
                        

                # Make list to send
                for robot in bot_sprites:
                    selectedLocationToSend.append([robot.rect.x,robot.rect.y,robot.AInumber,
                        robot.selected,robot.walking,robot.counter,robot.framesleft,robot.determinant])

                
                # If we indeed selected a robot, we want to send an updated list of coordinates with an updated state of selection
                msg = "selected = " + str(selectedLocationToSend) + '\n'
                print('sending: ', str(selectedLocationToSend))
                server.send(msg.encode())
                selectedLocationToSend = []

                selectedPlayerLocationToSend.append([opponent.rect.x,opponent.rect.y,
                    opponent.selected,opponent.walking,opponent.counter])
                msg = 'playerselected =' + str(selectedPlayerLocationToSend) + '\n'
                print('sending: ', str(selectedPlayerLocationToSend))
                server.send(msg.encode())
                selectedPlayerLocationToSend = []



            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if selectedRobot == True:
                        winText[0] = 'You Lose'
                        
                        msg = "You Win \n"                  
                        print('sending: ', msg)
                        server.send(msg.encode())
                    else:
                        winText[0] = 'You Win'

                        msg = "You Lose \n"                 
                        print('sending: ', msg)
                        server.send(msg.encode())

            #  check for closing window
            elif event.type == pygame.QUIT:
                running = False
        
        #  Update player
        player_sprites.update()
        bot_sprites.update()
        opponent_sprite.update()

        screen.fill(BLACK)

        # adjust background to camera accordingly
        screen.blit(backgroundSprite.image, gameCamera.apply(backgroundSprite))
                # draw the opponent
        for sprite in opponent_sprite:
            screen.blit(sprite.image,gameCamera.apply(sprite))

        for bot in bot_sprites:
            screen.blit(bot.image,gameCamera.apply(bot))





        # now clear the sprite group and the list
        bot_sprites.empty()
        opponent_sprite.empty()
        all_sprites.empty()
        # account for weird blank glitch
        checkPlayerBlankList = otherPlayer
        checkBlankList = botCoords
        botCoords = []
        otherPlayer = []

        # drawing timer
        screen.blit(font.render(text,True,(0,0,0)),(WIDTH/2-80,20))

        screen.blit(font.render(winText[0],True,(0,0,0)),(WIDTH/2-150,80))

        if blackScreen[0] == True:
            if counter > 25:
                screen.fill(BLACK)
                
        #  *after* drawing everything, flip the display
        pygame.display.flip()

    pygame.mixer.music.stop()
    pygame.quit()

#- Code to run role of hider-------------------------------------------------------------------------------------------------------------------------#
def runHider(IPadd):
    # Attempt to connect to the server
    HOST = IPadd
    PORT = 50020

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

    server.connect((HOST,PORT))
    print("connected to server")

    def handleServerMsg(server, serverMsg):
        server.setblocking(1)
        msg = ""
        command = ""
        while True:
            msg += server.recv(10).decode("UTF-8")
            command = msg.split("\n")
            while (len(command) > 1):
                readyMsg = command[0]
                msg = "\n".join(command[1:])
                serverMsg.put(readyMsg)
                command = msg.split("\n")

    def serverTimer():
        if (serverMsg.qsize() > 0):
            msg = serverMsg.get(False)
            try:
                print("recieved: ", msg)
                #retrieving if a new player connected
                if msg.startswith("newPlayer"):
                    msg = msg.split()
                    newPID = int(msg[1])
                    x = int(msg[2])
                    y = int(msg[3])
                    otherPlayer.append([x, y, newPID])
                #retrieving the player moving
                elif msg.startswith("playerMoved"):
                    msg = msg.split()
                    PID = int(msg[1])
                    dx = int(msg[2])
                    dy = int(msg[3])
                    for player in otherPlayer: #must update the otherStrangers
                        if player[2] == PID:
                            creeper[0] += dx * 10
                            creeper[1] += dy * 10
                            break
                            
                #retrieving the counter
                elif msg.startswith('counter'):
                    msg = msg.split()
                    counter = int(msg[2])
                    listCounter.pop()
                    listCounter.append(counter)

                #retrieving AI location
                elif msg.startswith('AILocation ='):
                    #strips the 'AILocation ='
                    msg = msg[13:]

                    #check if counter was included in the message and remove it
                    if not msg.endswith("]"):
                        msg = msg[:len(msg)-13]

                    #update our global variable to have our list of bot coordinates
                    listMsg = ast.literal_eval(msg)
                    for lists in listMsg:

                        botCoords.append(lists)
                elif msg.startswith('PlLocation ='):
                    #strips 'PlLocation ='
                    msg = msg[13:]

                elif msg.startswith('You Lose'):
                    winText.pop()
                    winText.append(msg)
                elif msg.startswith('You Win'):
                    winText.pop()
                    winText.append(msg)
                elif msg.startswith('selected'):
                    msg = msg[11:]
                    listMsg = ast.literal_eval(msg)
                    for lists in listMsg:
                        seekerList.append(lists)
                elif msg.startswith('playerselected'):
                    msg = msg[16:]
                    listMsg = ast.literal_eval(msg)
                    for coord in listMsg:
                        selectedPlayerList.append(coord)
                    print('imgay',selectedPlayerList)


            except:
                print("failed")
            serverMsg.task_done()

    #initialize our serverMsg and thread
    serverMsg = Queue(100)
    start_new_thread(handleServerMsg, (server, serverMsg))

    #------------------------------------------------------------------------------------#

    ##GLOBAL VARIABLES
    otherStrangers = []
    seekerList = []
    selectedPlayerList = []

    #define some base variables and parameters
    img_dir = path.join(path.dirname(__file__), 'img')

    #size of the actual game map
    MAP_XSIZE = 2000
    MAP_YSIZE = 900

    WIDTH = 900
    HEIGHT = 500
    FPS = 7
    PLAYER_MOVE = 10

    # define colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)

    # initialize pygame and create window
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("PAYDAY 2-D")
    clock = pygame.time.Clock()

    #initialize the timer
    listCounter = [240]
    counter, text = 240, '240'
    alarmCounter = 0
    pygame.time.set_timer(pygame.USEREVENT, 1000)
    font = pygame.font.SysFont('Subway Ticker', 90)
    messageFont = pygame.font.SysFont('Subway Ticker', 45)
    objectiveFont = pygame.font.SysFont('Subway Ticker', 20)

    # Load all game graphics
    background = pygame.image.load(path.join(img_dir, "background.png")).convert()
    background_rect = background.get_rect()
    player_img = pygame.image.load(os.path.join(img_dir, 'main_standing.png')).convert()
    player_img_selected = pygame.image.load(path.join(img_dir, "main_selected_walk_Animation 1_0.png")).convert()
    player_selected_walkf1 = pygame.image.load(path.join(img_dir, "main_selected_walk_Animation 1_0.png")).convert()
    player_selected_walkf2 = pygame.image.load(path.join(img_dir, "main_selected_walk_Animation 1_1.png")).convert()
    player_walkf1 = pygame.image.load(path.join(img_dir, "main_walking_Animation 1_0.png")).convert()
    player_walkf2 = pygame.image.load(path.join(img_dir, "main_walking_Animation 1_1.png")).convert()
    AI_img = pygame.image.load(os.path.join(img_dir, 'main_standing.png')).convert()
    indicator = pygame.image.load(os.path.join(img_dir, 'indicator.png')).convert()
    crossout_line = pygame.image.load(os.path.join(img_dir, 'crossout_line.png')).convert()
    c4 = pygame.image.load(os.path.join(img_dir, 'c4.png')).convert()

    # Sounds
    background_music = pygame.mixer.music.load('thegauntlet.mp3')
    alarm = pygame.mixer.Sound('alarm1.wav')
    place = pygame.mixer.Sound('place.wav')
    ecm = pygame.mixer.Sound('ecm.wav')
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1,0.0)

    # Winning condition variables
    winText = [' '] # The text we are displaying once the seeker has made a decision 
    selectedRobot = False # Check if the player selected an AI
    tasksComplete = ['Vault1','Vault2','Teller','Exit']
    tasksBoolean = [False,False,False,False]
    vault1_rect = pygame.Rect(1250,250,1,1)
    camera_rect = pygame.Rect(1780,250,1,1)
    teller_rect = pygame.Rect(320,609,1,1)
    exit_rect = pygame.Rect(830,240,90,1)

    # Checks if bots will make a legal move
    def isLegal(x,y):

        if (y - PLAYER_MOVE < 343 and x < 460):
            return False
        elif (y - PLAYER_MOVE < 563 and x < 420):
            return False
        elif (y - PLAYER_MOVE < 379 and x > 1750):
            return False
        elif (y - PLAYER_MOVE < 479 and x > 1800):
            return False
        elif (y - PLAYER_MOVE < 630 and x > 1850):
            return False
        elif (y - PLAYER_MOVE < 208 and x < 1069):
            return False
        elif (y - PLAYER_MOVE < 150):
            return False
        elif (y + PLAYER_MOVE > 700):
            return False
        elif (x + PLAYER_MOVE > 1750 and y < 379):
            return False
        elif (x + PLAYER_MOVE > 1800 and y < 479):
            return False
        elif (x + PLAYER_MOVE > 1850 and y < 630):
            return False
        elif (x + PLAYER_MOVE > 1900):
            return False
        elif (x - PLAYER_MOVE < 491 and y < 343):
            return False
        elif (x - PLAYER_MOVE < 431 and y < 563):
            return False
        elif (x - PLAYER_MOVE < 108):
            return False
        else:
            return True


    class Camera(object):
        def __init__(self,width,height):
            self.camera = pygame.Rect(0,0, width, height)
            self.width = width
            self.height = height
            self.cameraX = 0
            self.cameraY = 0

        def apply(self, entity):
            return entity.rect.move(self.camera.topleft)

        def update(self, target):
            x = -target.rect.x + int(WIDTH/2 - 100)
            y = -target.rect.y + int(HEIGHT/2 - 100)

            #limit scrolling to map size
            x = min(0, x+50)#left
            y = min(0, y+50)#top
            x = max(-(self.width - WIDTH), x) #right
            y = max(-(self.height - HEIGHT), y) #bot

            self.cameraX -= x
            self.cameraY -= y
            self.camera = pygame.Rect(x,y,self.width,self.height)

    # Class for player
    class Player(pygame.sprite.Sprite):
        def __init__(self,x=480,y=240,selected=False, walking= False,counter = 0):
            #initializing the image
            pygame.sprite.Sprite.__init__(self)
            self.image = player_img
            self.image.set_colorkey(BLACK)
            self.rect = self.image.get_rect()
            #initialize position (need to randomize)
            self.rect.x = x
            self.rect.y = y
            self.speedx = 0
            self.speedy = 0
            self.absoluteX = self.rect.x
            self.absoluteY = self.rect.y
            #properties to initialize walking
            self.walking = walking
            self.counter = counter
            self.player_walk = [player_walkf1,player_walkf2]
            self.player_selected_walk = [player_selected_walkf1,player_selected_walkf2]

            #testing out selection shit
            self.selected = selected

        def update(self):
            self.speedx = 0
            self.speedy = 0
            self.walking = False

            keystate = pygame.key.get_pressed()

            #if left key pressed
            if keystate[pygame.K_LEFT]:
                self.walking = True
                #check if too far left 
                if (self.rect.x - PLAYER_MOVE < 491 and self.rect.y < 343):
                    self.rect.x = self.rect.x
                elif (self.rect.x - PLAYER_MOVE < 431 and self.rect.y < 563):
                    self.rect.x = self.rect.x
                elif (self.rect.x - PLAYER_MOVE < 108):
                    self.rect.x = self.rect.x
                else:
                    self.rect.x += -PLAYER_MOVE

                #want to send location of new player location--> the same applies for the below movement blocks of code
                msg = "%d %d \n" % (self.rect.x, self.rect.y)
                print("sending: ", msg)
                server.send(msg.encode())

            if keystate[pygame.K_RIGHT]:
                self.walking = True
                if (self.rect.x + PLAYER_MOVE > 1750 and self.rect.y < 379):
                    self.rect.x = self.rect.x
                elif (self.rect.x + PLAYER_MOVE > 1800 and self.rect.y < 479):
                    self.rect.x = self.rect.x
                elif (self.rect.x + PLAYER_MOVE > 1850 and self.rect.y < 630):
                    self.rect.x = self.rect.x
                elif (self.rect.x + PLAYER_MOVE > 1900):
                    self.rect.x = self.rect.x
                else:
                    self.rect.x += PLAYER_MOVE


                msg = "%d %d \n" % (self.rect.x, self.rect.y)
                print("sending: ", msg)
                server.send(msg.encode())

            if keystate[pygame.K_UP]:
                self.walking = True
                if (self.rect.y - PLAYER_MOVE < 343 and self.rect.x < 460):
                    self.rect.y = self.rect.y
                elif (self.rect.y - PLAYER_MOVE < 563 and self.rect.x < 420):
                    self.rect.y = self.rect.y
                elif (self.rect.y - PLAYER_MOVE < 379 and self.rect.x > 1750):
                    self.rect.y = self.rect.y
                elif (self.rect.y - PLAYER_MOVE < 479 and self.rect.x > 1800):
                    self.rect.y = self.rect.y 
                elif (self.rect.y - PLAYER_MOVE < 630 and self.rect.x > 1850):
                    self.rect.y = self.rect.y
                elif (self.rect.y - PLAYER_MOVE < 208 and self.rect.x < 1069):
                    self.rect.y = self.rect.y
                elif (self.rect.y - PLAYER_MOVE < 150):
                    self.rect.y = self.rect.y
                else:
                    self.rect.y += -PLAYER_MOVE

            if keystate[pygame.K_DOWN]:
                self.walking = True
                if (self.rect.y + PLAYER_MOVE > 700):
                    self.rect.y = self.rect.y
                else:
                    self.rect.y += PLAYER_MOVE

            #changes the animation to walking
            if self.selected == True:
                if self.walking == True:
                    self.image = self.player_selected_walk[self.counter]
                    self.image.set_colorkey(BLACK)
                    self.counter = (self.counter + 1) % len(self.player_walk)
                else:
                    self.image = self.player_selected_walk[self.counter]
                    self.image.set_colorkey(BLACK)
            else:
                if self.walking == True: 
                    self.image = self.player_walk[self.counter]
                    self.image.set_colorkey(BLACK)
                    self.counter = (self.counter + 1) % len(self.player_walk)
                else:
                    self.image = self.player_walk[self.counter]
                    self.image.set_colorkey(BLACK)


    # Class for AI
    class robotPlayer(pygame.sprite.Sprite):
        def __init__(self,x,y,AIvariant=1,selected=False,walking=False,counter=0,framesleft=random.randint(15,20),newDeterminant=random.randint(0,10)):
            pygame.sprite.Sprite.__init__(self)
            self.image = AI_img
            self.image.set_colorkey(BLACK)
            self.rect = self.image.get_rect()
            self.rect.left = x
            self.rect.top = y
            self.speedx = 0
            self.speedy = 0

            #properities to initialize walking
            self.walking = walking
            self.counter = counter
            self.player_walk = [player_walkf1,player_walkf2]
            self.player_selected_walk = [player_selected_walkf1,player_selected_walkf2]

            self.selected = selected


            # Selecting which AI set to run
            self.AInumber = AIvariant
            self.framesleft = framesleft
            self.determinant = newDeterminant

        def update(self):
            self.speedx = 0
            self.speedy = 0
            self.walking = False

            # Algorithms for AI
            # Code for AI at bank tellers
            if self.AInumber == 1:
                # Randomly goes right
                if (self.determinant == 1):
                    self.walking = True
                    if self.framesleft != 0:
                        if isLegal(self.rect.x+PLAYER_MOVE,self.rect.y):    
                            self.rect.x += PLAYER_MOVE
                        self.framesleft -= 1
                    else:
                        self.framesleft = random.randint(3,7)
                        self.determinant = random.randint(0,20)
                # Randomly goes left
                elif(self.determinant == 2): 
                    self.walking = True
                    if self.framesleft != 0:
                        if isLegal(self.rect.x-PLAYER_MOVE,self.rect.y):
                            self.rect.x -= PLAYER_MOVE
                        self.framesleft -= 1
                    else:
                        self.framesleft = random.randint(5,10)
                        self.determinant = random.randint(0,20)
                # Randomly goes Up
                elif(self.determinant == 3):
                    self.walking = True
                    if self.framesleft != 0:
                        if isLegal(self.rect.x,self.rect.y-PLAYER_MOVE):
                            self.rect.y -= PLAYER_MOVE
                        self.framesleft -= 1
                    else:
                        self.framesleft = random.randint(3,5)
                        self.determinant = random.randint(0,20)
                # Randomly goes down
                elif(self.determinant == 4):
                    self.walking = True
                    if self.framesleft != 0:
                        if isLegal(self.rect.x,self.rect.y+PLAYER_MOVE):
                            self.rect.y += PLAYER_MOVE
                        self.framesleft -= 1
                    else:
                        self.framesleft = random.randint(3,5)
                        self.determinant = random.randint(0,20)
                else:
                    self.walking = False
                    if self.framesleft != 0:
                        self.framesleft -= 1
                    else:
                        self.determinant = random.randint(0,20)
                        self.framesleft = random.randint(5,10)
            
            # Wandering AI
            elif self.AInumber == 2:
                if (self.determinant <= 3):
                    self.walking = True
                    if self.framesleft != 0:
                        if (self.framesleft >= 10):
                            self.framesleft -=1
                            if isLegal(self.rect.x+PLAYER_MOVE,self.rect.y):    
                                self.rect.x += PLAYER_MOVE
                           
                        else:
                            self.framesleft -=1
                            if isLegal(self.rect.x,self.rect.y+PLAYER_MOVE):
                                self.rect.y += PLAYER_MOVE
                            
                    else:
                        self.framesleft = random.randint(15,20)
                        self.determinant = random.randint(0,20)

                elif (self.determinant >= 17):
                    self.walking = True
                    if self.framesleft != 0:
                        if (self.framesleft >= 5):
                            self.framesleft -=1
                            if isLegal(self.rect.x-PLAYER_MOVE,self.rect.y):    
                                self.rect.x -= PLAYER_MOVE
        
                        else:
                            self.framesleft -=1
                            if isLegal(self.rect.x,self.rect.y-PLAYER_MOVE):
                                self.rect.y -= PLAYER_MOVE
                            self.framesleft -= 1
                    else:
                        self.framesleft = random.randint(15,20)
                        self.determinant = random.randint(0,20)
                else:
                    self.walking = False
                    if self.framesleft != 0:
                        self.framesleft -= 1
                    else:
                        self.determinant = random.randint(0,20)
                        self.framesleft = random.randint(5,10)
            # AI spawning near the door to tellers and runs in a square like pattern
            elif self.AInumber == 3:
                if (self.determinant <= 3):
                    self.walking = True
                    if self.framesleft != 0:
                        if (self.framesleft >= 15):
                            self.framesleft -=1
                            if isLegal(self.rect.x-PLAYER_MOVE,self.rect.y):    
                                self.rect.x -= PLAYER_MOVE           
                        elif (self.framesleft >= 10 and self.framesleft < 15):
                            self.framesleft -=1
                            if isLegal(self.rect.x,self.rect.y+PLAYER_MOVE):
                                self.rect.y += PLAYER_MOVE
                        elif (self.framesleft >= 5 and self.framesleft < 10):
                            self.framesleft -=1
                            if isLegal(self.rect.x+PLAYER_MOVE,self.rect.y):
                                self.rect.x += PLAYER_MOVE
                        else:
                            self.framesleft -=1
                            if isLegal(self.rect.x,self.rect.y-PLAYER_MOVE):
                                self.rect.y -= PLAYER_MOVE
                    else: 
                        self.framesleft = random.randint(20,23)
                        self.determinant = random.randint(0,20)  
                elif (self.determinant >= 18):
                    self.walking = True
                    if self.framesleft != 0:
                        if(self.framesleft <= 6):
                            if isLegal(self.rect.x,self.rect.y-PLAYER_MOVE):
                                self.rect.y -=PLAYER_MOVE 
                            self.framesleft -= 1
                        else:
                            if isLegal(self.rect.x+PLAYER_MOVE,self.rect.y):
                                self.rect.x +=PLAYER_MOVE 
                            self.framesleft -= 1
                    else:
                        self.framesleft = random.randint(20,23)
                        self.determinant = random.randint(0,20)   
                else:
                    self.walking = False
                    if self.framesleft != 0:
                        self.framesleft -= 1
                    else:
                        self.determinant = random.randint(0,20)
                        self.framesleft = random.randint(20,23)
            # AI that runs across diagonally
            elif self.AInumber == 4:
                if (self.determinant == 1):
                    self.walking = True
                    if self.framesleft != 0:
                        if (isLegal(self.rect.x+PLAYER_MOVE,self.rect.y) and isLegal(self.rect.x,self.rect.y-PLAYER_MOVE)):
                            self.rect.y -= PLAYER_MOVE
                            self.rect.x += PLAYER_MOVE
                        self.framesleft -= 1
                    else:
                        self.determinant = random.randint(0,15)
                        self.framesleft = random.randint(5,10)
                elif (self.determinant == 2):
                    self.walking = True
                    if self.framesleft != 0:
                        if (isLegal(self.rect.x-PLAYER_MOVE,self.rect.y) and isLegal(self.rect.x,self.rect.y+PLAYER_MOVE)):
                            self.rect.y += PLAYER_MOVE
                            self.rect.x -= PLAYER_MOVE
                        self.framesleft -= 1
                    else:
                        self.determinant = random.randint(0,15)
                        self.framesleft = random.randint(5,10)
                else:
                    self.walking = False
                    if self.framesleft != 0:
                        self.framesleft -= 1
                    else:
                        self.determinant = random.randint(0,15)
                        self.framesleft = random.randint(5,10)
            # AI that runs across the screen
            elif self.AInumber == 5:
                if (self.determinant == 1):
                    self.walking = True
                    if self.framesleft != 0:
                        if isLegal(self.rect.x+PLAYER_MOVE,self.rect.y):
                            self.rect.x += PLAYER_MOVE
                        self.framesleft -= 1
                    else:
                        self.framesleft = random.randint(20,25)
                        self.determinant = random.randint(0,20)
                elif (self.determinant == 2):
                    self.walking = True
                    if self.framesleft != 0:
                        if isLegal(self.rect.x-PLAYER_MOVE,self.rect.y):
                            self.rect.x -= PLAYER_MOVE
                        self.framesleft -= 1
                    else:
                        self.framesleft = random.randint(20,25)
                        self.determinant = random.randint(0,20)

                else:
                    self.walking = False
                    if self.framesleft != 0:
                        self.framesleft -= 1
                    else:
                        self.determinant = random.randint(0,20)
                        self.framesleft = random.randint(20,25)
            # AI that hangs around the camera/vault area
            elif self.AInumber == 6:
                if (self.determinant <= 3):
                    self.walking = True
                    if self.framesleft != 0:
                        if (self.framesleft >= 18):
                            self.framesleft -=1
                            if isLegal(self.rect.x-PLAYER_MOVE,self.rect.y):    
                                self.rect.x -= PLAYER_MOVE
                        elif (self.framesleft >= 13 and self.framesleft < 18):
                            self.framesleft -=1
                            if isLegal(self.rect.x,self.rect.y+PLAYER_MOVE):
                                self.rect.y += PLAYER_MOVE
                        elif (self.framesleft >= 5 and self.framesleft < 13):
                            self.framesleft -=1
                            if isLegal(self.rect.x+PLAYER_MOVE,self.rect.y):
                                self.rect.x += PLAYER_MOVE      
                        else:
                            self.framesleft -=1
                            if isLegal(self.rect.x,self.rect.y-PLAYER_MOVE):
                                self.rect.y -= PLAYER_MOVE       
                    else: 
                        self.framesleft = random.randint(20,23)
                        self.determinant = random.randint(0,20)  

                elif (self.determinant >= 18):
                    self.walking = True
                    if self.framesleft != 0:
                        if(self.framesleft <= 6):
                            if isLegal(self.rect.x,self.rect.y-PLAYER_MOVE):
                                self.rect.y -= PLAYER_MOVE 
                            self.framesleft -= 1
                        else:
                            if isLegal(self.rect.x+PLAYER_MOVE,self.rect.y):
                                self.rect.x += PLAYER_MOVE 
                            self.framesleft -= 1
                    else:
                        self.framesleft = random.randint(20,23)
                        self.determinant = random.randint(0,20)   
                else:
                    self.walking = False
                    if self.framesleft != 0:
                        self.framesleft -= 1
                    else:
                        self.determinant = random.randint(0,20)
                        self.framesleft = random.randint(20,23)
            # Ai that hangs around the bottom right area
            elif self.AInumber == 7:
                # Randomly goes right
                if (self.determinant == 1):
                    self.walking = True
                    if self.framesleft != 0:
                        if isLegal(self.rect.x+PLAYER_MOVE,self.rect.y):    
                            self.rect.x += PLAYER_MOVE
                        self.framesleft -= 1
                    else:
                        self.framesleft = random.randint(3,7)
                        self.determinant = random.randint(0,20)
                # Randomly goes left
                elif(self.determinant == 2): 
                    self.walking = True
                    if self.framesleft != 0:
                        if isLegal(self.rect.x-PLAYER_MOVE,self.rect.y):
                            self.rect.x -= PLAYER_MOVE
                        self.framesleft -= 1
                    else:
                        self.framesleft = random.randint(5,10)
                        self.determinant = random.randint(0,20)
                # Randomly goes Up
                elif(self.determinant == 3):
                    self.walking = True
                    if self.framesleft != 0:
                        if isLegal(self.rect.x,self.rect.y-PLAYER_MOVE):
                            self.rect.y -= PLAYER_MOVE
                        self.framesleft -= 1
                    else:
                        self.framesleft = random.randint(3,5)
                        self.determinant = random.randint(0,20)
                # Randomly goes down
                elif(self.determinant == 4):
                    self.walking = True
                    if self.framesleft != 0:
                        if isLegal(self.rect.x,self.rect.y+PLAYER_MOVE):
                            self.rect.y += PLAYER_MOVE
                        self.framesleft -= 1
                    else:
                        self.framesleft = random.randint(3,5)
                        self.determinant = random.randint(0,20)
                else:
                    self.walking = False
                    if self.framesleft != 0:
                        self.framesleft -= 1
                    else:
                        self.determinant = random.randint(0,20)
                        self.framesleft = random.randint(5,10)

            # Changes the animation to walking
            if self.selected == True:
                if self.walking == True:
                    self.counter = (self.counter + 1) % len(self.player_walk)
                    self.image = self.player_selected_walk[self.counter]
                    self.image.set_colorkey(BLACK)
                else:
                    self.image = self.player_selected_walk[self.counter]
                    self.image.set_colorkey(BLACK)
            else:
                if self.walking == True: 
                    self.image = self.player_walk[self.counter]
                    self.image.set_colorkey(BLACK)
                    self.counter = (self.counter + 1) % len(self.player_walk)
                else:
                    self.image = self.player_walk[self.counter]
                    self.image.set_colorkey(BLACK)
       
    class Indicator(pygame.sprite.Sprite):
        def __init__(self,x=1150,y=150):
            pygame.sprite.Sprite.__init__(self)
            self.image = indicator
            self.image.set_colorkey(BLACK)
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y

    class BackGroundClass(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image = background
            self.rect = self.image.get_rect()

    class Crossout(pygame.sprite.Sprite):
        def __init__(self,x,y):
            pygame.sprite.Sprite.__init__(self)
            self.image = crossout_line
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y

    class C4(pygame.sprite.Sprite):
        def __init__(self,x=1200,y=200):
            pygame.sprite.Sprite.__init__(self)
            self.image = c4
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y

    #keeps container of all sprites
    all_sprites = pygame.sprite.Group()
    player_sprites = pygame.sprite.Group()
    bot_sprites = pygame.sprite.Group()
    bot_bank_sprites = pygame.sprite.Group()
    bot_small_wander_sprites = pygame.sprite.Group()
    bot_big_wander_sprites = pygame.sprite.Group()
    bot_teller_wander_sprites = pygame.sprite.Group()
    bot_diagonal_sprites = pygame.sprite.Group()
    bot_path_sprites = pygame.sprite.Group()
    bot_camera_sprites = pygame.sprite.Group()
    bot_bottom_sprites = pygame.sprite.Group()

    playerX = random.randint(430,1700)
    playerY = random.randint(300,740)
    player = Player(playerX,playerY)
    player_sprites.add(player)
    all_sprites.add(player)
    #sends the location of the player 
    msg = 'otherLocation = (%d,%d)' % (player.rect.x,player.rect.y) + '\n'
    print('sending: ', msg)
    server.send(msg.encode())

    #variables for drawing AI
    listOfBots = []
    listOfBotLocations = []
    rangeXSpawn = [494,1210]
    rangeYSpawn = [300,650]
    numberOfBotsGroup1 = random.randint(10,12)
    # Generates the crowd at the tellers
    for i in range(numberOfBotsGroup1):
        xSpawn = random.randint(523,883) # Generating the square that the crowd can spawn in
        ySpawn = random.randint(213,423)
        framesLeft = random.randint(5,15)
        randomDeterminant = random.randint(1,10)
        #generates an object for each AI and puts them in the group
        newBot = robotPlayer(xSpawn,ySpawn,1,False,False,0,framesLeft,randomDeterminant)
        bot_bank_sprites.add(newBot)
        bot_sprites.add(newBot)
        all_sprites.add(newBot)
        listOfBotLocations.append([newBot.rect.x,newBot.rect.y,newBot.AInumber,newBot.selected,newBot.walking,newBot.counter,newBot.framesleft,newBot.determinant])

    # Generating wandering AI Group #1
    numberOfBotsGroup2 = random.randint(7,10)
    for i in range(numberOfBotsGroup2):
        xSpawn = random.randint(494,1634)
        ySpawn = random.randint(230,650)
        framesLeft = random.randint(5,15)
        randomDeterminant = random.randint(0,20)
        newBot = robotPlayer(xSpawn,ySpawn,2,False,False,0,framesLeft,randomDeterminant)
        bot_big_wander_sprites.add(newBot)
        bot_sprites.add(newBot)
        all_sprites.add(newBot)
        listOfBotLocations.append([newBot.rect.x,newBot.rect.y,newBot.AInumber,newBot.selected,newBot.walking,newBot.counter,newBot.framesleft,newBot.determinant])

    # Generating group of AI walking in squares near the teller doors
    numberOfBotsGroup3 = random.randint(3,6)
    for i in range(numberOfBotsGroup3):
        xSpawn = random.randint(142,412)
        ySpawn = random.randint(570,700)
        framesLeft = random.randint(5,15)
        randomDeterminant = random.randint(0,20)
        newBot = robotPlayer(xSpawn,ySpawn,3,False,False,0,framesLeft,randomDeterminant)
        bot_teller_wander_sprites.add(newBot)
        bot_sprites.add(newBot)
        all_sprites.add(newBot)
        listOfBotLocations.append([newBot.rect.x,newBot.rect.y,newBot.AInumber,newBot.selected,newBot.walking,newBot.counter,newBot.framesleft,newBot.determinant])
   
    # Generates the AI that walks diagonally
    numberOfBotsGroup4 = random.randint(3,5)
    for i in range(numberOfBotsGroup4):
        xSpawn = random.randint(494,1634)
        ySpawn = random.randint(230,650)
        framesLeft = random.randint(15,25)
        randomDeterminant = random.randint(0,20)
        newBot = robotPlayer(xSpawn,ySpawn,4,False,False,0,framesLeft,randomDeterminant)
        bot_diagonal_sprites.add(newBot)
        bot_sprites.add(newBot)
        all_sprites.add(newBot)
        listOfBotLocations.append([newBot.rect.x,newBot.rect.y,newBot.AInumber,newBot.selected,newBot.walking,newBot.counter,newBot.framesleft,newBot.determinant])

    # Generates the AI that runs across screens
    numberOfBotsGroup5 = random.randint(6,7)
    for i in range(numberOfBotsGroup5):
        xSpawn = random.randint(494,1634)
        ySpawn = random.randint(230,650)
        framesLeft = random.randint(20,25)
        randomDeterminant = random.randint(0,20)
        newBot = robotPlayer(xSpawn,ySpawn,5,False,False,0,framesLeft,randomDeterminant)
        bot_path_sprites.add(newBot)
        bot_sprites.add(newBot)
        all_sprites.add(newBot)
        listOfBotLocations.append([newBot.rect.x,newBot.rect.y,newBot.AInumber,newBot.selected,newBot.walking,newBot.counter,newBot.framesleft,newBot.determinant])

    # Generates the AI near the bank vault
    numberOfBotsGroup6 = random.randint(6,8)
    for i in range(numberOfBotsGroup6):
        xSpawn = random.randint(1110,1670)
        ySpawn = random.randint(160,454)
        framesLeft = random.randint(20,25)
        randomDeterminant = random.randint(0,20)
        newBot = robotPlayer(xSpawn,ySpawn,6,False,False,0,framesLeft,randomDeterminant)
        bot_camera_sprites.add(newBot)
        bot_sprites.add(newBot)
        all_sprites.add(newBot)
        listOfBotLocations.append([newBot.rect.x,newBot.rect.y,newBot.AInumber,newBot.selected,newBot.walking,newBot.counter,newBot.framesleft,newBot.determinant])

    #Generates AI near bottom of screen
    numberOfBotsGroup7 = random.randint(4,6)
    for i in range(numberOfBotsGroup7):
        xSpawn = random.randint(1250,1670)
        ySpawn = random.randint(460,775)
        framesLeft = random.randint(15,20)
        randomDeterminant = random.randint(0,20)
        newBot = robotPlayer(xSpawn,ySpawn,7,False,False,0,framesLeft,randomDeterminant)
        bot_bottom_sprites.add(newBot)
        bot_sprites.add(newBot)
        all_sprites.add(newBot)
        listOfBotLocations.append([newBot.rect.x,newBot.rect.y,newBot.AInumber,newBot.selected,newBot.walking,newBot.counter,newBot.framesleft,newBot.determinant])
    
    #sends the location of the spawned AI
    msg = "AILocation = " + str(listOfBotLocations) + '\n'
    print('sending: ', str(listOfBotLocations))
    server.send(msg.encode())

    #bg as sprite
    backgroundSprite = BackGroundClass()
    indicatorSpr = Indicator()
    c4Spr = C4()

    # Game loop
    running = True
    while running == True:
        #reset list AI list
        listOfBotLocations = []
        # keep loop running at the right speed
        clock.tick(FPS)

        #handle our server
        serverTimer()

        #object for our gameCamera
        gameCamera = Camera(MAP_XSIZE,MAP_YSIZE)

        # Update player
        player.update()
        bot_sprites.update()

        #update our offset under the context of our player
        #allows us to change view, while keeping absolute location of everything
        gameCamera.update(player)

        # Process input (events)
        for event in pygame.event.get():
            keystate = pygame.key.get_pressed()
            #checking counter
            if event.type == pygame.USEREVENT:
                if counter < 1:
                    if winText[0] == 'You Win':
                        counter = 0
                    else:
                        winText[0] = 'You Lose'
                        msg = "You Win \n"                 
                        print('sending: ', msg)
                        server.send(msg.encode())
                        counter = 1
                        running = True
                    if (alarmCounter < 1 and winText[0] == 'You Lose'):
                        alarm.play()
                    else:
                        pass
                    alarmCounter += 1
                    running = True
                else:
                    counter -= 1
                    msg = "counter = %d \n" % (counter)
                    print("sending: ", msg)
                    server.send(msg.encode())
                    text = str(counter).rjust(3)
                #if counter is negative, for now just end the game


            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if player.rect.colliderect(vault1_rect):
                        tasksBoolean[0] = True
                        place.play()
                    if player.rect.colliderect(camera_rect):
                        tasksBoolean[1] = True
                        place.play()
                        counter = 30
                        #play noise you got 30 seconds until i'm pulling you out. the cops are coming!
                        msg = "counter = %d \n" % (counter)
                        print("sending: ", msg)
                        server.send(msg.encode())
                        text = str(counter).rjust(3)
                        msg = "blackout \n"
                        server.send(msg.encode())
                    if player.rect.colliderect(teller_rect):
                        tasksBoolean[2] = True
                        ecm.play()
                    if (player.rect.colliderect(exit_rect) and tasksBoolean[0] == True and tasksBoolean[1] == True and tasksBoolean[2] == True):
                        tasksBoolean[3] = True


            # check for closing window
            elif event.type == pygame.QUIT:
                running = False

        screen.fill(BLACK)
        # Adjust background to camera accordingly
        screen.blit(backgroundSprite.image, gameCamera.apply(backgroundSprite))

        
        # If we've received a selection for a bot from the seeker
        if seekerList != []:
            bot_sprites.empty()
            for newCoords in seekerList:
                newRobot = robotPlayer(newCoords[0],newCoords[1],newCoords[2],newCoords[3],newCoords[4],newCoords[5],newCoords[6],newCoords[7])
                bot_sprites.add(newRobot)
                all_sprites.add(newRobot)
            seekerList = [] #now reset 
 
        # Update the position of EVERY bot we have
        for sprite in bot_sprites:
            listOfBotLocations.append([sprite.rect.x,sprite.rect.y,sprite.AInumber,sprite.selected,sprite.walking,sprite.counter,sprite.framesleft,sprite.determinant])
            
        # Draw the player
        for sprite in player_sprites:
            screen.blit(sprite.image,gameCamera.apply(sprite))   
        for sprite in bot_sprites:
            screen.blit(sprite.image,gameCamera.apply(sprite))



        # Sends the location of the updated AI
        msg = "AILocation = " + str(listOfBotLocations) + '\n'
        print('sending: ', str(listOfBotLocations))
        server.send(msg.encode())

        # If we've received a selection for the player from the seeker
        if selectedPlayerList != []:
            player_sprites.empty()
            player = Player(selectedPlayerList[0][0],selectedPlayerList[0][1],selectedPlayerList[0][2],selectedPlayerList[0][3],selectedPlayerList[0][4])
            player_sprites.add(player)
            all_sprites.add(player)
            selectedPlayerList = []


        msg = 'otherLocation = [%d,%d,' % (player.rect.x,player.rect.y) + str(player.selected) + ',' + str(player.walking) + ',' + str(player.counter)+ '] \n'
        print('sending: ', msg)
        server.send(msg.encode())


        #checking to see if we're over a winning condition
        if (player.rect.colliderect(vault1_rect) and tasksBoolean[0] == False):
            screen.blit(messageFont.render('Press SPACE',True,(0,0,0)),(WIDTH/2-200,430))

        if (player.rect.colliderect(camera_rect) and tasksBoolean[1] == False):
            screen.blit(messageFont.render('Press SPACE',True,(0,0,0)),(WIDTH/2-200,430))

        if (player.rect.colliderect(teller_rect) and tasksBoolean[2] == False):
            screen.blit(messageFont.render('Press SPACE',True,(0,0,0)),(WIDTH/2-200,430))

        if (player.rect.colliderect(exit_rect)):
            if (tasksBoolean[0] == False or tasksBoolean[1] == False or tasksBoolean[2] == False):
                screen.blit(messageFont.render('You must still finish the job',True,(0,0,0)),(50,430))
            elif(tasksBoolean[3] == False and tasksBoolean[0] == True and tasksBoolean[1] == True and tasksBoolean[2] == True): 
                screen.blit(messageFont.render('Press SPACE',True,(0,0,0)),(WIDTH/2-200,430))

                
        # Drawing timer
        screen.blit(font.render(text,True,(0,0,0)),(WIDTH/2-80,20))

        # Drawing the indicator/c4 on the vault
        if tasksBoolean[0] == False:
            screen.blit(indicatorSpr.image,gameCamera.apply(indicatorSpr)) # Drawing vault1 indicator
        else:
            screen.blit(c4Spr.image,gameCamera.apply(c4Spr))


        screen.blit(objectiveFont.render('Plant C4 on Vault',True,(0,0,0)),(10,5))
        screen.blit(objectiveFont.render('Jam Cameras',True,(0,0,0)),(10,25))
        screen.blit(objectiveFont.render('ECM Teller Doors',True,(0,0,0)),(10,45))
        screen.blit(objectiveFont.render("Go to Exit Once Everything's Done",True,(0,0,0)),(10,65))
        #dealing with booleans and tasks to complete
        if tasksBoolean[0] == True:     
            pygame.draw.line(screen, BLACK, (10,10),(200,10))
            #blit a camera/somethign to shwo we've placed some shit
        if tasksBoolean[1] == True: 
            pygame.draw.line(screen, BLACK, (10,35),(150,35))

        if tasksBoolean[2] == True:
            pygame.draw.line(screen, BLACK, (10,55),(190,55))

        if tasksBoolean[3] == True:
            pygame.draw.line(screen, BLACK, (10,75),(350,75))

        if (tasksBoolean[0] == True and tasksBoolean[1] == True and tasksBoolean[2] == True and tasksBoolean[3] == True):
            winText[0] = 'You Win'
            msg = "You Lose \n"                 
            print('sending: ', msg)
            server.send(msg.encode())
            #pygame.mixer.music.stop()
            #play some sound to say u did it guys
            #and add a if pygame.mixer.music.get_busy() != True: go back to lobby 


        screen.blit(font.render(winText[0],True,(0,0,0)),(WIDTH/2-150,80))


        # *after* drawing everything, flip the display
        #pygame.display.update()
        pygame.display.flip()

    pygame.mixer.music.stop()
    #pygame.quit()

# Game loop
gameRunning = True
while gameRunning:
    # keep loop running at the right speed
    clock.tick(FPS)

    if mode == 'intro':
        # Process input (events)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if createButton_rect.collidepoint(pygame.mouse.get_pos()):
                    select_sound.play()
                    mode = 'newLobby'
                   
                elif connectButton_rect.collidepoint(pygame.mouse.get_pos()):
                    select_sound.play()
                    mode = 'connectLobby'

                elif helpButton_rect.collidepoint(pygame.mouse.get_pos()):
                    select_sound.play()
                    mode = 'helppg1'
                elif exitButton_rect.collidepoint(pygame.mouse.get_pos()):
                    gameRunning = False
                    
            # check for closing window
            if event.type == pygame.QUIT:
                gameRunning = False

        # Update

        # Draw / render
        # Blits are used for animating the background
        screen.fill(-1)
        screen.blit(background,(-lobbyBlit,0,50,50))
        if (lobbyBlit+0.5 == 1000 or lobbyBlit-0.5 == 300):    
            direc *= -1

        lobbyBlit += 0.5 * direc
        
        createButton = AAfilledRoundedRect(screen,(50,200,330,50),BUTTONBLUE,0.5)
        createButton_rect = Rect(50,200,330,50)
        if createButton_rect.collidepoint(pygame.mouse.get_pos()):
            createButton = AAfilledRoundedRect(screen,(50,200,330,50),BUTTONHIGHLIGHTEDBLUE,0.5)

        connectButton = AAfilledRoundedRect(screen,(50,252,330,50),BUTTONBLUE,0.5)
        connectButton_rect = Rect(50,252,330,50)
        if connectButton_rect.collidepoint(pygame.mouse.get_pos()):
            connectButton = AAfilledRoundedRect(screen,(50,252,330,50),BUTTONHIGHLIGHTEDBLUE,0.5)

        helpButton = AAfilledRoundedRect(screen,(50,304,330,50),BUTTONBLUE,0.5)
        helpButton_rect = Rect(50,304,330,50)
        if helpButton_rect.collidepoint(pygame.mouse.get_pos()):
            helpButton = AAfilledRoundedRect(screen,(50,304,330,50),BUTTONHIGHLIGHTEDBLUE,0.5)

        exitButton = AAfilledRoundedRect(screen,(50,356,330,50),BUTTONBLUE,0.5)
        exitButton_rect = Rect(50,356,330,50)
        if exitButton_rect.collidepoint(pygame.mouse.get_pos()):
            exitButton = AAfilledRoundedRect(screen,(50,356,330,50),BUTTONHIGHLIGHTEDBLUE,0.5)

        screen.blit(fontTitle.render('PAYDAY 2-D',True,(0,0,0)),(50,100))   
        screen.blit(fontButton.render('Create Lobby',True,(0,0,0)),(50,200))
        screen.blit(fontButton.render('Connect',True,(0,0,0)),(50,252))
        screen.blit(fontButton.render('Help',True,(0,0,0)),(50,304))
        screen.blit(fontButton.render('Exit',True,(0,0,0)),(50,356))

        # *after* drawing everything, flip the displayfor event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            if createButton_rect.collidepoint(pygame.mouse.get_pos()):
                select_sound.play()
                mode = 'createLobby'
                    
            # check for closing window
            if event.type == pygame.QUIT:
                gameRunning = False
        pygame.display.flip()

    elif mode == 'createLobby':
        #animating bg
        screen.fill(-1)
        screen.blit(background,(-lobbyBlit,0,50,50))
        helpBackButton = AAfilledRoundedRect(screen,(0,450,150,50),BUTTONBLUE,0.5)
        helpBackButton_rect = Rect(0,450,150,50)

        if helpBackButton_rect.collidepoint(pygame.mouse.get_pos()):
            helpBackButton = AAfilledRoundedRect(screen,(0,450,150,50),BUTTONHIGHLIGHTEDBLUE,0.5)


        if (lobbyBlit+0.5 == 1000 or lobbyBlit-0.5 == 300):    
            direc *= -1

        lobbyBlit += 0.5 * direc

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if lobbyButton_rect.collidepoint(pygame.mouse.get_pos()):
                    select_sound.play()
                    runHider(startInput)
                    gameRunning = False
                elif helpBackButton_rect.collidepoint(pygame.mouse.get_pos()):
                    select_sound.play()
                    mode = 'intro'

            if event.type == KEYDOWN:
                if (event.unicode.isnumeric() or event.unicode == '.'):
                    startInput += event.unicode
                elif event.key == K_BACKSPACE:
                    startInput = startInput[:-1]
                elif event.key == K_RETURN:
                    pass      
            # check for closing window
            if event.type == pygame.QUIT:
                gameRunning = False
                
        lobbyButton = AAfilledRoundedRect(screen,(300,304,330,50),BUTTONBLUE,0.5)
        lobbyButton_rect = Rect(300,304,330,50)
        if lobbyButton_rect.collidepoint(pygame.mouse.get_pos()):
            lobbyButton = AAfilledRoundedRect(screen,(300,304,330,50),BUTTONHIGHLIGHTEDBLUE,0.5)

        screen.blit(fontButton.render('Start',True,(0,0,0)),(300,304))      
        screen.blit(fontButton.render(startInput,True,(0,0,0)),(300,250))
        screen.blit(fontButton.render('Back',True,(0,0,0)),(2,450))
        screen.blit(fontButton.render('Type in Your IP',True,(0,0,0)),(270,100))
        pygame.display.flip()
        pygame.display.flip()

    elif mode == 'helppg1':
        screen.fill(-1)
        screen.blit(background,(0,helpBlit))
        if (helpBlit+0.5 == -300 or helpBlit-0.5 == 0):    
            direc *= -1
        helpBlit += 0.5 * direc


        helpBackButton = AAfilledRoundedRect(screen,(0,450,150,50),BUTTONBLUE,0.5)
        helpBackButton_rect = Rect(0,450,150,50)
        if helpBackButton_rect.collidepoint(pygame.mouse.get_pos()):
            helpBackButton = AAfilledRoundedRect(screen,(0,450,150,50),BUTTONHIGHLIGHTEDBLUE,0.5)

        helpNextButton = AAfilledRoundedRect(screen,(700,450,200,50),BUTTONBLUE,0.5)
        helpNextButton_rect = Rect(700,450,200,50)
        if helpNextButton_rect.collidepoint(pygame.mouse.get_pos()):
            helpNextButton = AAfilledRoundedRect(screen,(700,450,200,50),BUTTONHIGHLIGHTEDBLUE,0.5)


        screen.blit(help1,(25,0,50,50))
        help1.set_colorkey(OUTLINEREMOVE)
        screen.blit(fontButton.render('Back',True,(0,0,0)),(2,450))
        screen.blit(fontButton.render('Next pg.',True,(0,0,0)),(700,450))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if helpBackButton_rect.collidepoint(pygame.mouse.get_pos()):
                    select_sound.play()
                    mode = 'intro'
                if helpNextButton_rect.collidepoint(pygame.mouse.get_pos()):
                    select_sound.play()
                    mode = 'helppg2'
                         
            # check for closing window
            if event.type == pygame.QUIT:
                gameRunning = False

    elif mode == 'helppg2':
        screen.fill(-1)
        screen.blit(background,(0,helpBlit))
        if (helpBlit+0.5 == -300 or helpBlit-0.5 == 0):    
            direc *= -1
        helpBlit += 0.5 * direc


        helpPg2BackButton = AAfilledRoundedRect(screen,(0,450,200,50),BUTTONBLUE,0.5)
        helpPg2BackButton_rect = Rect(0,450,200,50)
        if helpPg2BackButton_rect.collidepoint(pygame.mouse.get_pos()):
            helpPg2BackButton = AAfilledRoundedRect(screen,(0,450,200,50),BUTTONHIGHLIGHTEDBLUE,0.5)

        helpPg2NextButton = AAfilledRoundedRect(screen,(700,450,200,50),BUTTONBLUE,0.5)
        helpPg2NextButton_rect = Rect(700,450,200,50)
        if helpPg2NextButton_rect.collidepoint(pygame.mouse.get_pos()):
            helpPg2NextButton = AAfilledRoundedRect(screen,(700,450,200,50),BUTTONHIGHLIGHTEDBLUE,0.5)

        screen.blit(help2,(25,0,50,50))
        help2.set_colorkey(OUTLINEREMOVE)
        screen.blit(fontButton.render('Prev. pg',True,(0,0,0)),(2,450))
        screen.blit(fontButton.render('Next pg.',True,(0,0,0)),(700,450))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if helpPg2BackButton_rect.collidepoint(pygame.mouse.get_pos()):
                    select_sound.play()
                    mode = 'helppg1'
                if helpPg2NextButton_rect.collidepoint(pygame.mouse.get_pos()):
                    select_sound.play()
                    mode = 'helppg3'
                         
            # check for closing window
            if event.type == pygame.QUIT:
                gameRunning = False

    elif mode == 'helppg3':
        screen.fill(-1)
        screen.blit(background,(0,helpBlit))
        if (helpBlit+0.5 == -300 or helpBlit-0.5 == 0):    
            direc *= -1
        helpBlit += 0.5 * direc


        helpPg3BackButton = AAfilledRoundedRect(screen,(0,450,200,50),BUTTONBLUE,0.5)
        helpPg3BackButton_rect = Rect(0,450,200,50)
        if helpPg3BackButton_rect.collidepoint(pygame.mouse.get_pos()):
            helpPg3BackButton = AAfilledRoundedRect(screen,(0,450,200,50),BUTTONHIGHLIGHTEDBLUE,0.5)

        screen.blit(help3,(25,0,50,50))
        help3.set_colorkey(OUTLINEREMOVE)
        screen.blit(fontButton.render('Prev. pg',True,(0,0,0)),(2,450))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if helpPg2BackButton_rect.collidepoint(pygame.mouse.get_pos()):
                    select_sound.play()
                    mode = 'helppg2'
                         
            # check for closing window
            if event.type == pygame.QUIT:
                gameRunning = False
    elif mode == 'gameLobby':
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if lobbyBackButton_rect.collidepoint(pygame.mouse.get_pos()):
                    select_sound.play()
                    mode = 'intro'
                         
            # check for closing window
            if event.type == pygame.QUIT:
                gameRunning = False

        screen.fill(-1)
        screen.blit(background,(-lobbyBlit,0,50,50))
        if (lobbyBlit+0.5 == 1000 or lobbyBlit-0.5 == 300):    
            direc *= -1

        lobbyBlit += 0.5 * direc

        lobbyBackButton = AAfilledRoundedRect(screen,(0,450,150,50),BUTTONBLUE,0.5)
        lobbyBackButton_rect = Rect(0,450,150,50)
        if lobbyBackButton_rect.collidepoint(pygame.mouse.get_pos()):
            lobbyBackButton = AAfilledRoundedRect(screen,(0,450,150,50),BUTTONHIGHLIGHTEDBLUE,0.5)
        screen.blit(fontButton.render('You are at the game lobby screen',True,(0,0,0)),(50,356))
        screen.blit(fontButton.render('Back',True,(0,0,0)),(2,450))
        pygame.display.flip()
        
    elif mode == 'connectLobby':
        screen.fill(-1)
        screen.blit(background,(-lobbyBlit,0,50,50))
        connectButtonTwo = AAfilledRoundedRect(screen,(300,304,330,50),BUTTONBLUE,0.5)
        connectButtonTwo_rect = Rect(300,304,330,50)
        helpBackButton = AAfilledRoundedRect(screen,(0,450,150,50),BUTTONBLUE,0.5)
        helpBackButton_rect = Rect(0,450,150,50)

        if helpBackButton_rect.collidepoint(pygame.mouse.get_pos()):
            helpBackButton = AAfilledRoundedRect(screen,(0,450,150,50),BUTTONHIGHLIGHTEDBLUE,0.5)
        if connectButtonTwo_rect.collidepoint(pygame.mouse.get_pos()):
            connectButtonTwo = AAfilledRoundedRect(screen,(300,304,330,50),BUTTONHIGHLIGHTEDBLUE,0.5)
        if (lobbyBlit+0.5 == 1000 or lobbyBlit-0.5 == 300):    
            direc *= -1

        lobbyBlit += 0.5 * direc

        for event in pygame.event.get():
            if event.type == KEYDOWN:
                # Draws out the user input
                if (event.unicode.isnumeric() or event.unicode == '.'):
                    connectInput += event.unicode
                elif event.key == K_BACKSPACE:
                    connectInput = connectInput[:-1]
                elif event.key == K_RETURN:
                    pass
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if connectButtonTwo_rect.collidepoint(pygame.mouse.get_pos()):
                    select_sound.play()
                    runSeeker(connectInput)
                    gameRunning = False
                elif helpBackButton_rect.collidepoint(pygame.mouse.get_pos()):
                    select_sound.play()
                    mode = 'intro'
                    
            elif event.type == QUIT:
                gameRunning = False

        screen.blit(fontButton.render('Connect',True,(0,0,0)),(320,304))        
        screen.blit(fontButton.render(connectInput,True,(0,0,0)),(300,250))
        screen.blit(fontButton.render('Back',True,(0,0,0)),(2,450))
        screen.blit(fontButton.render('Type in the IP to Connect To',True,(0,0,0)),(100,100))
        pygame.display.flip()

    elif mode == 'playGame':
        screen.fill(-1)
        pygame.display.flip()
        for event in pygame.event.get():
            # check for closing window
            if event.type == pygame.QUIT:
                gameRunning = False

pygame.mixer.music.stop()
pygame.quit()

