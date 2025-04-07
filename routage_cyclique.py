from christofides import apply_christophides
import christofides
from utils import transform_to_matrix,get_path_in_letters

routes = {
    'A': {'A':0, 'B': 1, 'C':2,'D': 1,'E':1},
    'B': {'A': 1, 'B':0, 'C':1, 'D': 2, 'E': 1},
    'C': {'A': 2, 'B':1, 'C':0, 'D': 1, 'E': 1},
    'D': {'A': 1, 'B':2, 'C':1, 'D': 0, 'E': 1},
    'E': {'A': 1, 'B':1, 'C':1, 'D': 1, 'E': 0},
}

blocages = [
    ['D', 'E']
]
def apply_routage_cyclique(routes,blocages):
    matrix = transform_to_matrix(routes)
    christofides_path = apply_christophides(matrix)
    path = get_path_in_letters(christofides_path,routes)
    print(path)
    # first iteration
    P1_cr = []

    i = 0

    for i in range(len(path)-1):

        source,dest = path[i],path[i+1]

        P1_cr.append(source)

        if [source,dest] in blocages:

            rest = path[i+1:]


            # it will find one for sure because we can't have more than m blockage
            for j in range(len(rest)):
                i += 1 # move to the next
                if [source,rest[j]] not in blocages:
                    break

    print(P1_cr)



apply_routage_cyclique(routes,blocages)
