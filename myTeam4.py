## this does not have jatin ka re-written code
from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util, sys
from game import Directions, Actions
import game
from util import nearestPoint



def createTeam(firstIndex, secondIndex, isRed, first = 'CollaborativeAgent', second = 'DefensiveReflexAgent'):
  off = eval(first)(firstIndex)
  defn = eval(second)(secondIndex)
  l = []
  l.append(off)
  l.append(defn)

  return(l)



class BaseClass(CaptureAgent):

  '''def __init__():
    self.start = None'''

 
  def registerInitialState(self,gameState):
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
    m = 0

    while(i<l):
      action = all_actions[i]
      action_val = self.evaluate(gameState,action)
      action_values.append(action_val)
      if(m < action_val):
        m = action_val
      i += 1

    #action_values = [self.evaluate(gameState, a) for a in all_actions]
    

    maxValue = max(action_values)
    #maxValue = m
    bestActions = [a for a, v in zip(all_actions, action_values) if v == maxValue]

    foodLeft = len(self.getFood(gameState).asList())

    if(foodLeft <= 2):
      bestDist = 9999
      for action in all_actions:
        successor = self.getSuccessor(gameState, action)
        pos2 = successor.getAgentPosition(self.index)
        dist = self.getMazeDistance(self.start,pos2)
        if dist < bestDist:
          bestAction = action
          bestDist = dist
      return bestAction

    return random.choice(bestActions)

  def getSuccessor(self, gameState, action):

    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def evaluate(self, gameState, action):
    
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights

  def getFeatures(self, gameState, action):
    
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)
    return features

  def getWeights(self, gameState, action):
    
    return {'successorScore': 1.0}


class DefensiveReflexAgent(BaseClass):
  

  def getFeatures(self, gameState, action):

    features = util.Counter()

    successor = self.getSuccessor(gameState, action)
    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()
    

    
    features['onDefense'] = 1

    if(myState.isPacman): 
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
        d = self.getMazeDistance(myPos,pos)
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
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2}



class CollaborativeAgent(BaseClass):
  
  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)
    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()
    myX, myY = myPos
    x, y = Actions.directionToVector(action)
    nextX, nextY = int(myX + x), int(myY + y)

    isFirst = self.index<2

    isFirstOffending = False 
    isSecondOffending = False 

    foodList = self.getFood(gameState).asList()
    

    walls = gameState.getWalls()
    vertical = walls.height/2
    horizontal = walls.width/2

    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [enemy for enemy in enemies if enemy.isPacman and enemy.getPosition()!=0]
    chasers = [a for a in enemies if not (a.isPacman) and a.getPosition() != None]
    pm_dists = [self.getMazeDistance(myPos,invader.getPosition()) for invader in invaders if invader.getPosition()!=None]
    pm_pos = [invader.getPosition() for invader in invaders if invader.getPosition() != None]
    ghost_dists = [self.getMazeDistance(myPos,ghost.getPosition()) for ghost in enemies if ghost.getPosition()!=None]

  
    
    if len(foodList) > 0:
      firstFood = [(x,y) for x,y in foodList if y > 1.5*vertical] 
      secondFood = [(x,y) for x,y in foodList if y < 1.5*vertical] 
      foodMinDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      if len(firstFood) > 0:
        firstMinDistance = min([self.getMazeDistance(myPos, food) for food in firstFood])
      else:
        firstMinDistance = 0
      if len(secondFood) > 0:
        secondMinDistance = min([self.getMazeDistance(myPos, food) for food in secondFood])
      else:
        secondMinDistance = 0

    

    
    if len(invaders) == 0:
      isFirstOffending = True 
      isSecondOffending = True
      features['firstEatFood'] = firstMinDistance
      features['secondEatFood'] = secondMinDistance
      features['eatInvader'] = 0
      
      dist2pill = [self.getMazeDistance(myPos,pill) for pill in gameState.getBlueCapsules()]
      if len(dist2pill) > 0:
        first2pill = min(dist2pill)
        second2pill = min(dist2pill)
      else:
        first2pill = 0
        second2pill = 0
      if isFirst:
        features['eatPowerPill'] = first2pill
      else:
        features['eatPowerPill'] = second2pill

      
      for ghost in chasers:
        if ghost.scaredTimer > 0:
          
          features['firstEatFood'] = 0
          features['secondEatFood'] = 0
          features['eatGhost'] = min(ghost_dists)
          features['ghostNearby'] = 0
        else:
          features['eatGhost'] = 0
          features['ghostNearby'] = min(ghost_dists)

        
    else:
      if isFirst and myState.isPacman:
        
        features['firstEatFood'] = foodMinDistance
        if len(ghost_dists) > 0:
          features['ghostNearby'] = min(ghost_dists)
        else:
          features['ghostNearby'] = 0
        if len(pm_dists)>0:
          features['secondEatFood'] = 1/(max(pm_dists)+1)**2 
        else:
          features['secondEatFood'] = 0

        features['eatInvader'] = 0 
        dist2pill = [self.getMazeDistance(myPos,pill) for pill in gameState.getBlueCapsules()]
        if len(dist2pill) > 0:
          first2pill = min(dist2pill)
        else:
          first2pill = 0
        if len(ghost_dists)!=0 and first2pill < min(ghost_dists):
          features['eatPowerPill'] = first2pill
        else:
          features['eatPowerPill'] = 0
        for ghosts in chasers:
          if ghosts.scaredTimer > 0:
            
            features['firstEatFood'] = 0
            features['eatGhost'] = min(ghost_dists)
          else: 
            features['eatGhost'] = 0
            if len(ghost_dists) > 0:
              features['ghostNearby'] = min(ghost_dists)
            else:
              features['ghostNearby'] = 0

      
      elif isFirst and not myState.isPacman:
        
        features['firstEatFood'] = -1
        features['secondEatFood'] = foodMinDistance
        if len(pm_dists) > 0:
          features['eatInvader'] = 1/(max(pm_dists)+1)**2
        features['eatInvader'] = 0

      elif not isFirst and not myState.isPacman:
        
        features['secondGetFood'] = -1
        features['firstGetFood'] = foodMinDistance
        if len(pm_dists) > 0:
          features['eatInvader'] = 1/(max(pm_dists)+1)**2
        features['eatInvader'] = 0
        

      elif not isFirst and myState.isPacman:
        
        isFirstOffending = False
        isSecondOffending = True 
        if len(pm_dists)>0:
          features['firstEatFood'] = 1/(max(pm_dists)+1)**2 
        else:
          features['firstEatFood'] = 0
        features['secondEatFood'] = foodMinDistance
        features['eatInvader'] = 0 
        if len(ghost_dists) > 0:
          features['ghostNearby'] = min(ghost_dists)
        else:
          features['ghostNearby'] = 0
        dist2pill = [self.getMazeDistance(myPos,pill) for pill in gameState.getBlueCapsules()]
        if len(dist2pill) > 0:
          second2pill = min(dist2pill)
        else:
          second2pill = 0
        if len(ghost_dists)!=0 and second2pill < min(ghost_dists):
          features['eatPowerPill'] = second2pill
        else:
          features['eatPowerPill'] = 0
        for ghost in chasers:
          if ghost.scaredTimer > 0:
            
            features['secondEatFood'] = 0
            features['eatGhost'] = min(ghost_dists)
          else:
            features['eatGhost'] = 0
            if len(ghost_dists) > 0:
              features['ghostNearby'] = min(ghost_dists)
            else:
              features['ghostNearby'] = 0
            if (nextX,nextY) in Actions.getLegalNeighbors(ghost.getPosition(), walls) or \
            (nextX,nextY) == ghost.getPosition():
              dists = [self.getMazeDistance(myPos,a.getPosition()) for a in chasers]
              features['stepBack'] = max(dists)


    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1
    return features

  def getWeights(self, gameState, action):
    import sys
    import ast
    # weights = ast.literal_eval("weights.txt") 
    #weights = [75, -10, -64, -43, -75, -82, -16, -37, 43, -200, -7] ## 1/5
    weights = [75, -10, -64, -43, -75, -82, -16, -37, 43, -200, -7]
    #weights = [125, -10, 0, 0, 0, 0, 0, 0, 50, -100, 0]
    succ,firsteat,stepback,secondeat,eatinv,eatfd,eatpp,eatghst,ghostnear,stop,rev=[int(weight) for weight in weights]
    return {'successorScore': succ, 'firstEatFood':firsteat, 'stepBack': stepback, \
    'secondEatFood':secondeat, 'eatInvader':eatinv, 'eatFood':eatfd,'eatPowerPill':eatpp, \
    'eatGhost':eatghst, 'ghostNearby':ghostnear, 'stop': stop, 'reverse': rev}


