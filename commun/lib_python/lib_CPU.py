import ctypes
import numpy as np
import os, math
from pprint import pprint
from PIL import Image
from pathlib import Path
import glob
import time

from constantesg import SIZE_TUILES


def  Get_Path_Base(path_base:str,lvl:int):
    path = os.path.join(path_base,str(lvl))
    if not os.path.isdir(path):
        Path(path).mkdir(parents=True,exist_ok=True)
    return path

def G2BW(data_G,constantes):
    output_BW = data_G.copy()
    for i in range(len(data_G)):
        output_BW[i] = data_G[i] %2 * 255
        if constantes.BOOL_INVERSE :
            output_BW[i] = 255- output_BW[i] 
    return output_BW


def G2G(data_G,constantes):
    output_G = data_G.copy()
    if constantes.BOOL_INVERSE :
        for i in range(len(data_G)):
            output_G[i] = 255- data_G[i] 
    return output_G
def Get_lvl_max(constantes):
    return int(math.ceil(math.log(constantes.NB_TUILES*SIZE_TUILES, 2))) + 1

def Get_dim_image_at_lvl(level,constantes):
    """Scale of a pyramid level."""
    max_level = Get_lvl_max(constantes)-1
    
    #print(f"max_level = {max_level}")
    #print(f"level = {level}")
    
    factor_size =  math.pow(0.5, max_level - level)
    new_NB_TUILES = math.floor((constantes.NB_TUILES*SIZE_TUILES*factor_size)/SIZE_TUILES)
    if new_NB_TUILES==0:
        new_NB_TUILES=1
    
    size_image= constantes.NB_TUILES*SIZE_TUILES * factor_size
    #print(f"factor_size = {factor_size}")
    #print(f"new_NB_TUILES = {new_NB_TUILES}")
    
    return new_NB_TUILES, size_image

def Get_diff_nb_tuile_lvl(lvl_start:int,lvl_current:int,constantes):
    nb_tuiles_start ,size_g_start = Get_dim_image_at_lvl(lvl_start,constantes)
    nb_tuiles_current,size_g_current  = Get_dim_image_at_lvl(lvl_current,constantes)
    factor_size = nb_tuiles_current/nb_tuiles_start
    return factor_size

def Get_diff_dim_image_at_lvl(lvl_start:int,lvl_current:int,constantes):
    nb_tuiles_start ,size_g_start = Get_dim_image_at_lvl(lvl_start,constantes)
    nb_tuiles_current,size_g_current  = Get_dim_image_at_lvl(lvl_current,constantes)
    factor_size = size_g_current/size_g_start
    return factor_size

    
def save_file(data,path_base,x,y):
    data_out = np.array(data,dtype=ctypes.c_uint8)
   

    x2 = data_out.reshape((SIZE_TUILES,SIZE_TUILES))
    im_out = Image.fromarray(x2).convert('L')
    #im_out.save(str(no_tuile)+".tif", format='TIFF', compression='tiff_lzw')
    
    if not os.path.isdir(path_base):
        Path(path_base).mkdir(parents=True,exist_ok=True)
    im_out.save(os.path.join(path_base,str(x)+"_"+str(y)+".png"), format='PNG', compression='tiff_lzw')

def sub_make_sub_tuile_base(lvl_start:int,lvl_current:int,nb_tuile_start, path_base:str,constantes):
    print("*****************************************************")
    print(f"Get_diff_dim_image_at_lvl({lvl_start},{lvl_current})")
    factor_size_image = Get_diff_dim_image_at_lvl(lvl_start,lvl_current,constantes)
    print(factor_size_image)
    print(f"Get_diff_nb_tuile_lvl({lvl_start},{lvl_current})")
    factor_size_tuile = Get_diff_nb_tuile_lvl(lvl_start,lvl_current,constantes)
    print(factor_size_tuile)
    nb_tuile_current = factor_size_tuile *nb_tuile_start 
    path_base_current = Get_Path_Base(path_base,lvl_current)
    path_base_start = Get_Path_Base(path_base,lvl_start)
    
    if factor_size_tuile == 1:
        files_in = glob.glob(path_base_start+"/*.png")
        for file_in in files_in:
            path_file_in = os.path.join(path_base_start,file_in.split("/")[-1])
            path_file_out = os.path.join(path_base_current,file_in.split("/")[-1])
            with Image.open(path_file_in) as im:
                print(f"w_base = {im.width}")
                print(f"w_current = {int(im.width*factor_size_image)}")
                im.resize((int(im.width*factor_size_image),int(im.height*factor_size_image))).save(path_file_out)          



def make_tuile_by_engine(engine,no_tuile,lvl,nb_tuiles,constantes):
    x_ = no_tuile % nb_tuiles
    y_ = int((no_tuile- x_)/nb_tuiles)
    path_base_G =Get_Path_Base(constantes.PATH_BASE_G,lvl=lvl)
    path_base_BW = Get_Path_Base(constantes.PATH_BASE_BW,lvl=lvl)
    path_file_G = os.path.join(path_base_G,str(x_)+"_"+str(y_)+".png")
    path_file_BW = os.path.join(path_base_BW,str(x_)+"_"+str(y_)+".png")
    if not (os.path.isfile(path_file_G) and os.path.isfile(path_file_BW)):
        # Prepare data
        x = np.ones((SIZE_TUILES*SIZE_TUILES), dtype=np.uint8)
        output_data = x.tolist()
        output_array = (ctypes.c_uint8 * (SIZE_TUILES*SIZE_TUILES))(*output_data)

    
        engine(no_tuile, nb_tuiles, output_array)
        data_G = list(output_array)
        data_G_OK =  G2G(data_G,constantes)
        data_BW_OK = G2BW(data_G,constantes)
        save_file(data_G_OK,path_base_G,x_,y_)
        save_file(data_BW_OK,path_base_BW,x_,y_)
