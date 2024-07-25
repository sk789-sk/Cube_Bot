#Bracket Gen Classes
from models import Match, Entrant
from collections import deque
from config import app , db
from pprint import pprint

class TreeNode:
    #Represent each node as a match. Parent is the next match for the winner, child could be the next match for the loser?
    def __init__(self,player_1=None,player_2=None, left=None,right=None,winner=None,parent=None, child=None,location=None):

        self.value = (player_1,player_2)
        
        self.left = left
        self.right = right
        
        self.winner = winner
        self.player_1 = player_1
        self.player_2 = player_2
        

        self.db_id = None
        self.child = child
        self.parent = parent
        self.location = location
    # def __repr__(self) -> str:
    #     return(f'{self.winner} has won, they will move to loser will move to {self.child}')

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
        match_leaf = TreeNode(player_1=x, player_2=y,winner=winner, location='Winners')
        matches.append(match_leaf)
        init_matches.append(match_leaf)
    #create subsequent matches
    
    for match in init_matches:
        print(match.player_1.id, match.player_2.id)


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

        new_match = TreeNode(player_1=p1_spot,player_2=p2_spot,left=prev_1, right= prev_2, location='Winners')
        matches.append(new_match)
    return matches[0] #root node

def build_loser_bracket(entrant_count):
    #creates the matches/bracket

    iter = 0 

    init_match_list = [TreeNode(location='Losers') for _ in range(entrant_count//4)]

    #init_match_list = (entrant_count//4)*[TreeNode(location='Losers')]
    
    while len(init_match_list) > 1:
        current_length = len(init_match_list)
        c = 0 
        #print(f'current iter {iter} has {current_length} matches')
        if iter%2 == 0: #new set is  winners dropdown + losers
            
            while c < current_length:
                prev_losers_side = init_match_list.pop(0)
                prev_winners_side = None
                new_match = TreeNode(
                    left=prev_winners_side,
                    right=prev_losers_side,
                    player_1= None,
                    player_2= None,
                    location= 'Losers'
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
                    player_1=p1_spot, player_2=p2_spot, left=prev_1, right=prev_2,
                    location='Losers'
                )
                init_match_list.append(new_loser_match)
                c+=2
            iter +=1
    
    #Need to create node loser of losers final to play the winner of the last node created as well
    temp = init_match_list.pop(0)
    prev_winners_side = None
    losers_GF = TreeNode(
        left=prev_winners_side,
        right=temp,
        player_1= None,
        player_2= None,
        location='Losers'
    )

    # print(f'final iter {iter} has {current_length} matches')
    # print(len(init_match_list))
    

    return losers_GF
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

    for participant in participant_list:
        print(participant.username)

    winners_final_node = build_single_elimination_bracket(participant_list)
    #display_bracket_BFS(winners_final_node)

    losers_final_node = build_loser_bracket(len(participant_list))
    #display_bracket_BFS(losers_final_node)

    print('winners')

    winners_traversal = return_winners_nodes_BFS(winners_final_node)

    print(len(winners_traversal))
    print('Losers Bracket')
    
    #losers_grand_final_node = TreeNode(right=losers_final_node)
    
    losers_traversal = return_losers_nodes_BFS(losers_final_node)
    print(len(losers_traversal)) #All the nodes in losers bracket that have a missing left or right
   
    #Creating connections by linking winners nodes to losers node by losers next match

    connections = 0
    while winners_traversal:
        node = winners_traversal.pop(0)
        if node.child == None:
            node.child = losers_traversal[0]
            #Proper tree we would have left and rights now but we already have it screwy in teh second part so lets just figure out what to do with the losers node

            #Decide if we need to add more connections to the losers node or not

            if losers_traversal[0].left or losers_traversal[0].right:
                losers_traversal.pop(0)
            else:
                connections += 1
                if connections ==2:
                    losers_traversal.pop(0)
                    connections = 0
            #losers_traversal[0].left = node
    #Connections created were correct 

    print('connections complete')
    
    
    
    grand_final_node = TreeNode(left = winners_final_node, right = losers_final_node)

    #display_bracket_BFS(grand_final_node)

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
        print(f" node location: {node},  Value: {node.value}, child: {node.child}, left:{node.left}, right: {node.right}, location: {node.location}")
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

def double_elim_tree2db(root,t_id,parent_id=None):
    #Would want to create the losers brackets matches
    #update the matches nodes so I have the info
    #then winners so we can reference the children on the winners side. Losers side is like a winners side in terms of only having a winners next match. 
    #start with the losers finals node. 
    #Add that to db flush so we have an id. Pass that id as the winners next node value. I would like to do this in a non-recursive manner since winners and losers have different requirements. Just follow same traversal we did earlier

    losers_node = root.right
    winners_final = root.left

    #Add losers bracket to DB
    #Start with the GF losers node and create the match and add it to db. Save the value as the parent node. 
    #Push all the children to a stack so it we have [1] then [2,3]. 
    #Then we take the first value and add the left and right child for that as well so we have [4,5,3] --> [8,9,5,3] #lets end on l4 so 15 matches only 
    # 8 and 9 have no chilrdren nodes so then we have nothing to push to front and then [5,3]
    #--> [10,11,3] 
    #We also need to store the parent node to the child as well. 

    stack = deque([losers_node])
    i = 0
    while stack:
        current_match = stack.popleft()
        #Create link for child to parent
        
        
        # current_match.right.parent = current_match
        # current_match.left.parent = current_match
        
        #Push the children nodes to front of the stack, go right first then left to keep order
        if current_match.right:
            stack.appendleft(current_match.right)
            current_match.right.parent = current_match

        if current_match.left:
            stack.appendleft(current_match.left)
            current_match.left.parent = current_match
        
        #Create match for the node
        try:
            #pprint(vars(current_match))
            #print('Parent info')
            # if current_match.parent:
            #     print(current_match.parent)

            new_match = Match(
                player_1_id = current_match.player_1.id if current_match.player_1 else None,
                player_2_id = current_match.player_2.id if current_match.player_2 else None,
                winner_next_match_id = current_match.parent.db_id if current_match.parent else None,
                loser_next_match_id = None,
                round = None,
                tournament = t_id,
                result = current_match.winner.id if current_match.winner else None
            )

            db.session.add(new_match)
            db.session.flush()
            current_match.db_id = new_match.id
            i+=1
        except Exception as e:
            print("Error creating losers bracket matches, 0 matches added to db")
            print(e)
    print(f'{i} matches made in losers')
    winners_stack = deque([winners_final])
    
    j=0
    while winners_stack:
        print(winners_stack)
        current_match = winners_stack.popleft()

        if current_match.right:
            winners_stack.appendleft(current_match.right) 
            current_match.right.parent = current_match

        if current_match.left:
            winners_stack.appendleft(current_match.left) #fkn typo did .right here also found error looking at the nodes memory addresses....
            current_match.left.parent = current_match

        try:
            #pprint(vars(current_match))
            print(f'Creating Match with the following \n parent {current_match.parent} \n child {current_match.child} \n left {current_match.left} \n right {current_match.right} \n values: {current_match.value}')

            new_match = Match(
                player_1_id = current_match.player_1.id if current_match.player_1 else None,
                player_2_id = current_match.player_2.id if current_match.player_2 else None,
                winner_next_match_id = current_match.parent.db_id if current_match.parent else None,
                loser_next_match_id = current_match.child.db_id,
                round = None,
                tournament = t_id,
                result = current_match.winner.id if current_match.winner else None
            )
            db.session.add(new_match)
            db.session.flush()
            current_match.db_id = new_match.id
            j+=1
        except Exception as e:
            print("Error creating winners bracket, 0 matches added")
            print(e)
    print(f'{j} matches made in winners')

    print('Matches created')
    db.session.commit()
    return

if __name__ == "__main__":

    with app.app_context():
        participation_list = Entrant.query.filter(Entrant.tournament_id==3).all()
        print(participation_list)
        print(len(participation_list))


        #GF = build_double_elim_bracket(['E1','E2','E3','E4','E5','E6','E7','E8']) 
        GF = build_double_elim_bracket(participation_list)   

        display_bracket_BFS(GF) 

        double_elim_tree2db(GF,3)

    pass