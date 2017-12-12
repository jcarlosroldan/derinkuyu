from random import randint, seed, choice, random
from numpy import zeros, uint8, cumsum, floor, ceil
from math import sqrt, log
from collections import namedtuple
from PIL import Image
from logging import info, getLogger

class Tree:
	def __init__(self, leaf):
		self.leaf = leaf
		self.lchild = None
		self.rchild = None
	def get_leafs(self):
		if self.lchild == None and self.rchild == None:
			return [self.leaf]
		else:
			return self.lchild.get_leafs()+self.rchild.get_leafs()
	def get_level(self, level, queue):
		if queue == None:
			queue = []
		if level == 1:
			queue.push(self)
		else:
			if self.lchild != None:
				self.lchild.get_level(level-1, queue)
			if self.rchild != None:
				self.rchild.get_level(level-1, queue)
		return queue
	def paint(self, c):
		self.leaf.paint(c)
		if self.lchild != None:
			self.lchild.paint(c)
		if self.rchild != None:
			self.rchild.paint(c)

class Container():
	def __init__(self, x, y, w, h):
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.center = (self.x+int(self.w/2),self.y+int(self.h/2))
		self.distance_from_center = sqrt((self.center[0]-MAP_WIDTH/2)**2 + (self.center[1]-MAP_HEIGHT/2)**2)
	def paint(self, c):
		c.stroke_rectangle(self.x, self.y, self.w, self.h)
	def draw_path(self,c,container):
		c.path(self.center[0],self.center[1],container.center[0],container.center[1])

class Canvas:
	brushes = {"empty":0, "hallway":1, "room":2}
	def __init__(self, w, h, color = "empty"):
		self.board = zeros((h,w), dtype=uint8)
		self.w = w
		self.h = h
		self.set_brush(color)
	def set_brush(self, code):
		self.color = self.brushes[code]
	def stroke_rectangle(self, x, y, w, h):
		self.line(x,y,w,True)
		self.line(x,y+h-1,w,True)
		self.line(x,y,h,False)
		self.line(x+w-1,y,h,False)
	def filled_rectangle(self, x, y, w, h):
		self.board[y:y+h,x:x+w] = self.color
	def line(self, x, y, length, horizontal):
		if horizontal:
			self.board[y,x:x+length] = self.color
		else:
			self.board[y:y+length,x] = self.color
	def path(self,x1,y1,x2,y2):
		self.board[y1:y2+1,x1:x2+1] = self.color
	def circle(self,x,y,r):
		for x_offset in range(-r,r+1):
			for y_offset in range(-r,r+1):
				if sqrt(x_offset**2+y_offset**2)<r:
					self.board[x+x_offset,y+y_offset] = self.color
	def draw(self):
		im = Image.fromarray(self.board)
		im.save(MAP_NAME)
	def __str__(self):
		return str(self.board)

class Room:
	environments = ["serene", "calm", "wild", "dangerous", "evil"]
	biomes = ["rock", "rugged", "sand", "mossy", "muddy", "flooded", "gelid", "gloomy", "magma"]
	biomes_CDF = cumsum([0.22,0.14,0.12,0.10,0.10,0.07,0.06,0.06,0.04,0.03,0.03,0.03])
	def __init__(self, container):
		self.x = container.x+randint(1, floor(container.w/3))
		self.y = container.y+randint(1, floor(container.h/3))
		self.w = container.w-(self.x-container.x)
		self.h = container.h-(self.y-container.y)
		self.w -= randint(0,floor(self.w/3))
		self.h -= randint(0,floor(self.w/3))
		self.environment = int(min(4,10*(container.distance_from_center/MAP_WIDTH)+random()*2-1))
		roll = random()*0.9+(2*container.distance_from_center/MAP_WIDTH)*0.1
		self.biome = next(n for n,b in enumerate(self.biomes_CDF) if roll<b)
	def paint(self,c):
		c.filled_rectangle(self.x, self.y,self.w, self.h)

def random_split(container):
	if container.w<MIN_ROOM_SIDE and container.h<MIN_ROOM_SIDE:
		return None
	def _split_vertical(container):
		r1 = None
		r2 = None
		min_w = int(W_RATIO*container.h)+1
		if container.w < 2*min_w:
			return None
		r1 = Container(container.x,container.y,randint(min_w, container.w-min_w),container.h)
		r2 = Container(container.x+r1.w,container.y,container.w-r1.w,container.h)
		return [r1, r2]
	def _split_horizontal(container):
		r1 = None
		r2 = None
		min_h = int(H_RATIO*container.w)+1
		if container.h < 2*min_h:
			return None
		r1 = Container(container.x,container.y,container.w,randint(min_h, container.h-min_h))
		r2 = Container(container.x,container.y+r1.h,container.w,container.h-r1.h)
		return [r1, r2]
	if randint(0,1) == 0:
		res = _split_vertical(container)
		if res == None:
			return _split_horizontal(container)
		return res
	else:
		res = _split_horizontal(container)
		if res == None:
			return _split_vertical(container)
		return res

def split_container(container, iter):
	root = Tree(container)
	if iter != 0:
		sr = random_split(container)
		if sr!=None:
			root.lchild = split_container(sr[0], iter-1)
			root.rchild = split_container(sr[1], iter-1)
	return root

def draw_paths(c, tree):
	if tree.lchild == None or tree.rchild == None:
		return
	tree.lchild.leaf.draw_path(c, tree.rchild.leaf)
	draw_paths(c, tree.lchild)
	draw_paths(c, tree.rchild)

MAP_WIDTH = 0
MAP_HEIGHT = 0
N_ITERATIONS = 0
H_RATIO = 0
W_RATIO = 0
MIN_ROOM_SIDE = 0
CENTER_HUB_HOLE = 0
CENTER_HUB_RADIO = 0
MAP_NAME = 0

def init(num_players):
	global MAP_WIDTH,MAP_HEIGHT,N_ITERATIONS,H_RATIO,W_RATIO,MIN_ROOM_SIDE,CENTER_HUB_HOLE,CENTER_HUB_RADIO,MAP_NAME
	MAP_WIDTH=int(500*sqrt(num_players))
	MAP_HEIGHT=MAP_WIDTH
	N_ITERATIONS=log(MAP_WIDTH*100,2)
	H_RATIO=0.49
	W_RATIO=H_RATIO
	MIN_ROOM_SIDE = 32
	CENTER_HUB_HOLE = 32
	CENTER_HUB_RADIO = CENTER_HUB_HOLE-MIN_ROOM_SIDE/2
	MAP_NAME="result%s.png"%MAP_WIDTH

def main(num_players, seed_number):
	logger = getLogger('BSPTree')

	logger.info("Initialising")
	init(num_players)
	seed(seed_number)
	canvas = Canvas(MAP_WIDTH, MAP_HEIGHT)
	canvas.set_brush("empty")
	canvas.filled_rectangle(0,0,MAP_WIDTH,MAP_HEIGHT)

	logger.info("Generating container tree")
	# -1 on the main container to remove borders to avoid opened border rooms
	main_container = Container(0, 0, MAP_WIDTH-1, MAP_HEIGHT-1)
	container_tree = split_container(main_container, N_ITERATIONS)

	logger.info("Generating hallways")
	canvas.set_brush("hallway")
	draw_paths(canvas, container_tree)

	logger.info("Generating rooms")
	canvas.set_brush("room")
	leafs = container_tree.get_leafs()
	rooms = []
	for i in range(0, len(leafs)):
		if CENTER_HUB_HOLE < leafs[i].distance_from_center < MAP_WIDTH/2:
			rooms.append(Room(leafs[i]))
			rooms[-1].paint(canvas)

	logger.info("Generating hub")
	canvas.circle(int(MAP_WIDTH/2),int(MAP_HEIGHT/2),int(CENTER_HUB_RADIO))
	#canvas.draw()

	return (rooms, canvas.board)