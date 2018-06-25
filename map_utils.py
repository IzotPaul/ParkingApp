from map_defines import *
from map_db import *
import queue as Queue

def mouse_press(event, grid):

	start_tile = [int(x) for x in event.widget.cget("text").split(" ")
							if x.strip()]
	active_tile = [int(x) for x in event.widget.cget("text").split(" ")
							if x.strip()]

	grid.start_tile = start_tile
	grid.active_tile = active_tile

	# Depending on the mode, modify the first tile immediately on mouse press
	if (grid.mode == PARK_SPOT):
		grid.mark_spot(
				 (start_tile[0], active_tile[0], start_tile[1], active_tile[1]),
				  grid.mode)
	elif (grid.mode == STREET):
		grid.draw_street((start_tile[0], start_tile[1]))
	elif (grid.mode == EMPTY):
		grid.place_obstacle( 
				(start_tile[0], active_tile[0], start_tile[1], active_tile[1]))

def mouse_release(event, grid):
	start_tile = grid.start_tile
	active_tile = grid.active_tile

	current_spot = order_axes(start_tile[0], active_tile[0], 
							  start_tile[1], active_tile[1])
	grid.check_spot(current_spot)

	del grid.street_line[:]
	for x in range(grid.max_x):
		for y in range(grid.max_y):
			grid.tiles[x][y].color = grid.tiles[x][y].button.cget("bg")
			grid.tiles[x][y].image = grid.textures[
				int(grid.tiles[x][y].button.cget("image")[7:]) - 1]

def mouse_over(event, grid):
	widget = grid.root.winfo_containing(event.x_root, event.y_root)
	current_tile = [int(x) for x in widget.cget("text").split(" ") if x.strip()]

	# Check current's tile position and only continue if the user moved the
	# mouse in another tile
	if (grid.active_tile == current_tile):
		return
	grid.active_tile = current_tile
	start_tile = grid.start_tile
	active_tile = grid.active_tile

	for x in range(grid.max_x):
		for y in range(grid.max_y):
			grid.tiles[x][y].button.configure(activebackground=grid.tiles[x][y].color)
			grid.tiles[x][y].button.configure(bg=grid.tiles[x][y].color)
			grid.tiles[x][y].button.configure(image=grid.tiles[x][y].image)


	if (grid.mode == PARK_SPOT):
		position = order_axes(start_tile[0], active_tile[0], 
							  start_tile[1], active_tile[1])
		grid.mark_spot(position, grid.mode)
	elif (grid.mode == STREET):
		grid.draw_street((active_tile[0], active_tile[1]))
	elif (grid.mode == EMPTY):
		position = order_axes(start_tile[0], active_tile[0], 
							  start_tile[1], active_tile[1])
		grid.place_obstacle(position)

def ignore_input(event):
	pass

class Grid_tile:

	def __init__(self, button, color, image, index, owner):
		self.button = button
		self.color = color
		self.image = image
		self.owner = owner
		self.index = index


class Grid:

	def __init__(self, frame1, frame2, error, root):
		self.max_x = 0
		self.max_y = 0
		self.root = root
		self.mode = EMPTY
		self.frame = frame1
		self.other_frame = frame2
		self.error = error
		self.textures = init_imgs()

		self.street_line = []
		self.park_spots = []
		self.avail = {}

		self.start_tile = (-1, -1)
		self.active_tile = (-1, -1)

	def generate_grid(self, max_x, max_y,):
		self.max_x = max_x
		self.max_y = max_y
		self.tiles = [[0 for y in range(max_y)] for x in range(max_x)]

		if (self.max_x * self.max_y <= 400):
			scale = 30
		else:
			scale = 20

		for x in range(self.max_x):
			for y in range(self.max_y):
				button = Button(self.frame, bd=1, height=scale, width=scale,
						image=self.textures[Void], bg=EMPTY, activebackground=EMPTY,
						text = str(x) + " " + str(y))
				button.grid(row=x, column=y)

				button.bind("<Button-1>", lambda event: mouse_press(event, self))
				button.bind("<ButtonRelease-1>", lambda event: mouse_release(event, self))
				button.bind("<Button1-Motion>", lambda event: mouse_over(event, self))

				self.tiles[x][y] = Grid_tile(button, EMPTY,
									self.textures[Void], NOT_CONNECTED, "")


	def select_mode(self, mode):
		self.mode = mode

	def mark_spot(self, position, color):
		(start_x, end_x, start_y, end_y) = position
		img = self.textures

		# Color each tile
		for x in range(start_x, end_x + 1):
			for y in range(start_y, end_y + 1):
				self.tiles[x][y].button.configure(activebackground=color)
				self.tiles[x][y].button.configure(bg=color)

		# If only one tile, then use FullSquare image
		if (start_x == end_x and start_y == end_y):
			self.tiles[start_x][start_y].button.configure(image=img[FullSquare])
			return

		# If one tile height rectangle (1xN), draw both ends and fill the rest
		if (start_x == end_x):
			self.tiles[start_x][start_y].button.configure(image=img[FullWest])
			self.tiles[end_x][end_y].button.configure(image=img[FullEast])
			for y in range(start_y + 1, end_y):
				self.tiles[start_x][y].button.configure(image=img[Horz])
			return

		# Same proccess for one tile width rectangle (Nx1)
		if (start_y == end_y):
			self.tiles[start_x][start_y].button.configure(image=img[FullNorth])
			self.tiles[end_x][end_y].button.configure(image=img[FullSouth])
			for x in range(start_x + 1, end_x):
				self.tiles[x][start_y].button.configure(image=img[Vert])
			return

		# In this case, the figure is at least a 2x2 sqare. Draw corners first
		self.tiles[start_x][start_y].button.configure(image=img[NorthWest])
		self.tiles[start_x][end_y].button.configure(image=img[NorthEast])
		self.tiles[end_x][start_y].button.configure(image=img[SouthWest])
		self.tiles[end_x][end_y].button.configure(image=img[SouthEast])

		# Fill side and middle tiles (if available)
		for x in range(start_x + 1, end_x):
			self.tiles[x][start_y].button.configure(image=img[West])
			self.tiles[x][end_y].button.configure(image=img[East])
		for y in range(start_y + 1, end_y):
			self.tiles[start_x][y].button.configure(image=img[North])
			self.tiles[end_x][y].button.configure(image=img[South])
		for x in range(start_x + 1, end_x):
			for y in range(start_y + 1, end_y):
				self.tiles[x][y].button.configure(image=img[Void])


	def draw_street(self, tile, redraw=False):
		if not redraw:
			self.street_line.append(tile)

		img = self.textures
		# In case there is only one tile on the street, use no arrow image
		if (len(self.street_line) == 1):
			(active_x, active_y) = self.street_line[0]
			self.tiles[active_x][active_y].button.configure(activebackground=STREET)
			self.tiles[active_x][active_y].button.configure(bg=STREET)
			self.tiles[active_x][active_y].button.configure(image=img[Point])
			return

		# In case the user moves backwards, delete the tiles
		if (len(self.street_line) > 2):
			if (self.street_line[-3] == self.street_line[-1]):
				self.street_line.pop()
				self.street_line.pop()

		# Draw the first tile on the street (by checking only the second tile)
		(x, y) = self.street_line[0]
		(next_x, next_y) = self.street_line[1]
		if (x == next_x + 1):
			self.tiles[x][y].button.configure(image=img[DownToUp])
		if (x == next_x - 1):
			self.tiles[x][y].button.configure(image=img[UpToDown])
		if (y == next_y + 1):
			self.tiles[x][y].button.configure(image=img[RightToLeft])
		if (y == next_y - 1):
			self.tiles[x][y].button.configure(image=img[LeftToRight])

		# Draw the last tile on the street (by checking only the tile before)
		(x, y) = self.street_line[-1]
		(prev_x, prev_y) = self.street_line[-2]
		if (x == prev_x + 1):
			self.tiles[x][y].button.configure(image=img[UpToDown])
		if (x == prev_x - 1):
			self.tiles[x][y].button.configure(image=img[DownToUp])
		if (y == prev_y + 1):
			self.tiles[x][y].button.configure(image=img[LeftToRight])
		if (y == prev_y - 1):
			self.tiles[x][y].button.configure(image=img[RightToLeft])

		# For the rest of the tiles, check both the next and the previous tiles
		for (x, y) in self.street_line[1:-1]:
			idx = self.street_line.index((x, y))
			(prev_x, prev_y) = self.street_line[idx - 1]
			(next_x, next_y) = self.street_line[idx + 1]
			
			if (x == prev_x + 1):
				source = "Up"
			if (x == prev_x - 1):
				source = "Down"
			if (y == prev_y + 1):
				source = "Left"
			if (y == prev_y - 1):
				source = "Right"

			if (x == next_x + 1):
				destination = "Up"
			if (x == next_x - 1):
				destination = "Down"
			if (y == next_y + 1):
				destination = "Left"
			if (y == next_y - 1):
				destination = "Right"

			image_name = source + "To" + destination
			exec("self.tiles[x][y].button.configure(image=img[" + image_name + "])")

		# Color all tiles on the street
		for (x, y) in self.street_line:
			self.tiles[x][y].button.configure(activebackground=STREET)
			self.tiles[x][y].button.configure(bg=STREET)

	def place_obstacle(self, position):
		(start_x, end_x, start_y, end_y) = position
		img = self.textures

		# Color and set default image for all tiles in the 'positions' range
		for x in range(start_x, end_x + 1):
			for y in range(start_y, end_y + 1):
				self.tiles[x][y].button.configure(activebackground=EMPTY)
				self.tiles[x][y].button.configure(bg=EMPTY)
				self.tiles[x][y].button.configure(image=img[Void])

	def check_spot(self, position):

		for spot in self.park_spots[:]:
			(start_x, end_x, start_y, end_y) = position
			(start_x2, end_x2, start_y2, end_y2) = spot

			# For parking spots check overlapping
			if (self.mode == PARK_SPOT or self.mode == EMPTY):
				# Check if it partially overlaps with other parking spots
				if ((start_x2 <= start_x <= end_x2 and
					 start_y2 <= start_y <= end_y2) or
					(start_x2 <= end_x <= end_x2 and
					 start_y2 <= start_y <= end_y2) or
					(start_x2 <= start_x <= end_x2 and
					 start_y2 <= end_y <= end_y2) or
					(start_x2 <= end_x <= end_x2 and
					 start_y2 <= end_y <= end_y2) or
					(start_x <= start_x2 <= end_x and
					 start_x <= end_x2 <= end_x and
					(start_y2 <= start_y <= end_y2 or
					 start_y2 <= end_y <= end_y2)) or
					((start_x2 <= start_x <= end_x2 or
					 start_x2 <= end_x <= end_x2) and
					 start_y <= start_y2 <= end_y and
					 start_y <= end_y2 <= end_y)):
					self.mark_spot(spot, INVALID)
					self.park_spots.remove(spot)
					continue

				# Check if it covers the entire spot
				if (start_x <= start_x2 <= end_x and
					start_x <= end_x2 <= end_x and
					start_y <= start_y2 <= end_y and
					start_y <= end_y2 <= end_y):
					self.park_spots.remove(spot)
					continue

			# For street, check each tile individually
			elif (self.mode == STREET):
				for (x, y) in self.street_line:
					if (start_x2 <= x <= end_x2 and
						start_y2 <= y <= end_y2):
						try:
							self.park_spots.remove(spot)
							self.mark_spot(spot, INVALID)
						except ValueError:
							pass

		# Redraw invalidated tiles
		if (self.mode == PARK_SPOT):
			self.mark_spot(position, PARK_SPOT)
			self.park_spots.append(position)
		elif (self.mode == STREET):
			self.draw_street((0, 0), True)
			pass
		elif (self.mode == EMPTY):
			self.place_obstacle(position)

	def save_grid(self):
		self.error.configure(text="")

		# Check for possible errors: Invalid tiles
		for x in range(self.max_x):
			for y in range(self.max_y):
				if (self.tiles[x][y].button.cget("bg") == INVALID):
					self.error.configure(text="Error: Remove invalid tiles!")
					return

		# Check for street tiles not connected to the exterior
		if (self.street_error_check()):
			self.error.configure(text="Error: Street tiles not connected to the exterior!")
			return

		# Check for parking spots not connected to one of the street tiles
		if (self.park_error_check()):
			self.error.configure(text="Error: Parking spots not connected to street!")
			return

		# Stop all input to map creator
		self.other_frame.destroy()
		for x in range(self.max_x):
			for y in range(self.max_y):
				self.tiles[x][y].button.bind("<Button-1>", ignore_input)
				self.tiles[x][y].button.bind("<ButtonRelease-1>", ignore_input)
				self.tiles[x][y].button.bind("<Button1-Motion>", ignore_input)

		file = open("map.layout", "w")
		file.write(str(self.max_x) + " " + str(self.max_y) + "\n")

		indexes = [[0 for x in range(self.max_y)] for x in range(self.max_x)]

		# First save the indexes in the map.layout file
		for spot in self.park_spots:
			(start_x, end_x, start_y, end_y) = spot

			idx = self.park_spots.index(spot)
			self.avail[idx] = (spot, True)

			for x in range(start_x, end_x + 1):
				for y in range(start_y, end_y + 1):
					self.tiles[x][y].index = idx

		for x in range(self.max_x):
			line = ""
			for y in range(self.max_y):
				if (self.tiles[x][y].button.cget("bg") == PARK_SPOT):
					line += str(self.tiles[x][y].index) + " "
				elif (self.tiles[x][y].button.cget("bg") == STREET):
					line += str(-2) + " "
				elif (self.tiles[x][y].button.cget("bg") == EMPTY):
					line += str(-1) + " "
			file.write(line[:-1] + "\n")

		# Save the images
		for x in range(self.max_x):
			line = ""
			for y in range(self.max_y):
				line += str(int(self.tiles[x][y].button.cget("image")[7:]) - 1)
				line += " "
			file.write(line[:-1] + "\n")

		# Save the colors
		for x in range(self.max_x):
			line = ""
			for y in range(self.max_y):
				line += self.tiles[x][y].button.cget("bg")
				line += " "
			file.write(line[:-1] + "\n")

		file.close()

		self.update_database()

	def street_error_check(self):
		q = Queue.Queue()

		for x in range(self.max_x):
			for y in range(self.max_y):
				if (self.tiles[x][y].index == CONNECTED):
					q.put((x, y))

				if (x == 0 or x == self.max_x - 1 or
					y == 0 or y == self.max_y - 1):
					q.put((x, y))

		while not q.empty():
			(x, y) = q.get()

			self.tiles[x][y].index = CONNECTED

			if (x > 0 and
				self.tiles[x - 1][y].button.cget("bg") == STREET and
				self.tiles[x - 1][y].index == NOT_CONNECTED):
				q.put((x - 1, y))
			if (x < self.max_x - 1 and
				self.tiles[x + 1][y].button.cget("bg") == STREET and
				self.tiles[x + 1][y].index == NOT_CONNECTED):
				q.put((x + 1, y))
			if (y > 0 and
				self.tiles[x][y - 1].button.cget("bg") == STREET and
				self.tiles[x][y - 1].index == NOT_CONNECTED):
				q.put((x, y - 1))
			if (y < self.max_y - 1 and
				self.tiles[x][y + 1].button.cget("bg") == STREET and
				self.tiles[x][y + 1].index == NOT_CONNECTED):
				q.put((x, y + 1))

		for x in range(self.max_x):
			for y in range(self.max_y):
				if (self.tiles[x][y].button.cget("bg") == STREET and
					self.tiles[x][y].index == NOT_CONNECTED):
					return True

		return False

	def park_error_check(self):
		for spot in self.park_spots[:]:
			(start_x, end_x, start_y, end_y) = spot
			connected = False

			if (start_x > 0):
				for y in range(start_y, end_y + 1):
					if (self.tiles[start_x - 1][y].button.cget("bg") == STREET and
						self.tiles[start_x - 1][y].index == CONNECTED):
						connected = True
			if (end_x < self.max_x - 1):
				for y in range(start_y, end_y + 1):
					if (self.tiles[end_x + 1][y].button.cget("bg") == STREET and
						self.tiles[end_x + 1][y].index == CONNECTED):
						connected = True
			if (start_y > 0):
				for x in range(start_x, end_x + 1):
					if (self.tiles[x][start_y - 1].button.cget("bg") == STREET and
						self.tiles[x][start_y - 1].index == CONNECTED):
						connected = True
			if (end_y < self.max_y - 1):
				for x in range(start_x, end_x + 1):
					if (self.tiles[x][end_y + 1].button.cget("bg") == STREET and
						self.tiles[x][end_y + 1].index == CONNECTED):
						connected = True

			if not connected:
				return True

		return False

	def update_database(self):
		for entry in Park_field.select().where(Park_field.park_id == -1):
			idx = self.find_spot((entry.entry_x, entry.entry_y))

			if (idx == -1):
				entry.delete_instance()

			entry.park_id = idx
			entry.save()

		for idx, (spot, avl) in self.avail.items():
			if (avl == False):
				still_exists = False

				for query in Park_field.select().where(Park_field.park_id == idx):
					still_exists = True

				if not still_exists:
					self.avail[idx] = (spot, True)
					self.mark_spot(spot, PARK_SPOT)

		self.root.after(100, lambda: self.update_database())

	def find_spot(self, entry_point):
		q = Queue.Queue()
		q.put(entry_point)
		discovered = []

		while not q.empty():
			(x, y) = q.get()

			if ((x, y) in discovered):
				continue

			if (self.tiles[x][y].button.cget("bg") == PARK_SPOT and
				self.avail[self.tiles[x][y].index][1] == True):
				self.avail[self.tiles[x][y].index] = (
					self.avail[self.tiles[x][y].index][0], False)
				self.mark_spot(self.avail[self.tiles[x][y].index][0], OCCUPIED)
				return self.tiles[x][y].index

			if x > 0:
				q.put((x - 1, y))
			if x < self.max_x - 1:
				q.put((x + 1, y))
			if y > 0:
				q.put((x, y - 1))
			if y < self.max_y - 1:
				q.put((x, y + 1))

			discovered.append((x, y))

		return -1


def order_axes(start_x, end_x, start_y, end_y):
	if start_x <= end_x:
		if start_y <= end_y:
			return (start_x, end_x, start_y, end_y)
		else:
			return (start_x, end_x, end_y, start_y)
	else:
		if start_y <= end_y:
			return (end_x, start_x, start_y, end_y)
		else:
			return (end_x, start_x, end_y, start_y)

def init_imgs():
	imgs = [0 for x in range(MAXIMG)]

	# Load textures for tiles
	imgs[Void] = PhotoImage(file="textures/Void.png")
	imgs[NorthWest] = PhotoImage(file="textures/NorthWest.png")
	imgs[North] = PhotoImage(file="textures/North.png")
	imgs[NorthEast] = PhotoImage(file="textures/NorthEast.png")
	imgs[West] = PhotoImage(file="textures/West.png")
	imgs[Point] = PhotoImage(file="textures/Point.png")
	imgs[East] = PhotoImage(file="textures/East.png")
	imgs[SouthWest] = PhotoImage(file="textures/SouthWest.png")
	imgs[South] = PhotoImage(file="textures/South.png")
	imgs[SouthEast] = PhotoImage(file="textures/SouthEast.png")
	imgs[FullNorth] = PhotoImage(file="textures/FullNorth.png")
	imgs[FullSouth] = PhotoImage(file="textures/FullSouth.png")
	imgs[FullEast] = PhotoImage(file="textures/FullEast.png")
	imgs[FullWest] = PhotoImage(file="textures/FullWest.png")
	imgs[Vert] = PhotoImage(file="textures/Vert.png")
	imgs[Horz] = PhotoImage(file="textures/Horz.png")
	imgs[FullSquare] = PhotoImage(file="textures/FullSquare.png")
	imgs[DownToUp] = PhotoImage(file="textures/ArrowUp.png")
	imgs[UpToDown] = PhotoImage(file="textures/ArrowDown.png")
	imgs[RightToLeft] = PhotoImage(file="textures/ArrowLeft.png")
	imgs[LeftToRight] = PhotoImage(file="textures/ArrowRight.png")
	imgs[UpToRight] = PhotoImage(file="textures/ArrowUpToRight.png")
	imgs[DownToRight] = PhotoImage(file="textures/ArrowDownToRight.png")
	imgs[LeftToUp] = PhotoImage(file="textures/ArrowLeftToUp.png")
	imgs[RightToUp] = PhotoImage(file="textures/ArrowRightToUp.png")
	imgs[UpToLeft] = PhotoImage(file="textures/ArrowUpToLeft.png")
	imgs[DownToLeft] = PhotoImage(file="textures/ArrowDownToLeft.png")
	imgs[LeftToDown] = PhotoImage(file="textures/ArrowLeftToDown.png")
	imgs[RightToDown] = PhotoImage(file="textures/ArrowRightToDown.png")

	return imgs