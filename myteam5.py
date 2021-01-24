# Smart Defence
# 

from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util, sys
from game import Directions, Actions
import game
from util import nearestPoint

'''border_openings = []
def get_border_openings(gameState):
  walls = gameState.getWalls()
  xMid = walls.width//2
  for y in range(walls.height):
    if gameState.hasWall(xMid, y):
      border_openings.append((xMid, y))'''

border_openings = []
def get_border_openings(gameState):
  if len(border_openings) != 0:
    return
  walls = gameState.getWalls()

  # print(walls.height, walls.width)
  # for y in range(walls.height):
  #   for x in range(walls.width):
  #     print(int(gameState.hasWall(x, y)), end=' ')
  #   print('')

  xMid = (walls.width)//2
  for y in range(walls.height):
    if not gameState.hasWall(xMid, y):
      border_openings.append((xMid, y))
  # print(border_openings)

def createTeam(firstIndex, secondIndex, isRed, first = 'CollaborativeAgent', second = 'DefensiveReflexAgent'):
  off = eval(first)(firstIndex)
  defn = eval(second)(secondIndex)
  l = []
  l.append(off)
  l.append(defn)

  return(l)


class BaseClass(CaptureAgent):
  
 
  def registerInitialState(self,gameState):

    get_border_openings(gameState)
    i = self.index
    ss = gameState.getAgentPosition(i)

    self.start = ss

    CaptureAgent.registerInitialState(self,gameState)

  def chooseAction(self,gameState):
    index = self.index

    all_actions = gameState.getLegalActions(self.index)

    l = len(all_actions)
    i = 0
    action_values = []
    m = -100000000
    max_indices = []

    food_list = self.getFood(gameState)
    food_list_list = food_list.asList()
    target_foods = len(food_list_list)
    

    while(i<l):
      action = all_actions[i]
      action_val = self.find_score(gameState,action)
      action_values.append(action_val)
      if(m < action_val):
        m = action_val
        #max_indices.append(i)
      i += 1

    
    

    #
    maxValue = m
    i = 0
    while(i<l):
      if(m==action_values[i]):

        max_indices.append(i)
      i+=1
    



    

    if(target_foods <= 2):
      farthest = 1000000
      i = 0
      while(i<l):
        curr_act = all_actions[i]
        curr_succ = self.find_succ(gameState,all_actions[i])
        d = self.getMazeDistance(self.start,curr_succ.getAgentPosition(index))
        if(farthest > d):
          a = curr_act
          farthest = d

        i+=1
      return(a)

    if(len(max_indices)==1):
      return all_actions[max_indices[0]]
    else:
      r = len(max_indices)
      i = random.randint(0,r)
      return(all_actions[i])


  def find_succ(self,gs,a):
    i = self.index

    potential_succ = gs.generateSuccessor(i,a)
    next_as = potential_succ.getAgentState(i)
    p_next_as = next_as.getPosition()

    dot = nearestPoint(p_next_as)
    if(dot == p_next_as):
      p = potential_succ
      #continue

    else:
      potential_succ = potential_succ.generateSuccessor(i,a)

    return(potential_succ)
    

  def find_score(self,gs,a):
    w = self.getWeights(gs,a)
    
    f = self.getFeatures(gs,a)

    score = f*w
    
    return(score)

  def getFeatures(self,gs,a):
    potential_succ = self.find_succ(gs,a)
    
    f1 = util.Counter()
    f2 = {}

    f = f1
    
    f['successorScore'] = self.getScore(potential_succ)
    f2['successorScore'] = self.getScore(potential_succ)
    return(f)

  def getWeights(self, gameState, action):
    temp_dict = {}
    temp_dict['successorScore'] = float(1)
    
    return(temp_dict)





class DefensiveReflexAgent(BaseClass):
  

  def getFeatures(self, gameState, action):

    features = util.Counter()

    successor = self.find_succ(gameState, action)
    currState = successor.getAgentState(self.index)
    currPos = currState.getPosition()
    

    
    features['onDefense'] = 1

    if(currState.isPacman): 
      features['onDefense'] = 0

    
    opponents = self.getOpponents(successor)
    enemies = []
    l = len(opponents)
    i = 0
    while(i<l):
      opponent = opponents[i]
      enemy = successor.getAgentState(opponent)
      enemies.append(enemy)

      i+=1

    invaders = []
    i = 0

    while(i<l):
      enemy = enemies[i]
      if(enemy.isPacman and (enemy.getPosition() != None)):
        invaders.append(enemy)

      i+=1

    l1 = len(invaders)
  
    features['numInvaders'] = l1

    if(l1 > 0):
      min_d = 1000000
      i = 0
      while(i<l1):
        pos = invaders[i].getPosition()
        d = self.getMazeDistance(currPos,pos)
        if(d<min_d):
          min_d = d

        i+=1
      
      features['invaderDistance'] = min_d

    if(action == Directions.STOP): 
      features['stop'] = 1

    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if(action == rev): 
      features['reverse'] = 1

    return(features)

  def getWeights(self, gameState, action):
    dicti = {}
    dicti['numInvaders'] = -1000
    dicti['onDefense'] = 100
    dicti['invaderDistance'] = -10
    dicti['stop'] = -100
    dicti['revverse'] = -2

    return(dicti)





class CollaborativeAgent(BaseClass):
  
  def getFeatures(self, gameState, action):
    features = util.Counter()

    succ = self.find_succ(gameState, action)
    features['successorScore'] = self.getScore(succ)

    currState = succ.getAgentState(self.index)
    currPos = currState.getPosition()
    X, Y = currPos
    x, y = Actions.directionToVector(action)
    nX, nY = int(X + x), int(Y + y)

    # DOUBT
    isFirst = self.index<2
    # DOUBT
    isFirstOffending = False 
    isSecondOffending = False 

    foodList = self.getFood(gameState).asList()

    walls = gameState.getWalls()
    yMax = walls.height/2

    
    enemies = []
    for e in self.getOpponents(succ):
      enemies.append(succ.getAgentState(e))
    
    invaders = []
    for enemy in enemies:
      if enemy.isPacman and enemy.getPosition()!=0:
        invaders.append(enemy)
    
    chasers = []
    for enemy in enemies:
      if enemy.getPosition()!=None and not(enemy.isPacman):
        chasers.append(enemy)
    
    dist_invaders = []
    for invader in invaders:
      if invader.getPosition()!=None:
        dist_invaders.append(self.getMazeDistance(currPos, invader.getPosition()))

    pos_invaders = []
    for invader in invaders:
      if invader.getPosition()!=None:
        pos_invaders.append(invader.getPosition())
    # DOUBT
    # ghost_dists = [self.getMazeDistance(currPos,ghost.getPosition()) for ghost in enemies if ghost.getPosition()!=None]
    dist_ghosts = []
    for enemy in enemies:
      if not enemy.isPacman:
        dist_ghosts.append(self.getMazeDistance(currPos, enemy.getPosition()))

  
    
    if len(foodList) > 0:
      
      firstFood = []
      secondFood = []
      firstMinDistance, secondMinDistance, foodMinDistance = 1e18, 1e18, 1e18
      for food in foodList:
        currDist = self.getMazeDistance(currPos, food)
        foodMinDistance = min(foodMinDistance, currDist)
        if food[1] > 1.5 * yMax:
          firstFood.append(food)
          firstMinDistance = min(firstMinDistance, currDist)
        else:
          secondFood.append(food)
          secondMinDistance = min(secondMinDistance, currDist)
      
      if len(firstFood) == 0:
        firstMinDistance = 0
      if len(secondFood) == 0:
        secondMinDistance = 0
      

    

    
    if len(invaders) == 0:
      isFirstOffending = True 
      isSecondOffending = True
      features['firstEatFood'] = firstMinDistance
      features['secondEatFood'] = secondMinDistance
      features['eatInvader'] = 0
      
      dist_capsules = []
      for capsule in gameState.getBlueCapsules():
        dist_capsules.append(self.getMazeDistance(currPos, capsule))

      if len(dist_capsules) > 0:
        first2pill = min(dist_capsules)
        second2pill = min(dist_capsules)
      else:
        first2pill = 0
        second2pill = 0
      
      features['eatPowerPill'] = first2pill if isFirst else second2pill

      
      for chaser in chasers:
        if chaser.scaredTimer > 0:
          
          features['firstEatFood'] = 0
          features['secondEatFood'] = 0
          features['eatGhost'] = min(dist_ghosts)
          features['ghostNearby'] = 0
        else:
          features['eatGhost'] = 0
          features['ghostNearby'] = min(dist_ghosts)

        
    else:
      if isFirst and currState.isPacman:
        
        features['firstEatFood'] = foodMinDistance
        
        features['ghostNearby'] = min(dist_ghosts) if len(dist_ghosts)>0 else 0
        
        features['secondEatFood'] = 1/(max(dist_invaders)+1)**2 if len(dist_invaders)>0 else 0

        features['eatInvader'] = 0 
        
        dist_capsules = []
        for capsule in gameState.getBlueCapsules():
          dist_capsules.append(self.getMazeDistance(currPos, capsule))
        first2pill = min(dist_capsules) if len(dist_capsules)>0 else 0

        
        features['eatPowerPill'] = first2pill if len(dist_ghosts)>0 and first2pill < min(dist_ghosts) else 0

        for chaser in chasers:
          if chaser.scaredTimer > 0:
            features['firstEatFood'] = 0
            features['eatGhost'] = min(dist_ghosts)
          else: 
            features['eatGhost'] = 0
            
            features['ghostNearby'] = min(dist_ghosts) if len(dist_ghosts)>0 else 0

      
      elif isFirst and not currState.isPacman:
        
        features['firstEatFood'] = -1
        features['secondEatFood'] = foodMinDistance
        
        features['eatInvader'] = 0

      


    if action == Directions.STOP:
      features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev:
      features['reverse'] = 1

    xMid = walls.width//2
    prevState = gameState.getAgentState(self.index)
    if prevState.numCarrying > 0:
      features['return'] = currPos[0] - xMid - 1
      # features['return'] = min([self.getMazeDistance(currPos, point) for point in border_openings])

    return features

  def getWeights(self, gameState, action):
    import sys
    import ast
    # weights = ast.literal_eval("weights.txt") 
    weights = [75, -10, -64, -43, -75, -82, -16, -37, 43, -200, -7, -100]

    succ,firsteat,stepback,secondeat,eatinv,eatfd,eatpp,eatghst,ghostnear,stop,rev,ret=[int(weight) for weight in weights]
    return {'successorScore': succ, 'firstEatFood':firsteat, 'stepBack': stepback, \
    'secondEatFood':secondeat, 'eatInvader':eatinv, 'eatFood':eatfd,'eatPowerPill':eatpp, \
    'eatGhost':eatghst, 'ghostNearby':ghostnear, 'stop': stop, 'reverse': rev, 'return': ret}