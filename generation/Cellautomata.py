from numpy import pad, array
from logging import info, getLogger

map = None
output_map = None
def remove_stray_hallways(i,j):
	global map
	if map[i,j]==1:
		neighbours = [map[i-1,j],map[i+1,j],map[i,j-1],map[i,j+1]]
		# remove stray hallways
		if (neighbours.count(0)+neighbours.count(5) == 3 and neighbours.count(1) == 1) or (neighbours.count(0)+neighbours.count(5) == 3 and neighbours.count(2)==1):
			map[i,j] = 5
			remove_stray_hallways(i-1,j)
			remove_stray_hallways(i,j-1)
			remove_stray_hallways(i+1,j)
			remove_stray_hallways(i,j+1)

def add_doors(i,j):
	global map
	if map[i,j]==1:
		neighbours = [map[i-1,j],map[i+1,j],map[i,j-1],map[i,j+1]]
		if (neighbours.count(0)>0 and neighbours.count(2)>0):
			if neighbours.count(4)+neighbours.count(6)==0:
				map[i,j] = 4
			else:
				map[i,j] = 6

def get_mold(i,j):
	global output_map
	if map[i,j]==0:
		if map[i-1,j]!=0 or map[i+1,j]!=0 or map[i,j-1]!=0 or map[i,j+1]!=0:
			output_map[i,j] = 2

def main(input_map):
	logger = getLogger('Cellautomata')
	# input: empty = 0, hallway = 1, room/hub = 2
	global map, output_map
	# add borders
	map = pad(input_map,1,'constant')

	logger.info("Removing stray hallways")
	for i in range(1,len(map)-1):
		for j in range(1,len(map[0])-1):
			remove_stray_hallways(i,j)# hallway to remove = 5
	
	logger.info("Adding doors")
	for i in range(1,len(map)-1):
		for j in range(1,len(map[0])-1):
			add_doors(i,j)

	logger.info("Replacing cellautomata values")
	map[map==5] = 0
	map[map==6] = 1
	output_map = array(map, copy=True)
	output_map[output_map==2] = 0

	logger.info("Getting mold")
	for i in range(1,len(map)-1):
		for j in range(1,len(map[0])-1):
			get_mold(i,j)
	output_map[output_map==3] = 0
	output_map[output_map==4] = 3
	# remove borders
	return output_map[1:-1,1:-1]