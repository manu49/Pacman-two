from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util
from game import Directions, Actions
import game
from util import nearestPoint

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'CollaborativeAgent', second = 'CollaborativeAgent'):

    return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class ReflexCaptureAgent(CaptureAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """
  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    actions = gameState.getLegalActions(self.index)

    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    return random.choice(bestActions)

  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
    # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights

  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)
    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore': 1.0}

class CollaborativeAgent(ReflexCaptureAgent):
  """
  A reflex agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """
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

    isFirstOffending = False #keep track of offensive and defensive agents
    isSecondOffending = False #keep track of offensive and defensive agents

    foodList = self.getFood(gameState).asList()
    """if self.isRed:
      ourFood = gameState.getRedCapsules()
    if self.isBlue:
      opponentFood = gameState.getBlueCapsules()"""

    walls = gameState.getWalls()
    vertical = walls.height/2
    horizontal = walls.width/2

    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [enemy for enemy in enemies if enemy.isPacman and enemy.getPosition()!=0]
    chasers = [a for a in enemies if not (a.isPacman) and a.getPosition() != None]
    pm_dists = [self.getMazeDistance(myPos,invader.getPosition()) for invader in invaders if invader.getPosition()!=None]
    pm_pos = [invader.getPosition() for invader in invaders if invader.getPosition() != None]
    ghost_dists = [self.getMazeDistance(myPos,ghost.getPosition()) for ghost in enemies if ghost.getPosition()!=None]

    "splitting food top and bottom"
    #make it get food by setting feature to closest pellet
    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      firstFood = [(x,y) for x,y in foodList if y > 1.5*vertical] #assign tophalf to first agent
      secondFood = [(x,y) for x,y in foodList if y < 1.5*vertical] #assign bottom half to second agent
      foodMinDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      if len(firstFood) > 0:
        firstMinDistance = min([self.getMazeDistance(myPos, food) for food in firstFood])
      else:
        firstMinDistance = 0
      if len(secondFood) > 0:
        secondMinDistance = min([self.getMazeDistance(myPos, food) for food in secondFood])
      else:
        secondMinDistance = 0

    "}"

    #there is no invader make both go get food in diff directions
    if len(invaders) == 0:
      isFirstOffending = True #we are only offending
      isSecondOffending = True
      features['firstEatFood'] = firstMinDistance
      features['secondEatFood'] = secondMinDistance
      features['eatInvader'] = 0
      #send closest offender to powerpill
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

      #eat ghost if scared
      for ghost in chasers:
        if ghost.scaredTimer > 0:
          #don't eat food eat ghost instead
          features['firstEatFood'] = 0
          features['secondEatFood'] = 0
          features['eatGhost'] = min(ghost_dists)
          features['ghostNearby'] = 0
        else:
          features['eatGhost'] = 0
          features['ghostNearby'] = min(ghost_dists)

        """
        if there is an invader and we are making one offensive and one defensive
        then either of the following cases are true:
          isFirst isPacman
          notisFirst not isPacman
          notisFirst isPacman
          isFirst not isPacman
        """
    else: #if there is invader make one offensive and one defensive
      if isFirst and myState.isPacman: #if its first and its a pacman
        # "isFirst is offending"
        features['firstEatFood'] = foodMinDistance
        if len(ghost_dists) > 0:
          features['ghostNearby'] = min(ghost_dists)
        else:
          features['ghostNearby'] = 0
        if len(pm_dists)>0:
          features['secondEatFood'] = 1/(max(pm_dists)+1)**2 #discourage second from getting food
        else:
          features['secondEatFood'] = 0

        features['eatInvader'] = 0 #don't care about the invader
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
            #don't eat food eat ghost instead
            features['firstEatFood'] = 0
            features['eatGhost'] = min(ghost_dists)
          else: #if ghost not scared, stay away
            features['eatGhost'] = 0
            if len(ghost_dists) > 0:
              features['ghostNearby'] = min(ghost_dists)
            else:
              features['ghostNearby'] = 0

      #whoever is defending (first or second) make them eat ghost
      elif isFirst and not myState.isPacman:
        # "isFirst is defending"
        features['firstEatFood'] = -1
        features['secondEatFood'] = foodMinDistance
        if len(pm_dists) > 0:
          features['eatInvader'] = 1/(max(pm_dists)+1)**2
        features['eatInvader'] = 0

      elif not isFirst and not myState.isPacman:
        #"isSecond is defending"
        features['secondGetFood'] = -1 #make sure its not getting food
        features['firstGetFood'] = foodMinDistance
        if len(pm_dists) > 0:
          features['eatInvader'] = 1/(max(pm_dists)+1)**2
        features['eatInvader'] = 0
        #use pm_pos to check if its close to our powerpill

      elif not isFirst and myState.isPacman:
        # "isSecond is offending"
        isFirstOffending = False
        isSecondOffending = True #make the second one defend
        #if its first and its a pacman
        if len(pm_dists)>0:
          features['firstEatFood'] = 1/(max(pm_dists)+1)**2 #discourage first from getting food
        else:
          features['firstEatFood'] = 0
        features['secondEatFood'] = foodMinDistance
        features['eatInvader'] = 0 #don't care about the invader
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
            #don't eat food eat ghost instead
            features['secondEatFood'] = 0
            features['eatGhost'] = min(ghost_dists)
          else: #if ghost not scared, stay away
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