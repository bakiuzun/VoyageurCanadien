from routage_cyclique import apply_routage_cyclique
from cnn_algorithm import apply_cnn_to_routes
from utils import construct_alea_graph,get_path_in_letters,calculate_cost
import numpy as np 
def main():



    CR = []
    CNN = []
    routess = []
    blockagess = []
    for _ in range(200):
        routes,blockages = construct_alea_graph()
        
        CR_PATH = apply_routage_cyclique(routes,blockages)

        tmp = apply_cnn_to_routes(routes, blockages)
        CNN_PATH = get_path_in_letters(solution=tmp,base_tuple=routes)
        
        cost_CNN = calculate_cost(CNN_PATH,routes)
        cost_CR = calculate_cost(CR_PATH,routes)
        
        if cost_CNN < cost_CR:
            routess.append(routes)
            blockagess.append(blockages)
        
        CR.append(cost_CR)
        CNN.append(cost_CNN)


    print("MEAN CR = ",np.mean(CR))
    print("MEAN CNN = ",np.mean(CNN))
    print("How many times CNN was better than CR: ",len(routess))


    


main()