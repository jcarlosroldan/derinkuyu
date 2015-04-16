from argparse import Action, ArgumentParser
from os.path import isdir
from os import access, R_OK
from logging import debug, info, warning, error, basicConfig, DEBUG
from datetime import datetime
import BSPTree, Cellautomata, RoomJoiner, Togetherness, BiomeSwitch

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

parser=ArgumentParser(description='Generates a map.')
parser.add_argument('-n','--nplayers',type=int,default=4,action=check_range(0,80,False,True),help='Number of players.')
parser.add_argument('-p','--path',type=str,required=True,action=CheckDirectory,help='Path where the map will be stored.')
parser.add_argument('-s','--seed',type=int,default=None,help='Generated room seed.')

arguments=parser.parse_args()
basicConfig(filename='./logs/%s'%datetime.now().strftime('%Y-%m-%d.txt'),level=DEBUG,format='%(asctime)s\t%(name)s\t%(message)s')

(rooms, map) = BSPTree.main(arguments.nplayers, arguments.seed)
map = Cellautomata.main(map)
rooms = Togetherness.main(RoomJoiner.main(rooms))
(rooms, map) = BiomeSwitch.main(rooms, map)