from gui_utils import *
from utils import *
import tkinter as tk
from tkinter import filedialog
from tkinter import scrolledtext
import os
import sys


class RedirectText:

    def __init__(self, text, window):
        self.output = text
        self.window = window

    def write(self, string):
        self.window.console.config(state=tk.NORMAL)
        self.output.insert(tk.END, string)
        self.window.console.config(state=tk.DISABLED)


class Window:

    def __init__(self, size_x, size_y):
        self.size_x = size_x
        self.size_y = size_y

        root = tk.Tk()
        root.title("arso-lidar2dtm")
        root.geometry(str(size_x) + "x" + str(size_y))
        root.resizable(width=False, height=False)

        canvas = tk.Canvas(root, width=size_x, height=size_y)
        canvas.pack()

        # Coordinate system definition
        self.coordinate_system = tk.StringVar()
        self.coordinate_system_definition(root, canvas)

        # Workspace definition
        self.workspace = tk.StringVar()
        self.workspace.set("Not set!")
        self.workspace_definition(root, canvas)

        # Area definition mode

        # Define area by central point
        self.x = tk.StringVar()
        self.y = tk.StringVar()
        self.dx = tk.StringVar()
        self.dy = tk.StringVar()

        self.x.set("142344,156")
        self.y.set("567536,214")
        self.dx.set("100")
        self.dy.set("250")

        self.y_entry = tk.Entry(root, textvariable=self.y, justify=tk.CENTER, state="disabled")
        self.x_entry = tk.Entry(root, textvariable=self.x, justify=tk.CENTER, state="disabled")
        self.dy_entry = tk.Entry(root, textvariable=self.dy, justify=tk.CENTER, state="disabled")
        self.dx_entry = tk.Entry(root, textvariable=self.dx, justify=tk.CENTER, state="disabled")

        self.area_by_point(root, canvas)

        # Define area by bounds

        self.x_min = tk.StringVar()
        self.y_min = tk.StringVar()
        self.x_max = tk.StringVar()
        self.y_max = tk.StringVar()

        self.y_min.set("567286,214")
        self.x_min.set("142244,156")
        self.y_max.set("567786,214")
        self.x_max.set("142444,156")

        self.ymin_entry = tk.Entry(root, textvariable=self.y_min, justify=tk.CENTER, state="disabled")
        self.xmin_entry = tk.Entry(root, textvariable=self.x_min, justify=tk.CENTER, state="disabled")
        self.ymax_entry = tk.Entry(root, textvariable=self.y_max, justify=tk.CENTER, state="disabled")
        self.xmax_entry = tk.Entry(root, textvariable=self.x_max, justify=tk.CENTER, state="disabled")

        self.area_by_bounds(root, canvas)

        # Create data download button
        self.data_confirmation(root)

        # Create area definition options
        self.adm = tk.StringVar()
        self.area_definition(root, canvas)

        # Show info on lidar data in area
        self.n_pts = tk.StringVar()
        self.n_pts.set("0")
        self.area = tk.StringVar()
        self.area.set("N/A")
        self.pt_density = tk.StringVar()
        self.pt_density.set("N/A")
        self.set_data(root)

        # Create console window in Tkinter
        self.frame = tk.Frame(root, height=241, width=140)
        self.frame.place(x=5, y=225)

        self.console = tk.scrolledtext.ScrolledText(self.frame, width=66, height=20,
                                                    state=tk.DISABLED, background=root["bg"])
        self.console.pack()
        redir = RedirectText(self.console, self)
        sys.stdout = redir

        # DEM generation settings
        self.step = tk.StringVar()
        self.output = tk.StringVar()
        self.start_index = tk.StringVar()

        self.step.set("10")
        self.output.set("dtm")
        self.start_index.set("20000")

        self.step_entry = tk.Entry(root, textvariable=self.step, justify=tk.CENTER, state="disabled")
        self.output_entry = tk.Entry(root, textvariable=self.output, justify=tk.CENTER, state="disabled")
        self.start_index_entry = tk.Entry(root, textvariable=self.start_index, justify=tk.CENTER, state="disabled")

        self.generate_button = tk.Button(root, text="Generate DTM", command=self.generate_dem, state="disabled")

        self.dem_settings(root, canvas)


        root.mainloop()

    def coordinate_system_definition(self, root, canvas):
        cs_rectangle = canvas.create_rectangle(5, 5, 145, 105)

        cs_label = tk.Label(root, text="Coordinate system")
        cs_label.place(x=70, y=20, anchor=tk.CENTER)
        self.coordinate_system.set("No value")

        gk_button = tk.Radiobutton(root, text="D48/GK", variable=self.coordinate_system, value="D48GK", indicatoron=0)
        tm_button = tk.Radiobutton(root, text="D96/TM", variable=self.coordinate_system, value="D96TM", indicatoron=0)

        gk_button.place(x=70, y=50, anchor=tk.CENTER)
        tm_button.place(x=70, y=80, anchor=tk.CENTER)

    def area_definition(self, root, canvas):
        adm_rectangle = canvas.create_rectangle(5, 115, 145, 215)

        adm_label = tk.Label(root, text="Area definition mode")
        adm_label.place(x=70, y=130, anchor=tk.CENTER)

        point_button = tk.Radiobutton(root, text="Center point", variable=self.adm, value="point", indicatoron=0,
                                      command=self.disable_bound)
        minmax_button = tk.Radiobutton(root, text="Bounds", variable=self.adm, value="minmax", indicatoron=0,
                                       command=self.disable_point)

        point_button.place(x=70, y=160, anchor=tk.CENTER)
        minmax_button.place(x=70, y=190, anchor=tk.CENTER)

    def workspace_definition(self, root, canvas):
        workspace_rectangle = canvas.create_rectangle(155, 5, self.size_x - 10, 35)

        workspace_label = tk.Label(root, text="Workspace:")
        workspace_label.place(x=195, y=20, anchor=tk.CENTER)

        workspace_tk = tk.StringVar()
        workspace_tk.set("None")

        workspace = tk.Button(root, text="Select", command=self.ask_directory)
        workspace.place(x=self.size_x - 35, y=20, anchor=tk.CENTER)

        directory_label = tk.Label(root, textvariable=self.workspace)
        directory_label.place(x=230, y=10)

    def area_by_point(self, root, canvas):
        point_rectangle = canvas.create_rectangle(155, 45, 155 + (self.size_x - 250) / 3, 215)
        area_point_label = tk.Label(root, text="Center point and offsets")
        area_point_label.place(x=155 + (self.size_x - 250) / 6, y=65, anchor=tk.CENTER)

        y_label = tk.Label(root, text="y/e")
        y_label.place(x=155 + 5, y=90)
        self.y_entry.place(x=175 + 25, y=90)

        x_label = tk.Label(root, text="x/n")
        x_label.place(x=155 + 5, y=120)
        self.x_entry.place(x=175 + 25, y=120)

        dy_label = tk.Label(root, text="dy/de")
        dy_label.place(x=155 + 5, y=150)
        self.dy_entry.place(x=175 + 25, y=150)

        dx_label = tk.Label(root, text="dx/dx")
        dx_label.place(x=155 + 5, y=180)
        self.dx_entry.place(x=175 + 25, y=180)

    def area_by_bounds(self, root, canvas):
        third = (self.size_x - 250) / 3

        bounds_rectangle = canvas.create_rectangle(165 + ((self.size_x - 250) / 3), 45, 185 + 2*third, 215)
        bounds_label = tk.Label(root, text="Bounds")
        bounds_label.place(x=175 + (self.size_x - 250) / 2, y=65, anchor=tk.CENTER)

        ymin_label = tk.Label(root, text="min y/e")
        ymin_label.place(x=170+third, y=90)
        self.ymin_entry.place(x=230+third, y=90)

        xmin_label = tk.Label(root, text="min x/n")
        xmin_label.place(x=170+third, y=120)
        self.xmin_entry.place(x=230+third, y=120)

        ymax_label = tk.Label(root, text="max y/e")
        ymax_label.place(x=170+third, y=150)
        self.ymax_entry.place(x=230+third, y=150)

        xmax_label = tk.Label(root, text="max x/n")
        xmax_label.place(x=170+third, y=180)
        self.xmax_entry.place(x=230+third, y=180)

    def disable_point(self):
        self.x_entry.config(state='disabled')
        self.y_entry.config(state='disabled')
        self.dx_entry.config(state='disabled')
        self.dy_entry.config(state='disabled')

        self.xmin_entry.config(state='normal')
        self.ymin_entry.config(state='normal')
        self.xmax_entry.config(state='normal')
        self.ymax_entry.config(state='normal')

        self.confirm_button.config(state='normal')

    def disable_bound(self):
        self.x_entry.config(state='normal')
        self.y_entry.config(state='normal')
        self.dx_entry.config(state='normal')
        self.dy_entry.config(state='normal')

        self.xmin_entry.config(state='disabled')
        self.ymin_entry.config(state='disabled')
        self.xmax_entry.config(state='disabled')
        self.ymax_entry.config(state='disabled')

        self.confirm_button.config(state='normal')

    def ask_directory(self):
        self.workspace.set(tk.filedialog.askdirectory(title='Select workspace.'))

    def process_input(self):
        tmp_workspace = self.workspace.get()

        if tmp_workspace == 'Not set!' or not os.path.exists(tmp_workspace):
            return errorbox_workspace()

        workspace = os.path.abspath(tmp_workspace)
        cs = self.coordinate_system.get()

        if cs == "No value":
            return errorbox_cs()

        dbf_file, fn_cs = initiate_gui(cs, workspace)

        if self.adm.get() == "point":
            _x = tkstr2float(self.x)
            _y = tkstr2float(self.y)
            _dx = tkstr2float(self.dx)
            _dy = tkstr2float(self.dy)

            x_range, y_range = pt2range(_x, _y, _dx, _dy)
            _x_min = _x - _dx
            _x_max = _x + _dx
            _y_min = _y - _dy
            _y_max = _y + _dy

            self.x_min.set(str(round(_x_min, 3)).replace(".", ","))
            self.y_min.set(str(round(_y_min, 3)).replace(".", ","))
            self.x_max.set(str(round(_x_max, 3)).replace(".", ","))
            self.y_max.set(str(round(_y_max, 3)).replace(".", ","))

        elif self.adm.get() == "minmax":
            _x_min = tkstr2float(self.x_min)
            _x_max = tkstr2float(self.x_max)
            _y_min = tkstr2float(self.y_min)
            _y_max = tkstr2float(self.y_max)

            _dx = (_x_max - _x_min) / 2
            _dy = (_y_max - _y_min) / 2
            _x = _x_min + _dx
            _y = _y_min + _dy

            self.dx.set(str(round(_dx, 3)).replace(".", ","))
            self.dy.set(str(round(_dy, 3)).replace(".", ","))
            self.x.set(str(round(_x, 3)).replace(".", ","))
            self.y.set(str(round(_y, 3)).replace(".", ","))

            x_range, y_range = minmax2range(_x_min, _y_min, _x_max, _y_max)

        else:
            raise ValueError

        _npts, _area, _ptden = get_data(workspace, dbf_file, cs, fn_cs,
                                        x_range, y_range, _x_min, _y_min, _x_max, _y_max)

        self.n_pts.set(str(_npts))
        self.area.set(str(round(_area, 2)))
        self.pt_density.set(str(round(_ptden, 2)))

        self.step_entry.config(state="normal")
        self.output_entry.config(state="normal")
        self.start_index_entry.config(state="normal")
        self.generate_button.config(state="normal")

    def data_confirmation(self, root):
        third = int((self.size_x - 250) / 3)

        self.confirm_button = tk.Button(root, text="Confirm selection", command=self.process_input, state="disabled")
        self.confirm_button.config(width=31, height=2)
        self.confirm_button.place(x = 196 + 2*third, y = 45)

    def set_data(self, root):
        third = int((self.size_x - 250) / 3)
        info_label = tk.Label(root, text="Information on current point selection")
        info_label.place(x=198+2*third, y=105)

        n_points_label = tk.Label(text="Number of points: ")
        n_points_label.place(x=198+2*third, y=145)
        n_points_variable = tk.Label(root, textvariable=self.n_pts)
        n_points_variable.place(x=300+2*third, y=145)

        area_label = tk.Label(text="Area [m²]: ")
        area_label.place(x=198+2*third, y=165)
        area_variable = tk.Label(root, textvariable=self.area)
        area_variable.place(x=257 + 2 * third, y=165)

        density_label = tk.Label(text="Point density [pt/m²]: ")
        density_label.place(x=198+2*third, y=185)
        density_variable = tk.Label(root, textvariable=self.pt_density)
        density_variable.place(x=317 + 2 * third, y=185)

    def dem_settings(self, root, canvas):
        third = (self.size_x - 250) / 3
        dem_settings_rectangle = canvas.create_rectangle(190 + 2 * third, 225, self.size_x - 10, self.size_y - 116)

        dem_settings_label = tk.Label(root, text="DTM Settings")
        dem_settings_label.place(x=196 + 5/2 * third - 17, y=self.size_y-310)

        step_label = tk.Label(root, text="Cell size [m]")
        step_label.place(x=196 + 2*third, y=self.size_y-260)
        self.step_entry.place(x=293+2*third, y=self.size_y-260)

        output_label = tk.Label(root, text="Output filename")
        output_label.place(x=196+2*third, y=self.size_y-220)
        self.output_entry.place(x=293 + 2 * third, y=self.size_y - 220)

        start_index_label = tk.Label(root, text="First index")
        start_index_label.place(x=196+2*third, y=self.size_y-180)
        self.start_index_entry.place(x=293 + 2 * third, y=self.size_y - 180)

        self.generate_button.config(width=31, height=2)
        self.generate_button.place(x=196 + 2 * third, y=self.size_y-80)

    def generate_dem(self):

        _workspace = os.path.abspath(self.workspace.get())
        _output = self.output.get()
        _step = tkstr2float(self.step.get())
        _start_index = int(tkstr2float(self.start_index.get()))

        create_grid(_workspace, _output, _step, _start_index)

def main():
    window = Window(800, 555)




if __name__ == "__main__":
    main()