#Bracket Gen Classes
from models import Match, Entrant
from collections import deque
from config import app , db

class TreeNode:
    #Represent each node as a match. Parent is the next match for the winner, child could be the next match for the loser?
    def __init__(self,player_1=None,player_2=None, left=None,right=None,winner=None,parent=None, child=None):
        self.value = (player_1,player_2)
        
        self.left = left
        self.right = right
        
        self.winner = winner
        self.player_1 = player_1
        self.player_2 = player_2
        
        self.db_id = None
        self.child = None
    
    # def __repr__(self) -> str:
    #     return(f'{self.winner} has won, they will move to loser will move to {self.child}')
    pass


class LosersNode:
    def __init__(self,player_1, player_2, left=None,right=None,winner=None,parent=None):
        self.left = left #Winners side node is here
        self.right = right #losers side node is here
        self.value = (player_1,player_2)

        self.winner = winner
        self.player_1 = player_1
        self.player_2 = player_2

        self.db_id=None
        self.child = None #Loser nodes have no next games



def next_power_of_2(n):
    # If n is already a power of 2, return n
    if n & (n - 1) == 0:
        return n

    # Find the position of the most significant bit in n
    msb_position = 0
    while n > 0:
        n >>= 1
        msb_position += 1

    # Return 2 raised to the power of the next highest bit position
    return 1 << msb_position

def build_single_elimination_bracket(player_list):
    
    matches = []
    init_matches = []
    #create initial matches
    for x,y in zip(*[iter(player_list)]*2): #this works from documentation as a trick 
        winner = x if y is None else y if x is None else None
        match_leaf = TreeNode(player_1=x, player_2=y,winner=winner)
        matches.append(match_leaf)
        init_matches.append(match_leaf)
    #create subsequent matches
    
    #If the  initial matches come in ordered this will work for 
    #loop through the matches, combine the first 2 into 1 and then push that to the end of the que. When the que has only 1 match left that would be the root node.

    while len(matches) >1:
        prev_1 = matches.pop(0)
        prev_2 = matches.pop(0)

        p1_spot = None
        p2_spot = None

        if prev_1.winner != None:
            p1_spot = prev_1.winner
        if prev_2.winner !=None:
            p2_spot =prev_2.winner

        new_match = TreeNode(player_1=p1_spot,player_2=p2_spot,left=prev_1, right= prev_2)
        matches.append(new_match)
    return matches[0] #root node

def build_loser_bracket(entrant_count):
    #Assume that we have the first set of losers matches created when we create the initial winners side matches
    #This will just create the bracket

    iter = 0 
    init_match_list = (entrant_count//4)*[TreeNode()]
    
    while len(init_match_list) > 1:
        current_length = len(init_match_list)
        c = 0 
        print(f'current iter {iter} has {current_length} matches')
        if iter%2 == 0: #new set is  winners dropdown + losers
            
            while c < current_length:
                prev_losers_side = init_match_list.pop(0)
                prev_winners_side = None
                new_match = TreeNode(
                    left=prev_winners_side,
                    right=prev_losers_side,
                    player_1= None,
                    player_2= None
                )

                init_match_list.append(new_match)
                c+=1
            iter +=1 
        elif iter%2 !=0:
            #new set of matches is losers v losers
            while c < current_length:
                prev_1 = init_match_list.pop(0)
                prev_2 = init_match_list.pop(0)
                
                p1_spot = None
                p2_spot = None

                if prev_1.winner != None:
                    p1_spot = prev_1.winner
                if prev_2.winner != None:
                    p2_spot = prev_2.winner

                new_loser_match = TreeNode(
                    player_1=p1_spot, player_2=p2_spot, left=prev_1, right=prev_2
                )
                init_match_list.append(new_loser_match)
                c+=2
            iter +=1
    
    # print(f'final iter {iter} has {current_length} matches')
    # print(len(init_match_list))
    return init_match_list[0] #root node 

def build_double_elim_bracket(participant_list):

    #Build out winners side (done)
    #Build out losers side (done)
    #Create losers grand finals
    #Create connections between winners and losers matches, BFS traversal and connect winners nodes without a child value to a losers node that does not have a left value. 
    #Add in Losers True Final node for 
    #Add in GF node for Winners side winner vs losers side winner, and the bracket reset node
    #Combine the 2 graphs by the GF node 
    #Convert the tree into a DB.
    #Need to know the results of the winners and the losers as they go to the lower bracket, We would nee


    winners_final_node = build_single_elimination_bracket(participant_list)
    losers_final_node = build_loser_bracket(len(participant_list))

    print('winners')

    winners_traversal = return_winners_nodes_BFS(winners_final_node)

    print(len(winners_traversal))
    print('Losers Bracket')
    
    losers_grand_final_node = TreeNode(right=losers_final_node)
    losers_traversal = return_losers_nodes_BFS(losers_grand_final_node)
    print(len(losers_traversal))
   
    #Creating connections

    while winners_traversal:
        node = winners_traversal.pop(0)
        if node.child == None:
            node.child = losers_traversal[0]
            if losers_traversal[0].left != None and losers_traversal[0].right != None:
                losers_traversal.pop(0)
    
    print('connections complete')
    
    
    
    grand_final_node = TreeNode(left = winners_final_node, right = losers_grand_final_node)

    display_bracket_BFS(grand_final_node)

    bracket_reset_node = TreeNode()

    return grand_final_node


def display_bracket_DFS(root_node, depth = 0):
    if root_node:
        print(depth , (root_node.value))
        display_bracket_DFS(root_node.left, depth+1)
        display_bracket_DFS(root_node.right, depth+1)

def display_bracket_BFS(root):
    if not root:
        return
    
    queue = deque([root])
    while queue:
        node = queue.popleft()
        print(f"depth: , Value: {node.value}")
        if node.left:
            queue.append((node.left)) #depth +1
        if node.right:
            queue.append((node.right)) #depth +1 
    return

def return_winners_nodes_BFS(root):
    #returns the winners nodes in BFS
    if not root:
        return
    
    queue = deque([root])
    node_path = []

    while queue:
        node = queue.popleft()
        node_path.append(node)
        if node.left:
            queue.append((node.left))
        if node.right:
            queue.append((node.right))
    return node_path

def return_losers_nodes_BFS(root):
    #returns the losers nodes that are missing left and rights
    if not root:
        return
    queue = deque([root])
    unfinished_nodes = []

    while queue:
        node = queue.popleft()
        if node.left is None or node.right is None:
            unfinished_nodes.append(node)
        if node.left:
            queue.append((node.left))
        if node.right:
            queue.append((node.right))
    return unfinished_nodes

def tree2db(root,t_id,parent_id=None):

    #i guess we could do this where we start with the root, we add the values 
    #We then access the children of the node which now has an id that we can use for the parent column. 
    #I think we should do DFS traversal then. so we have the parent into child for easier referencing. 

    if root:
        new_Match = Match(
            tournament = t_id,
            result = root.winner.id if root.winner else None,
            round = None,
            player_1_id = root.player_1.id if root.player_1 else None,
            player_2_id = root.player_2.id if root.player_2 else None,
            winner_next_match_id = parent_id,
            loser_next_match_id = None
        )

        with app.app_context():
            
            db.session.add(new_Match)            
            db.session.commit()

            #I do not like this i would rather flush get the id, defer the constraint check until the end of the transaction and commit all the changes at once. The way this is set up now if this treedb stopped mid execution I would just end up with some matches in the database that are stranded. Better to commit at the end once i have all the matches. 

            root.db_id = new_Match.id
            print(root.db_id)

        tree2db(root.left, t_id=t_id,parent_id=root.db_id)
        tree2db(root.right, t_id=t_id,parent_id=root.db_id)
    


    return 

def double_elim_tree2db(root,parent_id=None):
    #Would want to create the losers brackets matches
    #update the matches nodes so I have the info
    #then winners so we can reference the children on the winners side. Losers side is like a winners side in terms of only having a winners next match. 

    losers_node = root.right
    winners_final = root.left

    if losers_node:
        new_Match = Match(

        )

    pass

if __name__ == "__main__":
    match_list = [
        TreeNode(player_1='E1', player_2='E2'), TreeNode(player_1='E3', player_2='E4'), TreeNode(player_1='E5', player_2='E6'), TreeNode(player_1='E7', player_2='E8')
    ]


    # loser_root = build_loser_bracket(match_list)
    # display_bracket_BFS(loser_root)

    GF = build_double_elim_bracket(['E1','E2','E3','E4','E5','E6','E7','E8','E9','E10','E11','E12','E13','E14','E15','E16'])
    pass