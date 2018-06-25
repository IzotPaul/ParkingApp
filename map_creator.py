from tkinter import *
from map_defines import *
from map_utils import *

def main():
	root = Tk()

	config_frame = Frame(root)
	button_frame = Frame(root)
	grid_frame = Frame(config_frame)
	label10 = Label(grid_frame, text="Grid Size:")
	entry_x = Entry(grid_frame, bd=3, width=3)
	label11 = Label(grid_frame, text="x")
	entry_y = Entry(grid_frame, bd=3, width=3)
	label_error = Label(config_frame, wraplength=150)
	entry_x.insert(0, "20")
	entry_y.insert(0, "20")

	config_frame.pack(side=LEFT)
	button_frame.pack(side=RIGHT)
	grid_frame.pack(side=TOP)
	label10.pack(side=LEFT)
	entry_x.pack(side=LEFT)
	label11.pack(side=LEFT)
	entry_y.pack(side=LEFT)

	var = StringVar()
	grid = Grid(button_frame, config_frame, label_error, root)
	obstacle_btn = Radiobutton(config_frame, text="Obstacle", width=14,
					variable=var, value=EMPTY, bg=EMPTY,
					command=lambda: grid.select_mode(var.get()))
	street_btn = Radiobutton(config_frame, text="Street", width=14,
					variable=var, value=STREET, bg=STREET,
					command=lambda: grid.select_mode(var.get()))
	park_btn = Radiobutton(config_frame, text="Parking Spot", width=14,
					variable=var, value=PARK_SPOT, bg=PARK_SPOT,
					command=lambda: grid.select_mode(var.get()))
	save_btn = Button(config_frame, text="SAVE!",
					command=lambda: grid.save_grid())
	create_btn = Button(config_frame, text="CREATE!",
					command=lambda: grid.generate_grid(int(entry_x.get()),
														int(entry_y.get())))

	create_btn.pack()
	park_btn.pack()
	street_btn.pack()
	obstacle_btn.pack()
	save_btn.pack()
	label_error.pack()


	root.title("Parking App")
	root.mainloop()


if __name__ == "__main__":
    main()