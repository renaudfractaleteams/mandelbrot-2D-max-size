#include "cuda_runtime.h"
#include "device_launch_parameters.h"
#include <iostream>
#include <iterator>
#include <cmath>
#include <stdint.h>
#include <iostream>
#include <fstream>
#include <stdio.h>  // Pour fprintf et stderr
#include <stdlib.h> // Pour les fonctions standard C comme malloc
#include <stdint.h>
#include "picojson.h"
// Définition de l'énumération pour le type de fractale
enum Type_Fractal
{
    Mandelbrot,
    Julia
};
bool DEBUG = false;

// Définition de la structure Complex pour représenter les nombres complexes
struct Complex
{
    double x, y; // Partie réelle et imaginaire

    // Constructeur pour initialiser un nombre complexe
    __host__ __device__
    Complex(double a = 0.0, double b = 0.0) : x(a), y(b) {}

    // Surcharge de l'opérateur + pour l'addition de deux nombres complexes
    __host__ __device__
        Complex
        operator+(const Complex &other) const
    {
        return Complex(x + other.x, y + other.y);
    }

    // Surcharge de l'opérateur - pour la soustraction de deux nombres complexes
    __host__ __device__
        Complex
        operator-(const Complex &other) const
    {
        return Complex(x - other.x, y - other.y);
    }

    // Surcharge de l'opérateur * pour la multiplication de deux nombres complexes
    __host__ __device__
        Complex
        operator*(const Complex &other) const
    {
        return Complex(x * other.x - y * other.y, x * other.y + y * other.x);
    }

    // Fonction pour calculer la norme d'un nombre complexe
    __host__ __device__ double norm() const
    {
        return sqrt(x * x + y * y);
    }

    // Fonction pour élever un nombre complexe à une puissance donnée
    __host__ __device__
        Complex
        power(double p) const
    {
        double radius = sqrt(x * x + y * y);
        double angle = atan2(y, x);
        double radius_p = pow(radius, p);
        double angle_p = p * angle;

        return Complex(radius_p * cos(angle_p), radius_p * sin(angle_p));
    }
};

// Définition de la structure ParameterPicture pour stocker les paramètres de l'image fractale
__host__ __device__ struct ParameterPicture
{
    long len_image_per_tuile; // Longueur globale en 3D
    long nb_tuiles;           // Longueur locale en 2D
    long no_tuile;
    double2 start;             // Point de départ de l'image
    double size;               // Taille d'un côté de l'image
    Type_Fractal type_fractal; // Type de fractale (Mandelbrot ou Julia)
    double2 coef_julia;        // Coefficients pour la fractale de Julia
    double power_value;        // Valeur de la puissance
    long iter_max;             // Nombre maximal d'itérations
    long id;                   // Identifiant de l'image
    double pas_tuile;

    // Constructeur pour initialiser un objet ParameterPicture
    __host__ __device__ ParameterPicture(long no_tuile, long len_image_per_tuile, long nb_tuiles, double2 start, double size, double power_value, long iter_max, Type_Fractal type_fractal, double2 coef_julia = make_double2(0.0, 0.0))
        : no_tuile(no_tuile), power_value(power_value), iter_max(iter_max), type_fractal(type_fractal), coef_julia(coef_julia), len_image_per_tuile(len_image_per_tuile), nb_tuiles(nb_tuiles), start(start), size(size), pas_tuile(size / ((double)(nb_tuiles))) {};

    __host__ __device__ size_t get_size_array_2D_tuile() const
    {
        return (size_t)len_image_per_tuile * (size_t)len_image_per_tuile;
    }

    __host__ __device__ size_t get_len_global_image() const
    {
        return (size_t)nb_tuiles * (size_t)len_image_per_tuile;
    }

    __host__ __device__ long2 get_x_y_tuile_no_from_no_tuile() const
    {
        long x = no_tuile % nb_tuiles;
        long y = (no_tuile - x) / nb_tuiles;

        return make_long2(x, y);
    }

    __host__ __device__ long2 get_x_y_tuile_px_from_no_tuile() const
    {
        long2 pose_no = get_x_y_tuile_no_from_no_tuile();

        return make_long2(pose_no.x * len_image_per_tuile, pose_no.y * len_image_per_tuile);
    }

    __host__ __device__ double2 get_x_y_tuile_double_from_no_tuile() const
    {
        long2 pose_no = get_x_y_tuile_no_from_no_tuile();

        return make_double2((double)pose_no.x * pas_tuile, (double)pose_no.y * pas_tuile);
    }

    __host__ __device__ double2 get_x_y_globale_double_from_x_y(int x, int y) const
    {
        double2 pos_po_double = get_x_y_tuile_double_from_no_tuile();

        return make_double2(start.x + pos_po_double.x + (double)x / ((double)(len_image_per_tuile - 1)) * pas_tuile, start.y + pos_po_double.y + (double)y / ((double)(len_image_per_tuile - 1)) * pas_tuile);
    }

    __host__ __device__ long get_index_long_from_x_y(int x, int y) const
    {
        if (x < 0 || x >= (len_image_per_tuile))
        {
            return -2;
        }

        if (y < 0 || y >= (len_image_per_tuile))
        {
            return -1;
        }

        return (long)x + (long)y * len_image_per_tuile;
    }

    // Fonction pour imprimer les paramètres de l'image dans un fichier
    __host__ void print_file(std::string path_file) const
    {
        std::ofstream myfile;
        myfile.open(path_file, std::ios::app);
        myfile << "no_tuile = " << no_tuile << std::endl;

        myfile << "len_image_per_tuile = " << len_image_per_tuile << std::endl;
        myfile << "nb_tuiles = " << nb_tuiles << std::endl;
        myfile << "pas_tuile= " << pas_tuile << std::endl;

        myfile << "start_x = " << start.x << std::endl;
        myfile << "start_y = " << start.y << std::endl;

        myfile << "size = " << size << std::endl;
        myfile << "type_fractal = " << type_fractal << std::endl;
        myfile << "coef_julia_x = " << coef_julia.x << std::endl;
        myfile << "coef_julia_y = " << coef_julia.y << std::endl;

        myfile << "power_value = " << power_value << std::endl;
        myfile << "iter_max = " << iter_max << std::endl;

        myfile.close();
    }
};

__host__ __device__ int comptute_fractale(ParameterPicture parameter_picture, int x, int y)
{

    // Obtenir la position complexe correspondante
    double2 pos_double = parameter_picture.get_x_y_globale_double_from_x_y(x, y);
    Complex z(pos_double.x, pos_double.y);
    Complex c(pos_double.x, pos_double.y);

    // Si le type de fractale est Julia, utiliser les coefficients de Julia
    if (parameter_picture.type_fractal == Type_Fractal::Julia)
    {
        c.x = parameter_picture.coef_julia.x;
        c.y = parameter_picture.coef_julia.y;
    }

    int iter = 0;

    // Calculer le nombre d'itérations pour la fractale
    while (z.norm() < 2.0 && iter < parameter_picture.iter_max)
    {
        z = z.power(parameter_picture.power_value) + c;
        iter++;
    }

    return iter;
}

// Kernel CUDA pour générer une image fractale
__global__ void Kernel_Picture(ParameterPicture parameter_picture, unsigned char *data)
{
    // Calcul des indices 3D pour chaque thread
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    int idy = blockIdx.y * blockDim.y + threadIdx.y;

    // Obtenir l'index 2D correspondant
    long index = parameter_picture.get_index_long_from_x_y(idx, idy);

    // Si l'index est valide
    if (index >= 0)
    {
        int iter = comptute_fractale(parameter_picture, idx, idy);

        data[index] = (unsigned char)(iter % 256);
    }
}

void C_Picture(ParameterPicture parameter_picture)
{

    parameter_picture.print_file("file.txt");
    for (int idx = 0; idx < parameter_picture.len_image_per_tuile; idx++)
    {
        for (int idy = 0; idy < parameter_picture.len_image_per_tuile; idy++)
        {
            double2 pos_double = parameter_picture.get_x_y_globale_double_from_x_y(idx, idy);
            long index = parameter_picture.get_index_long_from_x_y(idx, idy);
            int iter = comptute_fractale(parameter_picture, idx, idy);

            std::cout << index << " ==> " << iter << " ==> " << idx << "/" << idy << " ==> " << pos_double.x << "/" << pos_double.y << std::endl;
        }
    }
}
// Fonction pour exécuter le kernel CUDA
extern "C" cudaError_t RUN(long no_tuile, long nb_tuiles, unsigned char *datas)
{

    std::string json_file = "config.json";

    std::ifstream t(json_file);
    std::string json_data((std::istreambuf_iterator<char>(t)),
                          std::istreambuf_iterator<char>());

    picojson::value v;

    picojson::parse(v, json_data);
    int id_cuda = std::stoi(v.get("id_cuda").to_str());
    // long no_tuile = std::stol(v.get("no_tuile").to_str());
    long len_image_per_tuile = std::stol(v.get("len_image_per_tuile").to_str());
    // long nb_tuiles = std::stol(v.get("nb_tuiles").to_str());
    double2 start = make_double2(std::stod(v.get("start_x").to_str()), std::stod(v.get("start_y").to_str()));
    double size_double = std::stod(v.get("size").to_str());
    double power_value = std::stod(v.get("power_value").to_str());
    long iter_max = std::stol(v.get("iter_max").to_str());
    Type_Fractal type_fractal = Type_Fractal::Mandelbrot;
    // long no_tuile = std::stol(v.get("no_tuile").to_str());
    ParameterPicture parameter_picture(no_tuile, len_image_per_tuile, nb_tuiles, start, size_double, power_value, iter_max, type_fractal);
    // ParameterPicture parameter_picture() Type_Fractal::Mandelbrot);

    // Calculer la taille des données à allouer
    size_t size = parameter_picture.get_size_array_2D_tuile() * sizeof(unsigned char);
    unsigned char *dev_datas = 0;
    cudaError_t cudaStatus;

    // Définir la configuration des threads et des blocs
    const dim3 threadsPerBlock(16, 16, 1);
    const dim3 numBlocks((parameter_picture.len_image_per_tuile + threadsPerBlock.x - 1) / threadsPerBlock.x,
                         (parameter_picture.len_image_per_tuile + threadsPerBlock.y - 1) / threadsPerBlock.y,
                         1);

    // Sélectionner le GPU à utiliser
    cudaStatus = cudaSetDevice(id_cuda);
    if (cudaStatus != cudaSuccess)
    {
        fprintf(stderr, "cudaSetDevice failed!  Do you have a CUDA-capable GPU installed?");
        goto Error;
    }

    // Allouer de la mémoire sur le GPU pour les données
    cudaStatus = cudaMalloc((void **)&dev_datas, size);
    if (cudaStatus != cudaSuccess)
    {
        fprintf(stderr, "cudaMalloc failed!");
        goto Error;
    }

    // Lancer le kernel CUDA
    if (DEBUG)
        std::cout << "Start Kernel_Picture" << std::endl;
    Kernel_Picture<<<numBlocks, threadsPerBlock>>>(parameter_picture, dev_datas);
    if (DEBUG)
        std::cout << "End Kernel_Picture" << std::endl;

    if (DEBUG)
        std::cout << "Start Vérifier si le lancement du kernel a échoué" << std::endl;
    // Vérifier si le lancement du kernel a échoué
    cudaStatus = cudaGetLastError();
    if (cudaStatus != cudaSuccess)
    {
        fprintf(stderr, "Kernel_Picture launch failed: %s\n", cudaGetErrorString(cudaStatus));
        goto Error;
    }
    if (DEBUG)
        std::cout << "End  Vérifier si le lancement du kernel a échoué" << std::endl;

    if (DEBUG)
        std::cout << "Start Attendre la fin de l'exécution du kernel" << std::endl;
    // Attendre la fin de l'exécution du kernel
    cudaStatus = cudaDeviceSynchronize();
    if (cudaStatus != cudaSuccess)
    {
        fprintf(stderr, "cudaDeviceSynchronize returned error code %d after launching Kernel_Picture!\n", cudaStatus);
        goto Error;
    }
    if (DEBUG)
        std::cout << "End Attendre la fin de l'exécution du kernel" << std::endl;

    // Copier les données du GPU vers la mémoire de l'hôte
    if (DEBUG)
        std::cout << "Start Copier les données du GPU vers la mémoire de l'hôte" << std::endl;
    cudaStatus = cudaMemcpy(datas, dev_datas, size, cudaMemcpyDeviceToHost);
    if (cudaStatus != cudaSuccess)
    {
        fprintf(stderr, "cudaMemcpy failed!");
        goto Error;
    }
    if (DEBUG)
        std::cout << "End Copier les données du GPU vers la mémoire de l'hôte" << std::endl;

    // Libérer la mémoire allouée sur le GPU
    if (DEBUG)
        std::cout << "Start Libérer la mémoire allouée sur le GPU" << std::endl;
    cudaFree(dev_datas);
    if (DEBUG)
        std::cout << "End Libérer la mémoire allouée sur le GPU" << std::endl;

    // Réinitialiser le GPU
    if (DEBUG)
        std::cout << "Start Réinitialiser le GPU" << std::endl;
    cudaStatus = cudaDeviceReset();
    if (DEBUG)
        std::cout << "End Réinitialiser le GPU" << std::endl;
    if (cudaStatus != cudaSuccess)
    {
        fprintf(stderr, "cudaDeviceReset failed!");
        return cudaStatus;
    }

    return cudaSuccess;

Error:
    // En cas d'erreur, libérer la mémoire allouée sur le GPU
    cudaFree(dev_datas);
    return cudaStatus;
}

int main()
{
    std::string json_file = "config.json";

    std::ifstream t(json_file);
    std::string json_data((std::istreambuf_iterator<char>(t)),
                          std::istreambuf_iterator<char>());

    picojson::value v;

    picojson::parse(v, json_data);
    int id_cuda = std::stoi(v.get("id_cuda").to_str());
    long no_tuile = std::stol(v.get("no_tuile").to_str());
    long len_image_per_tuile = std::stol(v.get("len_image_per_tuile").to_str());
    long nb_tuiles = std::stol(v.get("nb_tuiles").to_str());
    double2 start = make_double2(std::stod(v.get("start_x").to_str()), std::stod(v.get("start_y").to_str()));
    double size_double = std::stod(v.get("size").to_str());
    double power_value = std::stod(v.get("power_value").to_str());
    long iter_max = std::stol(v.get("iter_max").to_str());
    Type_Fractal type_fractal = Type_Fractal::Mandelbrot;
    // long no_tuile = std::stol(v.get("no_tuile").to_str());
    ParameterPicture parameter_picture(no_tuile, len_image_per_tuile, nb_tuiles, start, size_double, power_value, iter_max, type_fractal);

    C_Picture(parameter_picture);

    unsigned char *datas_G = 0;
    size_t size = 1024 * 1024 * sizeof(unsigned char);
    std::cout << "début malloc datas_BW" << std::endl;
    datas_G = (unsigned char *)malloc(size);
    std::cout << "fin malloc datas_BW" << std::endl;

    cudaError_t cudaStatus;

    std::cout << "début du RUN Cuda" << std::endl;
    cudaStatus = RUN(0, 2, datas_G);
    std::cout << "fin du RUN Cuda" << std::endl;
}