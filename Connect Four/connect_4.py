#!/usr/bin/env python

###############################################################################
# File:   connect_4.py
# Author: Norman Cunningham
# Class:  CIS 343
# Task:   Project 4
#
# Description: A basic command line version of connect four in python. The 
#              the objective was to gain familiarity with python and the use of
#			   lambda functions. This program uses recursion for various tasks
#			   which was choosen to illistrate the power of the lambda 
#			   capabilities, and sheer code length reduction.
#
# Note: Ran and tested on windows and linux. Currently set for linux, but can be
#		set for windows by changing the clear_console() lambda to 'cls'. Also,
#		testing on windows with a board size of 1000 by 1000 will take forever
#		print, eos was much faster.
#
###############################################################################


import errno
import getopt
import itertools
import os
import pickle
import sys
import time
 

###############################################################################
# Function: parse_args
# 
# Parse the command line arguments to deterime how variables should be
# initialized.
#
# @return (width)   Type: int     -The number of columns for the game board.
# @return (height)  Type: int     -The number of rows for the game board.
# @return (connect) Type: int     -The number of pieces in a row needed to win.
# @return (load)    Type: Boolean -Decision to load a previous game or not.
###############################################################################
def parse_args():

	# Temp Variables
	width = None
	height = None
	square = None
	connect = None
	load = False

	# Store the arguments.
	options, remainder = getopt.getopt(sys.argv[1:], 'w:h:s:c:l', ['width=', 
	                                                         	   'height=',
	                                                         	   'square=',
	                                                         	   'connect=',
	                                                         	   'load', 
	                                                         	   'help'
	                                                         ])

	# Loop through arguments, assign as found.
	for opt, arg in options:
	    if opt in ('-w', '--width'):
	        width = int(arg)
	    elif opt in ('-h', '--height'):
	        height = int(arg)
	    elif opt in ('-s', '--square'):
	        square = int(arg)
	    elif opt in ('-c', '--connect'):
	        connect = int(arg)
	    elif opt in ('-l', '--load'):
	        load = True
	    elif opt == '--help':
			print "\nconnect_4.py [-SHORT || --FULL]\n"
			print "--FULL----SHORT--------DESCRIPTION----------"
			print "width       w     The width of the game board."
			print "height      h     The height of the game board."
			print "square      s     Sets width and height."
			print "connect     c     The connect length to win."
			print "load        l     Load previous game."
			sys.exit()


	# Case 1: Invalid use of 'load', additional arguments present.
	if load is True and (width != None or height != None or square != None or connect != None):
			print "Cannot load a game and set parameters\n"
			sys.exit()

	# Case 2: Valid use of 'load'.
	elif load is True:
		width = 1
		height = 1

	# Case 3: 'Load' not specified.
	else:

		# Invalid use of 'square', specified with 'width'/'height'.
		if (width != None or height != None) and square != None:
			print "Cannot set square and width/height\n"
			sys.exit()

		# Valid use of 'square'.
		if square != None and square > 0:
			width = square
			height = square

		# Valid use of 'square' with an invalid value.
		elif square != None and square <= 0:
			print "Cannot use square argument with value less than one\n"
			sys.exit()

		# 'Square' was not specified, set 'width' and 'height' accordingly.
		else:
			if width is None:
				width = 7
			elif width < 1:
				print "Cannot use width argument with value less than one\n"
				sys.exit()
			if height is None:
				height = 7;
			elif height < 1:
				print "Cannot use height argument with value less than one\n"
				sys.exit()

		# 'Connect' was not specified, set default.
		if connect is None:
			connect = 4

		# 'Connect' was specified but with an invalid value.
		elif connect < 1:
			print "Cannot use connect argument with value less than one\n"
			sys.exit()

		# Check that win condition is possible given board sizing.
		if ((width < connect) and (height < connect)):
			print "Connect length makes for unwinnable game\n"
			sys.exit()

	# End of parsing command line arguments.
	return width, height, connect, load


###############################################################################
# Function: print_board
#
# Displays a simple GUI grid of the game board using '-' and '|' characters, 
# also displays curently placed game pieces in their respective positions.
#
# @params (board) Type: list  -The list that contains the game board positions.
# @params (cols)  Type: int   -The number of columns for the game board.
# @return (None)  Type: None  -Default return, unused.
###############################################################################
def print_board(board, cols):

	# Set up lambda that prints a horizontal line of '-' characters.
	lineLen = (cols * 2) + 1
	line = ['-'] * lineLen
	print_line = lambda x: sys.stdout.write('\n' + ''.join(map(str, x)) + '\n')
	
	# Loop to print every position of the board
	i = 0
	for item in board:

		# Once we reach the end of a column, print a new line below it.
		if i % cols == 0:
			
			print_line(line)
			sys.stdout.write('|')

		sys.stdout.write(item)
		sys.stdout.write('|')
		i = i + 1

	print_line(line)

	return None


###############################################################################
# Function: print_numbering
#
# Displays the numbering positions beneath the game board.
#
# @params (cols)  Type: int   -The number of columns for the game board.
# @return (None)  Type: None  -Default return, unused.
###############################################################################
def print_numbering(cols):

	# Create a temporary list to hold the values from 1 to the number of columns.
	tempList = [' '] * cols
	for i in range(0, cols):

		tempList[i] = str(i+1)

	# Iterate through the list such that it numbers the values vertically 
	# instead of horizontally.
	for i in itertools.izip_longest(*tempList, fillvalue=" "):

		if any(j != " " for j in i):

			print " " + " ".join(i)

	return None


###############################################################################
# Function: save_game
#
# Saves the game state to file.
#
# @return (None)      Type: None    -Default return, unused.
###############################################################################
def save_game(saveData):

	# Write saveData to file using pickle.
	fileObject = open(fileName, 'wb')
	pickle.dump(saveData, fileObject)
	fileObject.close()

	return None


###############################################################################
# Function: load_game
#
# Loads the game state from file. File format is specified in return descriptions.
#
# @params (fileName)    Type: string -The name of the file to save to.
# @return (saveData[0]) Type: list   -The game board.
# @return (saveData[1]) Type: int    -The number of columns for the game board.
# @return (saveData[2]) Type: int    -The number of rows for the game board.
# @return (saveData[3]) Type: int    -The number of pieces in a row needed to win.
# @return (saveData[4]) Type: tuple  -The players, being 'X' or 'O'.
###############################################################################
def load_game(fileName):

	# Read in saveData from file using pickle.
	fileObject = open(fileName, 'r')
	saveData = pickle.load(fileObject)
	fileObject.close()

	return saveData[0], saveData[1], saveData[2], saveData[3], saveData[4]


###############################################################################
# Function: check_win_pro
#
# Checks to see if a winning game condition was met. Uses a recursive lambda
# that takes options for every case. Options are defined below. 
# The lambda itself returns the number of times it encountered the players piece.
#
# ------------------------------------------------------------------
# | Condition to check     | Acronym | found | incr |     jump     |  
# |------------------------|---------|-------|------|--------------|
# | Vertical Downwards     |    vd   |   0   |   0  |     cols     |
# | Horizontal Left        |    hl   |   0   |  -1  |      -1      |
# | Horizontal Right       |    hr   |   0   |   1  |       1      |
# | Diagonal Bottom Left   |   dbl   |   0   |  -1  |   cols - 1   |
# | Diagonal Bottom Right  |   dbr   |   0   |   1  |   cols + 1   |
# | Diagonal Upper Left    |   dul   |   0   |  -1  | -(cols + 1)  |
# | Diagonal Upper Right   |   dur   |   0   |   1  | -(cols - 1)  |                    
# ------------------------------------------------------------------
# 
# LambdaParam (found) - The number of times it encountered the player piece.
# LambdaParam (incr)  - Determines direction of boundary checking.
#					  		  0 = Vertical.
#					         -1 = Left.
#					          1 = Right.
# LambdaParam (jump)  - The incrementing value used to set the next position.
#
# Notice: The use of the lambda can only check in one direction at a time, thus
#		  to check a full diagonal or horizontal line it must be used twice with
#         the appropriate inputs. Also, because it is used twice the combined
#         result of the two uses should be subtracted by one. This being that 
#         the original passed in possition will be counted twice. 
#
# @params (board)     Type: list -The game board.
# @params (cols)      Type: int  -The number of columns for the game board.
# @params (position)  Type: int  -The position of the last piece placed.
# @params (player)    Type: char -The current player.
# @params (winLength) Type: int  -The number of pieces in a row needed to win.
# @params (command)   Type: int  -The user selected column.
# @return (True)      Type: bool  -A win condition was met, the game is over.
# @return (False)     Type: bool  -A win condition was not met, the game is not over.
###############################################################################
def check_win_pro(board, cols, position, player, winLength, command):
	
	# Lambda construction.
	check_w = (lambda board, cols, pos, player, cmd, found, incr, jump: 
		check_w (board, cols, pos+jump, player, cmd+incr, found+1, incr, jump)
		if  ((pos)  <   len(board)) and 
			((pos)  >   -1)         and
			((cmd)  >   -1)         and
			((cmd)  <   cols)       and
			(board[pos]  ==  player) 
		else found)

	# Run through all conditions, store into appropriate acronym.
	vd  = check_w(board, cols, position, player, command, 0,  0,      cols)
	hl  = check_w(board, cols, position, player, command, 0, -1,        -1)
	hr  = check_w(board, cols, position, player, command, 0,  1,         1)
	dbl = check_w(board, cols, position, player, command, 0, -1,    cols-1)
	dbr = check_w(board, cols, position, player, command, 0,  1,    cols+1)
	dul = check_w(board, cols, position, player, command, 0, -1, -(cols+1))
	dur = check_w(board, cols, position, player, command, 0,  1, -(cols-1))
	
	# Combine cases that require two runs.
	h  = (hl  + hr)  - 1  # Horizontal.
	df = (dbl + dur) - 1  # Diagonal Forwards ( / ).
	db = (dul + dbr) - 1  # Diagonal Backwards ( \ ).

	# Check if a win condition was met.
	if vd >= winLength or h  >= winLength or df >= winLength or db >= winLength:
		return True

	# Default return, no win conditions met.
	return False


###############################################################################
#
# Main Game Flow
#
###############################################################################

# Set the limit of recursion to accept testing of a (max) 1000 by 1000 game board.
sys.setrecursionlimit(1001)

# The name of the save file.
fileName = 'save_file.txt'

# Arguments for os.open.
flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY

# Create the save file if it does not exist. 
try:
    file_handle = os.open(fileName, flags)

except OSError as e:
	# The file already exists.
    if e.errno == errno.EEXIST:  
        pass

    # An error occurred.
    else:  
    	print "Error with savefile"
        sys.exit()

###################
#    Variables    #
###################

# Was the last user entry valid or not.
errorMessage = False

# Holds the users input.
command = None

# Holds the previous command value.
prevCMD = None

# Player types.
player = ('X', 'O')

# The number of columns for the game board.
cols = None

# The number of rows for the game board.
rows = None

# The number of pieces that need to be in a sequence to win the game.
winLength = None

# The list that contains the game board positions.
board = []

# The position of where the last piece was placed.
position = None

# Boolean for if the game is over.
gameOver = None


###################
#     Lambdas     #
###################

# Clears the console screen.
clear_console = lambda: os.system('clear')

# Swaps the players.
change_player = lambda x: (x[1], x[0])

# Checks if a string is an integer.
#     Returns: The string as an int, or -1 if the string was not an int.
is_integer = lambda x: (int(x) - 1) if x.isdigit() else None

# Checks if a position is within a range of 0 to specified max.
# 	  Returns: The position, or -1 if the position was out of bounds.
in_range = lambda pos, max: pos if pos > -1 and pos < max else -1

# Checks if a position is valid given the current game board layout.
#     Returns: The position, or -1 if the position was not valid given the 
#			   current game board state.
is_valid = lambda pos, item: pos if item[pos] == ' ' else -1 

# Finds the correct board position to place a peice given a column. Recursively
# calls itself if it is still within the size of the board and has not 
# encountered a taken position.
#     Params: item=board, col=columns, cmd=command, i=incrementer. 
find_position = (lambda item, col, cmd, i: find_position (item, col, cmd, i+1)
	if (cmd+(col*i))<len(item) and item[cmd+(col*i)] == ' ' else cmd+(col*(i-1)))


##########################
#  Initialize Variables  #
##########################

cols, rows, winLength, load = parse_args()

# Load a previous game if specified by command line args.
if load == True:

	# Check that the file is not empty.
	if os.stat(fileName).st_size == 0:

		print "There was no game save to load\n"
		sys.exit()
	
	else:
		board, cols, rows, winLength, player = load_game(fileName)

# Else create a blank board.
else:
	board = [' '] * (cols * rows)


##########################
#     Main Game Loop     #
##########################
while True:

	# Clear the terminal, then print player info, board, and numbering.
	clear_console()
	print "\nCurrent Player: ( " + str(player[0]) + " )\n"
	print_board(board, cols)
	print_numbering(cols)
	print ''

	# Case 1: Error, print error message if we have one.
	if errorMessage is True:

		print "Previous command '"+ prevCMD +"' was invalid, please try again\n"
		errorMessage = False

	# Case 2: save
	elif prevCMD == "save":
		
		# Store game state into saveData.
		saveData = [board, cols, rows, winLength, player]

		save_game(saveData)
		print "The current game state was saved\n"

	# Case 3: load.
	elif prevCMD == "load":

		# Check that the file is not empty.
		if os.stat(fileName).st_size == 0:

			print "There was no game save to load\n"
		
		# The file contained data.
		else:
			
			# Load the game state, print new screen.
			board, cols, rows, winLength, player = load_game(fileName)
			clear_console()
			print "\nCurrent Player: ( " + str(player[0]) + " )\n"
			print_board(board, cols)
			print_numbering(cols)
			print ''
			print "The last saved game state was loaded\n"

	# Case 4: default.
	else:

		print '\n'

	# Print options for user.
	print "Enter a command:"
	print "    - 'quit' to exit"
	print "    - 'save' to save the current game state"
	print "    - 'load' to load the last saved game"
	print "    - The desired column to drop your piece\n"

	# Grab the user input.
	command = raw_input("Command: ")

	# Case A1: quit.
	if command == "quit":

		clear_console()

		# Break the game loop.
		break

	# Case B1: save or load.
	elif command == "save" or command == "load":

		# Set to prevCMD to be executed in the next loop iteration.
		prevCMD = command

	# Case C1: all other possible inputs.
	else:

		# Set prevCMD, used to let user know what they typed if invalid entry.
		prevCMD = command

		# Check that the input was an integer.
		command = is_integer(command)

		# Case A2: the input was an integer.
		if command is not None:

			# Check if the input was a valid entry given the board state.
			command = is_valid(in_range(command, cols), board)
			
			# Case A3: the input was valid given the board state.
			if command is not -1:

				# Find the position where the piece should be put (simulate dropping rows).
				position = find_position(board, cols, command, 1)

				# Set the board at position to the players type.
				board[position] = player[0]

				# Check to see if a win condition was met.
				#gameOver = check_win_pro(board, cols, position, player[0], winLength, command)


				gameOver = check_win_pro(board, cols, position, player[0], winLength, command)


				# Case A4: game is over.
				if (gameOver is True):

					# Reset command, will be used to get user input again.
					command = None

					# Loop until command is 'y' or 'n'.
					while command != "y" and command != "n":

						# Clear the screen, reprint all info.
						clear_console()
						print "\nCurrent Player: ( " + str(player[0]) + " )\n"
						print_board(board, cols)
						print_numbering(cols)
						print "\n\nPlayer ( " + str(player[0]) + " ) Wins!!\n"

						# Print error message for invalid entry.
						if command is not None:
							print "Invalid entry, please enter 'y' or 'n'\n"

						# Grab user input.
						command = raw_input("Would you like to play again? (y/n) : ")

					# Case A5: user input is 'n', exit the game.
					if command == "n":
						clear_console()
						break

					# Case B5: user input is 'y', reset the board.
					else:
						board = [' '] * (cols * rows)

				# Case B4: game is not over.
				else:

					player = change_player(player)

			# Case B3: the input was not valid given the board state.
			else:

				errorMessage = True

		# Case B2: the input was not an integer.
		else:

			errorMessage = True