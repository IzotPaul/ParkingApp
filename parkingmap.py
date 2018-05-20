import time
import Queue

class Park_spot():
    def __init__(self, avl, name, plate, time):
        self.avl = avl
        self.name = name
        self.plate = plate
        self.time = time

def find_park_spot(entry_point, name, plate, Park):
	q = Queue.Queue()
	q.put(entry_point)

	while not q.empty():
		(i, j) = q.get()

		if Park[i][j].avl == True and Park[i][j].name == 'None':
			Park[i][j].name = name
			Park[i][j].plate = plate
			return (i, j)

		if i > 0:
			q.put((i - 1, j))
		if i < len(Park) - 1:
			q.put((i + 1, j))
		if j > 0:
			q.put((i, j - 1))
		if j < len(Park[0]):
			q.put((i, j + 1))
	return 'No available spot found'