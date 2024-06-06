import sys
from pprint import pprint

sys.path.append('../commun/lib_python')

import constantesg #import SIZE_TUILES, CUDA_LIB, TEMPALETE_DZI, PATH_BASE
import constantes #import BOOL_INVERSE, NB_TUILES, PATH_BASE_G, PATH_BASE_BW

from lib_CPU import make_tuiles

#make_sub_tuile_base()
make_tuiles(engine=constantesg.CUDA_LIB.RUN_CUDA,UseCoef2=True, UseEngine=False,constantes=constantes)