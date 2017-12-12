from argparse import Action, ArgumentParser
from os.path import isdir
from os import access, R_OK
from logging import debug, info, warning, error, basicConfig, DEBUG, getLogger
from datetime import datetime
import BSPTree, Cellautomata, Togetherness, BiomeRenderer
from numpy import zeros

def check_range(min_value,max_value,min_included=True,max_included=True):
	class CheckRange(Action):
		def __call__(self,parser,namespace,values,option_string=None):
			if (not min_included and values == min_value) or values < min_value or (not max_included and values == max_value) or values > max_value:
				parser.error("%s must be between bigger than %s and smaller than %s"%(option_string,min_value,max_value))
			setattr(namespace,self.dest,values)
	return CheckRange

class CheckDirectory(Action):
	def __call__(self,parser,namespace,values,option_string=None):
		prospective_dir=values
		if not isdir(prospective_dir):
			raise parser.error("%s is not a valid path."%prospective_dir)
		if access(prospective_dir,R_OK):
			setattr(namespace,self.dest,prospective_dir)
		else:
			raise parser.error("%s is not a readable directory."%prospective_dir)
		setattr(namespace,self.dest,values)

from time import time
_tstart_stack = []
def tic():
    _tstart_stack.append(time())
def toc(fmt="Elapsed: %s s"):
    print(fmt % (time() - _tstart_stack.pop()))

parser=ArgumentParser(description='Generates a map.')
parser.add_argument('-n','--nplayers',type=int,default=1,action=check_range(0,80,False,True),help='Number of players.')
parser.add_argument('-p','--path',type=str,default='.',action=CheckDirectory,help='Path where the map will be stored.')
parser.add_argument('-s','--seed',type=int,default=None,help='Generated room seed.')

arguments=parser.parse_args()
basicConfig(filename='./logs/%s'%datetime.now().strftime('%Y-%m-%d.txt'),level=DEBUG,format='%(asctime)s\t%(name)s\t%(message)s')

from PIL import Image
from numpy import amax

logger = getLogger('Main')

(rooms, map) = BSPTree.main(arguments.nplayers, arguments.seed)

logger.info("Saving BSPTree.png")
im = Image.fromarray(255*(map/amax(map))).convert('RGB')
im.save(arguments.path+"/BSPTree.png")

map = Cellautomata.main(map)

logger.info("Saving Cellautomata.png")
im = Image.fromarray(255*(map/amax(map))).convert('RGB')
im.save(arguments.path+"/Cellautomata.png")

rooms = Togetherness.main(rooms)

logger.info("Saving Togetherness.png")
arr = zeros((len(map),len(map)))
for room in rooms:
	arr[room.y:room.y+room.h,room.x:room.x+room.w] = room.biome+1
im = Image.fromarray(255*(arr/amax(arr))).convert('RGB')
im.save("./Togetherness.png")

final_map = BiomeRenderer.main(rooms, map)