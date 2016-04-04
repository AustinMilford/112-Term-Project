#beginnig of final project

from tkinter import *
import math
import random
import copy
import tkinter.messagebox

def drawClearHexagon(pointList,canvas):
    #takes a list of tuples and draws a clear hexagon
    prevPoint = None
    for i in range(len(pointList)):
        point = pointList[i]
        if(prevPoint != None):
            (x1,y1) = prevPoint
            (x2,y2) = point
            canvas.create_line(x1,y1,x2,y2,fill="black",width=2)
        prevPoint = point

class Tile(object):

    def __init__(self,x,y,ACx,ACy,data):
        self.x = x
        self.y = y
        self.ACx = ACx #axial x-coord
        self.ACy = ACy #axial y-coord
        self.r = 32 #side length of an equilateral triangle (6 in a hex)
        self.theta = 1.047 #the number of radians in 60 degrees
        self.stomped = False
        self.contents = []

    def draw(self,canvas):
        #Draw just a hexagon in here,unless if it's stomped
        xmod = self.r * math.cos(self.theta)
        ymod = self.r * math.sin(self.theta)
        pointList = [(self.x-self.r,self.y),(self.x-xmod,self.y-ymod),
            (self.x+xmod,self.y-ymod),(self.x+self.r,self.y),(self.x+xmod,
             self.y+ymod),(self.x-xmod,self.y+ymod),(self.x-self.r,self.y)]
        #the initial point is at the front and end so it draws both lines
        if(self.stomped):
            canvas.create_polygon(pointList[:-1],fill="brown")
        else:
            drawClearHexagon(pointList,canvas)

    def drawCoords(self,canvas):
        #draws the coordinates of the hexagon
        canvas.create_text(self.x,self.y,text=str(self.ACx)+","+str(self.ACy),
            fill="darkBlue",font="Times 12")

    def containsPoint(self,x,y):
        #finds if a point is in this hexagon
        (mouseX,mouseY) = (x-self.x,y-self.y) #center our hexagon at 0,0
        xmod = self.r * math.cos(self.theta) #1/2 length of a side
        ymod = self.r * math.sin(self.theta) #the apothem
        heightSlope = -(3**(0.5)) #slope of top-right diagonal side
        maxHeight = (heightSlope*abs(mouseX)) + (self.r*(3**0.5)) #equation
        if(abs(mouseY)>(ymod) or abs(mouseX)>self.r):
            return False
        elif(abs(mouseY)>maxHeight):
            return False
        else:
            return True

    def getStomped(self,data):
        #you can't stop a regular tile...
        pass

class City(Tile):

    def __init__(self,x,y,name,size,ACx,ACy,data):
        super(City,self).__init__(x,y,ACx,ACy,data)
        self.x = x
        self.y = y
        self.ACx = ACx #axial x-coord
        self.ACy = ACy #axial y-coord
        self.size = size
        self.status = "safe"
        self.name = name
        self.stomped = False
        self.contents = []

    def getStomped(self,data):
        #here is where the city gets stomped more specifically
        #when you stomp a tile, you can't keep moving
        if(data.stompCount>0):
            self.stomped = True
            for die in range(self.size):
                data.movingMonster.health += random.randint(1,6)
            data.isMoving = False
            data.movingMonster.movesLeft = 1
            data.stompCount -= 1

    def draw(self,canvas):
        super().draw(canvas)
        #here is where I draw the city things, also redraw a hexagon first
        canvas.create_text(self.x,self.y,anchor=N,
            text=self.name,fill="Black",font="Helvetica 8")
        canvas.create_text(self.x,self.y,anchor=S,
            text=str(self.size),fill="Red",font="Helvetica 10")

class MilitaryBase(Tile):

    def __init__(self,x,y,ACx,ACy,data):
        super(MilitaryBase,self).__init__(x,y,ACx,ACy,data)
        self.x = x
        self.y = y
        self.ACx = ACx #axial x-coord
        self.ACy = ACy #axial y-coord
        self.status = "safe"
        self.contents = []

    def getStomped(self,data):
        #here is where the military base gets stomped more specifically
        if(data.stompCount>0):
            self.stomped = True
            data.movingMonster.infamy += 2
            data.isMoving = False
            data.movingMonster.movesLeft = 1
            data.stompCount -= 1

    def draw(self,canvas):
        super().draw(canvas)
        #here is where I draw the military base things, also redraw hexagon
        cx,cy,r = (self.x,self.y,self.r)
        (point,vert) = (r/2,r/4) #distance from center of points and verts
        canvas.create_polygon(cx-point,cy,cx-vert,cy-vert,cx,cy-point,
            cx+vert,cy-vert,cx+point,cy,cx+vert,cy+vert,cx,
            cy+point,cx-vert,cy+vert,fill="dark goldenrod")

class MutationPoint(Tile):

    def __init__(self,x,y,ACx,ACy,data):
        super(MutationPoint,self).__init__(x,y,ACx,ACy,data)
        self.x = x
        self.y = y
        self.ACx = ACx #axial x-coord
        self.ACy = ACy #axial y-coord
        self.status = "active"
        self.contents = []
        self.mutations = [1,2,3,2,1]
        self.mutableStats = ["Attack","Defense","Damage"]

    def getStomped(self,data):
        #here is where the military base gets stomped more specifically
        if(data.stompCount>0):
            thisStat = random.choice(self.mutableStats)
            mutation = random.choice(self.mutations)
            if(thisStat == "Attack"):
                data.movingMonster.attack += mutation
            elif(thisStat == "Defense" and 
                (data.movingMonster.defense + mutation) < 6):
                data.movingMonster.defense += mutation
            else:
                data.movingMonster.damage += mutation
            self.stomped = True
            data.isMoving = False
            data.movingMonster.movesLeft = 1
            data.stompCount -= 1
        # randomMutation = random.randint(range(len(data.mutations)-1))
        # thisMutation = data.mutations.pop(randomMutation)
        # print(thisMutation)

    def draw(self,canvas):
        super().draw(canvas)
        #here we draw the mutation point and the original hexagon
        canvas.create_text(self.x,self.y,text="MUTATE",
            fill="Purple",font="Helvetica 10")

class Arena(Tile):

    def __init__(self,x,y,ACx,ACy,data):
        super(Arena,self).__init__(x,y,ACx,ACy,data)
        self.x = x
        self.y = y
        self.ACx = ACx #axial x-coord
        self.ACy = ACy #axial y-coord
        self.contents = []

    def getStomped(self,data):
        #here is where battle is initiated
        if(data.stompCount>0):
            pass
        else:
            data.isMoving = False
            data.stageCompleted = True
            data.movingMonster.movesLeft = 1 #because I take away 1 down low
            data.stageTimer = 1 #to lower the delay before the next stage here
            data.fightingMonster = data.movingMonster

    def draw(self,canvas):
        super().draw(canvas)
        #here we draw the mutation point and the original hexagon
        canvas.create_text(self.x,self.y,text="Arena",
            fill="cyan4",font="Helvetica 12")

class Monster(object):

    def __init__(self,ACx,ACy,move,defense,attack,damage,color,image,
        data,health=10):
        self.ACx = ACx #axial x-coord
        self.ACy = ACy #axial y-coord
        self.r = 12
        self.health = health
        self.move = move
        self.defense = defense
        self.attack = attack
        self.damage = damage
        self.color = color
        self.image = None
        self.imageString = image
        self.infamy = 0 #this can be used in phase 2 of the game
        self.movesLeft = self.move
        (self.x,self.y) = self.centerMonster(data)
        #maybe have a card for each monster?

    def moveMonster(self,tile,data):
        # I will add in a bunch of conditionals here to limit move range
        if(self.movesLeft>0):
            if(tile.ACx == self.ACx and tile.ACy == self.ACy):
                pass
            elif((tile.ACx == self.ACx-1 or tile.ACx == self.ACx+1 or
                tile.ACx == self.ACx) and (tile.ACy == self.ACy-1 or 
                tile.ACy == self.ACy+1 or tile.ACy == self.ACy)):
                (self.ACx,self.ACy) = (tile.ACx,tile.ACy)
                tile.getStomped(data)
                self.movesLeft -= 1
            else:
                pass
        else:
            data.isMoving = False

    def onTile(self,tile):
        #determines if a monster is on a tile
        if(self.ACx == tile.ACx and self.ACy == tile.ACy):
            return True
        else: return False

    def centerMonster(self,data):
        #here I center the monster on the center of the hexagon it's in
        for tile in data.tileList:
            if(tile.ACx == self.ACx and tile.ACy == self.ACy):
                return (tile.x,tile.y)

    def drawMonster(self,data,canvas):
        #here I draw the monster
        #below are the circles
        if(data.nextStage != 5):
            (self.x,self.y) = self.centerMonster(data)
        #we did that above so we can draw the winner off-grid at the end
        # canvas.create_oval(self.x-self.r,self.y-self.r,self.x+self.r,
        #     self.y+self.r,fill=self.color)
        if(self.image == None):
            self.image = PhotoImage(file=self.imageString)
        canvas.create_image(self.x,self.y,image=self.image)

class Card(object):
    #I can use this to draw a card for current player

    def __init__(self,monster,data):
        self.cardWidth = data.width-(31*data.width)//40
        self.cardHeight = (11*data.height)//12 - data.height//12
        self.top = False #is it the 1st to the arena?
        self.cardColor = "cyan4"
        self.outlineColor = "DeepSkyBlue4"
        self.width = 4
        self.textColor = "gray24"
        self.cardFont = "GillSansUltraBold 20"
        self.gap = 32
        self.monster = monster
        self.color = monster.color
        (self.leftX,self.topY) = (0,0)

    def drawCard(self,data,leftX,topY,canvas):
        #here we draw the card for the current monster
        (self.leftX,self.topY) = (leftX,topY) #reseting top corner's coords
        rightX = leftX+self.cardWidth
        bottomY = topY+self.cardHeight
        if(self.top == True): self.outlineColor = "goldenrod"
        canvas.create_rectangle(leftX,topY,rightX,bottomY,
            fill=self.cardColor,outline=self.outlineColor,width=self.width)
        canvas.create_text(leftX+(rightX-leftX)//2,
            topY+self.gap,fill=self.textColor,font=self.cardFont,
            text="MOVES LEFT: %d" % (self.monster.movesLeft))
        canvas.create_text(leftX+(rightX-leftX)//2,
            topY+2*self.gap,fill=self.textColor,font=self.cardFont,
            text="HEALTH: %d" % (self.monster.health))
        canvas.create_text(leftX+(rightX-leftX)//2,
            topY+3*self.gap,fill=self.textColor,font=self.cardFont,
            text="INFAMY: %d" % (self.monster.infamy))
        self.drawStats(data,leftX,topY,rightX,canvas)
        canvas.create_text(leftX+(rightX-leftX)//2,
            topY+7*self.gap,fill=self.color,font=self.cardFont,
            text="COLOR: " + self.monster.color)
        self.BattleInstructions(data,leftX,topY,rightX,canvas)

    def BattleInstructions(self,data,leftX,topY,rightX,canvas):
        #here are the instructions in the event of battle time
        if(data.stompCount<1 and data.nextStage == False):
            canvas.create_text(leftX+(rightX-leftX)//2,
                topY+10*self.gap,fill=self.textColor,font=self.cardFont,
                text="GO TO AN")
            canvas.create_text(leftX+(rightX-leftX)//2,
                topY+11*self.gap,fill=self.textColor,font=self.cardFont,
                text="ARENA!!")

    def drawStats(self,data,leftX,topY,rightX,canvas):
        #here I draw some stats in a helper function for good style
        canvas.create_text(leftX+(rightX-leftX)//2,
            topY+4*self.gap,fill=self.textColor,font=self.cardFont,
            text="DEFENSE: %d" % (self.monster.defense))
        canvas.create_text(leftX+(rightX-leftX)//2,
            topY+5*self.gap,fill=self.textColor,font=self.cardFont,
            text="ATTACK: %d" % (self.monster.attack))
        canvas.create_text(leftX+(rightX-leftX)//2,
            topY+6*self.gap,fill=self.textColor,font=self.cardFont,
            text="DAMAGE: %d" % (self.monster.damage))

    def containsPoint(self,inputX,inputY):
        #determines if someone clicks on this card
        if(inputX>self.leftX and inputX<(self.leftX+self.cardWidth) and
           inputY>self.topY and inputY<(self.topY+self.cardHeight)):
            return True
        return False

class BattleControls(object):
    #here are the controlls for fighting
    def __init__(self,monster,data):
        self.monster = monster
        self.width = data.width//7
        self.height = data.height//4
        self.vertSpacing = data.height//5
        self.leftX = 0
        self.topY = 0
        self.buttonR = self.width//8
        self.canChangeColor = "green"
        self.cantChangeColor = "red"
        self.maxAttacksLeft = self.monster.infamy+self.monster.attack
        (self.attacks,self.hits) = (self.monster.attack,0)
        self.weighInHealth = self.monster.health
        (self.textColor,self.outlineColor) = "orange","dark slate gray"
        (self.minusX,self.minusY) = (0,0)
        (self.plusX,self.plusY) = (0,0)
        (self.attackX,self.attackY) = (0,0)
        #the above three will be assigned within the draw function
        self.sideLength = self.buttonR//2
        (self.attackWidth,self.attackHeight) = (self.width//3,self.height//10)

    def drawBattleControls(self,leftX,topY,canvas):
        #here we draw the controls
        (self.leftX,self.topY) = (leftX,topY)
        (self.attackX,self.attackY) = (self.leftX+self.width//2,self.topY+
            (self.height*2//3))
        canvas.create_rectangle(self.leftX,self.topY,self.leftX+self.width,
            self.topY+self.height,fill="dark slate gray",
            outline=self.outlineColor,width=2)
        self.drawMoreAttacks(self.leftX+self.width//2,self.topY+self.height//3,
            canvas)
        self.drawAttackButton(canvas)

    def modifyAttack(self,inputX,inputY):
        #here we determine if the user clicks on a specific thingy
        #then appropriately modify the attack
        dPlus = ((self.plusX - inputX)**2 + (self.plusY - inputY)**2)**0.5
        dMinus = ((self.minusX - inputX)**2 + (self.minusY - inputY)**2)**0.5
        if(dPlus <= self.buttonR and self.monster.infamy>0):
            self.attacks += 1
            self.monster.infamy -= 1
        elif(dMinus <= self.buttonR and self.attacks>self.monster.attack):
            self.attacks -= 1
            self.monster.infamy += 1
        self.maxAttacksLeft = self.monster.infamy+self.monster.attack

    def drawMoreAttacks(self,centerX,centerY,canvas):
        #here we draw a symbol to click for more lives
        horizSpace = self.width//4
        (self.minusX,self.minusY) = (centerX-horizSpace,centerY)
        (self.plusX,self.plusY) = (centerX+horizSpace,centerY)
        self.drawIncrement(canvas)
        self.drawDecrement(canvas)
        canvas.create_text(centerX,centerY,fill=self.textColor,
            font="Times 12",text="%d" % (self.attacks))
        canvas.create_text(centerX,centerY+self.height,fill="red",
            font="Times 16 bold",text="%d HITS!" % (self.hits))

    def drawIncrement(self,canvas):
        #here we draw a button to increment attacks
        if(self.monster.infamy>0): plusColor = self.canChangeColor
        else: plusColor = self.cantChangeColor
        canvas.create_oval(self.plusX-self.buttonR,self.plusY-self.buttonR,
            self.plusX+self.buttonR,self.plusY+self.buttonR,fill=plusColor)
        canvas.create_rectangle(self.plusX-self.sideLength,self.plusY-
            self.sideLength//3,self.plusX+self.sideLength,self.plusY+
            self.sideLength//3,fill="yellow",outline="yellow")
        canvas.create_rectangle(self.plusX-self.sideLength//3,self.plusY-
            self.sideLength,self.plusX+self.sideLength//3,self.plusY+
            self.sideLength,fill="yellow",outline="yellow")

    def drawDecrement(self,canvas):
        #here we draw a button to decrement attacks
        if(self.attacks>self.monster.attack): minusColor = self.canChangeColor
        else: minusColor = self.cantChangeColor
        canvas.create_oval(self.minusX-self.buttonR,self.minusY-self.buttonR,
            self.minusX+self.buttonR,self.minusY+self.buttonR,fill=minusColor)
        canvas.create_rectangle(self.minusX-self.sideLength,self.minusY-
            self.sideLength//3,self.minusX+self.sideLength,self.minusY+
            self.sideLength//3,fill="yellow",outline="yellow")

    def attack(self,inputX,inputY,targetMonster,data):
        #here is where we actually attack the other monsters
        (leftX,highY,rightX,lowY) = (self.attackX-self.attackWidth,
            self.attackY-self.attackHeight,self.attackX+self.attackWidth,
            self.attackY+self.attackHeight)
        (attackRolls,hits) = ([],[])
        if(leftX<inputX and rightX>inputX and highY<inputY and
           lowY>inputY):
            for attack in range(self.attacks):
                thisAttack = random.randint(1,6)
                attackRolls.append(thisAttack)
                if(thisAttack >= targetMonster.defense):
                    targetMonster.health -= self.monster.damage
                    hits.append(thisAttack)
            data.fightCounter += 1
            self.attacks = self.monster.attack
            self.hits = len(hits)

    def drawAttackButton(self,canvas):
        #here we draw the attack button
        canvas.create_rectangle(self.attackX-self.attackWidth,
            self.attackY-self.attackHeight,self.attackX+self.attackWidth,
            self.attackY+self.attackHeight,fill="orange")
        canvas.create_text(self.attackX,self.attackY,text="ATTACK!",
            font="times 12")

    def resetWeighInHealth(self):
        #here we weigh in the monster at the beginning of each combat
        self.weighInHealth = self.monster.health

class Instructions(object):
    #Here are the instructions
    def __init__(self,data):
        self.width = data.width
        self.height = data.height
        (self.lineSpacing,self.leftMargin,self.topMargin) = (20,40,100)
        self.lineSpacing = 25
        self.instructionString = self.createInstructions()
        (self.startButtonX,self.startButtonY) = (self.width-120,self.height-80)
        self.buttonWidth = 60
        self.buttonHeight = 20
        (self.regFont,self.exampleFont) = "Helvetica 12","Times 14"
        (self.tileX,self.textX) = (700,750)
        (self.cityY,self.baseY,self.mutateY,self.arenaY) = (100,200,300,400)
        self.exampleCity = City(self.tileX,self.cityY,"Seattle",2,0,0,data)
        self.exampleBase = MilitaryBase(self.tileX,self.baseY,0,1,data)
        self.exampleMutation = MutationPoint(self.tileX,self.mutateY,0,2,data)
        self.exampleArena = Arena(self.tileX,self.arenaY,0,5,data)
        self.imageString = "rsz_instructionimg.png"
        #image url - http://i281.photobucket.com/albums/kk208/classicgamer-3dt/
        #Environment__POST_APOCALYPSE_by_I_NetGraFX.jpg
        self.image = None
        (self.gettingHelp,self.prevStage) = (False,0)

    def createInstructions(self):
        #here I write the instructions:
        initialInstructions = """          OVERVIEW
    In this game, each monster will try to defeat the 3 other monsters
    to be the most fearsome monster in the land. This is accomplished 
    by slaying your adversaries in an epic battle series, with the champion 
    of each match choosing his opponent in the next round of combat."""
        movementRules = """        PRE-COMBAT
    The monsters will be able to rampage across the 
    landscape "stomping" various types of spaces to power up for 
    the final showdown. 
      - Stomping a city results in a random health 
    increase proportional to the size of the city, ranging from 1 to 4. 
      - Stomping a military base results in the monster gaining 2 infamy, which
    can be used to boost the monster's attack in the battle phase.  
      - Stomping a mutation point results in a random boost to a monster's 
    attack, defense, or damage. 
    For your first move, click on your monster, then click on adjacent spaces 
    you wish to travel to until your move counter becomes 0. After every player
    has had one turn, the game will rotate players automatically in the 
    same order they initially determined. When 12 spaces have been stomped, 
    stomps cease to work and the first monster to an arena gets to pick an
    opponent to fight."""
        combatRules = """         COMBAT
    In the battle, you can increase or decrease the number of attacks 
    you make with the plus and minus buttons on the attack controller, 
    as long as you have enough infamy or are not going below your standard 
    attack.  You know it is your turn when your monster controls are 
    highlighted in orange.  Press the attack button to attack.  The winner
    picks the next challenger.

        REMEMBER: 
    At any time, press r to restart the game or h for the instructions."""
        return (initialInstructions,movementRules,combatRules)

    def drawInstructions(self,data,canvas):
        #here we draw the instructions
        if(data.nextStage == 6):
            theseInstructions = self.instructionString[0]
        elif(data.nextStage == 7):
            theseInstructions = self.instructionString[1]
        elif(data.nextStage == 8):
            theseInstructions = self.instructionString[2]
        if(self.image == None):
            self.image = PhotoImage(file=self.imageString)
        canvas.create_image(self.width//2,self.height//2,image=self.image)
        self.createCurrentInstructions(theseInstructions,data,canvas)
        self.createButton(data,canvas)

    def createCurrentInstructions(self,theseInstructions,data,canvas):
        #here we write this screen's instructions
        vertLine = self.topMargin
        canvas.create_text(2*self.leftMargin,vertLine//2,anchor="w",
            text="MEGA MONSTER RAMPAGE!",font="Helvetica 24",fill="red")
        for line in theseInstructions.splitlines():
            canvas.create_text(self.leftMargin,vertLine,anchor="w",
                text=line,font=self.regFont,fill="white")
            vertLine += self.lineSpacing
        canvas.create_text(self.width//2,self.height-20,#anchor="s",
            text="If you're getting help, press h to return to game",
            font=self.regFont,fill="white")

    def createButton(self,data,canvas):
        #here we create that button to move on
        if(data.nextStage == 8): btnString = "START"
        else: btnString = "NEXT"
        canvas.create_rectangle(self.startButtonX-self.buttonWidth,
            self.startButtonY-self.buttonHeight,self.startButtonX+
            self.buttonWidth,self.startButtonY+self.buttonHeight,
            outline="alice blue",width=2)
        canvas.create_text(self.startButtonX,self.startButtonY,
            text=btnString,font="Helvetica 16",fill="alice blue")
        self.drawExamples(canvas)

    def drawExamples(self,canvas):
        #here we draw example tiles
        self.exampleCity.draw(canvas)
        canvas.create_text(self.textX,self.cityY,anchor="w",
            text="Here is a city",font=self.exampleFont)
        self.exampleBase.draw(canvas)
        canvas.create_text(self.textX,self.baseY,anchor="w",
            text="Here is a military base",font=self.exampleFont)
        self.exampleMutation.draw(canvas)
        canvas.create_text(self.textX,self.mutateY,anchor="w",fill="white",
            text="Here is a mutation point",font=self.exampleFont)
        self.exampleArena.draw(canvas)
        canvas.create_text(self.textX,self.arenaY,anchor="w",fill="white",
            text="Here is an arena",font=self.exampleFont)

    def startGame(self,data,inputX,inputY):
        minX = self.startButtonX-self.buttonWidth
        maxX = self.startButtonX+self.buttonWidth
        minY = self.startButtonY-self.buttonHeight
        maxY = self.startButtonY+self.buttonHeight
        if(minX<inputX and inputX<maxX and minY<inputY and inputY<maxY):
            if(data.nextStage == 8):
                data.nextStage = 0
            else:
                data.nextStage += 1

    def giveHelp(self,data):
        #here we give the players help
        if(self.gettingHelp == False):
            self.gettingHelp = True
            self.prevStage = data.nextStage
            if(data.nextStage == 0):
                data.nextStage = 7
            elif(data.nextStage == 3):
                data.nextStage = 8
            else:
                data.nextStage = 6
        else:
            self.gettingHelp = False
            data.nextStage = self.prevStage

####################################
# customize these functions, partially courtesy of 112 notes
####################################

def init(data):
    #initialize a bunch of important things here
    (data.r,data.theta) = (32,1.047)
    data.hexHeight = int(2*(data.r*math.sin(data.theta)))
    data.ACxRange = data.width//(2*data.r)
    data.ACyRange = data.height//data.hexHeight-1
    data.tileList = []
    createBoard(data)
    data.thisTile,data.opening = Tile(-20,-20,-2,-2,data),Instructions(data)
    #a tile off the board that won't draw, since thisTile can't be empty
    (data.monsterList,data.battleCardList,data.battleControls) = ([],[],[])
    createMonsters(data)
    createBattleCards(data)
    createMonsterControls(data)
    (data.stage1Image,data.stage2Image,data.stage4Image) = (None,None,None)
    (data.movingMonster,data.isMoving) = (data.monsterList[0],False)
    data.stompCount = 12 #after 12 stomps, the battles begin!
    (data.stageTimer,data.stageCompleted,data.nextStage) = (8,False,6)
    (data.p1,data.p2) = (data.battleCardList[0],data.battleCardList[1])
    (data.p1Controls,data.p2Controls,data.fightingMonster) = (
        data.battleControls[0],data.battleControls[1],data.monsterList[0])
    #we reassign the above two values to something logical when appropriate
    (data.fightCounter,data.turnOrder,data.turnIndex) = (0,[],0)
    #find a way to make a mandatory turn order after 1st 4 turns

def createMonsters(data):
    #here is where I position the monsters
    images = ["rsz_redmonster2.png",
    "yellowmonster1.png",
    "rsz_blue-monster.png",
    "rsz_green-monster.png"]
    #urls for monster images
    #red monster - http://pre04.deviantart.net/a2d9/th/pre/i/2012/218/a/8/r
    #ed_monster_by_fokito82-d5a1d69.png
    #yellow monster - http://www.woodus.com/den/gallery/graphics/dw1gbc/
    #monster/golem.png
    #blue monster - http://www.iconarchive.com/show/monster-icons-by-spoon-
    #graphics/Blue-Monster-icon.html
    #green monster - http://www.iconarchive.com/show/monster-icons-by-spoon-
    #graphics/Green-Monster-icon.html
    numMonsters = 4
    monsterCoords = [(0,0),(data.ACxRange-1,0),(data.ACxRange-1,
        data.ACyRange-1),(0,data.ACyRange-1)]
    monsterColors = ["red","yellow","blue","green"]
    for monster in range(numMonsters):
        (x,y) = monsterCoords.pop() #axial coords
        data.monsterList.append(Monster(x,y,random.randint(4,5),
            random.randint(1,5),random.randint(2,4),random.randint(1,5),
            monsterColors.pop(),images.pop(),data))

def initializeCities(L):
    #takes an empty list and returns a list of cities
    L = [("Houston",4),("Dallas",3),("Fort Worth",2),("San Antonio",3),
        ("Austin",2),("El Paso",2),("Pittsburgh",2),("Tulsa",1),("St. Louis",
        2),("San Francisco",3),("San Jose",3),("Oakland",1),("Los Angeles",
        4),("New York City",4),("New Jersey",4),("Philadelphia",3),("Denver",
        1),("Cleveland",2),("Indianapolis",3),("Chicago",4),("Boston",2),
        ("Detroit",1),("Miami",2),("Atlanta",2),("Charlotte",1),("Orlando",
        1),("Memphis",2),("New Orleans",1),("Portland",1),("Seattle",2)]
    return copy.deepcopy(L)

def createContent(data):
    #here I create the types of spaces that will be on the board
    cities = initializeCities([])
    (totalTiles,tileTypes) = (data.ACxRange*data.ACyRange,[])
    (cityPercentage,basePercentage,mutationPercentage,arenaPercentage) = (
        2/9*totalTiles,3/27*totalTiles,4,4)
    for tileIndex in range(totalTiles):
        if(tileIndex<cityPercentage and len(cities)>0):
            city = cities.pop(random.randint(0,len(cities)-1))
            tileTypes.append(["City",city])
        elif(tileIndex<(cityPercentage+basePercentage)):
            tileTypes.append(["MilitaryBase"])
        elif(tileIndex<(cityPercentage+basePercentage+mutationPercentage)):
            tileTypes.append(["Mutation"])
        elif(tileIndex<(cityPercentage+basePercentage+
             mutationPercentage+arenaPercentage)):
            tileTypes.append(["Arena"])
        else:
            tileTypes.append(["Regular"])
    return tileTypes

def createBoard(data):
    #I learned how to space hexagons and how axial coords worked from:
    #http://www.redblobgames.com/grids/hexagons/
    (xCoord,yCoord,xdraw,ydraw) = (0,0,0,0)
    #axial coords of hexagons then reg coords of the center of each hex
    tileTypes = createContent(data)
    for x in range(data.ACxRange):
        xdraw += 1.5*data.r
        if(x%2 == 0): ydraw = data.hexHeight
        else: ydraw = data.hexHeight//2
        for y in range(data.ACyRange):
            ydraw += data.hexHeight
            if(x%2 != 0): yVal = y-1
            else: yVal = y
            tile = tileTypes.pop(random.randint(0,len(tileTypes)-1))
            if(tile[0] == "City"):
                data.tileList.append(City(xdraw,ydraw,tile[1][0],tile[1][1],
                    x,yVal,data))
            elif(tile[0] == "MilitaryBase"):
                data.tileList.append(MilitaryBase(xdraw,ydraw,x,yVal,data))
            elif(tile[0] == "Mutation"):
                data.tileList.append(MutationPoint(xdraw,ydraw,x,yVal,data))
            elif(tile[0] == "Arena"):
                data.tileList.append(Arena(xdraw,ydraw,x,yVal,data))
            else:
                data.tileList.append(Tile(xdraw,ydraw,x,yVal,data))

def createBattleCards(data):
    #here I create a list of 4 battle cards, 1 for each monster
    battleCardList = []
    for monster in data.monsterList:
        battleCardList.append(Card(monster,data))
    data.battleCardList = battleCardList

def drawSingularCard(data,canvas):
    #here I draw a singular card during the first phase
    for card in data.battleCardList:
        if(card.color == data.movingMonster.color):
            card.drawCard(data,(31*data.width)//40,data.height//12,canvas)

def drawBattleCards(data,canvas):
    #here I actually draw my battle Cards for the battle selection
    step = data.width//4
    leftStart = 10
    startY = data.height//24
    index = 0
    for index in range(len(data.battleCardList)):
        thisCard = data.battleCardList[index]
        if(thisCard.monster == data.fightingMonster):
            thisCard.top = True
        thisCard.drawCard(data,leftStart,startY,canvas)
        leftStart += step

def createMonsterControls(data):
    #here we create a list of controls that corresponds to monsters
    battleControls = []
    for monster in data.monsterList:
        battleControls.append(BattleControls(monster,data))
    data.battleControls = battleControls

def stageOneScreen(data,canvas):
    #here is the view for stage 1
    canvas.create_rectangle(0,0,data.width,data.height,fill="light sky blue")
    for tile in data.tileList:
        tile.draw(canvas)
        for monster in data.monsterList:
            monster.drawMonster(data,canvas)
    # data.thisTile.drawCoords(canvas)
    #cool, but not really a game feature, just nice for debugging
    drawSingularCard(data,canvas)

def stageOneActions(data,inputX,inputY):
    #here we check for mouspressed stuff in stage 1
    for tile in data.tileList:
        if(tile.containsPoint(inputX,inputY)):
            data.thisTile = tile
            if(data.isMoving == True):
                data.movingMonster.moveMonster(tile,data)
            else:
                for monster in data.monsterList:
                    if(monster.onTile(tile)):
                        data.isMoving = True
                        data.movingMonster = monster
                        data.movingMonster.movesLeft = data.movingMonster.move
                        if(monster not in data.turnOrder):
                            data.turnOrder.append(monster)

def stageOneAutomove(data):
    #here we automatically advance turn order
    if(data.movingMonster.movesLeft == 0 and data.stageCompleted == False):
        data.isMoving = False
    if(len(data.turnOrder) >= 4 and data.isMoving == False):
        data.movingMonster = data.turnOrder[data.turnIndex]
        data.isMoving = True
        data.movingMonster.movesLeft = data.movingMonster.move
        if(data.turnIndex<len(data.turnOrder)-1):
            data.turnIndex += 1
        else:
            data.turnIndex = 0

def stageTwoWelcomeScreen(data,canvas):
    #here is the welcome screen for stage 2
    drawBattleCards(data,canvas)
    startX = data.width//2
    startY = 23*(data.height//24) #where our text will go
    canvas.create_text(startX,startY,fill="white",font="Arial 24",
        anchor=S,text=data.fightingMonster.color+", Pick Your Opponent!")

def stageTwoWelcomeScreenActions(data,inputX,inputY):
    #here we run the actions of the welcome screen
    for controller in data.battleControls:
        controller.resetWeighInHealth()
    for card in data.battleCardList:
        if(card.outlineColor == "goldenrod"):
            data.p1 = card
        elif(card.containsPoint(inputX,inputY)):
            data.p2 = card
            data.stageCompleted = True

def stageTwoPreFight(data,canvas):
    #here we draw the pre-fight scene! yipee!
    (startX1,startX2) = (data.width//5,(3*data.width)//5)
    startY = data.height//24
    textX = data.width//2
    textY = 23*(data.height//24)
    data.p1.drawCard(data,startX1,startY,canvas)
    data.p2.drawCard(data,startX2,startY,canvas)
    canvas.create_text(textX,textY,fill="dark slate gray",font="Arial 24",
        anchor=S,text=data.p1.color+" VS "+data.p2.color)
    data.stageCompleted = True

def drawFight(data,canvas):
    #here we draw the fighting!
    cardX1,cardX2 = (5,(3*data.width//4)+5)
    cardY = data.height//24
    p1ControlsX,p2ControlsX = (data.width//4,(3*data.width//5))
    controlsY = data.height//5
    data.p1.drawCard(data,cardX1,cardY,canvas)
    data.p2.drawCard(data,cardX2,cardY,canvas)
    for controlBoard in data.battleControls:
        if(controlBoard.monster == data.p1.monster):
            # controlBoard.drawBattleControls(p1ControlsX,controlsY,canvas)
            data.p1Controls = controlBoard
        elif(controlBoard.monster == data.p2.monster):
            # controlBoard.drawBattleControls(p2ControlsX,controlsY,canvas)
            data.p2Controls = controlBoard
    if(data.fightCounter%2 == 0):
        (data.p1Controls.outlineColor,data.p2Controls.outlineColor) = (
            "orange","dark slate gray")
    else:
        (data.p2Controls.outlineColor,data.p1Controls.outlineColor) = (
            "orange","dark slate gray")
    data.p1Controls.drawBattleControls(p1ControlsX,controlsY,canvas)
    data.p2Controls.drawBattleControls(p2ControlsX,controlsY,canvas)

def executeFight(data,inputX,inputY):
    #here are the fighting mechanics
    if(data.fightCounter%2 == 0):
        data.p1Controls.modifyAttack(inputX,inputY)
        data.p1Controls.attack(inputX,inputY,data.p2.monster,data)
    else:
        data.p2Controls.modifyAttack(inputX,inputY)
        data.p2Controls.attack(inputX,inputY,data.p1.monster,data)
    if(data.p1.monster.health<1 or data.p2.monster.health<1):
        if(data.p1.monster.health<1): 
            (loser,losingCard,winner) = (data.p1Controls,data.p1,
                data.p2Controls)
        else: 
            (loser,losingCard,winner) = (data.p2Controls,data.p2,
                data.p1Controls)
        data.fightingMonster = winner.monster
        data.fightCounter = 0
        winner.monster.health += loser.weighInHealth
        winner.hits = 0
        takeOutLoser(data,loser,losingCard)

def takeOutLoser(data,loser,losingCard):
    #here we take out the loser
    copiedList = copy.copy(data.battleCardList)
    indexToRemove = 0
    for index in range(len(data.battleCardList)):
        card = data.battleCardList[index]
        if(card.monster == losingCard.monster):
            indexToRemove = index
    data.battleCardList.pop(indexToRemove)
    if(len(data.battleCardList)>1):
        data.nextStage = 4
    else:
        data.nextStage = 5

def drawResult(data,canvas):
    #here we draw the result of each fight
    winningColor = data.fightingMonster.color
    winningMonsterString = winningColor + " Wins!!!!"
    drawFight(data,canvas)
    canvas.create_text(data.width//2,data.height//2,fill=winningColor,
        font="Helvetica 24 bold",text=winningMonsterString)
    data.stageCompleted = True

def gameOver(data,canvas):
    #this is what we draw when the game is over
    stage4ImageString = "rsz_arena.png"
    #arena image - http://static.comicvine.com/uploads/original/13/131238/
    #2546280-coliseum_arena_ckim.jpg
    if(data.stage4Image == None):
        data.stage4Image = PhotoImage(file=stage4ImageString)
    canvas.create_image(data.width//2,data.height//2,image=data.stage4Image)
    winningColor = data.fightingMonster.color
    winningMonsterString = winningColor + " Wins!!!!"
    (stageX,stageY) = (518,448)
    (data.fightingMonster.x,data.fightingMonster.y) = (stageX,stageY)
    canvas.create_text(data.width//2,data.height//10,fill=winningColor,
        font="Helvetica 24 bold",text=winningMonsterString)
    canvas.create_text(data.width//2,data.height,anchor="s",
        fill="white",text="Press r to restart!",font="Helvetica 24")
    data.fightingMonster.drawMonster(data,canvas)

def mousePressed(event,data):
    # use event.x and event.y
    if(data.nextStage == 0):
        stageOneActions(data,event.x,event.y)
    elif(data.nextStage == 1):
        stageTwoWelcomeScreenActions(data,event.x,event.y)
    elif(data.nextStage == 3):
        executeFight(data,event.x,event.y)
    elif(data.nextStage > 5):
        data.opening.startGame(data,event.x,event.y)
    else:
        pass

def keyPressed(event,data):
    # use event.char and event.keysym
    if(event.keysym == "r"):
        init(data)
    elif(event.keysym == "h"):
        data.opening.giveHelp(data)

def timerFired(data):
    #if it's time for the next phase...
    if(data.nextStage == 0):
        stageOneAutomove(data) 
    if(data.stageCompleted == True):
        data.stageTimer -= 1
        if(data.stageTimer == 0):
            if(data.nextStage == 4):
                if(len(data.battleCardList)>1): data.nextStage = 1
                if(len(data.battleCardList)<1): pass
            else: data.nextStage += 1
            data.stageCompleted = False
            data.stageTimer = 8

def redrawAll(canvas,data):
    # draw in canvas
    if(data.nextStage >= 1 and data.nextStage<3):
        stage2ImageString = "rsz_ogstreet.png"
        # image url - http://orig03.deviantart.net/858f/f/2012/128/d/e/
        #overgrown_by_joakimolofsson-d4yx6ky.jpg
        if(data.stage2Image == None):
            data.stage2Image = PhotoImage(file=stage2ImageString)
    canvas.create_image(data.width//2,data.height//2,image=data.stage2Image)
    if(data.nextStage == 1):
        stageTwoWelcomeScreen(data,canvas)
    elif(data.nextStage == 2):
        stageTwoPreFight(data,canvas)
    elif(data.nextStage == 3):
        drawFight(data,canvas)
    elif(data.nextStage == 4):
        drawResult(data,canvas)
    elif(data.nextStage == 5):
        gameOver(data,canvas)
    elif(data.nextStage > 5):
        data.opening.drawInstructions(data,canvas)
    else:
        stageOneScreen(data,canvas)

####################################
# use the run function as-is, courtesy of 112 class notes
####################################

def run(width=400, height=400):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        redrawAll(canvas, data)
        canvas.update()    

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 100 # milliseconds
    init(data)
    # create the root and the canvas
    root = Tk()
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run(1000, 600)

###############Tests!!!!!!!!!!!!!!!!!!

#I cited pictures in-text
#I resized pictures here - http://www.picresize.com/

#I commented out the below test case after I finished using it just so it
#wouldn't keep printing

# def testContainsPoint():
#     print("Testing containsPoint()...", end="")
#     A = Tile(50,50,0,0)
#     print(A.containsPoint(50,50) == True)
#     #test case recommended by roommate b/c it tests every point
#     #if it makes an ascii hexagon, it's good!
#     for x in range(35,65):
#         for y in range(35,65):
#             if(A.containsPoint(x,y)):
#                 print("*",end="")
#             else:
#                 print("-",end="")
#         print("")
#     print("Passed. (Add more tests to be more sure!)")
 
def testAll():
    #testContainsPoint()
    pass

if __name__ == "__main__":
    testAll()

