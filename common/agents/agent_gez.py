from common.base_agent import BaseAgent
from common.move import Move
import random


class Agent(BaseAgent):

    ''' Beginning of the code:
    We define the methods used to decide the move before the method get_move (see bellow).'''


    def get_move(self):
        """
        Only one method: we basically just look for a passenger, then go to the zone till we have 0 passengers.
        """
        # Variables
        #toutes les infos sur notre train, import
        self.train = self.all_trains[self.nickname]
        #toutes infos sur l'autre train, import
        self.autre = self.all_trains["Agent1"]
        #info sur les passagers
        passagers = self.passengers

        # Utiles:
        zone_loc = self.delivery_zone["position"]
        passenger_loc = passagers[0]["position"]
        length = len(self.train["wagons"])
        our_head = tuple(self.train["position"])
        self.cur_dir = Move(self.train["direction"])

        dict_opposite_dir = {"up":"down","right":"left","down":"up","left":"right"}
        dict_str_to_command = {"up":Move.UP, "down":Move.DOWN, "right":Move.RIGHT, "left":Move.LEFT}

        # Détermination de la cible
        if length == 0:
            target = passenger_loc
        elif our_head != zone_loc[0]:
            target = zone_loc[0]
        else:
            target = zone_loc[1]

        # Détermination des directions idéales
        if our_head[0] - target[0] < 0:
            if our_head[1] - target[1] < 0:
                ideal_directions = ("right","down")
            elif our_head[1] - target[1] > 0:
                ideal_directions = ("right","up")
            else:                # our_head[1] - target[1] == 0
                ideal_directions = ("right",None)
        elif our_head[0] - target[0] > 0:
            if our_head[1] - target[1] < 0:
                ideal_directions = ("left","down")
            elif our_head[1] - target[1] > 0:
                ideal_directions = ("left","up")
            else:
                ideal_directions = ("left",None)
        else:                     # our_head[0] - target[0] == 0
            if our_head[1] - target[1] < 0:
                ideal_directions = ("down",None)
            else:                 # our_head[1] - target[1] > 0
                ideal_directions = ("up",None)

        # Détermination des mouvements
        if self.cur_dir not in ideal_directions: # Means there can be only one of the "good" directions we can go
            
            if ideal_directions[1]: # != None, means the target is on a diagonal (two directions "wanted")
                if ideal_directions[0] == dict_opposite_dir[self.cur_dir]:
                    directions = (ideal_directions[1], None)
                else: # directions[1] == dict_opposite_dir[self.cur_dir]
                    directions = (ideal_directions[0], None)
            
            else: # Two possibilities: the target is next to us, or behind us (both on "strait line")
                if self.cur_dir == dict_opposite_dir(ideal_directions[0]): # It's behind us: we have to go back
                    if self.cur_dir == "up" or self.cur_dir == "down":
                        directions = ("right","left")
                    else:
                        directions = ("up","down")
        
        moves = [Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT]
        #return final_choice
        return random.choice(moves) # Replace this with your own logic
        return dict_str_to_command(directions[0])