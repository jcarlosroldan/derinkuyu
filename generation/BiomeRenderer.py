from logging import info, getLogger

def fix_map(rooms):
	# at least 1 room of each biome
	# add events to the rooms (fixed proportion, at least one of each)
	return rooms

def generate_rooms(rooms, map):
	pass

def main(input_rooms, input_map):
	logger = getLogger("BiomeRenderer")
	logger.info("Fixing map constraints")
	rooms = fix_map(input_rooms)
	logger.info("Generating rooms")
	final_map = generate_rooms(rooms, input_map)
	return final_map # 3 arrays, first one with blocks, second one with biomes, third one with difficulty