import pygame
from pygame.locals import *
import random
import os
import time
import neat
import pickle
pygame.init()
pygame.font.init()  # init font

WIN_WIDTH = 1200
WIN_HEIGHT = 800
NUM_COLS = 7
NUM_ROWS = 6
FLOOR = 730
STAT_FONT = pygame.font.SysFont("comicsans", 50)
END_FONT = pygame.font.SysFont("comicsans", 70)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
BLACK = (0,0,0)
BLUE = (87,155,252)
RADIUS = 50
MARGIN = 50
gen = 0
playPC = False


class Game:
	def __init__(self, x=0, y=0):
		self.x = x
		self.y = y
	    
		self.frame = Rect(MARGIN/2, MARGIN/2, WIN_WIDTH-MARGIN, WIN_HEIGHT-MARGIN)

	def draw(self, win):
		"""
		draw both the top and bottom of the pipe
		:param win: pygame window/surface
		:return: None
		"""
		pygame.draw.rect(win, BLUE, self.frame)
		win.blit(win, (self.x, self.y))

class Move:
	def __init__(self, col, row):
		self.row = row
		self.col = col
		self.pt = (col, row)
		#		(0, 0) -> ()
		self.y = MARGIN//2+RADIUS + (self.row*(WIN_HEIGHT-MARGIN//2)//6)
		self.x = MARGIN+RADIUS + (self.col*WIN_WIDTH//8)
		self.active = False
		self.color = RED if self.active else WHITE

	def draw(self, win):
		pygame.draw.circle(win, self.color, (self.x, self.y), RADIUS)

	def setActive(self, state, color):
		self.active = state
		self.color = color

class Board:
	def __init__(self):
		self.moves = []
		self.color = None
		for col in range(NUM_COLS):
			cols = []
			for row in range(NUM_ROWS):
				cols.append(Move(col, row))
			self.moves.append(cols)

	def reset(self):
		self.moves = []
		for col in range(NUM_COLS):
			cols = []
			for row in range(NUM_ROWS):
				cols.append(Move(col, row))
			self.moves.append(cols)

	def draw(self, win):
		for col in self.moves:
			for move in col:
				move.draw(win)

	def move(self, col, row, state, color):
		if self.isValidMove(col, row):
			name = "BLACK" if color == BLACK else "RED"
			# print(f"{name} moves ({col}, {row})")
			self.moves[col][row].setActive(state, color)
			return True
		return False

	def getMoves(self):
		moves = []
		for col in self.moves:
			for move in col:
				if not move.active:
					moves.append(0)
				elif move.color == "RED":
					moves.append(1)
				elif move.color == "BLACK":
					moves.append(-1)
		return tuple(moves)

	def isValidMove(self, col, row):
		if self.moves[col][row].active: #first check if slot is available
			return False
		for i in range(row+1, len(self.moves[col])): #then check if all slots underneath are filled
			# print(self.moves[col][i].pt)
			if not self.moves[col][i].active:
				return False
		return True

	def getValidMoves(self):
		validMoves = []
		for col in range(NUM_COLS-1, -1, -1):
			for row in range(NUM_ROWS-1, -1, -1):
				if self.isValidMove(col, row):
					validMoves.append((col, row))
					if len(validMoves) == NUM_COLS:
						return validMoves
					break
		if not validMoves:
			# print("Draw")
			return False
		return validMoves

	def updateValidMoves(self):
		pass

	def isGameOver(self, col, row, color):
		#check horizontal
		count = 0
		for offset in range(-NUM_COLS, NUM_COLS):
			if count == 4:
				return True

			cOffset = (row+offset)
			if cOffset < 0 or cOffset > NUM_COLS-1:
				continue

			if self.moves[cOffset][row].active and self.moves[cOffset][row].color == color:
				count += 1
			else:
				count = 0

		#check vertical
		count = 0
		for offset in range(-NUM_ROWS, NUM_ROWS):
			if count == 4:
				return True

			rOffset = (row+offset)
			if rOffset < 0 or rOffset > NUM_ROWS-1:
				continue

			if self.moves[col][rOffset].active and self.moves[col][rOffset].color == color:
				count += 1
			else:
				count = 0

		#check positive diagonal /
		count = 0
		for offset in range(-4, 5):
			if count == 4:
				return True
						#min(6, max(0, 0+0)), min(5, max(0, 5-1))
			offsetFix = (col+offset, row-offset)
			if offsetFix[0] < 0 or offsetFix[0] > NUM_COLS-1 or offsetFix[1] < 0 or offsetFix[1] > NUM_ROWS-1:
				continue
			# print(offsetFix)
			if self.moves[offsetFix[0]][offsetFix[1]].active and self.moves[offsetFix[0]][offsetFix[1]].color == color:
				count += 1
			else:
				count = 0

		#check negative diagonal \
		count = 0
		for offset in range(-4, 5):
			if count == 4:
				return True
						#min(6, max(0, 0+0)), min(5, max(0, 5-1))
			offsetFix = (col+offset, row-offset)
			if offsetFix[0] < 0 or offsetFix[0] > NUM_COLS-1 or offsetFix[1] < 0 or offsetFix[1] > NUM_ROWS-1:
				continue
			# print(offsetFix)
			if self.moves[offsetFix[0]][offsetFix[1]].active and self.moves[offsetFix[0]][offsetFix[1]].color == color:
				count += 1
			else:
				count = 0

	def getCol(self, pos):
		offset = 75
		for i in range(len(self.moves)):
			if pos[0] < self.moves[i][0].x+offset:
				return i

	def setWinner(self, color):
		self.winner = color

class Player:
	def __init__(self, color):
		self.color = color
		self.name = "BLACK" if color == BLACK else "RED"

	def move(self, board, col, row):
		board.move(col, row, True, self.color)
		# draw_window(WIN, gen, game, board)
		if board.isGameOver(col, row, self.color):
			board.setWinner(self.color)
			# print(f"{self.color} wins!")
			return True
		return False


def draw_window(win, gen, game, board):
	"""
	draws the windows for the main game loop
	:param win: pygame window surface
	:param bird: a Bird object
	:param pipes: List of pipes
	:param score: score of the game (int)
	:param gen: current generation
	:param pipe_ind: index of closest pipe
	:return: None
	"""
	win.fill((255,255,255))

	# generations

	game.draw(win)
	board.draw(win)
	score_label = STAT_FONT.render("Gens: " + str(gen-1),1,(0,0,0))
	win.blit(score_label, (10, 10))
	pygame.display.update()


# run = True
# game = Game()
# board = Board()

# player1 = Player(RED)
# player2 = Player(BLACK)
# board.move(6, 5, True)
flip = True


def play():
	global flip
	if flip:
		validMoves = board.getValidMoves()
		if validMoves:
			col, row = random.choice(validMoves)
		if not validMoves or player1.move(board, col, row):
			return False
		flip = not flip
	else:
		validMoves = board.getValidMoves()
		if validMoves:
			col, row = random.choice(validMoves)
		if not validMoves or player2.move(board, col, row):
			return False
		flip = not flip
	return True

def playComputer(board, players):
	global flip, playPC
	net = pickle.load(open("best.pickle", "rb"))
	playPC = True
	run = True
	clock = pygame.time.Clock()
	while run:
		clock.tick(5)
		if flip:
			validMoves = board.getValidMoves()
			if validMoves:
				###
				output = net.activate(board.getMoves())
				outputMaxIndex = output.index(max(output))
				#pick column based on index of output
				if len(validMoves) == 7:
					for move in validMoves:
						if move[0] == outputMaxIndex:
							col, row = move
							break
					
				else:
					while outputMaxIndex not in [z[0] for z in validMoves]:
						if outputMaxIndex == 0:
							outputMaxIndex = NUM_COLS
						outputMaxIndex -= 1
					for move in validMoves:
						if move[0] == outputMaxIndex:
							col, row = move
							break



			if not validMoves:
				board.reset()
				run = False
			result = players[0].move(board, col, row)
			if result:
				board.reset()
				run = False

			flip = not flip
		else:
			run2 = True
			while run2:
				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						run = False
						pygame.quit()
						quit()
						break
					elif event.type == pygame.MOUSEBUTTONUP:
						pos = pygame.mouse.get_pos()
						clickedColumn = board.getCol(pos)
						# print(clickedColumn)
						#if available move at the column
						for move in board.getValidMoves():
							if move[0] == clickedColumn:
								#play it
								if players[1].move(board, move[0], move[1]):
									board.reset()
									run = False
								run2 = False
								break

			flip = not flip
						# run = False

		
		draw_window(WIN, gen, game, board)
	# return True
	playComputer(board, players)


#########AI STUFF#######

def eval_genomes(genomes, config):
	"""
	runs the simulation of the current population of
	birds and sets their fitness based on the distance they
	reach in the game.
	"""
	global WIN, gen
	win = WIN
	gen += 1

	# start by creating lists holding the genome itself, the
	# neural network associated with the genome and the
	# bird object that uses that network to play
	nets = []
	players = []
	ge = []
	FLIP = True


	board = Board()
	for genome_id, genome in genomes:
		genome.fitness = 0  # start with fitness level of 0
		net = neat.nn.FeedForwardNetwork.create(genome, config)
		nets.append(net)
		if FLIP:
			players.append(Player("BLACK"))
			FLIP = not FLIP
		else:
			players.append(Player("RED"))
			FLIP = not FLIP
		ge.append(genome)

	clock = pygame.time.Clock()
	run = True
	print("RUNNING")
	while run:
		clock.tick(600)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				pygame.quit()
				quit()
				break
			# elif event.type == pygame.MOUSEBUTTONUP or playPC:
			# 	playComputer(board, players)

		for x, player in enumerate(players):
			validMoves = board.getValidMoves()
			if validMoves:
				output = nets[players.index(player)].activate(board.getMoves())
				if output[0] > 0.75:  # we use a tanh activation function so result will be between -1 and 1. if over 0.5 jump
					col, row = validMoves[0]
				elif output[0] > 0.5 and len(validMoves) > 1:
					col, row = validMoves[1]
				elif output[0] > 0.25 and len(validMoves) > 2:
					col, row = validMoves[2]
				elif output[0] > 0 and len(validMoves) > 3:
					col, row = validMoves[3]
				elif output[0] > -0.25 and len(validMoves) > 4:
					col, row = validMoves[4]
				elif output[0] > -0.5 and len(validMoves) > 5:
					col, row = validMoves[5]
				elif output[0] > -0.75 and len(validMoves) > 6:
					col, row = validMoves[6]
				else:
					col, row = random.choice(validMoves)
			# print(validMoves)
			# print(col, row)
			if not validMoves:
				ge[x].fitness -= .1
				board.reset()
				return
			result = player.move(board, col, row)
			if result:
				ge[x].fitness += 1
				board.reset()
				pickle.dump(nets[0],open("best.pickle", "wb"))
				return
			# flip = not flip

		# draw_window(WIN, gen, game, board)

		# break if score gets large enough
		# if score > 20:
		# 	pickle.dump(nets[0],open("best.pickle", "wb"))
		# 	break


def eval_multiple_genomes(genomes, config):
	"""
	runs the simulation of the current population of
	birds and sets their fitness based on the distance they
	reach in the game.
	"""

	# start by creating lists holding the genome itself, the
	# neural network associated with the genome and the
	# bird object that uses that network to play
	nets = []
	players = []
	ge = []
	boards = []
	for genome_id, genome in genomes:
		genome.fitness = 0  # start with fitness level of 0
		net = neat.nn.FeedForwardNetwork.create(genome, config)
		nets.append(net)
		players.append((Player("RED"), Player("BLACK")))
		boards.append(Board())
		ge.append(genome)
	clock = pygame.time.Clock()
	count = 0
	# if True:
		
	# for i in range(10): #play 10 games each

	
		# elif event.type == pygame.MOUSEBUTTONUP or playPC:
		# 	playComputer(board, players)
	lastNet = False
	for x, playerTuple in enumerate(players):
		try:
			lastNet = random.choice(nets)
		except:
			pass
		ge[x].fitness -= 1
		boards[x].reset()

		run = True
		while run:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					run = False
					pygame.quit()
					quit()
					break
			for y, player in enumerate(playerTuple):
				validMoves = boards[x].getValidMoves()
				if validMoves:
					if y == 0: #make player 1 train to git good
						# ge[x].fitness -= .01
						#pick move based on output
						output = nets[x].activate(boards[x].getMoves())
						outputMaxIndex = output.index(max(output))
						#pick column based on index of output
						if len(validMoves) == 7:
							for move in validMoves:
								if move[0] == outputMaxIndex:
									col, row = move
									break
							
						else:
							while outputMaxIndex not in [z[0] for z in validMoves]:
								if outputMaxIndex == 0:
									outputMaxIndex = NUM_COLS
								outputMaxIndex -= 1
							for move in validMoves:
								if move[0] == outputMaxIndex:
									col, row = move
									break
					elif lastNet:
						# ge[x].fitness -= .01
						#pick move based on output
						output = lastNet.activate(boards[x].getMoves())
						outputMaxIndex = output.index(max(output))
						#pick column based on index of output
						if len(validMoves) == 7:
							for move in validMoves:
								if move[0] == outputMaxIndex:
									col, row = move
									break
							
						else:
							while outputMaxIndex not in [z[0] for z in validMoves]:
								if outputMaxIndex == 0:
									outputMaxIndex = NUM_COLS
								outputMaxIndex -= 1
							for move in validMoves:
								if move[0] == outputMaxIndex:
									col, row = move
									break

					else: #make player 2 play randomly
						col, row = random.choice(validMoves)


				else: #if not validMoves:
					count += 1
					ge[x].fitness -= .1
					boards[x].reset()
					run = False
				result = player.move(boards[x], col, row)
				ge[x].fitness -= .05
				if result:
					if boards[x].winner == player.color:
						ge[x].fitness += 2
					count += 1
					boards[x].reset()
					pickle.dump(nets[0],open("best.pickle", "wb"))
					run = False
		# flip = not flip

				# draw_window(WIN, gen, game, boards[x])

def run(config_file):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
    :return: None
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    #p.add_reporter(neat.Checkpointer(5))

    # Run for up to 50 generations.
    winner = p.run(eval_multiple_genomes, 1000)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
	local_dir = os.path.dirname(__file__)
	config_path = os.path.join(local_dir, 'config-feedforward.txt')
	# run(config_path) #trainer

	#play against computer
	WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
	pygame.display.set_caption("Connect-4!")
	game = Game()
	playComputer(Board(), [Player("RED"), Player("BLACK")])