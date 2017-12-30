from utils import *
import tkinter as tk
from tkinter import messagebox
import os


def errorbox_file(filename):
    tk.messagebox.showerror(title="File missing",
                            message="Cannot find " + filename + "!")


def errorbox_workspace():
    tk.messagebox.showerror(title="Workspace error",
                            message="Current workspace is not valid.")


def errorbox_cs():
    tk.messagebox.showerror(title="Coordinate system error",
                            message="Coordinate system is not set.")


def tkstr2float(var_tk):
    var_str = var_tk.get()
    var_str = var_str.replace(",", ".")

    try:
        return float(var_str)
    except ValueError:
        tk.messagebox.showerror(title="Input error",
                                message="The following input is invalid:\n\n" + str(var_tk))


def initiate_gui(ks, workspace):
    if ks == "D48GK":
        fn_ks = "GKR"
    elif ks == "D96TM":
        fn_ks = "TMR"
    else:
        raise ValueError

    # Check if all necessary files exist

    program_folder = os.getcwd()
    ezlas_file = os.path.join(program_folder, 'EzLAS.exe')
    las2dem_file = os.path.join(program_folder, 'las2dem.exe')
    lasmerge_file = os.path.join(program_folder, 'lasmerge.exe')
    lasinfo_file = os.path.join(program_folder, 'lasinfo.exe')

    if not os.path.exists(ezlas_file):
        raise errorbox_file("EzLAS.exe")

    if not os.path.exists(lasmerge_file):
        raise errorbox_file("lasmerge.exe")

    if not os.path.exists(las2dem_file):
        raise errorbox_file("las2dem.exe")

    if not os.path.exists(lasinfo_file):
        raise errorbox_file("lasinfo.exe")

    # Check if fishnet exist, else download it

    fishnet_folder = os.path.join(program_folder, 'fishnet')

    if not os.path.exists(fishnet_folder):
        os.makedirs(fishnet_folder)

    if ks=="D48GK":
        dbf_file = os.path.join(fishnet_folder, 'LIDAR_FISHNET_{}.dbf'.format(ks))
    else:
        tmp_ks = ks[0:3]  # Naming inconsisteny at eVode
        dbf_file = os.path.join(fishnet_folder, 'LIDAR_FISHNET_{}.dbf'.format(tmp_ks))

    if not os.path.isfile(dbf_file):

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

    # Set the workspace

    zlas_folder = os.path.join(workspace, 'zlas')
    las_folder = os.path.join(workspace, 'las')

    if not os.path.exists(zlas_folder):
        os.makedirs(zlas_folder)

    if not os.path.exists(las_folder):
        os.makedirs(las_folder)

    return dbf_file, fn_ks

