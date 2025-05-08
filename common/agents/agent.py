from common.base_agent import BaseAgent
from common.move import Move


class Agent(BaseAgent):

    ''' Beginning of the code:
    We define the methods used to decide the move before the method get_move (see bellow).'''

    def main_path(self):
        try:
            '''This method will determine the "main strategy": it will decide the next main "target",
            and returns 2 directions (among up, down, left or right) corresponding to the moves the
            train has to do in the future to reach it.'''

            # We rename the variables we'll call in the method to simplify the syntax
            
            """ Infos sur les 2 Trains """
            for i in self.all_trains.keys():
                if i == self.nickname:
                    self.train = self.all_trains[i]
                else:
                    self.autre = self.all_trains[i]

            """ Infos sur l'autre"""
            match self.autre["direction"]:
                case [1,0]:
                    self.opp_cur_dir = "right"
                case [-1,0]:
                    self.opp_cur_dir = "left"
                case [0,1]:
                    self.opp_cur_dir = "down"
                case [0,-1]:
                    self.opp_cur_dir = "up"
            self.opp_len = len(self.autre["wagons"])
            self.opponent_loc = [[i[0]//self.cell_size, i[1]//self.cell_size] for i in self.autre["wagons"]]
            self.opponent_head = (self.autre["position"][0]//self.cell_size,self.autre["position"][1]//self.cell_size)
            self.aura = [[self.opponent_head[0] + x, self.opponent_head[1] + y] for x in range(-2,3) for y in range(-2,3)]

            """ info sur delivery zone"""
            self.zone_loc = [(self.delivery_zone["position"][0]//self.cell_size , self.delivery_zone["position"][1]//self.cell_size)] # zone_loc = [x,y] case de la zone de livraison
            znch = self.delivery_zone["height"]//self.cell_size # zone_nb_case_haut
            zncl = self.delivery_zone["width"]//self.cell_size # zone_nb_case_large
            
            match znch :
                case 1:
                    match zncl:
                        case 1:
                            print()
                        case _:
                            for x in range(1,zncl):
                                self.zone_loc.append((self.zone_loc[0][0]+x,self.zone_loc[0][1]))
                case _:
                    match zncl:
                        case 1:
                            for y in range(1,znch):
                                self.zone_loc.append((self.zone_loc[0][0],self.zone_loc[0][1]+y))
                        case _:
                            for y in range(1,znch):
                                for x in range(1,zncl):
                                    self.zone_loc.append((self.zone_loc[0][0] + x,self.zone_loc[0][1] + y)) # à voir si le dernier cas suffit pas, histoire de faire propre
            """ info sur passagers"""
            passagers = self.passengers
            passen1_loc = (passagers[0]["position"][0]//self.cell_size, passagers[0]["position"][1]//self.cell_size)
            passen1_value = passagers[0]["value"]
            passen2_loc = (passagers[1]["position"][0]//self.cell_size, passagers[1]["position"][1]//self.cell_size)
            passen2_value = passagers[1]["value"]

            """ Our own attributes"""
            match self.train["direction"]:
                case [1,0]:
                    self.cur_dir = "right"
                case [-1,0]:
                    self.cur_dir = "left"
                case [0,1]:
                    self.cur_dir = "down"
                case [0,-1]:
                    self.cur_dir = "up"
            self.our_len = int(len(self.train["wagons"]))
            self.our_loc = [[i[0]//self.cell_size, i[1]//self.cell_size] for i in self.train["wagons"]]
            self.our_head = (self.train["position"][0]//self.cell_size , self.train["position"][1]//self.cell_size)

            """ Les distances """
            d_passen1 = abs(passen1_loc[0] - self.our_head[0]) + abs(passen1_loc[1] - self.our_head[1])
            d_passen2 = abs(passen2_loc[0] - self.our_head[0]) + abs(passen2_loc[1] - self.our_head[1])
            d_oppo_passen1 = abs(passen1_loc[0] - self.opponent_head[0]) + abs(passen1_loc[1] - self.opponent_head[1])
            d_oppo_passen2 = abs(passen2_loc[0] - self.opponent_head[0]) + abs(passen2_loc[1] - self.opponent_head[1])
            d_zone = 50 # Valeur arbitraire, théoriquement plus grande que n'importe quelle distance
            self.zone_min = self.zone_loc[0] # zone la plus proche de nous (initialement, c'est la zone d'origine)
            for i,c in enumerate(self.zone_loc):
                d = abs(c[0] - self.our_head[0]) + abs(c[1] - self.our_head[1])
                if d < d_zone:
                    d_zone = d
                    self.zone_min = self.zone_loc[i] # case de zone la plus proche de nous
            
            # We also create new variables to help us "making choices". It will give to each parameter
            # that can have an importance in our choice a "weight". (here, "c" means "coefficient")
            # /!\ This part will have to be adapted by experiments ! '''
            c_len = 9
            c_passen_val = 10
            c_d_zone = 3
            c_d_passen = 3
            c_d_oppo_passen = 0.5


            ''' Beginning of the method: we'll compact the parameters into two variables: one for each
            "target a passenger" choice, and one for the "target zone" choice.'''
            
            # Deciding section:
            # In-zone handler, in case we are in the zone and still need to let passengers:
            # We call a variable "d" to gain space: its the distance on (x, y) between the first corner point
            # of the zone and us
            self.target = None
            if self.our_len != 0 and self.our_head in self.zone_loc:
                for i in self.zone_loc:
                    if i == self.our_head or i in self.our_loc or i in self.opponent_loc:
                        continue
                    self.target = list(i)
                    break
                if not self.target: # Si toutes les cases de zone sont occupées
                    self.target = self.zone_loc[0]

            # Determinig next target:
            else:
                weight_zone = (c_len * self.our_len)**1.5 / (c_d_zone * d_zone) if self.our_len != 0 else -100000
                # Three parameters to target a passenger: their distance, value and the distance with the opponent's head.
                weight_passen1 = (c_passen_val * passen1_value) / (c_d_passen * d_passen1) if d_passen1 != 0 else -100000 #- (c_d_oppo_passen * d_oppo_passen1)**2
                weight_passen2 = (c_passen_val * passen2_value) / (c_d_passen * d_passen2) if d_passen2 != 0 else -100000 #- (c_d_oppo_passen * d_oppo_passen2)**2
                if weight_passen1 >= weight_passen2:
                    if weight_passen1 >= weight_zone:
                        self.target = passen1_loc
                    else:
                        self.target = self.zone_min
                elif weight_passen2 >= weight_zone:
                    self.target = passen2_loc
                else:
                    self.target = self.zone_min
            print(self.target, d_passen2, d_passen1)

            """ Détermination des directions idéales """
            if self.our_head[0] - self.target[0] < 0:
                if self.our_head[1] - self.target[1] < 0:
                    ideal_directions = ("right","down")
                elif self.our_head[1] - self.target[1] > 0:
                    ideal_directions = ("right","up")
                else:                # our_head[1] - target[1] == 0
                    ideal_directions = ("right",None)
            elif self.our_head[0] - self.target[0] > 0:
                if self.our_head[1] - self.target[1] < 0:
                    ideal_directions = ("left","down")
                elif self.our_head[1] - self.target[1] > 0:
                    ideal_directions = ("left","up")
                else:
                    ideal_directions = ("left",None)
            else:                     # our_head[0] - target[0] == 0
                if self.our_head[1] - self.target[1] < 0:
                    ideal_directions = ("down",None)
                else:                 # our_head[1] - target[1] > 0
                    ideal_directions = ("up",None)
        
            return ideal_directions
            # FIN DE MAIN_PATH
        except ZeroDivisionError:
            print()
    


    def adapt_path(self, ideal_directions): 
        '''This method is used to change / chose among the directions given by main_path
        if there is a "danger" on the way. It will have the "last word" to decide which
        way to go. Convert the "directions"-2-elements tuple (among "up", "down", "right",
        "left" and / or None) into the command of the chosen move.
        
        - 1 (FAIT): Déterminer parmis les deux directions données, si il y en a une "prioritaire" (e.t. si une
        des directions (ou LA direction) donné.e.s est derrière nous, et donc inateignable en 1 action) ET
        déterminer la (les) direction(s) de secour(s) (au cas où les directions souhaitées seraient dangereuses).

        - 2 (A COMPLETER): Danger imminent: Evaluer le danger de chacune des direction possible ("directions"
        ET "other_directions") et remplacer par "None" celles qui sont dangereuses.
        ! Cette partie est nécessaire mais pas suffisante: si elle s'active (et élimine une
        direction dangereuse dans l'immédiat), mais qu'il reste à choisir entre deux directions (même
        si il y en a une prioritaire), il est tout de même important de tester la suite avant de
        prendre une décision;

        - 3: Danger potentiel: Trouver des "situations dangereuses", et la logique du
        code pour les identifier et les éviter;

        Très (très) Optionnel:
        - 4: Pas de danger: En cas de nullité des 3 premiers cas, trouver un "paterne idéal"
        (e.d. la suite de mouvement la plus "safe" et "optimisée" possible) -> Idée: essayer le plus
        possible de passer vers le centre du terrain, d'où tous les points sont atteignable rapidement'''

        # Dictionaries to convert the directions-string into something else
        dict_str_to_command = {"up":Move.UP, "down":Move.DOWN, "right":Move.RIGHT, "left":Move.LEFT}
        dict_str_to_values = {"up":(0,-1), "down":(0,1), "right":(1,0), "left":(-1,0)}
        dict_opposite_dir = {"up":"down","right":"left","down":"up","left":"right"}

        try:
            # Partie 1: Direction prioritaire + Déterminer les "autres directions", soient les directions "possibles"
            # mais pas prioritaires (pas de return ici) 
            if self.cur_dir not in ideal_directions: # Means there can be only one of the "good" directions we can go
                
                if ideal_directions[1] is not None: # != None, means the target is on a diagonal (two directions "wanted")
                    if ideal_directions[0] == dict_opposite_dir[self.cur_dir]:
                        other_directions = [self.cur_dir, dict_opposite_dir[ideal_directions[1]]] # Les deux autres directions possibles
                        directions = [ideal_directions[1], None]
                    else: # directions[1] == dict_opposite_dir[self.cur_dir]
                        other_directions = [self.cur_dir, dict_opposite_dir[ideal_directions[0]]]
                        directions = [ideal_directions[0], None]
                
                else: # Two possibilities: the target is next to us, or behind us (both on "strait line")
                    if self.cur_dir == dict_opposite_dir[ideal_directions[0]]: # It's behind us: we have to go back
                        other_directions = [self.cur_dir, None]
                        if self.cur_dir == "up" or self.cur_dir == "down":
                            directions = ["right","left"]
                        else:
                            directions = ["up","down"]
                    else: # We don't change the tuple "directions", as we can go there: just have to change "other_directions"
                        directions = list(ideal_directions)
                        other_directions = [self.cur_dir, dict_opposite_dir[ideal_directions[0]]]

            else: # Means that we can go in (both) direction(s) and that we are already going the right way
                if ideal_directions[1]: # Target on diagonal
                    directions = list(ideal_directions)
                    if self.cur_dir == ideal_directions[0]:
                        other_directions = [dict_opposite_dir[ideal_directions[1]], None]
                        
                    else: # self.cur_dir == directions[1]
                        other_directions = [dict_opposite_dir[ideal_directions[0]], None]
                else: # If target is not on a diagonal, it means we're rushing toward it
                    directions = [ideal_directions[0], None]    
                    if self.cur_dir == "up" or self.cur_dir == "down":
                        other_directions = ["right","left"]
                    else:
                        other_directions = ["up","down"] 
            
            # Partie 2: Danger imminent (pas de return: check "danger potentiel" avant?)
            # TODO: Find a way to check if "out-limits", and if we re "rushing toward" the opponent
            # We have to check both directions, starting by the first given by the variable "directions"
            # The priority direction:
            def out_of_bounds(coordinates):
                if coordinates[0] > 21 or coordinates[0] < 0:
                    return True
                if coordinates[1] > 21 or coordinates[1] < 0:
                    return True
                return False
            
            for i in range(2): # First, let's check directions
                if not directions[i]: # == None
                    continue
                next_loc = [(self.our_head[0] + dict_str_to_values[directions[i]][0]), (self.our_head[1] + dict_str_to_values[directions[i]][1])]
                if  next_loc in self.opponent_loc  or  next_loc in self.our_loc  or  next_loc in self.aura  or  out_of_bounds(next_loc):
                    directions[i] = None
                    # Then we want the other priority direction, or if it doesn't exist, one of other_directions
            for j in range(2): # Now, let's check other_directions
                if not other_directions[i]: # == None
                    continue
                next_loc = [(self.our_head[0] + dict_str_to_values[other_directions[j]][0]), (self.our_head[1] + dict_str_to_values[other_directions[j]][1])]
                if next_loc in self.opponent_loc  or  next_loc in self.our_loc  or  next_loc in self.aura  or  out_of_bounds(next_loc):
                    other_directions[i] = None
                    # Then we want the other priority direction, or if it doesn't exist, one of other_directions

            # Return part (if no return before)
            if directions[0]: # != None: means there is still a priority direction available
                return dict_str_to_command[directions[0]]
            else: # Emergency: we have to escape in another direction
                return dict_str_to_command[other_directions[0]]
        except ZeroDivisionError:
            print()
        

    def get_move(self):

        return self.adapt_path(self.main_path())