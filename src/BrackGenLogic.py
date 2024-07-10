import networkx as nx
import random as rn

from BrackGenClass import TreeNode
from models import Entrant
from config import app, db


def build_single_elim_bracket(player_list):
    pass


def build_double_elim_bracket(player_list):
    pass


def build_next_round_swiss(player_list):
    pass

def bipartite_matchmaking(player_list):
    #Given a list of Entrant_objects, returns a set of tuples where each tuple represents 1 match between 2 entrants.
    
    matching_graph = nx.Graph()
    rn.shuffle(player_list)
    A_set = player_list[len(player_list)//2:]
    B_set = player_list[:len(player_list)//2]

    matching_graph.add_nodes_from(A_set, bipartite = 0)
    matching_graph.add_nodes_from(B_set, bipartite = 1)

    #Add edges between All A and B with weights

    for entrant_in_a in A_set:
        for entrant_in_b in B_set:
            #if a and b have played each other the weight is -inf
            # if they have no played each other then the weight is the sum of their point totals        
            if entrant_in_a.id in list(entrant_in_b.opponents):
                e_weight = -100000
            else:
                e_weight = entrant_in_a.point_total + entrant_in_b.point_total

            matching_graph.add_edge(entrant_in_a,entrant_in_b,edge_weight=e_weight)
            print(f"Link between A{entrant_in_a.id} and B{entrant_in_b.id} with a weight of {e_weight}")
    pairings = nx.max_weight_matching(matching_graph, maxcardinality=True)
    return pairings



    pass

def alt_matchmaking(player_list):
    pass

def next_power_of_2(n):
    pass

def testMatchMaking():
    entrants_list = []
    names= ['Shamu', "Wz", "TrapMoneys", "loofbone", "Bendystraw", "J.Fird", "Suavocado", "LuckExtreme"]
    
    for name in names:
        new_entrant = Entrant(
            username = name,
            point_total = 0,
            opponents = [] 
        )
        entrants_list.append(new_entrant)
    pass

if __name__ == "__main__":
    with app.app_context():
        entrants_list = []
        names= ['Shamu', "Wz", "TrapMoneys", "loofbone", "Bendystraw", "J.Fird", "Suavocado", "LuckExtreme"]

        for name in names:
            new_entrant = Entrant(
                username = name,
                point_total = 0, 
                #opponents = []
            )
            entrants_list.append(new_entrant)

        db.session.add_all(entrants_list)
        db.session.commit()
        bipartite_matchmaking(entrants_list)
    