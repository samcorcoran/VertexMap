__author__ = 'Sam'

import random
import math

nodes = list()

class Resource:
  def __init__(self, name, low=1, high=2, falloff=0.25):
    self.name = name
    self.low = low
    self.high = high
    self.falloff = falloff

base_resources = list()
base_resources.append(Resource('wood', 2, 3))
base_resources.append(Resource('stone', 1, 2))
base_resources.append(Resource('wool', 1, 2))
base_resources.append(Resource('meat', 3, 5))

res_dict = dict()
for r in base_resources:
  res_dict[r.name] = r

class Node():
  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.neighbours = set()
    self.resources = dict()
    self.influencers = dict()

  def addNeighbour(self, n):
    #print('trying to add')
    if not n in self.neighbours:
      self.neighbours.add(n)

  def getRes(self, r):
    if r in self.resources:
      return self.resources[r]
    else:
      return 0

  def addInfluencer(self, inf):
    for r in inf.res.keys():
      if not r in self.influencers.keys():
        self.influencers[r] = [inf]
      else:
        if not inf in self.influencers[r]:
          self.influencers[r].append(inf)

  def removeInfluencer(self, inf):
    for r in inf.res.keys():
      for index, n in enumerate(self.influencers[r]):
        if n == inf:
          infs = self.influencers[r]
          del infs[index]

  def get_dist_from(self, x, y):
    xdist = abs(self.x - x)
    ydist = abs(self.y - y)
    return math.sqrt(xdist**2 + ydist**2)

  def getInfluence(self, r):
    total = 0
    if not r in self.influencers.keys():
        return total
    for inf in self.influencers[r]:
      dist = self.get_dist_from(inf.x, inf.y)
      total += inf.res[r] * (inf.strength_at_dist(dist))
    return total


# Create grid
totalRows = 30
totalCols = 30
for row in range(totalRows):
  for col in range(totalCols):
    nodes.append(Node(col, row))
print("Total nodes: {0}".format(len(nodes)))

def grid_to_node_index(x, y):
  return y*totalCols + x

def find_nearest_adjacent_nodes(x, y):
  nearest = list()
  if x < 0 or x > totalCols-1 or y < 0 or y > totalCols-1:
    print("Error: searching for point outside of grid!")
    return nearest
  nearest.append(nodes[grid_to_node_index(math.floor(x), math.floor(y))])
  nearest.append(nodes[grid_to_node_index(math.floor(x), math.ceil(y))])
  nearest.append(nodes[grid_to_node_index(math.ceil(x), math.floor(y))])
  nearest.append(nodes[grid_to_node_index(math.ceil(x), math.ceil(y))])
  return nearest

# ASSUMPTION WARNING #
# This method fails if there can be node A that is not within distance
# but has a neighbour node B which is and will not otherwise be reached.
# Convex shapes and multiple start points should make this safe.
def find_nodes_within_distance(x, y, dist):
  leaves = list()
  for n in find_nearest_adjacent_nodes(x, y):
      if n.get_dist_from(x, y) < dist:
          leaves.append(n)
  for n in leaves:
      for neighbour in n.neighbours:
          if neighbour in leaves:
              continue
          if neighbour.get_dist_from(x, y) < dist:
              leaves.append(neighbour)
  return leaves

# Artificially enforce node neighbours
for row in range(totalRows):
  for col in range(totalCols):
    index = row*totalCols + col
    #print("Ind {0} (x{1}, y{2})".format(index, col, row))
    n = nodes[index]
    # Above
    if row > 0:
      n.addNeighbour(nodes[index-totalCols])
    # Left
    if col > 0:
      n.addNeighbour(nodes[index-1])
    # Right
    if col < totalCols-1:
      n.addNeighbour(nodes[index+1])
    # Below
    if row < totalRows-1:
      n.addNeighbour(nodes[index+totalCols])

# Test neighbour count by drawing as grid
for row in range(totalRows):
  rowstr = ""
  for col in range(totalCols):
    n = nodes[row*totalCols+col]
    rowstr += str(len(n.neighbours))
  print(rowstr)

# Assign resource values
for n in nodes:
  r = random.choice(base_resources)
  n.resources[r.name] = random.randint(r.low, r.high)

# Influencers can increase supply in surrounding area
class Influencer:
  def __init__(self, x, y, res, max_dist=2):
    # Attributes
    self.x = x
    self.y = y
    self.res = res
    self.inf_nodes = list()
    self.max_dist = max_dist
    # Setup
    self.updateNodes(True)

  def updateNodes(self, on_create = False):
    if not on_create:
    # TODO: Nodes should recalculate influence
      pass
    else:
      # New influences must fin
      for n in find_nodes_within_distance(self.x, self.y, self.max_dist):
          n.addInfluencer(self)

  def strength_at_dist(self, dist):
      if dist > self.max_dist:
          return 0
      # 0 at max_dist
      # 1 at same location
      return (1 - dist/self.max_dist)

num_inf = 2
num_inf_res = 2
for i in range(num_inf):
  res = dict()
  choices = random.sample(base_resources, num_inf_res)
  for c in choices:
    res[c.name] = random.randint(c.low, 9)#c.high)
  print(res)
  inf = Influencer(random.random()*(totalCols-1), random.random()*(totalRows-1), res, 5)

# Print resource grids
for r in base_resources:
  print(r.name)
  for row in range(totalRows):
    rowstr = ""
    surround_rowstr = ""
    inf_rowstr = ""
    for col in range(totalCols):
      n = nodes[row*totalCols+col]
      local = n.getRes(r.name)
      surround = int(sum([x.getRes(r.name)*r.falloff for x in n.neighbours]))
      # Node's influencers of type r.name should be used to request influence contributions
      influence = int(n.getInfluence(r.name))
      #influences = int(sum([inf.getInfluence(r.name) for inf in n.influencers[r.name]]))
      rowstr += str(local)
      surround_rowstr += str(local+surround)
      inf_rowstr += str(influence)
    print(rowstr + "   " + surround_rowstr + "   " + inf_rowstr)
  print()