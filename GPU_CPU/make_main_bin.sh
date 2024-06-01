#/usr/local/cuda/bin/nvcc -c src_char/main.cu -o bin/main.o -I/usr/local/cuda/lib64 -I/usr/local/cuda/extras/CUPTI/lib64
#g++ -c -I/usr/local/cuda/include  src_char/main.cpp -o bin/main_cpp.o 
#g++ bin/main.o bin/main_cpp.o -o main_char -lcudart -L/usr/local/cuda/lib64 -L/usr/local/cuda/extras/CUPTI/lib64

#/usr/local/cuda/bin/nvcc ./src_bit/main.cu  ./src_bit/main.cpp -o executable_bit

/usr/local/cuda/bin/nvcc ./src_char/main.cu  -o executable_char

/usr/local/cuda/bin/nvcc -o ./bin/main_cuda.so -shared -Xcompiler -fPIC  ./src_char/main.cu 

