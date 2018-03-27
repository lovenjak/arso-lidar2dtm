from utils import *


def main():
    # Using arso-lidar2dtm in Python
    y = 438263
    x = 110318
    dy = 5000
    dx = 5000

    x_min = x - dx
    x_max = x + dx
    y_min = y - dy
    y_max = y + dy

    boundaries = Boundaries(y_min, x_min, y_max, x_max)
    # boundaries = Boundaries.point_constructor(y, x, dy, dx) works too.

    workspace_folder = os.path.abspath('C:/Users/klemen/prj/output/arso-lidar2dtm')
    workspace = Workspace(workspace_folder)

    ks = "D48GK"  # or "D96TM"

    # Prepare requests.
    my_request = request_everything(workspace, ks)

    # Download LIDAR data.
    download_requests(workspace, my_request)


if __name__ == "__main__":
    main()
