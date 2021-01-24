'''
Manupriya Gupta 2018cs10355
Jatin Munjal 2018cs10343
'''
from captureAgents import CaptureAgent
import distanceCalculator
import random
import time
import util
import sys
from game import Directions
from game import Actions
import game
from util import nearestPoint

holes = []
def createTeam(firstIndex,secondIndex,isRed,first='OffensiveReflexAgent',second='DefensiveReflexAgent'):
  off = eval(first)(firstIndex)
  defn = eval(second)(secondIndex)
  l = []
  l.append(off)
  l.append(defn)

  return(l)

def get_holes(gameState):
  if len(holes) != 0:
    return
  boundaries = gameState.getWalls()

  broadness = boundaries.width
  h = boundaries.height
  xMid = (broadness)//2

  for y in range(h):

    if(not(gameState.hasWall(xMid, y))):
      holes.append((xMid, y))
  

class BaseClass(CaptureAgent):
  
 
  def registerInitialState(self,gameState):

    get_holes(gameState)
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
    m = (-1)*1e18
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

    
    

    #########################
    maxValue = m
    i = 0
    while(i<l):
      if(m==action_values[i]):

        max_indices.append(i)
      i+=1
    



    

    if(target_foods <= 2):
      farthest = 1e18
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
    
    f['succ_sc'] = self.getScore(potential_succ)
    f2['succ_sc'] = self.getScore(potential_succ)
    return(f)

  def getWeights(self, gameState, action):
    temp_dict = {}
    temp_dict['succ_sc'] = float(1)
    
    return(temp_dict)





class OffensiveReflexAgent(BaseClass):
  
  def getFeatures(self,gameState,action):

    features = util.Counter()
    index = self.index

    succ = self.find_succ(gameState, action)

    features['succ_sc'] = self.getScore(succ)

    presentState = succ.getAgentState(index)
    curr_X, curr_Y = presentState.getPosition()

         

    foods = self.getFood(gameState)
    foods_list = foods.asList()

    number_of_foods = len(foods_list)

    boundaries = gameState.getWalls()
    

    all_opps = self.getOpponents(succ)
    all_caps = gameState.getBlueCapsules()
    all_enemies = []
    all_invaders = []
    all_chasers = []
    pos_invaders = []
    invader_locations = []
    ghost_distances = []
    capsule_locations = []
    yMax = boundaries.height/2

    number_of_capsules = len(all_caps)

    for e in all_opps:
      e1 = succ.getAgentState(e)
      all_enemies.append(e1)
    

    
    for e in all_enemies:
      ip = e.isPacman
      ig = not(ip)

      if(ig):
        d1 = e.getPosition()
        d2 = presentState.getPosition()
        d = self.getMazeDistance(d1,d2)
        ghost_distances.append(d)
      pe = e.getPosition()

      if(ip and pe !=0):
        all_invaders.append(e)
      elif(ig and e.getPosition()!=None):
        all_chasers.append(e)
    
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

        invader_locations.append(d)
    

    #nearest_ghost = min(ghost_distances)
    number_of_ghosts = len(ghost_distances)

    #farthest_invader = max()
    

    ## check out this line
    # closest_first,closest_second,closest = 1e18,1e18,1e18

    if(number_of_foods != 0):
      
      ff = []
      sf = []

      closest_first,closest_second,closest = 1e18, 1e18, 1e18

      for f in foods_list:
        d1 = presentState.getPosition()
        d2 = f
        d = self.getMazeDistance(d1,d2)

        

        max_y = yMax*1.5

        if(f[1] > max_y):
          
          if(closest_first > d):
            closest_first = d
          ff.append(f)
          
        else:
          
          if(closest_second > d):
            closest_second = d
          sf.append(f)

        if(closest > d):
          closest = d
          
      
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

      features['fef'] = closest_first

      features['sef'] = closest_second

      features['ei'] = 0
      
      
      
      
      for c in all_caps:
        d1 = presentState.getPosition()
        d2 = c
        d = self.getMazeDistance(d1,d2)
        capsule_locations.append(d)


      if(number_of_capsules == 0):
        targeted_capsule = 0

      else:

        nearest_cap = min(capsule_locations)


        ##################
        targeted_capsule = nearest_cap
        
        

      features['epp'] = targeted_capsule

      
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

        #farthest_invader = min()

        f1 = 1/(min(invader_locations)+1)**2 if num_of_invaders>0 else 0
        features['sef'] = f1
        
        features['fef'] = closest
        #nearest_ghost = min(ghost_distances)
        
        f2 = min(ghost_distances) if number_of_ghosts>0 else 0
        features['gnb'] = f2
        
        

        features['ei'] = 0 

        m = 1e18
        
        capsule_locations = []
        for c in all_caps:
          d1 = presentState.getPosition()
          d2 = c
          d = self.getMazeDistance(d1,d2)
          if(d < m):
            m = d
          capsule_locations.append(d)


        n_caps = len(capsule_locations)
        ## n_cap = number_of_capsules
        targeted_capsule = m if n_caps>0 else 0


        f_temp = targeted_capsule if number_of_ghosts>0 and targeted_capsule < min(ghost_distances) else 0
        #nearest_ghost = min(ghost_distances
        features['epp'] = f_temp


        for chaser in all_chasers:
          isScared = (chaser.scaredTimer>0)


          if(not(isScared)):
            f1 = min(ghost_distances) if number_of_ghosts>0 else 0
            #nearest_ghost = min(ghost_distances)


            features['gnb'] = f1
            # f42 = 9
            features['eg'] = 0
            
            
          else: 

            nearest_ghost = min(ghost_distances)
            features['eg'] = nearest_ghost
            # f_d = -1
            features['fef'] = 0
            
            

      
      elif(index < 2):
        if(not(presentState.isPacman)):
          # f2 = closest
          features['sef'] = closest
        
          features['fef'] = -1
        
        
          features['ei'] = 0

      
        

      


    
    

    xMid = boundaries.width//2
    prevState = gameState.getAgentState(index)
    if prevState.numCarrying > 0 and presentState.numCarrying != 0:
      
      features['ret'] = min([self.getMazeDistance(presentState.getPosition(), point) for point in holes])

    return features

  def getWeights(self, gameState, action):
    
    
    '''weights = [75, -10, -64, -43, -75, -82, -16, -37, 43, -200, -7, -40]
    weights = [75, -10, -64, -43, -75, -97, -16, -37, 43, -200, -7, -40]
    weights = [75, -10, -64, -43, -75, -82, -16, -37, 70, -200, -7, -40]
    weights = [75, -10, -64, -43, -75, -82, -16, -37, 43, -20, -7, -40]
    weights = [75, -10, -64, -43, -75, -82, -16, -37, 43, -200, -71, -40]
    weights = [75, -10, -64, -43, -75, -82, -16, -37, 43, -200, -7, -50]
    '''

    weights_dict = {}
    weights_dict['succ_sc'] = 75
    weights_dict['fef'] = -10
    weights_dict['sb'] = -64
    weights_dict['sef'] = -43
    weights_dict['ei'] = -75
    weights_dict['ef'] = -82
    weights_dict['epp'] = -20
    weights_dict['eg'] = -37
    weights_dict['gnb'] = 43
    weights_dict['stop'] = -200
    weights_dict['rev'] = -7
    weights_dict['ret'] = -100


    #return({})

    return(weights_dict)


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

    all_enemies = []
    all_invaders = []

    
    if(a == rev_a_s_d): 
      features['rev'] = 1

    successor = self.find_succ(gs,a)
    presentState = successor.getAgentState(i_g)
    

    
    opponents = self.getOpponents(successor)
    
    l = len(opponents)
    i = 0
    while(i<l):
      opponent = opponents[i]
      e = successor.getAgentState(opponent)
      all_enemies.append(e)
      if((e.isPacman) and (e.getPosition() != None)):
        all_invaders.append(e)

      i+=1

    
    i = 0

    

    l1 = len(all_invaders)
  

    if l1 == 0:
      protect = self.getFoodYouAreDefending(successor).asList()
      min_dist = 1e18
      target = presentState.getPosition()
      for food in protect:
        for enemy in all_enemies:
          # print(food, enemy)
          dist = self.getMazeDistance(food, enemy.getPosition())
          if dist < min_dist:
            min_dist = dist
            target = food

      d1 = presentState.getPosition()
      features['target'] = self.getMazeDistance(d1, target)

    if(l1 > 0):
      min_d = 1e18
      i = 0
      while(i<l1):
        pos = all_invaders[i].getPosition()
        d1 = presentState.getPosition()
        d = self.getMazeDistance(d1,pos)
        if(d<min_d):
          min_d = d

        i+=1
      
      features['id'] = min_d



    features['ni'] = l1
    if(presentState.isPacman): 
      features['d'] = 0
    else:
      features['d'] = 1

    return(features)

  def getWeights(self,gs,a):

    dicti = {}
    dicti['stop'] = -100
    
    dicti['rev'] = -2

    dicti['target'] = -50

    dicti['ni'] = -1000

    dicti['d'] = 100
    
    dicti['id'] = -10
    
    

    return(dicti)
