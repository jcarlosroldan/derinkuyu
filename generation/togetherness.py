from math import sqrt
from numpy import cumsum, array, uint8, histogram
from random import random, randint, seed, shuffle
from PIL import Image
from matplotlib import pyplot

SIDE = 400

biomes = ["rock", "rugged", "sand", "mossy", "muddy", "flooded", "gelid", "gloomy", "ruins", "magma", "chamber", "temple"]
biomes_CDF = cumsum([0.25,0.14,0.12,0.09,0.11,0.07,0.06,0.06,0.04,0.02,0.02,0.02])
side = int(SIDE/16)*2
board = [[-1 for x in range(side)] for x in range(side)]
iterations = side*1000
seed(0)
# generate a board according to the probabilities
for x in range(side):
	for y in range(side):
		distance_from_center = sqrt((x-side/2)**2+(y-side/2)**2)
		if distance_from_center>side/2:
			continue
		roll = random()*0.9+(2*distance_from_center/side)*0.1
		board[x][y] = next(n for n,b in enumerate(biomes_CDF) if roll<b)

def adjacents(x,y):
	global side
	return [(x-1,y),((x+1)%side,y),(x,y-1),(x,(y+1)%side),(x-1,(y+1)%side),((x+1)%side,(y+1)%side),((x+1)%side,y-1),(x-1,(y+1)%side)]

print(adjacents(0,0))

def environment(x,y):
	global board
	return [board[a[0]][a[1]] for a in adjacents(x,y)]

# execute togetherness rule http://www.hermetic.ch/pca/tg.htm
x = 0
y = 0
for _ in range(iterations):
	x +=1
	if x==side:
		x = 0
		y = (y+1)%side
	c1 = board[x][y]
	if c1 == -1:
		continue
	adjs = adjacents(x,y)
	c1_env = environment(x,y)

	best_adj = -1
	max_improvement = 0
	shuffle(adjs)
	for n,(ax,ay) in enumerate(adjs):
		c2 = board[ax][ay]
		if c2==-1:
			continue
		c2_env = environment(ax,ay)
		real_score = c2_env.count(c2)+c1_env.count(c1)
		next_score = c2_env.count(c1)+c1_env.count(c2)
		improvement = next_score-real_score
		if improvement>max_improvement:
			max_improvement = improvement
			best_adj = n


	if max_improvement>0:
		board[x][y],board[adjs[best_adj][0]][adjs[best_adj][1]] = board[adjs[best_adj][0]][adjs[best_adj][1]],board[x][y]

h = histogram(board)[0]
print(h)
pyplot.plot(h)
pyplot.show()

im = Image.fromarray(array(board, dtype=uint8))
im.save('test.png')