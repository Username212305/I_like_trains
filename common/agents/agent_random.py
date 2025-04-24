from common.base_agent import BaseAgent
from common.move import Move
import random


class Agent(BaseAgent):

    def get_move(self):
        
        moves = [Move.UP, Move.LEFT, Move.RIGHT, Move.DOWN]
        return random.choice(moves)