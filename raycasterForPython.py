import pygame
import math
import numpy
import operator
import time

global playerAngle
global playerX
global playerY
global RESOLUTION
global MAPSIZE
global SCREENSIZE
global FOV

SCREENSIZE = 1024
FOV = 128 ###buged does not work
MAPSIZE = 8
NUMBEROFRAYS = 64#512#256
RENDER_DISTANCE = 8

gameMap = [[1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 1, 0, 0, 0, 0, 1],
        [1, 0, 0, 1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1]]  

playerX = 100
playerY = 100
playerAngle = 0

def drawPlayer():
    pygame.draw.rect(screen, [255, 50, 255], [playerX, playerY, 4, 4], 0)
    pygame.draw.line(screen, [255, 50, 255], [playerX, playerY], 
        [playerX - math.cos(playerAngle)*10, playerY-math.sin(playerAngle)*10])

def createWindow(background_colour):
    screen = pygame.display.set_mode((1024, 512))
    screen.fill(background_colour)
    pygame.display.flip()
    running =True
    return screen

def stdDevCalc(numlist):
    numSum1 = 0
    numSum2 = 0
    for i in numlist:
        numSum1 += i**2
        numSum2 += i
    stdDev = math.sqrt(((numSum1)/len(numlist))-((numSum2/len(numlist))**2))
    #print(numlist)
    #print(stdDev)
    #print("-----")
    return stdDev

def drawMap(gameMap, screen):
    color = (255, 0, 0)
    for i in range(0, len(gameMap)):
        for j in range(0, len(gameMap)):
            if gameMap[j][i] == 1:
                pygame.draw.rect(screen, [150, 150, 150], [i*64, j*64, 64, 64], 0)

def drawPysudo3d(anglesAndDistance):
    screenIndex = 0
    for i in anglesAndDistance:#depth sorting
        i[1] = i[1] * (math.cos(playerAngle - i[0]))
    anglesAndDistance.sort(key=operator.itemgetter(1))
    anglesAndDistance = reversed(anglesAndDistance)
    idealRay = SCREENSIZE/2/math.tan(FOV/2)
    for i in anglesAndDistance:
        angle = i[0]
        distance = i[1]
        screenIndex = i[3]
        rColour = max(200-distance/2.5,0); 
        gColour = max(50-distance/2.5, 0); 
        bColour = max(200-distance/2.5, 0)
        if i[2]:
            rColour+=30; gColour -=0; bColour+=30#shade virticalWalls
        if distance != 0:
            pygame.draw.rect(screen, [rColour, gColour, bColour], 
                [SCREENSIZE/NUMBEROFRAYS*screenIndex, 248, 20, idealRay/(distance)*10], 0)
            pygame.draw.rect(screen, [rColour, gColour, bColour], 
                [SCREENSIZE/NUMBEROFRAYS*screenIndex, 248-(idealRay/(distance)*10)+1, 20, (idealRay/(distance)*10)], 0)
        screenIndex+=1

def castAllRays():
    rayIndex = -.5*SCREENSIZE
    idealRay = SCREENSIZE/2/math.tan(FOV/2)
    anglesAndDistance = []
    index = 0
    while rayIndex < .5*SCREENSIZE:
        angle = math.atan(rayIndex/idealRay)
        if angle == 0:
            angle += .01
        distance, wallType, isVertical = castRay(playerAngle+angle)
        anglesAndDistance.append([playerAngle+angle, distance, isVertical, index])
        rayIndex += SCREENSIZE/NUMBEROFRAYS
        index +=1
    for i in range(len(anglesAndDistance)):
        try: 
            stdErr = stdDevCalc([anglesAndDistance[i-2][1], anglesAndDistance[i-1][1], anglesAndDistance[i][1], anglesAndDistance[i+1][1], anglesAndDistance[i+2][1]])/math.sqrt(5)
        except:
            pass
            #print("out of range")
        #print(stdErr)
        print(2*stdErr+anglesAndDistance[i-1][1]- anglesAndDistance[i][1])
        if anglesAndDistance[i][1] >2*stdErr+anglesAndDistance[i-1][1]:
            print("eeee")
            print(anglesAndDistance[i])
            try:
                average=((anglesAndDistance[i-2][1]+anglesAndDistance[i-1][1]+anglesAndDistance[i+1][1]+anglesAndDistance[i+2][1])/4)
            except:
                average=((anglesAndDistance[i-2][1]+anglesAndDistance[i-1][1])/2)
            anglesAndDistance[i][1]= average



    drawPysudo3d(anglesAndDistance)


def castRay(angle):
    wallType =0
    if angle < 0:#alter angles so we do not go above 2pi or below zero
        angle = 2*math.pi+angle
    if angle > 2*math.pi:
        angle = angle -2*math.pi
    #cast the first ray, I cast to rays from the player which eventully hit a wall or end at the render distance,
    distanceV = 0
    rayLen = 0
    if angle < math.pi and angle > 0:#use the direction the player is looking and their releative position in 64x64 grid boxes to generate the length from them to the edge of the 64px square
        rayDistanceY1 = round((playerY%64) / math.sin(angle))
        rayLen = rayDistanceY1
    elif angle > math.pi:
        rayDistanceY1 = round((64-(playerY%64)) / math.sin(angle))*-1
        rayLen=rayDistanceY1
    for i in range(RENDER_DISTANCE):
        offset = -1
        if (angle > 3*math.pi/2 or (angle > 0 and angle < math.pi/2)):#the horizantal rays clip through at an exact point and hit a virtical line this make that imposable
            offset = 1
        rayHitX = math.floor((playerX-math.cos(angle)*rayLen+offset)/64)
        if angle < math.pi and angle > 0:
            rayHitY = math.floor((playerY-math.sin(angle)*rayLen-20)/64)
        elif angle > math.pi:
            rayHitY = math.floor((playerY-math.sin(angle)*rayLen+1)/64)
        try:#if the ray misses and hits something way out we dont want to crash
            if gameMap[(rayHitY)][(rayHitX)] != 0:
                wallType = gameMap[(rayHitY)][(rayHitX)]#cheak line colision point to see if it hit a wall
                break
        except:
            pass
        if angle < math.pi and angle > 0:
            rayDistanceY2 = 64 / (math.sin(angle))
            rayLen += rayDistanceY2
        elif angle > math.pi:
            rayDistanceY2 = -64 / (math.sin(angle))
            rayLen += rayDistanceY2
    distanceV = rayLen
    #// cast ray to hit vertical rows-----------------
    distanceH = 0
    rayLen = 0
    if (angle > 3*math.pi/2 or (angle > 0 and angle < math.pi/2)):
        rayDistanceX1 = round(((playerX%64)) / math.cos(angle))
        rayLen = rayDistanceX1
    elif (angle >= math.pi/2 and angle <3*math.pi/2):
        rayDistanceX1 = round((64-(playerX%64)) / math.cos(angle))*-1
        rayLen=rayDistanceX1
    for i in range(RENDER_DISTANCE):
        offset = -1
        if (angle > math.pi):#the horizantal rays clip through at an exact point and hit a virtical line this make that imposable
            offset = 1
        rayHitY = math.floor((playerY-math.sin(angle)*rayLen-offset)/64)
        if (angle > 3*math.pi/2 or (angle > 0 and angle < math.pi/2)):
            rayHitX = math.floor((playerX-math.cos(angle)*rayLen-20)/64)
        elif  (angle >= math.pi/2 and angle < 3*math.pi/2):
            rayHitX = math.floor((playerX-math.cos(angle)*rayLen+20)/64)
        try:
            if gameMap[(rayHitY)][(rayHitX)] != 0:
                wallType =gameMap[(rayHitY)][(rayHitX)]
                break
        except:
            pass
        if (angle > 3*math.pi/2 or (angle > 0 and angle < math.pi/2)):
            rayDistanceY2 = 64 / (math.cos(angle))
            rayLen += rayDistanceY2
        elif (angle >= math.pi/2 and angle <3*math.pi/2):
            rayDistanceY2 = -64 / (math.cos(angle))
            rayLen += rayDistanceY2
    distanceH=rayLen
    trueDistance = min(distanceH, distanceV)
    pygame.draw.line(screen, [255, 50, 255], [playerX, playerY], [playerX-math.cos(angle)*trueDistance , playerY-math.sin(angle)*trueDistance])
    isVertical = True
    if distanceH < distanceV:
        isVertical = False
    return trueDistance, wallType, isVertical


background_colour = (0, 0, 0)
screen = createWindow(background_colour)
#drawMap(gameMap, screen)
#drawPlayer()
pygame.display.flip()
clock = pygame.time.Clock()
pygame.font.init()
font = pygame.font.SysFont("freesans" , 18 , bold = True)
running = True
while running:
    for event in pygame.event.get():
        # Check for QUIT event      
        if event.type == pygame.QUIT:
            running = False
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        playerY -= math.sin(playerAngle) * 2
        playerX -= math.cos(playerAngle) * 2
    if keys[pygame.K_s]:
        playerY += math.sin(playerAngle) * 2
        playerX += math.cos(playerAngle) * 2
    if keys[pygame.K_a]:
        playerAngle -= math.pi/24
    if keys[pygame.K_d]:
        playerAngle += math.pi/24

    if playerAngle > math.pi*2: playerAngle = 0
    if playerAngle < 0: playerAngle = math.pi*2

    screen.fill(background_colour)
    #drawMap(gameMap, screen)
    drawPlayer()
    castAllRays()


    #keep framerate
    fps = str(int(clock.get_fps()))
    fps_t = font.render(fps , 1, pygame.Color("RED"))
    screen.blit(fps_t,(10,10))
    pygame.display.flip()
    clock.tick(60)
