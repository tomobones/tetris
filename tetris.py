import pygame
import random
import pandas

# variables
timeGameLoop = 20
timeFalling = 500
timeLevel = 10000

windowsSize = (1000, 1000)
windowsBackgroundColor = (50, 50, 50)

gameGridSize = (10, 20)
gameSurfaceSize = (400, 800)
gameBackgroundColor = (100, 100, 100)

gridColor = windowsBackgroundColor
titleName = "Tetris"

# setup
pygame.init() # initialize several mudules, e.g. pygame.display.init()
win = pygame.display.set_mode(windowsSize) # create a graphical window - the main surface
win.fill(windowsBackgroundColor)
pygame.display.set_caption(titleName)

# fallinBlockTypes - center of mass (1, 1) for all but "O"
positionsOfI = [(1, 0), (1, 1), (1, 2), (1, 3)]
positionsOfL = [(1, 0), (1, 1), (1, 2), (2, 2)]
positionsOfJ = [(1, 0), (1, 1), (1, 2), (0, 2)]
positionsOfT = [(0, 1), (1, 1), (2, 1), (1, 2)]
positionsOfS = [(0, 1), (1, 1), (1, 0), (2, 0)]
positionsOfZ = [(0, 0), (1, 0), (1, 1), (2, 1)]
positionsOfO = [(0, 0), (1, 0), (0, 1), (1, 1)]

colorOfI = (255, 0, 0)
colorOfL = (0, 255, 0)
colorOfJ = (0, 0, 255)
colorOfT = (255, 0, 255)
colorOfS = (0, 255, 255)
colorOfZ = (255, 255, 255)
colorOfO = (255, 255, 0)

shapes = ["I", "L", "J", "T", "S", "Z", "O"]
positionsForShape = {"I": positionsOfI, "L": positionsOfL, "J": positionsOfJ, "T": positionsOfT, "S": positionsOfS, "Z": positionsOfZ, "O": positionsOfO}
colorForShape = {"I": colorOfI, "L": colorOfL, "J": colorOfJ, "T": colorOfT, "S": colorOfS, "Z": colorOfZ, "O": colorOfO}
rotationsForShape = {"I": 2, "L": 4, "J": 4, "T": 4, "S": 2, "Z": 2, "O": 1}

class FallingBlocks(object):

    def __init__(self, x=4, y=-2, shape=""):
        if (shape == ""):
            shape = random.sample(shapes, 1)[0]
        self.x = x
        self.y = y
        self.shape = shape
        self.rotation = 0

    def getBlockAsDict(self):
        blocks = {}
        for positionX, positionY in positionsForShape[self.shape]:
            for rotationIterator in range(self.rotation):
                translatedX, translatedY = positionX - 1, positionY - 1
                rotatedX, rotatedY = translatedY, -translatedX
                positionX, positionY = rotatedX + 1, rotatedY + 1

            blocks[(positionX + self.x, positionY + self.y)] = colorForShape[self.shape]
        return blocks

    def fallsOneStepWithSuccess(self, blocks):
        self.y += 1
        if (self.collidesWithEdgeOrBlocks(blocks)):
            self.y -= 1
            return False
        return True

    def moveRightWithSuccess(self, blocks):
        self.x += 1
        if (self.collidesWithEdgeOrBlocks(blocks)):
            self.x -= 1
            return False
        return True

    def moveLeftWithSuccess(self, blocks):
        self.x -= 1
        if (self.collidesWithEdgeOrBlocks(blocks)):
            self.x += 1
            return False
        return True

    def rotateWithSuccess(self, blocks):
        self.rotation += 1
        self.rotation = self.rotation % rotationsForShape[self.shape]
        if (self.collidesWithEdgeOrBlocks(blocks)):
            self.rotation -= 1
            self.rotation = self.rotation % rotationsForShape[self.shape]
            return False
        return True

    def collidesWithEdgeOrBlocks(self, blocks):
        for positionX, positionY in positionsForShape[self.shape]:
            for rotationIterator in range(self.rotation):
                translatedX, translatedY = positionX - 1, positionY - 1
                rotatedX, rotatedY = translatedY, -translatedX
                positionX, positionY = rotatedX + 1, rotatedY + 1
            positionX, positionY = positionX + self.x, positionY + self.y
            if ((positionX < 0) or (positionX > 9)): return True
            for blockPosition, color in blocks.items():
                if (blockPosition == (positionX, positionY)):
                    return True
        return False

    def stopsOnBottom(self, blocks={}):
        return False

def surfaceWithGridAndBlocks(blocks={}):

    gameSurface = pygame.Surface(gameSurfaceSize)
    gameSurface.fill(gameBackgroundColor)

    blockHeight = gameSurfaceSize[1]//gameGridSize[1]
    blockWidth = gameSurfaceSize[0]//gameGridSize[0]

    for position, color in blocks.items():
        pygame.draw.rect(gameSurface, color, pygame.Rect(position[0]*blockWidth, position[1]*blockHeight, blockWidth, blockHeight))

    for i in range(gameGridSize[1]):
        if (i != 0):
            yOffset = i * blockHeight
            pygame.draw.line(gameSurface, gridColor, (0, yOffset), (gameSurfaceSize[0], yOffset), 1)

    for j in range(gameGridSize[0]):
        if (j != 0):
            xOffset = j * blockWidth
            pygame.draw.line(gameSurface, gridColor, (xOffset, 0), (xOffset, gameSurfaceSize[1]), 1)

    return gameSurface

def surfaceWithNextFallingBlocks(blocks):

    blockHeight = gameSurfaceSize[1] // gameGridSize[1]
    blockWidth = gameSurfaceSize[0] // gameGridSize[0]
    blockSurfaceSize = (4 * blockWidth, 4 * blockHeight)

    blocksSurface = pygame.Surface(blockSurfaceSize)
    blocksSurface.fill(windowsBackgroundColor)

    for position, color in blocks.items():
        positionX, positionY = position[0] - 4, position[1] + 2
        pygame.draw.rect(blocksSurface, color, pygame.Rect(positionX * blockWidth, positionY * blockHeight, blockWidth, blockHeight))

    for i in range(4):
        if (i != 0):
            yOffset = i * blockHeight
            pygame.draw.line(blocksSurface, windowsBackgroundColor, (0, yOffset), (gameSurfaceSize[0], yOffset), 1)

    for j in range(4):
        if (j != 0):
            xOffset = j * blockWidth
            pygame.draw.line(blocksSurface, windowsBackgroundColor, (xOffset, 0), (xOffset, gameSurfaceSize[1]), 1)

    return blocksSurface

def refreshGameDisplayWithBlockDictionary(fallingBlocks, staticBlocks):

    allBlocks = {}
    allBlocks.update(fallingBlocks)
    allBlocks.update(staticBlocks)
    win.blit(surfaceWithGridAndBlocks(allBlocks), (100, 100))
    pygame.display.update()

def refreshSidePanelDisplayWithBlockDictionary(nextFallingBlocks):
    font = pygame.font.SysFont('comicsans', 30)
    text = font.render('Next Shape', 1, (255, 255, 255))
    temp_surface = pygame.Surface(text.get_size())
    temp_surface.fill(windowsBackgroundColor)
    temp_surface.blit(text, (0, 0))

    win.blit(surfaceWithNextFallingBlocks(nextFallingBlocks), (200+gameSurfaceSize[0], 150))
    win.blit(temp_surface, (200+gameSurfaceSize[0], 100))
    pygame.display.update()

def refreshSidePanelDisplayWithPoints(points):
    font = pygame.font.SysFont('comicsans', 30)
    text = font.render('Points: '+str(points), 1, (255, 255, 255))
    temp_surface = pygame.Surface(text.get_size())
    temp_surface.fill(windowsBackgroundColor)
    temp_surface.blit(text, (0, 0))

    win.blit(temp_surface, (400+gameSurfaceSize[0], 100))
    pygame.display.update()

def getPointIncrease(blocks):
    rowCounter = [0 for _ in range(gameGridSize[1])]
    for position, color in blocks.items():
        if position[1] < 20: rowCounter[position[1]] += 1

    rowIsFull = [False for _ in range(gameGridSize[1])]
    for index, row in enumerate(rowCounter):
        if row == 10: rowIsFull[index] = True

    return sum(rowIsFull)

def deleteFullRows(blocks):
    newBlocks = {(x, gameGridSize[1]): (0,0,0) for x in range(10)}

    # check for full rows
    rowCounter = [0 for _ in range(gameGridSize[1])]
    for position, color in blocks.items():
        if position[1] < 20: rowCounter[position[1]] += 1

    rowIsFull = [False for _ in range(gameGridSize[1])]
    for index, row in enumerate(rowCounter):
        if row == 10: rowIsFull[index] = True

    offsetY = [0 for _ in range(gameGridSize[1])]
    fullRowsAboveThisRow = 0
    for row, isFull in enumerate(rowIsFull):
        if isFull: fullRowsAboveThisRow += 1
        offsetY[row] = sum(rowIsFull) - fullRowsAboveThisRow

    # transform blocks
    if sum(rowIsFull):
        for position, color in blocks.items():
            if position[1] < 20 and not rowIsFull[position[1]]:
                newBlocks[(position[0], position[1] + offsetY[position[1]])] = color
        blocks = newBlocks

    return blocks

def isGameOver(blocks):
    for position, color in blocks.items():
        positionX, positionY = position
        if positionY < 1: return True
    return False

def mainMenu():
    font = pygame.font.SysFont('comicsans', 30)
    text = font.render('Tetris: (N)ext Game or (Q)uit', 1, (255, 255, 255))

    win.fill(windowsBackgroundColor)
    win.blit(text, (380,400))
    pygame.display.update()

    menuLoopIsRunning = True

    while menuLoopIsRunning:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menuLoopIsRunning = False
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_n):
                    gameLoop()
                if (event.key == pygame.K_q):
                    pygame.quit()


def gameLoop():

    countFallingTime = 0
    countLevelTime = 0

    mustFall = False
    mustIncreaseLevel = False

    points = 0

    clock = pygame.time.Clock()
    clock.tick()

    staticBlocksDict = {(x, gameGridSize[1]): (0,0,0) for x in range(10)}
    actualFallingBlocks = FallingBlocks()
    nextFallingBlocks = FallingBlocks()
    win.fill(windowsBackgroundColor)
    refreshGameDisplayWithBlockDictionary(actualFallingBlocks.getBlockAsDict(), staticBlocksDict)
    refreshSidePanelDisplayWithBlockDictionary(nextFallingBlocks.getBlockAsDict())
    refreshSidePanelDisplayWithPoints(points)

    gameLoopIsRunning = True

    def handleEndOfFalling():
        pass

    while gameLoopIsRunning:
        countFallingTime += clock.get_rawtime()
        countLevelTime += clock.get_rawtime()
        clock.tick()

        # check time for next step of falling
        if countFallingTime > timeFalling:
            mustFall = True
            countFallingTime %= timeFalling

        # check key events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gameLoopIsRunning = False

            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_LEFT) or (event.key == pygame.K_h):
                    if actualFallingBlocks.moveLeftWithSuccess(staticBlocksDict):
                        refreshGameDisplayWithBlockDictionary(actualFallingBlocks.getBlockAsDict(), staticBlocksDict)
                if (event.key == pygame.K_RIGHT) or (event.key == pygame.K_l):
                    if actualFallingBlocks.moveRightWithSuccess(staticBlocksDict):
                        refreshGameDisplayWithBlockDictionary(actualFallingBlocks.getBlockAsDict(), staticBlocksDict)
                if (event.key == pygame.K_UP) or (event.key == pygame.K_k):
                    if actualFallingBlocks.rotateWithSuccess(staticBlocksDict):
                        refreshGameDisplayWithBlockDictionary(actualFallingBlocks.getBlockAsDict(), staticBlocksDict)
                if (event.key == pygame.K_DOWN) or (event.key == pygame.K_j):
                    mustFall = True
                if (event.key == pygame.K_q):
                    gameLoopIsRunning = False

        # handle diverse cases
        if mustFall:
            if actualFallingBlocks.fallsOneStepWithSuccess(staticBlocksDict):
                mustFall = False
                refreshGameDisplayWithBlockDictionary(actualFallingBlocks.getBlockAsDict(), staticBlocksDict)
            else:
                staticBlocksDict.update(actualFallingBlocks.getBlockAsDict())
                actualFallingBlocks = nextFallingBlocks
                nextFallingBlocks = FallingBlocks()
                refreshSidePanelDisplayWithBlockDictionary(nextFallingBlocks.getBlockAsDict())
                # check full rows - return number of deleted rows -> points, "full row counter"
                points += getPointIncrease(staticBlocksDict)
                refreshSidePanelDisplayWithPoints(points)
                staticBlocksDict = deleteFullRows(staticBlocksDict)
                # set 'full row counter' -> in case increase level
                # check game over -> save points... input name ec
                if (isGameOver(staticBlocksDict)): gameLoopIsRunning = False
                # update points

        if mustIncreaseLevel:
            print('Level Increase!')
            mustIncreaseLevel = False
    mainMenu()

mainMenu()
pygame.quit()
