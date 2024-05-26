import ctypes
import numpy as np
import os, math
from pprint import pprint
from PIL import Image
from pathlib import Path
import glob
NB_TUILES = 512
SIZE_TUILES = 1024
# Load the CUDA library 
#https://vitalitylearning.medium.com/using-c-c-and-cuda-functions-as-regular-python-functions-716f01f7ca22
CUDA_LIB = ctypes.CDLL('./bin/main_cuda.so')  # Update with the correct path

PATH_BASE_G = "./web/pan/mandelbrot_G_files"
PATH_BASE_BW = "./web/pan/mandelbrot_BW_files"


def  Get_Path_Base(path_base:str,lvl:int):
    path = os.path.join(path_base,str(lvl))
    if not os.path.isdir(path):
        Path(path).mkdir(parents=True,exist_ok=True)
    return path

def G2BW(data_G):
    output_BW = data_G.copy()
    for i in range(len(data_G)):
        output_BW[i] = data_G[i] %2 * 255
    return output_BW

def Get_lvl_max():
    return int(math.ceil(math.log(NB_TUILES*SIZE_TUILES, 2))) + 1

def Get_dim_image_at_lvl(level):
    """Scale of a pyramid level."""
    max_level = Get_lvl_max()-1
    
    #print(f"max_level = {max_level}")
    #print(f"level = {level}")
    
    factor_size =  math.pow(0.5, max_level - level)
    new_NB_TUILES = math.floor((NB_TUILES*SIZE_TUILES*factor_size)/SIZE_TUILES)
    if new_NB_TUILES==0:
        new_NB_TUILES=1
    
    size_image= NB_TUILES*SIZE_TUILES * factor_size
    #print(f"factor_size = {factor_size}")
    #print(f"new_NB_TUILES = {new_NB_TUILES}")
    
    return new_NB_TUILES, size_image

def Get_diff_nb_tuile_lvl(lvl_start:int,lvl_current:int):
    nb_tuiles_start ,size_g_start = Get_dim_image_at_lvl(lvl_start)
    nb_tuiles_current,size_g_current  = Get_dim_image_at_lvl(lvl_current)
    factor_size = nb_tuiles_current/nb_tuiles_start
    return factor_size

def Get_diff_dim_image_at_lvl(lvl_start:int,lvl_current:int):
    nb_tuiles_start ,size_g_start = Get_dim_image_at_lvl(lvl_start)
    nb_tuiles_current,size_g_current  = Get_dim_image_at_lvl(lvl_current)
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

def sub_make_tuile_basen(no_tuile):

    x_ = no_tuile % NB_TUILES
    y_ = int((no_tuile- x_)/NB_TUILES)
    
    # Prepare data
    x = np.ones((SIZE_TUILES*SIZE_TUILES), dtype=np.uint8)
    output_data = x.tolist()
    output_array = (ctypes.c_uint8 * (SIZE_TUILES*SIZE_TUILES))(*output_data)

    # Call the CUDA function
    lvl_max = Get_lvl_max() -1

    path_base_G =Get_Path_Base(PATH_BASE_G,lvl=lvl_max)
    path_base_BW = Get_Path_Base(PATH_BASE_BW,lvl=lvl_max)
    path_file_G = os.path.join(path_base_G,str(x)+"_"+str(y)+".png")
    path_file_BW = os.path.join(path_base_BW,str(x)+"_"+str(y)+".png")
    if not (os.path.isfile(path_file_G) and os.path.isfile(path_file_BW)):
        CUDA_LIB.RUN(no_tuile, NB_TUILES, output_array)
        data_G = list(output_array)
        data_BW = G2BW(data_G)
        save_file(data_G,path_base_G,x_,y_)
        save_file(data_BW,path_base_BW,x_,y_)

def make_tuile_base():
    # Define the function prototype
    CUDA_LIB.RUN.argtypes = [ctypes.c_long,ctypes.c_long ,ctypes.POINTER(ctypes.c_uint8)]
    CUDA_LIB.RUN.restype = None

    for no_tuile in range(NB_TUILES*NB_TUILES):
        sub_make_tuile_basen(no_tuile)

def sub_make_sub_tuile_base(lvl_start:int,lvl_current:int,nb_tuile_start, path_base:str):
    print("*****************************************************")
    print(f"Get_diff_dim_image_at_lvl({lvl_start},{lvl_current})")
    factor_size_image = Get_diff_dim_image_at_lvl(lvl_start,lvl_current)
    print(factor_size_image)
    print(f"Get_diff_nb_tuile_lvl({lvl_start},{lvl_current})")
    factor_size_tuile = Get_diff_nb_tuile_lvl(lvl_start,lvl_current)
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
    else :
        nb_tuile_group = int( math.ceil(1/factor_size_image))
        
    return factor_size_tuile *nb_tuile_start 

def make_sub_tuile_base():
    lvl_max = Get_lvl_max()-1
    nb_tuile_BW = int(str(NB_TUILES))
    nb_tuile_G = int(str(NB_TUILES))    
    for lvl_value in range(-lvl_max,0,1):
        lvl_start = abs(lvl_value)
        lvl_current = lvl_start-1
        nb_tuile_BW=  sub_make_sub_tuile_base(lvl_start,lvl_current, nb_tuile_BW,PATH_BASE_BW)
        nb_tuile_G=  sub_make_sub_tuile_base(lvl_start,lvl_current, nb_tuile_G,PATH_BASE_G)


make_sub_tuile_base()
