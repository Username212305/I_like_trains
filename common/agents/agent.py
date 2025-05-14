from common.base_agent import BaseAgent
from common.move import Move
import random
import math

class Agent(BaseAgent):

    ''' Beginning of the code:
    We define the methods used to decide the move before the method get_move (see bellow).'''


    
    def main_path(self):
        '''This method will determine the "main strategy": it will decide the next main "target",
        and returns 2 directions (among up, down, left or right) corresponding to the moves the
        train has to do in the future to reach it.'''

        # Dictionaries to convert the directions-string into something else
        self.dict_str_to_command = {"up":Move.UP, "down":Move.DOWN, "right":Move.RIGHT, "left":Move.LEFT}
        self.dict_str_to_values = {"up":(0,-1), "down":(0,1), "right":(1,0), "left":(-1,0)}
        self.dict_opposite_dir = {"up":"down","right":"left","down":"up","left":"right"}

        """ Infos sur les Trains """
        self.autre = []
        for i in self.all_trains.keys():
            if i == self.nickname:
                self.train = self.all_trains[i]
            else:
                self.autre.append(self.all_trains[i])

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
                self.opponent_loc.append([i[0]//self.cell_size, i[1]//self.cell_size] for i in self.autre[k]["wagons"])
                self.opponent_head.append((self.autre[k]["position"][0]//self.cell_size,self.autre[k]["position"][1]//self.cell_size))
            
            self.aura = []
            self.opp_cur_dir = []
            for m in range(len(self.autre)):
                match self.autre[m]["direction"]:
                    case [1,0]:
                        self.opp_cur_dir.append("right")
                        self.aura.append([[self.opponent_head[m][0]+1,self.opponent_head[m][1]],
                                    [self.opponent_head[m][0]+1,self.opponent_head[m][1]-1],
                                    [self.opponent_head[m][0]+1,self.opponent_head[m][1]+1],
                                    [self.opponent_head[m][0]+2,self.opponent_head[m][1]],
                                    [self.opponent_head[m][0],self.opponent_head[m][1]-1],
                                    [self.opponent_head[m][0],self.opponent_head[m][1]+1]])
                    case [-1,0]:
                        self.opp_cur_dir.append("left")
                        self.aura.append([[self.opponent_head[m][0]-1,self.opponent_head[m][1]],
                                    [self.opponent_head[m][0]-1,self.opponent_head[m][1]-1],
                                    [self.opponent_head[m][0]-1,self.opponent_head[m][1]+1],
                                    [self.opponent_head[m][0]-2,self.opponent_head[m][1]],
                                    [self.opponent_head[m][0],self.opponent_head[m][1]-1],
                                    [self.opponent_head[m][0],self.opponent_head[m][1]+1]])
                    case [0,1]:
                        self.opp_cur_dir.append("down")
                        self.aura.append([[self.opponent_head[m][0],self.opponent_head[m][1]+1],
                                    [self.opponent_head[m][0]-1,self.opponent_head[m][1]+1],
                                    [self.opponent_head[m][0]+1,self.opponent_head[m][1]+1],
                                    [self.opponent_head[m][0],self.opponent_head[m][1]+2],
                                    [self.opponent_head[m][0]-1,self.opponent_head[m][1]],
                                    [self.opponent_head[m][0]+1,self.opponent_head[m][1]]])
                    case [0,-1]:
                        self.opp_cur_dir.append("up")
                        self.aura.append([[self.opponent_head[m][0],self.opponent_head[m][1]-1],
                                    [self.opponent_head[m][0]-1,self.opponent_head[m][1]-1],
                                    [self.opponent_head[m][0]+1,self.opponent_head[1]-1],
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
            # TODO Adapter LES weight passagers
            weight_zone = 7**self.our_len - d_zmin if self.our_len != 0 else -100000 #7 et 4 passagers => on priorise un passager à 2 de dist même si nous collé à la zone
            # Three parameters to target a passenger: their distance, value and the distance with the opponent's head.
            weight_passen = []
            for w in range(passagers):
                x = -2497.5*d_passen + 7502.5*passen_value if d_passen != 0 else -100000
                weight_passen.append(x)
            
            # Définition du passager le "plus lourd"
            max = weight_passen[0]
            index = 0
            for i, weight in enumerate(passen_loc):
                if weight > max:
                    max = weight
                    index = i

            if weight_zone >= max(weight_passen):
                self.target = self.zone_min
            else:
                self.target = passen_loc[index]
            
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
        
        # Partie 2: Danger imminent (pas de return: check "danger potentiel" avant?)
        # We have to check both directions, starting by the first given by the variable "directions"
        # The priority direction:
        if not self.is_alone:
            def out_of_bounds(coordinates):
                if coordinates[0] > 21 or coordinates[0] < 0:
                    return True
                if coordinates[1] > 21 or coordinates[1] < 0:
                    return True
                return False
            
            for i in range(2): # First, let's check directions
                if not directions[i]: # == None
                    continue
                next_loc = [(self.our_head[0] + self.dict_str_to_values[directions[i]][0]), (self.our_head[1] + self.dict_str_to_values[directions[i]][1])]
                if  next_loc in self.opponent_loc  or  next_loc in self.our_loc  or  next_loc in self.aura  or  out_of_bounds(next_loc) or next_loc in self.opponent_head:
                    directions[i] = None
                    # Then we want the other priority direction, or if it doesn't exist, one of other_directions
            for j in range(2): # Now, let's check other_directions
                if not other_directions[j]: # == None
                    continue
                next_loc = [(self.our_head[0] + self.dict_str_to_values[other_directions[j]][0]), (self.our_head[1] + self.dict_str_to_values[other_directions[j]][1])]
                if next_loc in self.opponent_loc  or  next_loc in self.our_loc  or  next_loc in self.aura  or  out_of_bounds(next_loc) or next_loc in self.opponent_head:
                    other_directions[j] = None
                    # Then we want the other priority direction, or if it doesn't exist, one of other_directions


        # Partie 3: Danger futur
        def loop_trap(coordinates):
            '''On lance cette fonction lorsqu'on s'apprête à avancer sur notre propre corps, et que les cases à
            gauche et à droite sont libres: il faut vérifier que la direction qu'on s'apprête à prendre ne va pas
            nous coincer dans un piège où l'on s'enroulerait sur nous même.
            Elle prend les coordonnées de la case sur laquelle on "voudrait aller", et check les cases autour:
            on forme une "frontière" sur les cases libres qui sont checkées pour la première fois (la frontière s'éloigne
            petit à petit de la case de départ). Si au bout de 4 itérations, il existe toujours des cases libres au delà 
            de la frontière, on considère que aller sur lacase de départ est safe. Au contraire, si à un moment il n'y
            a plus de cases dans la frontiere, c'est que toutes les cases "au-delà" de notre frontière précédente sont
            obstruées: c'est un piège'''

            # On vérifie au préalable que les conditions du piège sont favorables:
            
            cases_check = [coordinates] # L'ensembles des cases qui ont été parcourues
            frontiere_precedente = [coordinates] # Les cases parcourues dans la dernière itération
            frontiere_nouvelle = [] # Les cases de la prochaine frontière de vérification

            for k in range(4): # On limite notre nombre d'itérations de la fonction à 4

                for j in frontiere_precedente: # On réitère le programme pour chaque case de la frontière actuelle
                    for i in [(j[0] + x, j[1] + y) for x in range(-1,2) for y in range(-1,2)]: # On parcours toutes les cases autour de la cible
                        if not (i in cases_check or i in self.our_loc or i == self.our_head or out_of_bounds(i)):
                            # On rajoute uniquement les cases libres, présente dans aucune des deux frontieres
                            frontiere_nouvelle.append(i)
                            cases_check.append(i)
                    
                if len(cases_check) > 10: # arret prématuré si jamais il y a beaucoup de cases safe
                    return False

                if not frontiere_nouvelle: # Si aucune case n'est ajoutée à la nouvelle frontiere, c est qu il n y a plus de case libre
                    return True
                
                frontiere_precedente = frontiere_nouvelle
                frontiere_nouvelle = []
            return False

        """print zone"""
        print("---------------")
        print("target: ",self.target, " | ", "cur_dir: ",self.cur_dir, " | ", "our_head: ", self.our_head)
        print("ideal_directions: ", ideal_directions, " | ","directions: ",directions, " | ", "other_directions: ", other_directions)
        print("aura: ",self.aura)
        print("opponent_loc: ",self.opponent_loc, " | ", "our_loc: ",self.our_loc)
        
        # Return part (if no return before)
        r = random.randint(0,1)
        if directions[0]: # != None: means there is still a priority direction available
            if directions[1]:
                return self.dict_str_to_command[directions[r]]
            else:
                return self.dict_str_to_command[directions[0]]
        elif directions[1]: 
            return self.dict_str_to_command[directions[1]]
        else: # Emergency: we have to escape in another direction
            if other_directions[0]:
                if other_directions[1]:
                    return self.dict_str_to_command[other_directions[r]]
            else:
                return self.dict_str_to_command[other_directions[1]]

    def get_move(self):

        return self.adapt_path(self.main_path())