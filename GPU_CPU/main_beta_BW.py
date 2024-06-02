import libs
from constantes import CUDA_LIB, NB_TUILES, PATH_BASE,PATH_BASE_BW,SIZE_TUILES,TEMPALETE_DZI
import logging
import time
LOGGER =logging.getLogger("default")

def make_tuile_base(PATH_BASE_IN:str):
    # Define the function prototype
    LOGGER.info("Define the function prototype  : CUDA_LIB.RUN")
    CUDA_LIB.RUN.argtypes = [libs.ctypes.c_long,libs.ctypes.c_long ,libs.ctypes.POINTER(libs.ctypes.c_uint8)]
    CUDA_LIB.RUN.restype = None
    
    LOGGER.info("Create DZI files")
    dsi_xml = ""
    with open(TEMPALETE_DZI,"r") as f:
        dsi_xml = f.readline().replace("size_g",str(NB_TUILES*SIZE_TUILES))
    
    name_dzi = PATH_BASE_IN.split("/")[-1].replace("_files","")+".dzi"
    
    path_dz = libs.os.path.join(PATH_BASE,name_dzi)
        
    with open(path_dz,"w") as f:
        f.write(dsi_xml)
        
    LOGGER.info("Init valued of loop")
    nb_tuiles = int(str(NB_TUILES))
    lvl_max = libs.Get_lvl_max()-1

    for lvl in range(-lvl_max,0,1):
        LOGGER.info("lvl = "+str(abs(lvl)))
        factor_nb_tuiles = None
        if abs(lvl) < lvl_max:
            factor_nb_tuiles = libs.Get_diff_nb_tuile_lvl(abs(lvl)+1,abs(lvl))
            nb_tuiles=int(nb_tuiles*factor_nb_tuiles)
        if factor_nb_tuiles==1:
            LOGGER.info("lvl = "+str(abs(lvl)) + " ==> no_tuile  = 1" )
            
            libs.sub_make_sub_tuile_base(abs(lvl)+1,abs(lvl),nb_tuiles,PATH_BASE_IN)
        elif factor_nb_tuiles==0.5:
            LOGGER.info("lvl = "+str(abs(lvl)) + " ==> no_tuile  = 2" )
            libs.sub_make_sub_tuile_base_coef2(abs(lvl)+1,abs(lvl),nb_tuiles,PATH_BASE_IN)
        else :
            LOGGER.info("lvl = "+str(abs(lvl))+" ingored") 
            



if __name__ == "__main__":
    LOGGER= libs.init_log("BW",LOGGER)
    make_tuile_base(PATH_BASE_BW)