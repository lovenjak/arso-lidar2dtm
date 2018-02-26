from utils import *


def main():

    # Using arso-lidar2dtm in Python

    y = 438263
    x = 110318
    dx = 50000
    dy = 50000

    x_min = x - dx
    x_max = x + dx
    y_min = y - dy
    y_max = y + dy

    step = 15
    output = "output"
    start_index = 20000
    workspace = os.path.abspath('C:/Users/Lovenjak/Desktop/test')

    ks = "D48GK"  # or "D96TM"
    x_range, y_range = pt2range(x, y, dx, dy)

    # Initiate program.
    dbf_file, fn_ks = initiate(ks, workspace)

    # Download LIDAR data.
    get_data(workspace, dbf_file, ks, fn_ks, x_range, y_range, x_min, y_min, x_max, y_max)

    # Create grid file.
    create_grid(workspace, output, step, start_index)


if __name__ == "__main__":
    main()
