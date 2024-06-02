import  ctypes

SIZE_TUILES = 1024
# Load the CUDA library 
#https://vitalitylearning.medium.com/using-c-c-and-cuda-functions-as-regular-python-functions-716f01f7ca22
CUDA_LIB = ctypes.CDLL('../commun/bin/main_cuda.so')  # Update with the correct path

TEMPALETE_DZI = "../commun/resources/dzi.xml"

PATH_BASE = "./web/pan"