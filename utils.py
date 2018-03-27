from dbfread import DBF
import os
import requests
import shutil
import subprocess
import warnings
import zipfile

from download import *
from workspace_managment import *

"""
Dependencies:
Python3.6 + libraries
EzLAS
las2dem
las2txt
lasinfo

TO-DO:
Try using PyQt for GUI
"""


def ks2fn_ks(ks):
    if ks == "D48GK":
        return "GKR"
    elif ks == "D96TM":
        return "TMR"
    else:
        raise ValueError


def request_sheet(workspace, sheet_names, ks):
    request_data = []

    for record in DBF(workspace.fishnet_path[ks]):
        name = record['NAME']

        if name in sheet_names:
            sheet_names.remove(name)
            block = record['BLOK']
            filename = '{0}_{1}'.format(ks2fn_ks(ks), name)
            url = 'http://gis.arso.gov.si/lidar/otr/{0}/{1}/{2}.zlas'.format(block, ks, filename)
            request_data.append([filename, url])

    if sheet_names:
        print("The following files do not even exist:")
        [print(" *" + name) for name in sheet_names]
        print("Get your facts straight.")

    return request_data


def request_block(workspace, block_names, ks):
    request_data = []

    for record in DBF(workspace.fishnet_path[ks]):
        block = record['BLOK']

        if block in block_names:
            name = record['NAME']
            filename = '{0}_{1}'.format(ks2fn_ks(ks), name)
            url = 'http://gis.arso.gov.si/lidar/otr/{0}/{1}/{2}.zlas'.format(block, ks, filename)
            request_data.append([filename, url])

    return request_data


def request_everything(workspace, ks):
    request_data = []

    for record in DBF(workspace.fishnet_path[ks]):
        name = record['NAME']
        block = record['BLOK']
        filename = '{0}_{1}'.format(ks2fn_ks(ks), name)
        url = 'http://gis.arso.gov.si/lidar/otr/{0}/{1}/{2}.zlas'.format(block, ks, filename)
        request_data.append([filename, url])

    return request_data
