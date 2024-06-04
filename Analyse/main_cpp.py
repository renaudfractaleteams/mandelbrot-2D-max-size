import json

from numpy import true_divide


cuda_files = ["Statistique_CPP.json"]

csv = list()
bool_titre = True

for cuda_file in cuda_files:
    f = open(cuda_file, "r")
    datas = json.loads("".join(f.readlines()))
    f.close()
    for data in datas:
        if bool_titre:
            line = ""
            for titre in data.keys():
                line =line+titre+";"
            csv.append(line+"\r")
            bool_titre=False
        line = ""
        for titre in data.keys():
            line =line +str(data[titre])+";"
        csv.append(line+"\r")

f_g = open("cpp_file.csv", "w")
f_g.writelines(csv)
f_g.close()