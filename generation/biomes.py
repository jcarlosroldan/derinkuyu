from noise import snoise3
from numpy import zeros, uint8, amin, amax, array, histogram
from PIL import Image
from math import sqrt
from time import time
from matplotlib import pyplot

class Biome:
	colors = [[186,187,170],[174,143,112],[240,144,24],[29,125,23],[158,136,0],[35,122,186],[73,215,226],[51,2,45],[115,154,157],[198,20,0]]
	biomes = [[3,3,3,5,5,5,5,5,5,6,6],
			  [3,3,3,5,5,5,5,4,5,6,6],
			  [3,3,4,4,4,4,4,4,4,6,6],
			  [3,2,3,4,4,4,1,1,1,6,7],
			  [2,2,2,4,4,1,1,1,0,7,7],
			  [2,2,2,2,1,1,1,0,0,7,7],
			  [8,2,2,1,1,1,0,0,0,7,7],
			  [8,2,2,1,1,0,0,0,0,7,7],
			  [8,2,2,1,1,0,0,0,0,7,7],
			  [8,8,2,1,1,0,0,0,7,7,7],
			  [8,8,2,1,0,0,0,0,7,7,7]]
	matches = zeros((11,11),dtype=int)
	def __init__(self, width, height, seed=time(), octaves = 6, frequency = 16.):
		self.seed = seed
		self.octaves = octaves
		self.frequency = frequency*octaves
		self.width = width
		self.height = height
		self.array = zeros((width,height,3),dtype=uint8)
	def generate(self):
		temperature = zeros((self.width,self.height))
		humidity = zeros((self.width,self.height))
		for y in range(self.height):
			for x in range(self.width):
				temperature[x,y] = int(6+18*(snoise3(x/self.frequency, y/self.frequency, self.seed, self.octaves)/2))
				humidity[x,y] = int(6+18*(snoise3(x/self.frequency, y/self.frequency, self.seed+100000, self.octaves)/2))-1
		print(amax(temperature))
		print(amin(temperature))
		temperature = self.linear_expansion(temperature,10)

		humidity = self.linear_expansion(humidity,10)
		h = histogram(temperature)[0]
		pyplot.plot(h)
		pyplot.show()
		for y in range(self.height):
			for x in range(self.width):
				h=int(humidity[x,y])
				t=int(temperature[x,y])
				self.matches[h,t]+=1
				self.array[x,y] = self.colors[self.biomes[h][t]]
	def linear_expansion(self,arr,max_value):
		arr_min = amin(arr)
		arr_max = amax(arr)
		return array((arr-arr_min)*max_value/(arr_max-arr_min))
	def draw(self):
		im = Image.fromarray(self.array,'RGB')
		Image.fromarray(255*self.matches/amax(self.matches)).show()
		im.save("res.png")

def main():
	MAP_WIDTH = 500
	biome = Biome(MAP_WIDTH, MAP_WIDTH,1)
	biome.generate()

	print(biome.matches)
	biome.draw()

if __name__ == '__main__':
	main()