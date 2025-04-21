# RP Projet 
Auteurs: UZUN Baki | NGUYEN Nhung Kieu <p>

## Description 
**Projet M1 S2 - Résolution de Problèmes | Sorbonne Université 2024-2025**  
Dans ce projet, nous avons exploré deux algorithmes pour résoudre le problème du *Voyageur Canadien* :  

- **CR (Routage Cyclique)** avec un rapport de compétitivité de $\sqrt{k}$ avec $k$ le nombre de blocages. 

- **CNN** avec un rapport de compétitivité de $\log k$.


## CR 
Afin d'exécuter l'algorithme de routage cyclique il faut utiliser le fichier <code>routage_cyclique.py</code> Il suffit de renseigner les routes et les blockages (ligne 310 )
Un exemple de routes et de blockage: 
```python

routes = {
    'A': {'A':0, 'B': 1, 'C':2},
    'B': {'A': 1, 'B':0, 'C':1},
    'C': {'A': 2, 'B':1, 'C':0},
}
blockages = [
    ['B', 'C']
]
```
Les blocages sont symmétrique il suffira de renseigner seulement une seul direction 
```python 
blockages = [
    ['D', 'E']
]
#Il n ya pas besoin de renseigner les deux direction.
blockages = [
    ['D', 'E'],['E','D']
]
```
La fonction  <code>apply_routage_cyclique(routes,blockages)</code>
nous retourne le chemin complet après exécution de l'algorithme.

La fonction  <code>calculate_cost(complete_path,base_tuple=routes)</code>
nous retourne le coût du chemin retourné.



## CNN 
Pour l'algorithme CNN nous utilisons le fichier <code>cnn_algorithm.py</code>
Pour CNN c'est exactement le même principe que avec CR, il suffit de renseigner les routes et les blockages:
```python
routes = {
        'A': {'A':0, 'B': 1, 'C':2},
        'B': {'A': 1, 'B':0, 'C':1},
        'C': {'A': 2, 'B':1, 'C':0},
    }

blockages = [ ["B", "C"] ]
```
La fonction <code> final_path = apply_cnn_to_routes(routes, blockages) </code> permet d'exécuter l'algorithme CNN 

Le chemin retourner sera en Index, pour l'avoir en Lettre il faut appeler la fonction <code> f = get_path_in_letters(solution=final_path,base_tuple=routes) </code>
La fonction  <code>calculate_cost(f,routes)</code>
nous retourne le coût du chemin retourné.


## Comparaison 
Pour comparer les deux algorithmes nous utilisons le fichier <code> comparison.py </code>
Le code va lancé 200 experience sur des graph aléatoire de taille variant entre 50 et 100 avec un nombre de blocages = 10*n où n est le nombre de sommets.
Vous pouvez renseigner le nombre de sommet et le nombre de blocages pour des expérience + controllé. e.g: 
<code> construct_alea_graph(nb_vertices=40,nb_blockages=10 </code>
Il suffit juste de lancer le code pour avoir un résultat. 
Le code retournera le nombre de fois que CNN a été supérieur à CR 
vous pouvez avoir la moyenne des coûts aussi en enlevant les commantaires en lignes (32,33)
