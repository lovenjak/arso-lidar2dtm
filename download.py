from utils import *


class Boundaries:
    # Primary constructor
    def __init__(self, y_min, x_min, y_max, x_max):
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.area = (x_max - x_min) * (y_max - y_min)
        self.sheet_names = self.get_sheet_names()

    # Secondary constructor (basically a wrapper)
    @classmethod
    def point_constructor(cls, y, x, dy, dx):
        y_min = y - dy
        x_min = x - dx
        y_max = y + dy
        x_max = x + dx
        return cls(y_min, x_min, y_max, x_max)

    def get_sheet_names(self):
        x_range = list(range(int(self.x_min / 1000), int(self.x_max / 1000)))
        y_range = list(range(int(self.y_min / 1000), int(self.y_max / 1000)))

        names = list()
        for x in x_range:
            for y in y_range:
                name = '{}_{}'.format(y, x)
                names.append(name)

        return names


def download_requests(workspace, request_data, extract_to_las=False):
    lidar_list_file = os.path.join(workspace.workspace_folder, 'lidar_list.txt')

    # If data does not exist already, download and (optionally) decompress it.
    with open(lidar_list_file, "w") as text_file:

        for d in request_data:

            filename = d[0] + '.zlas'
            zlas_file = os.path.join(workspace.zlas_folder, filename)

            if not os.path.exists(zlas_file):

                response = requests.get(d[1], stream=True)
                print('Downloading file: {}'.format(filename))

                with open(zlas_file, 'wb') as new_file:
                    shutil.copyfileobj(response.raw, new_file)

                del response

                if extract_to_las:
                    print('Unpacking file: {}'.format(filename))
                    subprocess.call('.\EzLAS.exe -d {} {}'.format(zlas_file, workspace.las_folder), shell=True)

                    filename = d[0] + '.las'

                    las_file = os.path.join(workspace.las_folder, filename)
                    print(las_file, file=text_file)