#Create Exex
#/usr/local/cuda/bin/nvcc ./src_char/main.cu  -o executable_char
#crete .so lib Python 
/usr/local/cuda/bin/nvcc -o ./bin/main_cuda.so -shared -Xcompiler -fPIC  ./src_char/main.cu 

