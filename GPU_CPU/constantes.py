NB_TUILES = 512
SIZE_TUILES = 1024
# Load the CUDA library 
#https://vitalitylearning.medium.com/using-c-c-and-cuda-functions-as-regular-python-functions-716f01f7ca22
CUDA_LIB = ctypes.CDLL('./bin/main_cuda.so')  # Update with the correct path
TEMPALETE_DZI = "./resources/dzi.xml"

PATH_BASE_G = "./web/pan/mandelbrot_G_files"
PATH_BASE_BW = "./web/pan/mandelbrot_BW_files"
"""
PATH_BASE_G = "./web/pan/mandelbrot_G_test_files"
PATH_BASE_BW = "./web/pan/mandelbrot_BW_test_files"
"""
PATH_BASE = "./web/pan"