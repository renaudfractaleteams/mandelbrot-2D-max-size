import gc
import os
import json
import math
import glob
from types import ModuleType
import time
import ctypes
import numpy as np
from PIL import Image
from pathlib import Path
from pprint import pprint


import constantesg 

############# LIB Utilitaire ##################

# Crée le dossiser du niveau <lvl> dans le dossier <path_base> ==> return <path> : str
def  Get_Path_Base(path_base:str,lvl:int):
    path = os.path.join(path_base,str(lvl))
    if not os.path.isdir(path):
        Path(path).mkdir(parents=True,exist_ok=True)
    return path

# Renvoit le niveau max // taille de l'image (NB_TUILES x constantesg.SIZE_TUILES)
def Get_lvl_max(constantes):
    return int(math.ceil(math.log(constantes.NB_TUILES*constantesg.SIZE_TUILES, 2))) + 1

# Renvoit le nombre de tuiles par coté et la taille de l'image pour un niveau donné
def Get_dim_image_at_lvl(level,constantes):
    """Scale of a pyramid level."""
    max_level = Get_lvl_max(constantes)-1
    factor_size =  math.pow(0.5, max_level - level)
    new_NB_TUILES = math.floor((constantes.NB_TUILES*constantesg.SIZE_TUILES*factor_size)/constantesg.SIZE_TUILES)
    if new_NB_TUILES==0:
        new_NB_TUILES=1
    size_image= constantes.NB_TUILES*constantesg.SIZE_TUILES * factor_size  
    return new_NB_TUILES, size_image

# Renvoit le coefficient entre 2 niveaux des nombre de tuiles
def Get_diff_nb_tuile_lvl(lvl_start:int,lvl_current:int,constantes):
    nb_tuiles_start ,size_g_start = Get_dim_image_at_lvl(lvl_start,constantes)
    nb_tuiles_current,size_g_current  = Get_dim_image_at_lvl(lvl_current,constantes)
    factor_size = nb_tuiles_current/nb_tuiles_start
    return factor_size

# Renvoit le coefficient entre 2 niveaux de la taille de l'image
def Get_diff_dim_image_at_lvl(lvl_start:int,lvl_current:int,constantes):
    nb_tuiles_start ,size_g_start = Get_dim_image_at_lvl(lvl_start,constantes)
    nb_tuiles_current,size_g_current  = Get_dim_image_at_lvl(lvl_current,constantes)
    factor_size = size_g_current/size_g_start
    return factor_size

# Enregistre un fichier PNG issus d'un tableau 1D de nuance de gris
def save_file(data,path_base,x,y):
    # Conversion en unsigned char le tableau <data> 
    data_out = np.array(data,dtype=ctypes.c_uint8)
    # Conversion d'un tableau <data_out> 1D en tableau 2D <x2>
    x2 = data_out.reshape((constantesg.SIZE_TUILES,constantesg.SIZE_TUILES))
    # Creation de l'image en nuance de gris
    im_out = Image.fromarray(x2).convert('L')
    # Si le <path_base> n'esiste pas, on le crée 
    if not os.path.isdir(path_base):
        Path(path_base).mkdir(parents=True,exist_ok=True)
    #Creation de l'image 
    im_out.save(os.path.join(path_base,str(x)+"_"+str(y)+".png"), format='PNG', optimize=True)
    # netoyage des variables
    del im_out
    del x2
    del data_out
    gc.collect()

############# LIB Graphiques ##################

# Convertie une nuance de gris en noir et blanc
def G2BW(data_G:list,constantes):
    output_BW = data_G.copy()
    for i in range(len(data_G)):
        output_BW[i] = data_G[i] %2 * 255
        if constantes.BOOL_INVERSE :
            output_BW[i] = 255- output_BW[i] 
    return output_BW

# Convertie une nuance de gris en nuance de gris inverse si constantes.BOOL_INVERSE  == True
def G2G(data_G,constantes):
    output_G = data_G.copy()
    if constantes.BOOL_INVERSE :
        for i in range(len(data_G)):
            output_G[i] = 255- data_G[i] 
    return output_G


#################### Fonctions Créateur de tuiles ##########################

def make_tuile_coef_1(lvl_start:int,lvl_current:int,path_base:str,constantes):
    # Facteur de réduction de taille de l'image
    factor_size_image = Get_diff_dim_image_at_lvl(lvl_start,lvl_current,constantes)
    # Facteur de réduction du nombre de tuile
    factor_size_tuile = Get_diff_nb_tuile_lvl(lvl_start,lvl_current,constantes)
    # récupération  path_base_current
    path_base_current = Get_Path_Base(path_base,lvl_current)
    # récupération path_base_start
    path_base_start = Get_Path_Base(path_base,lvl_start)
    #si Facteur de réduction du nombre de tuile est  égale 1
    if factor_size_tuile == 1:
        files_in = glob.glob(path_base_start+"/*.png")
        for file_in in files_in:
            path_file_in = os.path.join(path_base_start,file_in.split("/")[-1])
            path_file_out = os.path.join(path_base_current,file_in.split("/")[-1])
            with Image.open(path_file_in) as im:
                im.resize((int(im.width*factor_size_image),int(im.height*factor_size_image))).save(path_file_out)          

def make_tuile_coef_2(lvl_start:int,lvl_current:int,nb_tuile_start,path_base:str,constantes):
    # Facteur de l'inverse de la réduction du nombre de tuile
    factor_size_tuile = int(1/Get_diff_nb_tuile_lvl(lvl_start,lvl_current,constantes=constantes))
    # récupération path_base_current
    path_base_current = Get_Path_Base(path_base,lvl_current)
    # récupération path_base_start
    path_base_start = Get_Path_Base(path_base,lvl_start)
    if factor_size_tuile ==2:
        for y in range(nb_tuile_start):
            print(f" y = {y}/{nb_tuile_start-1}")
            for x in range(nb_tuile_start):
                name_file_out = f"{x}_{y}.png"
                path_file_out = os.path.join(path_base_current,name_file_out)
                if not os.path.isfile(path_file_out):
                    im = Image.new('RGB',(constantesg.SIZE_TUILES*factor_size_tuile,constantesg.SIZE_TUILES*factor_size_tuile))
                    for x_ in range(factor_size_tuile):
                        for y_ in range(factor_size_tuile):
                            name_file_in = f"{x*factor_size_tuile+x_}_{y*factor_size_tuile+y_}.png"
                            path_file_in = os.path.join(path_base_start,name_file_in)
                            with Image.open(path_file_in) as imAdd:
                                im.paste(imAdd,(x_*constantesg.SIZE_TUILES,y_*constantesg.SIZE_TUILES))
                    im.resize((constantesg.SIZE_TUILES,constantesg.SIZE_TUILES),Image.Resampling.BICUBIC).save(path_file_out,optimize=True)
                    
                    del im
                    gc.collect()

def make_tuile_by_engine(engine,no_tuile,lvl,nb_tuiles,constantes):
    x_ = no_tuile % nb_tuiles
    y_ = int((no_tuile- x_)/nb_tuiles)
    path_base_G =Get_Path_Base(constantes.PATH_BASE_G,lvl=lvl)
    path_base_BW = Get_Path_Base(constantes.PATH_BASE_BW,lvl=lvl)
    path_file_G = os.path.join(path_base_G,str(x_)+"_"+str(y_)+".png")
    path_file_BW = os.path.join(path_base_BW,str(x_)+"_"+str(y_)+".png")
    if not (os.path.isfile(path_file_G) and os.path.isfile(path_file_BW)):
        # Prepare data
        x = np.ones((constantesg.SIZE_TUILES*constantesg.SIZE_TUILES), dtype=np.uint8)
        output_data = x.tolist()
        output_array = (ctypes.c_uint8 * (constantesg.SIZE_TUILES*constantesg.SIZE_TUILES))(*output_data)

        engine(no_tuile, nb_tuiles, output_array)
        data_G = list(output_array)
        data_G_OK =  G2G(data_G,constantes)
        data_BW_OK = G2BW(data_G,constantes)
        save_file(data_G_OK,path_base_G,x_,y_)
        save_file(data_BW_OK,path_base_BW,x_,y_)

        del x
        del data_G
        del output_array
        del data_G_OK
        del data_BW_OK
        gc.collect()


def Save_Statistique(Statistique:list):
    f = open("Statistique.json", "w")
    f.write(json.dumps(Statistique,indent=4))
    f.close()

   

def make_tuiles(engine, UseCoef2=True,UseEngine=True,constantes=ModuleType):
    Statistique  = list()
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
            factor_nb_tuiles = Get_diff_nb_tuile_lvl(abs(lvl)+1,abs(lvl),constantes)
            nb_tuiles=int(nb_tuiles*factor_nb_tuiles)
        if factor_nb_tuiles==1:
            print("lvl = "+str(abs(lvl)) + " ==> no_tuile  = 1" )
            start = time.time()
            make_tuile_coef_1(abs(lvl)+1,abs(lvl),constantes.PATH_BASE_BW,constantes)
            duration = time.time()-start
            Statistique.append( {
            "function" : "make_tuile_coef_1",
            "lvl" : abs(lvl),
            "duration" : duration,
            "type" : "BW",
            "nb_tuiles" : nb_tuiles*nb_tuiles
            })
            Save_Statistique(Statistique)
            
            start = time.time()
            make_tuile_coef_1(abs(lvl)+1,abs(lvl),constantes.PATH_BASE_G,constantes)
            duration = time.time()-start
            Statistique.append( {
            "function" : "make_tuile_coef_1",
            "lvl" : abs(lvl),
            "duration" : duration,
            "type" : "G",
            "nb_tuiles" : nb_tuiles*nb_tuiles
            })
            Save_Statistique(Statistique)  
        elif factor_nb_tuiles==0.5 and UseCoef2:
            print("lvl = "+str(abs(lvl)) + " ==> no_tuile  = 2" )
            start = time.time()
            make_tuile_coef_2(abs(lvl)+1,abs(lvl),nb_tuiles,constantes.PATH_BASE_BW,constantes)
            duration = time.time()-start
            Statistique.append( {
            "function" : "make_tuile_coef_2",
            "lvl" : abs(lvl),
            "duration" : duration,
            "type" : "BW",
            "nb_tuiles" : nb_tuiles*nb_tuiles
            })
            Save_Statistique(Statistique)
            
            start = time.time()
            make_tuile_coef_2(abs(lvl)+1,abs(lvl),nb_tuiles,constantes.PATH_BASE_G,constantes)
            duration = time.time()-start
            Statistique.append( {
            "function" : "make_tuile_coef_2",
            "lvl" : abs(lvl),
            "duration" : duration,
            "type" : "G",
            "nb_tuiles" : nb_tuiles*nb_tuiles
            })
            Save_Statistique(Statistique)
            
        else :
            if not UseEngine:
                continue
            start_G = time.time()
            for no_tuile in range(nb_tuiles*nb_tuiles):
                start = time.time()
                make_tuile_by_engine(engine=engine,no_tuile=no_tuile,lvl=abs(lvl),nb_tuiles=nb_tuiles,constantes=constantes)
                duration = time.time()-start
                Statistique.append( {
                "function" : "make_tuile_by_engine",
                "lvl" : abs(lvl),
                "duration" : duration,
                "type" : "G and BW",
                "nb_tuiles" : 1            
                })
                print("lvl = "+str(abs(lvl)) + " "+ "==> time "+ str(round(time.time()-start,3))  +"==> no_tuile  = "+str(no_tuile)+"/" +str(nb_tuiles*nb_tuiles) +"==> "+str(int(no_tuile/float(nb_tuiles*nb_tuiles)*100)))
            duration = time.time()-start_G
            Statistique.append( {
            "function" : "make_tuile_by_engine",
            "lvl" : abs(lvl),
            "duration" : duration,
            "type" : "G and BW",
            "nb_tuiles" : nb_tuiles*nb_tuiles            
            })
            Save_Statistique(Statistique)
            print("lvl = "+str(abs(lvl)) + " "+ "==> time "+ str(round(time.time()-start_G,3)))
           