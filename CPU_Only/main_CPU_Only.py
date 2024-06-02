import ctypes
import numpy as np
import os, math
from pprint import pprint
from PIL import Image
from pathlib import Path
import glob
import time
import sys
sys.path.append('../commun/lib_python')

global BOOL_INVERSE, NB_TUILES, PATH_BASE_G, PATH_BASE_BW, SIZE_TUILES, CUDA_LIB, TEMPALETE_DZI
import constantesg #import SIZE_TUILES, CUDA_LIB, TEMPALETE_DZI, PATH_BASE
import constantes #import BOOL_INVERSE, NB_TUILES, PATH_BASE_G, PATH_BASE_BW

from lib_CPU import Get_lvl_max,Get_diff_nb_tuile_lvl, sub_make_sub_tuile_base, make_tuile_by_engine


def make_tuiles(engine):
    # Define the function prototype
    engine.argtypes = [ctypes.c_long,ctypes.c_long ,ctypes.POINTER(ctypes.c_uint8)]
    engine.restype = None
    
    dsi_xml = ""
    with open(constantesg.TEMPALETE_DZI,"r") as f:
        dsi_xml = f.readline().replace("size_g",str(constantes.NB_TUILES*constantesg.SIZE_TUILES))
    
    name_dzi_BW = constantes.PATH_BASE_BW.split("/")[-1].replace("_files","")+".dzi"
    name_dzi_G = constantes.PATH_BASE_G.split("/")[-1].replace("_files","")+".dzi"
    
    path_dzi_BW = os.path.join(constantesg.PATH_BASE,name_dzi_BW)
    path_dzi_G = os.path.join(constantesg.PATH_BASE,name_dzi_G)
    
    with open(path_dzi_BW,"w") as f:
        f.write(dsi_xml)
        
    with open(path_dzi_G,"w") as f:
        f.write(dsi_xml)
        
        
    nb_tuiles = int(str(constantes.NB_TUILES))
    lvl_max = Get_lvl_max(constantes)-1
    for lvl in range(-lvl_max,0,1):
        print("lvl = "+str(abs(lvl)))
        factor_nb_tuiles = None
        if abs(lvl) < lvl_max:
            factor_nb_tuiles = Get_diff_nb_tuile_lvl(abs(lvl)+1,abs(lvl))
            nb_tuiles=int(nb_tuiles*factor_nb_tuiles)
        if factor_nb_tuiles==1:
            print("lvl = "+str(abs(lvl)) + " ==> no_tuile  = 1" )
            sub_make_sub_tuile_base(abs(lvl)+1,abs(lvl),nb_tuiles,constantes.PATH_BASE_BW,constantes)
            sub_make_sub_tuile_base(abs(lvl)+1,abs(lvl),nb_tuiles,constantes.PATH_BASE_G,constantes)
        else : 
            start_G = time.time()
            for no_tuile in range(nb_tuiles*nb_tuiles):
                start = time.time()
                make_tuile_by_engine(engine=engine,no_tuile=no_tuile,lvl=abs(lvl),nb_tuiles=nb_tuiles,constantes=constantes)
                print("lvl = "+str(abs(lvl)) + " "+ "==> time "+ str(round(time.time()-start,3))  +"==> no_tuile  = "+str(no_tuile)+"/" +str(nb_tuiles*nb_tuiles) +"==> "+str(int(no_tuile/float(nb_tuiles*nb_tuiles)*100)))
            print("lvl = "+str(abs(lvl)) + " "+ "==> time "+ str(round(time.time()-start_G,3)))
            

#make_sub_tuile_base()
make_tuiles(constantesg.CUDA_LIB.RUN_CUDA)