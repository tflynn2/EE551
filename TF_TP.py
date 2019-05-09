import math, random
import numpy as np
from os import name as OSname, system as OSsys

# Top Level Character Class
class Character:
    def __init__(self,name,maxHP,inventory,moves,exp,level):
        self.name=name
        self.maxHP=maxHP
        self.inventory=inventory
        self.moves=moves
        self.exp = exp
        self.level=level
        
        self.currentEnemy = None
        self.currentHP = self.maxHP
        
    def SetEnemy(self, enemy):
        self.currentEnemy = enemy

#Enemy Definitions 
class Enemy(Character):
    def __init__(self, name, maxHP, items, expValue, level, moves):
        super().__init__(name,maxHP,items,moves,expValue,level)
    def PerformMove(self):
        m = random.choice(self.moves)
        m.Execute(self)
    
class RandomEnemy(Enemy):
    def __init__(self, level):
        #Generate Random Enemy
        rName = RandomAdjective() + " " + RandomNoun()        
        rmaxHP = math.floor(abs(np.random.normal(10*level*1.55,level/3,size=None)))
        rexpValue = math.ceil((rmaxHP/1.2));

        rMoves = [AttackMove("Attack", 2.2, 0, .5)]
        numExtraMoves = min(10, math.floor(level/2))
        for i in range(numExtraMoves):
            modifierP = np.random.uniform(.1,.99,size=None)
            rMoves.append(AttackMove(RandomAttackVerb(), (level+1)*(1-modifierP), (1-modifierP), modifierP))

        items = []
        super().__init__(rName,rmaxHP,items,rexpValue,level,rMoves)


class CaveCreature(Enemy):
    def __init__(self):
        #Generate Random Enemy
        level = 4
        rName = "Cave-Dwelling, Rock-Eating, Bloby Creeper Creature"      
        rmaxHP = 1500
        rexpValue = 400

        rMoves = [AttackMove("Shadow Sweat Bomb", 1.3, 0, .8),
                  HealMove("Eating Cave Rocks", 2,0,.7),
                  AttackMove("Rock Smash", 5, 2.0,.35)]
        items = []
        super().__init__(rName,rmaxHP,items,rexpValue,level,rMoves)



#Player Definitions
class Player(Character):
    def __init__(self, maxHP, inventory, moves, exp, level):
        super().__init__(input("Name your character: "), maxHP, inventory, moves, exp, level)        
        self.isRunnningAway = False
        self.StoryLocation = "Cave"
        self.StoryLocationLevel = 0
        self.StoryVisited = {"Cave": [], "Forest": [], "Village": []}

    def tryRunning(self):
        successChance = .6;
        if np.random.uniform(0,1,size=None) <= successChance:
            return True
        else:
            return False

    def SelectMove(self):
        print("\nSelect a move:")
        for i in range(len(self.moves)):
            print(str(i) + ". " + self.moves[i].name)

        while True:
            sel = input("Enter a number to make your move: ")
            try: #quick way of making sure sel input is in the list...
                self.moves[int(sel)].Execute(self)
                break
            except:
                pass

    def GainExperience(self, xpGain):
        StatusMessage("Gained " + str(xpGain) + " Experience")
        self.exp = self.exp + xpGain
        newLevel = math.floor(self.exp/(self.level*self.level*10)) + 1
        if newLevel > self.level:
            self.level = newLevel
            self.maxHP = math.ceil(10*self.level*1.6)
            self.currentHP = self.maxHP
            StatusMessageNoPause(self.name + " reached level " + str(self.level) + "!!")
            self.UpdateCharacterForLevel()
            
    def DisplayCharState(self):
        print(self.name + " is a level " + str(self.level) + " " + self.charclass + " located in " + self.StoryLocation + "(" + str(self.StoryLocationLevel)  +")")
        print("HP: " +  str(self.currentHP) + "/" + str(self.maxHP))

    def DisplayBattleState(self):
        print(self.name +"- HP: " +  str(self.currentHP) + "/" + str(self.maxHP) + "     ||      " + 
              self.currentEnemy.name + " HP: " +  str(self.currentEnemy.currentHP) + "/" + 
              str(self.currentEnemy.maxHP))
                
    def isPlayerAlive(self):
        if self.currentHP == 0:
            return False
        else:
            return True
    def isEnemyAlive(self):
        if self.currentEnemy.currentHP == 0:
            return False
        else:
            return True
        
class Fighter(Player):
    def __init__(self):
        super().__init__(10,["Rusty Sword"],[AttackMove("Slash", 4,.1,.8)],0,1)
        self.charclass = "Fighter"

    def UpdateCharacterForLevel(self):      
        if self.level == 2:
            StatusMessageNoPause("Gained a new move! Haymaker")
            newMove = AttackMove("Haymaker", 4, 2, .35)
            self.moves.append(newMove)
        if self.level == 4:
            StatusMessageNoPause("Gained a new move! Gather Strength")
            newMove = HealMove("Gather Strength", 2.5, .2, .8)
            self.moves.append(newMove)
            

class Wizard(Player):
    def __init__(self):
        super().__init__(10,["Plain Staff"],[AttackMove("Arcane Bolt", 5, 1.7,.80)],0,1)  
        self.charclass = "Wizard"

    def UpdateCharacterForLevel(self):
        if self.level == 2:
            StatusMessageNoPause("Gained a new move! Lightning Storm")
            newMove = AttackMove("Lightning Storm", 4, 7, .35)
            self.moves.append(newMove)


# Move Commands        
class AttackMove:
    def __init__(self,name,basedmg,modifierpercent,chance):
        self.name=name
        self.basedmg=basedmg
        self.modifierpercent=modifierpercent
        self.chance = chance
    def Execute(self,CastingCharacter):
        dmgCalc = abs(np.floor((np.random.normal(self.basedmg,self.modifierpercent*self.basedmg,size=None))*CastingCharacter.level))
        
        if np.random.uniform(low=0.0, high=1.0, size=None) <= self.chance:
            CastingCharacter.currentEnemy.currentHP = CastingCharacter.currentEnemy.currentHP - dmgCalc
            if CastingCharacter.currentEnemy.currentHP < 0:
                CastingCharacter.currentEnemy.currentHP = 0
            StatusMessageNoPause(CastingCharacter.name + " hit "  + CastingCharacter.currentEnemy.name  + " with " +  self.name +  " for "  + str(dmgCalc))
        else:
            StatusMessageNoPause(CastingCharacter.name +  "s " +  self.name +  " missed " +  CastingCharacter.currentEnemy.name)

class HealMove:
    def __init__(self,name,baseheal,modifierpercent,chance):
        self.name=name
        self.baseheal=baseheal
        self.modifierpercent=modifierpercent
        self.chance = chance
    def Execute(self,CastingCharacter):
        healCalc = abs(np.floor((np.random.normal(self.baseheal,self.modifierpercent,size=None))*CastingCharacter.level))
        
        if np.random.uniform(low=0.0, high=1.0, size=None) <= self.chance:
            CastingCharacter.currentHP = CastingCharacter.currentHP + healCalc
            if CastingCharacter.currentHP > CastingCharacter.maxHP:
                CastingCharacter.currentHP = CastingCharacter.maxHP
            StatusMessageNoPause(CastingCharacter.name + " healed by " + self.name +  " for "  + str(healCalc))
        else:
            StatusMessageNoPause(CastingCharacter.name +  "s " +  self.name +  " missed ")

#Helper Functions
def ClearTerminal(): 
    if OSname == 'nt': 
        OSsys("cls") 
    else: 
        OSsys("clear")         
            
def StatusMessage(msg):
    global currentMessages

    if len(currentMessages) > 10:
        currentMessages.pop(1)

    ClearTerminal()
    Player1.DisplayBattleState()
    currentMessages.append(msg)
    for m in currentMessages:
        print(m)
    
    input("press enter to continue...")

def StatusMessageNoPause(msg):
    global currentMessages

    if len(currentMessages) > 10:
        currentMessages.pop(1)

    ClearTerminal()
    Player1.DisplayBattleState()
    currentMessages.append(msg)
    for m in currentMessages:
        print(m)

def ClearStatusMessages():
    global currentMessages
    currentMessages=[]

def DisplayBattleEvent(msg, PlayerCharacter):
    print(msg)
    print("What will you do?")
    print("0. Battle Time!")
    print("1. Try and run away...")
    while True:
        sel = input("Enter a number to make your move: ")
        try: #quick way of making sure sel input error checking
            val = int(sel)
            if val == 0:
                break
            elif val == 1:
                PlayerCharacter.isRunnningAway = True;
                break
            else:
                pass
        except:
            pass
    ClearTerminal()
    ClearStatusMessages()

def DisplayEvent(msg):
    print(msg)
    input("press enter to continue...")
    ClearTerminal()
    ClearStatusMessages()


def RandomNoun():
    nouns = ["Falcon", "Elephant", "Monkey", "Turtle",
            "Bicycle", "Lawyer", "Influencer", "Rabbit",
            "Beetle", "Gnome", "Dragon", "Viper", "Orc", "House Plant"
            ]
    return random.choice(nouns)

def RandomAdjective():
    adjs = ["Faulty", "Dingy", "Feral", "Beautiful", "Ugly", "Lumpy", "Pudgy",
            "Stinky", "Slinky", "Stiff", "Rugged", "Tenacious", "Tantilizing", "Diseased",
            "Tyrannical", "Seductive", "Sassy", "Sedentary", "Solid", "Sneaky", "Sad", "Angry", "Pimply"]
    return random.choice(adjs)

def RandomAttackVerb():
    verbs = ["Punch", "Kick", "Face Smash", "Bash", "Smush", "Stab", "Vomit",
            "Ridicule", "Teasing", "Insults", "Slap", "Hug", "Kisses", "Slash", "Slice", "Snuggle"]
    return random.choice(verbs)

def SelectOptions(question,optionsArray):
    print("\n" + question)
    for i in range(len(optionsArray)):
        print(str(i) + ". " + optionsArray[i])

    while True:
        sel = input("Select an option: ")
        try: #quick way of making sure sel input is in the list...
            val = int(sel)   
            ClearTerminal()         
            break
        except:
            pass
    return val

def CurrentEventStep(PlayerCharacter):
    PlayerCharacter.DisplayCharState()

    #Store Locations Visited to not repeat some text when returning
    visitedPlaces = PlayerCharacter.StoryVisited.get(PlayerCharacter.StoryLocation)

    #Cave Path
    if PlayerCharacter.StoryLocation == "Cave":

        if PlayerCharacter.StoryLocationLevel == 0:
            if not(PlayerCharacter.StoryLocationLevel in visitedPlaces):
                visitedPlaces.append(PlayerCharacter.StoryLocationLevel)
            else:
                DisplayEvent("You arrive back in your cave, its feeling more like home.")
            val = SelectOptions("What's the plan?",["Venture deeper into the cave", "Head down the mountain into the forest", "Sleep at the fire"])
            
            if val==0:                
                PlayerCharacter.StoryLocationLevel = 1
                if PlayerCharacter.StoryLocationLevel in visitedPlaces:
                    DisplayEvent("Back into the depths you go.")
                else:                    
                    DisplayEvent("Fear won't keep you from investigating the cave. Deeper into the darkness you go...")
                    DisplayEvent("As you creep further into the cave, it begins to slant downward, falling deeper into the mountain")
                    DisplayEvent("Suddenly, you hear something scurrying behind you")
                StartRandomBattleEncounter(Player1, 1)
            if val==1:# Forest Branch   
                PlayerCharacter.StoryLocation = "Forest"
                PlayerCharacter.StoryLocationLevel = 0 
                visitedPlaces = PlayerCharacter.StoryVisited.get(PlayerCharacter.StoryLocation)

                if not(PlayerCharacter.StoryLocationLevel in visitedPlaces):
                    visitedPlaces.append(PlayerCharacter.StoryLocationLevel)
                    DisplayEvent("You decide to make your way for the village in the distance")
                    DisplayEvent("Heading out into the night, you begin to descend the mountain. An owl hoots in the distance, making you aware of how empty the forest seems")
                    DisplayEvent("A faint odor is disguised on the wind as you continue downward. Just what is that smell?")
                    DisplayEvent("You travel a bit further as the stink increases, you identify the smell. Blood. All of a sudden, a wild creature leaps out at you from behind a tree!")
                else:                    
                    DisplayEvent("You decide to take another pass through the forest of your nightmares")
                    DisplayEvent("The fresh air of the forest fills your lungs as you begin to descend into the horror")

                StartRandomBattleEncounter(Player1, 1)         
            if val==2:
                DisplayEvent("You rest by the fire, eventually falling asleep. You awake inside the cave feelin refreshed.")
                PlayerCharacter.currentHP = PlayerCharacter.maxHP



        elif PlayerCharacter.StoryLocationLevel >= 1 and PlayerCharacter.StoryLocationLevel < 5 :
            if not(PlayerCharacter.StoryLocationLevel in visitedPlaces):
                visitedPlaces.append(PlayerCharacter.StoryLocationLevel)

            val = SelectOptions("What's the plan?",["Venture deeper into the cave", "Head back to the cave's entrance", "Sit and cry"])
            if val==0:
                DisplayEvent("Onward into the darkness...")
                StartRandomBattleEncounter(Player1, PlayerCharacter.StoryLocationLevel)
                PlayerCharacter.StoryLocationLevel = PlayerCharacter.StoryLocationLevel + 1
            if val==1:
                DisplayEvent("You head back toward the caves entrance")
                StartRandomBattleEncounter(Player1, PlayerCharacter.StoryLocationLevel)                               
                PlayerCharacter.StoryLocationLevel = PlayerCharacter.StoryLocationLevel - 1
            if val==2:
                DisplayEvent("You sit in the cave crying baby tears of unfathomable sorrow.")

        elif PlayerCharacter.StoryLocationLevel == 5:
            if not(PlayerCharacter.StoryLocationLevel in visitedPlaces):
                visitedPlaces.append(PlayerCharacter.StoryLocationLevel)
                DisplayEvent("You come across what a scary creature in the shadows, ")
                EnemyInstance = CaveCreature();
                StartBattleEncounter(PlayerCharacter, EnemyInstance)
            else:
                DisplayEvent("You reminiss on the time you slaughtered that rock-eating cave monster...")
                PlayerCharacter.StoryLocationLevel = PlayerCharacter.StoryLocationLevel + 1

        elif PlayerCharacter.StoryLocationLevel >= 6 and PlayerCharacter.StoryLocationLevel:
            if not(PlayerCharacter.StoryLocationLevel in visitedPlaces):
                visitedPlaces.append(PlayerCharacter.StoryLocationLevel)

            val = SelectOptions("What's the plan?",["Venture deeper into the cave", "Head back to the cave's entrance", "Sit and cry"])
            if val==0:
                DisplayEvent("Onward into the darkness...")
                StartRandomBattleEncounter(Player1, PlayerCharacter.StoryLocationLevel)
                PlayerCharacter.StoryLocationLevel = PlayerCharacter.StoryLocationLevel + 1
            if val==1:
                DisplayEvent("You head back to the caves entrance")
                StartRandomBattleEncounter(Player1, PlayerCharacter.StoryLocationLevel)                               
                PlayerCharacter.StoryLocationLevel = PlayerCharacter.StoryLocationLevel - 1
            if val==2:
                DisplayEvent("You sit in the cave crying baby tears of unfathomable sorrow.")


    if PlayerCharacter.StoryLocation == "Forest":
        if PlayerCharacter.StoryLocationLevel == 0:
            if not(PlayerCharacter.StoryLocationLevel in visitedPlaces):
                visitedPlaces.append(PlayerCharacter.StoryLocationLevel)
                DisplayEvent("As you first embark on an adventure through the forest, you wonder if the village ahead will hold some answers to our perilous situtation")
            else:
                DisplayEvent("Ah back to the empty forest, empty except for the endless stream of bloodthirsty creatures.")

            val = SelectOptions("What's the plan?",["Venture deeper into the forest", "Head back up the mountain towards the cave", "Hug a tree"])
            
            if val==0:                
                PlayerCharacter.StoryLocationLevel = 1
                DisplayEvent("You head back down the mountain into the forest")                   
                StartRandomBattleEncounter(Player1, 1)
            if val==1:# Forest Branch   
                DisplayEvent("You sense the cave is near and push forward towards it")
                StartRandomBattleEncounter(Player1, 1)                
                PlayerCharacter.StoryLocation = "Cave"
                PlayerCharacter.StoryLocationLevel = 0 
            if val==2:
                DisplayEvent("Hugging this tree brings joy to your broken spirit")

        elif PlayerCharacter.StoryLocationLevel >= 1:
            if not(PlayerCharacter.StoryLocationLevel in visitedPlaces):
                visitedPlaces.append(PlayerCharacter.StoryLocationLevel)

            val = SelectOptions("What's the plan?",["Venture deeper into the forest", "Head back to the cave", "Hug a tree"])
            if val==0:
                DisplayEvent("Deeper into the forest you go. Seems like a good idea, given all these murderous creatures.")
                StartRandomBattleEncounter(Player1, PlayerCharacter.StoryLocationLevel)
                PlayerCharacter.StoryLocationLevel = PlayerCharacter.StoryLocationLevel + 1
            if val==1:
                DisplayEvent("You head back toward the caves entrance, seeking refuge.")
                StartRandomBattleEncounter(Player1, PlayerCharacter.StoryLocationLevel)                               
                PlayerCharacter.StoryLocationLevel = PlayerCharacter.StoryLocationLevel - 1
            if val==2:
                DisplayEvent("Hugging this tree brings joy to your broken spirit")

# Game Flow Methods
def StartRandomBattleEncounter(PlayerCharacter, EnemyLevel):
    EnemyInstance =  RandomEnemy(EnemyLevel)
    PlayerCharacter.SetEnemy(EnemyInstance)
    EnemyInstance.SetEnemy(PlayerCharacter)
    DisplayBattleEvent("You encountered a level " + str(EnemyInstance.level) + " " + EnemyInstance.name, PlayerCharacter)
    StatusMessageNoPause("")

    while True:      
        if PlayerCharacter.isRunnningAway == True:   
            PlayerCharacter.isRunnningAway = False         
            if PlayerCharacter.tryRunning() == True:
                StatusMessage("Successfully ran away!")
                break;
            else:
                StatusMessage("Failed to run away, " + PlayerCharacter.currentEnemy.name + " gets the first attack")
        else:
            PlayerCharacter.SelectMove()

        if PlayerCharacter.isEnemyAlive() == False:
            StatusMessageNoPause(" ")
            StatusMessageNoPause(PlayerCharacter.name + " defeated " + PlayerCharacter.currentEnemy.name + "!")
            PlayerCharacter.GainExperience(PlayerCharacter.currentEnemy.exp)
            break;

        EnemyInstance.PerformMove()
        if PlayerCharacter.isPlayerAlive() == False:
            StatusMessageNoPause(PlayerCharacter.name + " died :(")
            quit() #end game

def StartBattleEncounter(PlayerCharacter, EnemyInstance):
    PlayerCharacter.SetEnemy(EnemyInstance)
    EnemyInstance.SetEnemy(PlayerCharacter)
    DisplayBattleEvent("You encountered a level " + str(EnemyInstance.level) + " " + EnemyInstance.name, PlayerCharacter)
    StatusMessageNoPause("")

    while True:      
        if PlayerCharacter.isRunnningAway == True:   
            PlayerCharacter.isRunnningAway = False         
            if PlayerCharacter.tryRunning() == True:
                StatusMessage("Successfully ran away!")
                break;
            else:
                StatusMessage("Failed to run away, " + PlayerCharacter.currentEnemy.name + " gets the first attack")
        else:
            PlayerCharacter.SelectMove()

        if PlayerCharacter.isEnemyAlive() == False:
            StatusMessageNoPause(" ")
            StatusMessageNoPause(PlayerCharacter.name + " defeated " + PlayerCharacter.currentEnemy.name + "!")
            PlayerCharacter.GainExperience(PlayerCharacter.currentEnemy.exp)
            break;

        EnemyInstance.PerformMove()
        if PlayerCharacter.isPlayerAlive() == False:
            StatusMessageNoPause(PlayerCharacter.name + " died :(")
            quit() #end game







#Initialize Screen and Message List
ClearTerminal()
ClearStatusMessages()

#Create Character
Player1 = Fighter()

#Basic Intro
DisplayEvent("You wake up inside an unfamiliar cave. The faint glow of fire warms your skin as you realize you have no idea how you ended up in this cave.")
DisplayEvent("A brief glimpse outside shows you're located near the top of a mountain deep within a forest. In the far off distance, you see a clearing containing a small village.")

#Game Loop
while True:
    CurrentEventStep(Player1)
    
    ClearTerminal()
    ClearStatusMessages()       
