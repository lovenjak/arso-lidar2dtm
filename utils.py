from dbfread import DBF
import os
import requests
import shutil
import subprocess
import zipfile

"""
Dependencies:
Python3.6 + libraries
EzLAS
las2dem
las2txt
lasinfo

TO-DO:
Find whats wrong with current version
Add step and output file entry
Add console output
"""


def pt2range(x, y, dx, dy):

    x_range = list(range(int((x - dx) / 1000), int((x + dx) / 1000) + 1))
    y_range = list(range(int((y - dy) / 1000), int((y + dy) / 1000) + 1))

    return x_range, y_range


def minmax2range(x_min, y_min, x_max, y_max):

    x_range = list(range(int(x_min / 1000), int(x_max / 1000)))
    y_range = list(range(int(y_min / 1000), int(y_max / 1000)))

    return x_range, y_range


def initiate(ks, workspace):

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
    lasinfo_file  = os.path.join(program_folder, 'lasinfo.exe')

    if not os.path.exists(ezlas_file):
        return print("Cannot find EzLAS.exe.")

    if not os.path.exists(lasmerge_file):
        return print("Cannot find lasmerge.exe.")

    if not os.path.exists(las2dem_file):
        return print("Cannot find las2dem.exe.")

    if not os.path.exists(lasinfo_file):
        return print("Cannot find lasinfo.exe.")

    # Check if fishnet exist, else download it

    fishnet_folder = os.path.join(program_folder, 'fishnet')

    if not os.path.exists(fishnet_folder):
        os.makedirs(fishnet_folder)

    dbf_file = os.path.join(fishnet_folder, 'LIDAR_FISHNET_{}.dbf'.format(ks))

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


def get_data(workspace, dbf_file, ks, fn_ks, x_range, y_range, x_min, y_min, x_max, y_max):

    names = []

    lidar_list_file = os.path.join(workspace, 'lidar_list.txt')
    zlas_folder = os.path.join(workspace, 'zlas')
    las_folder = os.path.join(workspace, 'las')

    for x in x_range:
        for y in y_range:
            name = '{}_{}'.format(y, x)
            names.append(name)

    data = []

    for record in DBF(dbf_file):
        name = record['NAME']

        if name in names:
            names.remove(name)
            block = record['BLOK']
            filename = '{0}_{1}'.format(fn_ks, name)
            url = 'http://gis.arso.gov.si/lidar/otr/{0}/{1}/{2}.zlas'.format(block, ks, filename)
            data.append([filename, url])

    if names:
        return print("Some files were not found on the server. Task aborted.")

    # http://gis.arso.gov.si/lidar/otr/b_24/D48GK/GKR_572_131.zlas

    # If data does not exist already, download and decompress it.

    with open(lidar_list_file, "w") as text_file:

        for d in data:

            filename = d[0] + '.zlas'
            zlas_file = os.path.join(zlas_folder, filename)

            if not os.path.exists(zlas_file):

                response = requests.get(d[1], stream=True)
                print('Downloading file: {}'.format(filename))

                with open(zlas_file, 'wb') as new_file:
                    shutil.copyfileobj(response.raw, new_file)

                del response

                print('Unpacking file: {}'.format(filename))
                subprocess.call('.\EzLAS.exe -d {} {}'.format(zlas_file, las_folder), shell=True)

            filename = d[0] + '.las'

            las_file = os.path.join(las_folder, filename)
            print(las_file, file=text_file)

    # Merge and clip data.
    print("Merging and clipping files.")
    subprocess.call('.\lasmerge.exe -lof {4}\lidar_list.txt -keep_xy {0} {1} {2} {3} -o {4}\clip.las'
                    .format(y_min, x_min, y_max, x_max, workspace))

    # Get info on clip.
    print("Getting info on clip.")
    info = subprocess.check_output('.\lasinfo.exe {4}/clip.las', stderr=subprocess.STDOUT,
                                   shell=True, universal_newlines=True)
    info = info.splitlines()
    n_points = int((" ".join(info[15].split())).split()[4])
    area = (x_max - x_min) * (y_max - y_min)
    avg_pt_density = n_points / area

    print("Done!")

    return n_points, area, avg_pt_density


def create_grid(workspace, output, step, start_index):

    # Create grid file.
    print("Creating grid file in XYZ format.")
    subprocess.call('.\las2dem.exe -i clip.las -o {2}\{0}.xyz -step {1}'
                    .format(output, step, workspace))

    # Rename extension to *.txt and add point indices (GEOS compatibility)
    print("Converting XYZ to GEOS-compatible TXT file.")

    dem_file = os.path.join(workspace, output + ".xyz")
    txt_file = os.path.join(workspace, output + ".txt")

    if os.path.exists(txt_file):
        os.remove(txt_file)

    with open(txt_file, 'w') as out_file:
        with open(dem_file, 'r') as in_file:
            for line in in_file:
                out_file.write(str(start_index) + "," + line)
                start_index += 1

    print("Done!")


def example():

    x = 567536
    y = 142344
    dx = 600
    dy = 400

    x_min = x - dx
    x_max = x + dx
    y_min = y - dy
    y_max = y + dy

    step = 0.5
    output = "output"
    start_index = 20000
    workspace = os.path.abspath('C:/Users/Lovenjak/Desktop/fun/arso-lidar2dtm')

    ks = "D48GK"  # or "D96TM"
    x_range, y_range = pt2range(x, y, dx, dy)

    # Initiate program.
    dbf_file, fn_ks = initiate(ks)

    # Download LIDAR data.
    get_data(workspace, dbf_file, ks, fn_ks, x_range, y_range, x_min, y_min, x_max, y_max)

    # Create grid file.
    create_grid(workspace, output, step, start_index)


if __name__ == "__main__":
    example()