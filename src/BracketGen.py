import networkx as nx   
from itertools import combinations
from collections import defaultdict
import random
from math import log2, ceil
from BrackGenLogic import bipartite_matchmaking
from config import app , db
from models import Tournament, Entrant , Match



#Function to create Brackets SE, DE, RR, ETC


def createSingleElim():
    pass

def createDoubleElim():
    pass

def createSwissR1(t_id):
    #Get the entrants from the T_id, do not include dropped participants
    
    participants = Entrant.query.filter(Entrant.tournament_id==t_id,Entrant.dropped!=True).all()
    tournament_info = Tournament.query.filter(Tournament.id==t_id).first()

    print(tournament_info)

    match_list = bipartite_matchmaking(participants)
    print(match_list)
    
    match_obj_list = []
    for match in match_list:
        new_Match = Match(
            round = 1,
            tournament = tournament_info.id,
            player_1_id = match[0].id,
            player_2_id = match[1].id,
        )

        match_obj_list.append(new_Match)

    db.session.add_all(match_obj_list)
    db.session.commit()


def createRoundRobinR1():
    pass


if __name__ == "__main__":
    with app.app_context():
        createSwissR1(1)