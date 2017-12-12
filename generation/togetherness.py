from numpy import zeros, concatenate, amax
from random import randint
from PIL import Image
from logging import info, getLogger

def manhattan(room1, room2):
	return abs(room1.x-room2.x)+abs(room1.y-room2.y)

def nearest_dict(n, rooms):
	N = len(rooms)
	# build distance matrix
	distances = zeros((N,N))
	for r1 in range(0,N):
		for r2 in range(r1+1,N):
			distances[r1,r2] = manhattan(rooms[r1],rooms[r2])
	# get the top-n nearest rooms
	result = {}
	for r in range(0,N):
		neighbours = concatenate((distances[0:r,r],distances[r,r:N]), axis = 1)
		result[r] = neighbours.argsort()[:n]
	return result

def score(room, neighbours):
	biome = room.biome
	result = 0
	for room in neighbours:
		if room.biome == biome:
			result += 1
	return result

def togetherness(rooms, nearest, iterations):
	N = len(rooms)-1
	result = rooms
	for _ in range(0, iterations):
		r1 = randint(0,N)
		r1_near = [result[r] for r in nearest[r1]]
		r2 = randint(0,N)
		r2_near = [result[r] for r in nearest[r2]]
		previous_score = score(rooms[r1], r1_near)+score(rooms[r2], r2_near)
		new_score = score(rooms[r1], r2_near)+score(rooms[r2], r1_near)
		if new_score>previous_score:
			result[r1].biome, result[r2].biome = result[r2].biome, result[r1].biome
	return result

def main(rooms):
	logger = getLogger('Togetherness')

	logger.info("Calculating nearest neighbours dictionary")
	nearest = nearest_dict(5, rooms)

	logger.info("Applying %s iterations of Togetherness"%len(rooms)**2)
	rooms = togetherness(rooms, nearest,len(rooms)**2)
	return rooms