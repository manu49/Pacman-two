# Smart Defence
# 

from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util, sys
from game import Directions, Actions
import game
from util import nearestPoint

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

def createTeam(firstIndex, secondIndex, isRed, first = 'OffensiveReflexAgent', second = 'DefensiveReflexAgent'):
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

    all_actions = gameState.getLegalActions(index)

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
  

  def getFeatures(self,gs,a):

    st = Directions.STOP
    features = util.Counter()

    if(a == st): 
      features['stop'] = 1

    
    i_g = self.index
    fwd_a_s = gs.getAgentState(i_g)
    fwd_a_s_d = fwd_a_s.configuration.direction 
    rev_a_s_d = Directions.REVERSE[fwd_a_s_d]

    

    
    if(a == rev_a_s_d): 
      features['reverse'] = 1

    successor = self.find_succ(gs,a)
    presentState = successor.getAgentState(i_g)
    currPos = presentState.getPosition()
    

    
    

    if(presentState.isPacman): 
      features['onDefense'] = 0
    else:
      features['onDefense'] = 1

    
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

    

    return(features)

  def getWeights(self,gs,a):

    dicti = {}
    dicti['numInvaders'] = -1000

    dicti['onDefense'] = 100
    
    dicti['invaderDistance'] = -10
    
    dicti['stop'] = -100
    
    dicti['reverse'] = -2

    return(dicti)



class OffensiveReflexAgent(BaseClass):
  
  def getFeatures(self,gameState,action):

    features = util.Counter()
    index = self.index

    succ = self.find_succ(gameState, action)

    features['succ_sc'] = self.getScore(succ)

    presentState = succ.getAgentState(index)
    curr_X, curr_Y = presentState.getPosition()


    x, y = Actions.directionToVector(action)
    nX = int(curr_X + x)
    nY = int(curr_Y + y)

    
    isFirstOffending = False 
    isSecondOffending = False 

    foods = self.getFood(gameState)
    foods_list = foods.asList()

    number_of_foods = len(foods_list)

    walls = gameState.getWalls()
    yMax = walls.height/2

    all_opps = self.getOpponents(succ)
    all_caps = gameState.getBlueCapsules()
    all_enemies = []
    all_invaders = []
    all_chasers = []
    pos_invaders = []
    dist_invaders = []
    ghost_distances = []
    dist_capsules = []

    number_of_capsules = len(all_caps)

    for e in all_opps:
      all_enemies.append(succ.getAgentState(e))
    

    
    for enemy in all_enemies:
      ip = enemy.isPacman
      ig = not(ip)

      if(ig):
        d1 = enemy.getPosition()
        d2 = presentState.getPosition()
        d = self.getMazeDistance(d1,d2)
        ghost_distances.append(d)

      if(ip and enemy.getPosition()!=0):
        all_invaders.append(enemy)
      elif(ig and enemy.getPosition()!=None):
        all_chasers.append(enemy)
    
    num_of_opps = len(all_opps)
    num_of_enemies = len(all_enemies)
    num_of_invaders = len(all_invaders)

    for inv in all_invaders:
      p = inv.getPosition()
      if(p!=None):
        pos_invaders.append(p)
        d1 = inv.getPosition()
        d2 = presentState.getPosition()
        d = self.getMazeDistance(d1,d2)

        dist_invaders.append(d)
    

    #nearest_ghost = min(ghost_distances)
    number_of_ghosts = len(ghost_distances)

    #farthest_invader = max(dist_invaders)
    

    ## check out this line
    #closest_first,closest_second,closest = 1e18,1e18,1e18

    if(number_of_foods != 0):
      
      ff = []
      sf = []

      closest_first,closest_second,closest = 1e18, 1e18, 1e18

      for f in foods_list:
        d1 = presentState.getPosition()
        d2 = f
        d = self.getMazeDistance(d1,d2)

        if(closest > d):
          closest = d

        max_y = yMax*1.5

        if(f[1] > max_y):
          ff.append(f)
          if(closest_first > d):
            closest_first = d
          
        else:
          sf.append(f)
          if(closest_second > d):
            closest_second = d
          
      
      if(len(ff) == 0):
        closest_first = 0
      if(len(sf) == 0):
        closest_second = 0
      

    if action == Directions.STOP:
      features['stop'] = 1

    
    a1 = gameState.getAgentState(index)
    a2 = a1.configuration.direction
    a3 = Directions.REVERSE[a2]


    if(a3==action):
      features['rev'] = 1
    if(num_of_invaders == 0):

      isFirstOffending = True 
      isSecondOffending = True
      features['ei'] = 0
      features['fef'] = closest_first
      features['sef'] = closest_second
      
      
      
      for c in all_caps:
        d1 = presentState.getPosition()
        d2 = c
        d = self.getMazeDistance(d1,d2)
        dist_capsules.append(d)



      if(number_of_capsules != 0):

        nearest_cap = min(dist_capsules)
        
        first2pill = nearest_cap

      else:

        first2pill = 0
      features['epp'] = first2pill

      
      for chaser in all_chasers:
        isScared = (chaser.scaredTimer > 0)

        if(not(isScared)):
          nearest_ghost = min(ghost_distances)

          
          features['gnb'] = nearest_ghost
          features['eg'] = 0
          
          

        else:
          nearest_ghost = min(ghost_distances)

          features['eg'] = nearest_ghost
          features['fef'] = 0
          features['sef'] = 0
          
          features['gnb'] = 0
          

        
    else:
      ip = presentState.isPacman


      if((index<2) and ip):

        #farthest_invader = min(dist_invaders)

        features['sef'] = 1/(min(dist_invaders)+1)**2 if num_of_invaders>0 else 0
        
        features['fef'] = closest
        #nearest_ghost = min(ghost_distances)
        
        features['gnb'] = min(ghost_distances) if number_of_ghosts>0 else 0
        
        

        features['ei'] = 0 

        m = 1e18
        
        dist_capsules = []
        for c in all_caps:
          d1 = presentState.getPosition()
          d2 = c
          d = self.getMazeDistance(d1,d2)
          if(d < m):
            m = d
          dist_capsules.append(d)

        first2pill = m if len(dist_capsules)>0 else 0

        #nearest_ghost = min(ghost_distances)
        features['epp'] = first2pill if number_of_ghosts>0 and first2pill < min(ghost_distances) else 0


        for chaser in all_chasers:
          isScared = (chaser.scaredTimer>0)


          if(not(isScared)):
            #nearest_ghost = min(ghost_distances)


            features['gnb'] = min(ghost_distances) if number_of_ghosts>0 else 0
            features['eg'] = 0
            
            
          else: 
            nearest_ghost = min(ghost_distances)
            features['eg'] = nearest_ghost
            features['fef'] = 0
            
            

      
      elif((index < 2) and (not(presentState.isPacman))):

        features['sef'] = closest
        
        features['fef'] = -1
        
        
        features['ei'] = 0

      
        

      


    
    

    xMid = walls.width//2
    prevState = gameState.getAgentState(index)
    if prevState.numCarrying > 0:
      
      features['ret'] = min([self.getMazeDistance(presentState.getPosition(), point) for point in border_openings])+1

    return features

  def getWeights(self, gameState, action):
    
    

    weights_dict = {}
    weights_dict['succ_sc'] = 75
    weights_dict['fef'] = -10
    weights_dict['sb'] = -64
    weights_dict['sef'] = -43
    weights_dict['ei'] = -75
    weights_dict['ef'] = -82
    weights_dict['epp'] = -16
    weights_dict['eg'] = -37
    weights_dict['gnb'] = 43
    weights_dict['stop'] = -200
    weights_dict['rev'] = -7
    weights_dict['ret'] = -40



    return(weights_dict)


# closest food point