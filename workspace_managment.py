import os
import requests
import shutil
import warnings
import zipfile


class Workspace:
    def __init__(self, workspace_folder):
        self.workspace_folder = workspace_folder
        self.cwd = os.getcwd()
        self.fishnet_path = dict()
        self.check_for_fishnet("D96TM")
        self.check_for_fishnet("D48GK")

        zlas_folder = os.path.join(self.workspace_folder, 'zlas')
        self.set_folder(zlas_folder)
        self.zlas_folder = zlas_folder

        las_folder = os.path.join(self.workspace_folder, 'las')
        self.set_folder(las_folder)
        self.las_folder = las_folder

    def check_for_dependencies(self):
        self.check_for_file('las2dem.exe')
        self.check_for_file('lasmerge.exe')
        self.check_for_file('EzLAS.exe', warning=True)

    def set_folder(self, name):
        folder = os.path.join(self.workspace_folder, name)
        if not os.path.exists(folder):
            os.makedirs(folder)

    def check_for_file(self, filename, warning=False):
        path = os.path.join(self.workspace_folder, filename)
        if not os.path.isfile(path):
            if warning:
                warnings.warn("Cannot find " + filename + ".")
            else:
                raise IOError("Cannot find " + filename + ".")

    def check_for_fishnet(self, ks):
        fishnet_folder = os.path.join(self.workspace_folder, 'fishnet')
        if not os.path.exists(fishnet_folder):
            os.makedirs(fishnet_folder)

        fishnet_filename = 'LIDAR_FISHNET_{}.dbf'.format(ks)
        self.fishnet_path[ks] = os.path.join(fishnet_folder, 'LIDAR_FISHNET_{}.dbf'.format(ks))

        if not os.path.isfile(self.fishnet_path[ks]):
            url = 'http://gis.arso.gov.si/related/lidar_porocila/lidar_fishnet_{}.zip'.format(ks)
            fishnet_zipfile = os.path.join(fishnet_folder, 'LIDAR_FISHNET_{}.zip'.format(ks))

            response = requests.get(url, stream=True)
            print('Downloading file: lidar_fishnet_{}.zip'.format(ks))

            with open(fishnet_zipfile, 'wb') as new_file:
                shutil.copyfileobj(response.raw, new_file)

            del response

            fishnet_zipfile_obj = zipfile.ZipFile(fishnet_zipfile, 'r')
            fishnet_zipfile_obj.extractall(fishnet_folder)
            fishnet_zipfile_obj.close()
