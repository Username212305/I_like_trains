from common.base_agent import BaseAgent
from common.move import Move
import random

#128.179.154.221
#127.0.0.1
class Agent(BaseAgent):

    ''' Beginning of the code:
    We define the methods used to decide the move before the method get_move (see bellow).'''
    '''TODO:
    - Implémenter tactique d'esquive de la tête + efficace (situation du "L")
    - Adaptation des formules de weight (value -, length + ET d_oppo_passen)
    - Finir fonction looptrap
    - Corriger bugs pour 3 adversaires
    - Implémenter boost (/!\ cooldown)
    - End_game_protocol()'''


    
    def main_path(self):
        '''This method will determine the "main strategy": it will decide the next main "target",
        and returns 2 directions (among up, down, left or right) corresponding to the moves the
        train has to do in the future to reach it.'''

        # Variable initialisée seulement en début de partie


        # Dictionaries to convert the directions-string into something else
        self.dict_str_to_command = {"up":Move.UP, "down":Move.DOWN, "right":Move.RIGHT, "left":Move.LEFT}
        self.dict_str_to_values = {"up":(0,-1), "down":(0,1), "right":(1,0), "left":(-1,0)}
        self.dict_opposite_dir = {"up":"down","right":"left","down":"up","left":"right"}

        """ Infos sur les Trains """
        self.autre = []
        self.autre_nicknames = []
        for i in self.all_trains.keys():
            if i == self.nickname:
                self.train = self.all_trains[i]
            else:
                self.autre.append(self.all_trains[i])
                self.autre_nicknames.append(i)

        self.is_alone = False
        if not self.autre:
            self.is_alone = True

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

        """d_zone elaborée"""
        d_zmin = abs(self.zone_loc[0][0] - self.our_head[0]) + abs(self.zone_loc[0][1] - self.our_head[1]) # distance zone de livraison case origine
        self.zone_min = self.zone_loc[0]
        for i,c in enumerate(self.zone_loc):
            d = abs(c[0] - self.our_head[0]) + abs(c[1] - self.our_head[1])
            if d < d_zmin:
                d_zmin = d
                self.zone_min = self.zone_loc[i] # case de zone la plus proche de nous
        
        """ Infos sur l(es) autre(s)"""
        if not self.is_alone:
            self.opp_len = []
            self.opponent_loc = []
            self.opponent_head = []
            for k in range(len(self.autre)):
                self.opp_len.append(len(self.autre[k]["wagons"]))
                # opponent_loc a toutes les coordonnées des wagons de tous les adversaires (les coo ne sont pas "differenciées")
                self.opponent_loc.extend([[i[0]//self.cell_size, i[1]//self.cell_size] for i in self.autre[k]["wagons"]])
                self.opponent_head.append((self.autre[k]["position"][0]//self.cell_size,self.autre[k]["position"][1]//self.cell_size))
            
            self.aura = []
            self.opp_cur_dir = []
            for m in range(len(self.autre)):
                match self.autre[m]["direction"]:
                    case [1,0]:
                        self.opp_cur_dir.append("right")
                        self.aura.extend([[self.opponent_head[m][0]+1,self.opponent_head[m][1]],
                                    [self.opponent_head[m][0]+1,self.opponent_head[m][1]-1],
                                    [self.opponent_head[m][0]+1,self.opponent_head[m][1]+1],
                                    [self.opponent_head[m][0]+2,self.opponent_head[m][1]],
                                    [self.opponent_head[m][0],self.opponent_head[m][1]-1],
                                    [self.opponent_head[m][0],self.opponent_head[m][1]+1]])
                    case [-1,0]:
                        self.opp_cur_dir.append("left")
                        self.aura.extend([[self.opponent_head[m][0]-1,self.opponent_head[m][1]],
                                    [self.opponent_head[m][0]-1,self.opponent_head[m][1]-1],
                                    [self.opponent_head[m][0]-1,self.opponent_head[m][1]+1],
                                    [self.opponent_head[m][0]-2,self.opponent_head[m][1]],
                                    [self.opponent_head[m][0],self.opponent_head[m][1]-1],
                                    [self.opponent_head[m][0],self.opponent_head[m][1]+1]])
                    case [0,1]:
                        self.opp_cur_dir.append("down")
                        self.aura.extend([[self.opponent_head[m][0],self.opponent_head[m][1]+1],
                                    [self.opponent_head[m][0]-1,self.opponent_head[m][1]+1],
                                    [self.opponent_head[m][0]+1,self.opponent_head[m][1]+1],
                                    [self.opponent_head[m][0],self.opponent_head[m][1]+2],
                                    [self.opponent_head[m][0]-1,self.opponent_head[m][1]],
                                    [self.opponent_head[m][0]+1,self.opponent_head[m][1]]])
                    case [0,-1]:
                        self.opp_cur_dir.append("up")
                        self.aura.extend([[self.opponent_head[m][0],self.opponent_head[m][1]-1],
                                    [self.opponent_head[m][0]-1,self.opponent_head[m][1]-1],
                                    [self.opponent_head[m][0]+1,self.opponent_head[m][1]-1],
                                    [self.opponent_head[m][0],self.opponent_head[m][1]-2],
                                    [self.opponent_head[m][0]-1,self.opponent_head[m][1]],
                                    [self.opponent_head[m][0]+1,self.opponent_head[m][1]]])

        """ info sur passagers"""
        passagers = self.passengers
        passen_loc = []
        passen_value = []
        d_passen = []
        d_oppo_passen = []
        for j in range(len(passagers)):
            passen_loc.append((passagers[j]["position"][0]//self.cell_size, passagers[j]["position"][1]//self.cell_size))
            passen_value.append(passagers[j]["value"])
            d_passen.append(abs(passen_loc[j][0] - self.our_head[0]) + abs(passen_loc[j][1] - self.our_head[1]))
            all_distances_passen_oppo = [] # Variable temporaire pour déterminer le minimum des valeurs de cette liste
            for head in self.opponent_head:
                all_distances_passen_oppo.append(abs(passen_loc[j][0] - head[0]) + abs(passen_loc[j][1] - head[1]))
            d_oppo_passen.append(min(all_distances_passen_oppo)) # correspond aux distances minimales de chaque passager avec l'adversaire le plus proche d'eux
        
        def code_47():
            '''Cette fonction est appellée lorsque l'écart de best score avec l'adversaire est assez grand:
            la stratégie consiste alors à tuer l'adversaire en boucle en fonçant sur sa tête.'''

            # On passe à l'attaque si et seulement si on a aucun passager (maximisation de la vitesse)
            if self.our_len >= 1:
                if not self.train["boost_cooldown_active"]:
                    return Move.DROP
                return self.zone_min
            
            # On vise la tête adverse
            if self.autre[0]["alive"]:
                tar = self.opponent_head[0]
            else:
                tar = [self.game_width//(2*self.cell_size),self.game_height//(2*self.cell_size)]

            # On désactive l'esquive de l'aura et de la tête adverse
            self.aura = []
            self.opponent_head = []

            # On évite les passagers
            self.opponent_loc.extend(passen_loc)

            return tar

        
        ''' ------------------------Deciding section:------------------------'''
        self.target = None

        '''In-zone-handler'''
        if self.our_len != 0 and self.our_head in self.zone_loc:
            for i in self.zone_loc:
                if i == self.our_head or i in self.our_loc or i in self.opponent_loc:
                    continue
                self.target = list(i)
                break
            if not self.target: # Si toutes les cases de zone sont occupées
                self.target = self.zone_loc[0]
        

            '''Choice in basic case'''
        else:
            weight_zone = 7**self.our_len - d_zmin if self.our_len != 0 else -100000 #7 et 4 passagers => on priorise un passager à 2 de dist même si nous collé à la zone
            # Three parameters to target a passenger: their distance, value and the distance with the opponent's head.
            weight_passen = []
            for w in range(len(passagers)):
                x = -2497.5*d_passen[w] + 7502.5*passen_value[w] if d_passen[w] != 0 else -100000
                weight_passen.append(x)

            # Détermination de la target
            if weight_zone >= max(weight_passen):
                self.target = self.zone_min
            else:
                self.target = passen_loc[weight_passen.index(max(weight_passen))]


            
        '''Code_47 check:'''
        # On regarde si le code_47 est déjà en train de run
        try:
            if self.code_47_running:
                ecart = 5 # Si c'est le cas, on réduit l'écart de score avec l'adversaire pour le déclencher à 5
            else:
                ecart = 15
        except: # Au tout premier lancement de get_move, code_47_running n'existe pas: on l'initialise à False
            self.code_47_running = False
            ecart = 15

        # On vérifie qu'il y a un seul adversaire, puis que best scores a été initialisé, pour ne pas avoir d'erreur ensuite
        if len(self.autre_nicknames) == 1 and self.best_scores.get(self.nickname):
            # Check si best score adverse a été initialisé
            if self.best_scores.get(self.autre_nicknames[0]):
                oppo_best_score = self.best_scores[self.autre_nicknames[0]]
            else:
                oppo_best_score = 0

            if self.best_scores[self.nickname]  > oppo_best_score + ecart:
                self.target = code_47()
                self.code_47_running = True
            else:
                self.code_47_running = False


        """ Détermination des directions idéales """
        if self.target == Move.DROP:
            return Move.DROP
        elif self.our_head[0] - self.target[0] < 0:
            if self.our_head[1] - self.target[1] < 0:
                ideal_directions = ("right","down")
            elif self.our_head[1] - self.target[1] > 0:
                ideal_directions = ("right","up")
            else: # our_head[1] - target[1] == 0
                ideal_directions = ("right",None)
        elif self.our_head[0] - self.target[0] > 0:
            if self.our_head[1] - self.target[1] < 0:
                ideal_directions = ("left","down")
            elif self.our_head[1] - self.target[1] > 0:
                ideal_directions = ("left","up")
            else:
                ideal_directions = ("left",None)
        else: # our_head[0] - target[0] == 0
            if self.our_head[1] - self.target[1] < 0:
                ideal_directions = ("down",None)
            else: # our_head[1] - target[1] > 0
                ideal_directions = ("up",None)
     
        return ideal_directions
        # FIN DE MAIN_PATH
    

    def adapt_path(self, ideal_directions): 
        '''This method is used to change / chose among the directions given by main_path
        if there is a "danger" on the way. It will have the "last word" to decide which
        way to go. Convert the "directions"-2-elements tuple (among "up", "down", "right",
        "left" and / or None) into the command of the chosen move.
        
        - 1 Déterminer parmis les deux directions données, si il y en a une "prioritaire" (e.t. si une
        des directions (ou LA direction) donné.e.s est derrière nous, et donc inateignable en 1 action) ET
        déterminer la (les) direction(s) de secour(s) (au cas où les directions souhaitées seraient dangereuses).

        - 2 Danger imminent: Evaluer le danger de chacune des direction possible ("directions"
        ET "other_directions") et remplacer par "None" celles qui sont dangereuses.

        - 3 Danger futur: fonction permettant d'éviter le "piège de la boucle" (train qui s'enroule sur lui même)

        - 4 Return final
        '''
        # Partie 1: Direction prioritaire + Déterminer les "autres directions", soient les directions "possibles"
        # mais pas prioritaires (pas de return ici) 
        if not ideal_directions == Move.DROP:
            if self.cur_dir not in ideal_directions: # Means there can be only one of the "good" directions we can go
                
                if ideal_directions[1] is not None: # != None, means the target is on a diagonal (two directions "wanted")
                    if ideal_directions[0] == self.dict_opposite_dir[self.cur_dir]:
                        other_directions = [self.cur_dir, self.dict_opposite_dir[ideal_directions[1]]] # Les deux autres directions possibles
                        directions = [ideal_directions[1], None]
                    else: # directions[1] == dict_opposite_dir[self.cur_dir]
                        other_directions = [self.cur_dir, self.dict_opposite_dir[ideal_directions[0]]]
                        directions = [ideal_directions[0], None]
                
                else: # Two possibilities: the target is next to us, or behind us (both on "strait line")
                    if self.cur_dir == self.dict_opposite_dir[ideal_directions[0]]: # It's behind us: we have to go back
                        other_directions = [self.cur_dir, None]
                        if self.cur_dir == "up" or self.cur_dir == "down":
                            directions = ["right","left"]
                        else:
                            directions = ["up","down"]
                    else: # We don't change the tuple "directions", as we can go there: just have to change "other_directions"
                        directions = list(ideal_directions)
                        other_directions = [self.cur_dir, self.dict_opposite_dir[ideal_directions[0]]]

            else: # Means that we can go in (both) direction(s) and that we are already going the right way
                if ideal_directions[1]: # Target on diagonal
                    directions = list(ideal_directions)
                    if self.cur_dir == ideal_directions[0]:
                        other_directions = [self.dict_opposite_dir[ideal_directions[1]], None]
                        
                    else: # self.cur_dir == directions[1]
                        other_directions = [self.dict_opposite_dir[ideal_directions[0]], None]
                else: # If target is not on a diagonal, it means we're rushing toward it
                    directions = [ideal_directions[0], None]    
                    if self.cur_dir == "up" or self.cur_dir == "down":
                        other_directions = ["right","left"]
                    else:
                        other_directions = ["up","down"] 
        else: # On veut drop un passager
            directions = [self.cur_dir, None]
            if self.cur_dir == "up" or self.cur_dir == "down":
                other_directions = ["right","left"]
            else:
                other_directions = ["up","down"] 
        
        # Partie 2: Danger imminent (pas de return: check "danger potentiel" avant?)
        # We have to check both directions, starting by the first given by the variable "directions"
        # The priority direction:
        if not self.is_alone:
            def out_of_bounds(coordinates):
                if coordinates[0] > self.game_width//self.cell_size or coordinates[0] < 0:
                    return True
                if coordinates[1] > self.game_height//self.cell_size or coordinates[1] < 0:
                    return True
                return False
            
            for i in range(2): # First, let's check directions
                if not directions[i]: # == None
                    continue
                next_loc = [self.our_head[0] + self.dict_str_to_values[directions[i]][0], self.our_head[1] + self.dict_str_to_values[directions[i]][1]]
                if  next_loc in self.opponent_loc  or  next_loc in self.our_loc  or  next_loc in self.aura  or  out_of_bounds(next_loc) or next_loc in self.opponent_head:
                    directions[i] = None
                    # Then we want the other priority direction, or if it doesn't exist, one of other_directions
            for j in range(2): # Now, let's check other_directions
                if not other_directions[j]: # == None
                    continue
                next_loc = [self.our_head[0] + self.dict_str_to_values[other_directions[j]][0], self.our_head[1] + self.dict_str_to_values[other_directions[j]][1]]
                if next_loc in self.opponent_loc  or  next_loc in self.our_loc  or  next_loc in self.aura  or  out_of_bounds(next_loc) or next_loc in self.opponent_head:
                    other_directions[j] = None
                    # Then we want the other priority direction, or if it doesn't exist, one of other_directions

        '''print zone'''
        print("---------------")
        print("target: ",self.target, " | ", "cur_dir: ",self.cur_dir, " | ", "our_head: ", self.our_head)
        print("ideal_directions: ", ideal_directions, " | ","directions: ",directions, " | ", "other_directions: ", other_directions)
        print("aura: ",self.aura, " | ", "Opponent head: ", self.opponent_head)
        print("opponent_loc: ",self.opponent_loc, " | ", "our_loc: ",self.our_loc)
        
        # Return part (if no return before)
        r = random.randint(0,1)
        if directions[0]: # != None: means there is still a priority direction available
            if ideal_directions == Move.DROP:
                return Move.DROP
            elif directions[1]:
                return self.dict_str_to_command[directions[r]]
            else:
                return self.dict_str_to_command[directions[0]]
        elif directions[1]: 
            return self.dict_str_to_command[directions[1]]
        
        else: # There is no "best" direction available, we have to escape in another
            if other_directions[0]:
                if other_directions[1]:
                    return self.dict_str_to_command[other_directions[r]]
                else:
                    return self.dict_str_to_command[other_directions[0]]
            else:
                return self.dict_str_to_command[other_directions[1]]


    def get_move(self):
        '''get_move appelle les autres méthodes de la classe agent. Si jamais adapt_path a éliminé tous les
        mouvements "possibles" (car danger imminent / potentiel partout), on relance une itération de la méthode
        en désactivant l'aura pour essayer de rendre un mouvement "possible" (dans le cas où l'on se trouverait à
        proximité de la tête adverse), et ainsi nous laisser une chance de survivre ou de tuer l'adversaire avec
        nous.'''

        path = self.main_path()
        move = self.adapt_path(path)
        if move:
            return move
        else:
            self.aura = []
            return self.adapt_path(path)