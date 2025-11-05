"""
================================================================================
TETRIS BOT - ML CHALLENGE
================================================================================

OBJECTIVE:
----------
Build an ML/AI bot that plays Tetris by implementing the `decide()` method below.
Your bot will receive game state information and must return the action to take.

HOW IT WORKS:
-------------
1. The game calls `bot.decide(obs)` approximately every 120ms (8-9 times per second)
2. Your bot receives a dictionary (`obs`) containing complete game state
3. You analyze the state and return one action string
4. The game executes your action and continues

IMPORTS YOU MIGHT NEED:
-----------------------
"""
from __future__ import annotations
from typing import Optional, List, Dict, Any

# Add your imports here (numpy, tensorflow, pytorch, etc.)
# import numpy as np
# import torch
# from your_model import YourModel


"""
================================================================================
IMPLEMENT YOUR BOT HERE
================================================================================
"""


class Bot:
    """
    Your Tetris Bot Implementation.
    
    Initialize your model, load weights, set up any required state in __init__().
    Implement your decision logic in the decide() method.
    """
    
    def __init__(self) -> None:
        """
        Initialize your bot here.
        
        Examples:
        ---------
        # Load a trained model
        # self.model = YourModel()
        # self.model.load_weights('model.pth')
        
        # Initialize any state tracking
        # self.move_history = []
        # self.strategy = "aggressive"
        """
        pass  # Replace with your initialization code

    def decide(self, obs: Optional[dict]) -> Optional[str]:
        """
        ====================================================================
        MAIN DECISION FUNCTION - IMPLEMENT YOUR BOT LOGIC HERE
        ====================================================================
        
        This method is called every ~120ms during gameplay.
        Analyze the game state and return the action you want to take.
        
        PARAMETERS:
        -----------
        obs : dict or None
            Game state observation dictionary (see structure below)
            Will be None if game state is unavailable (rare)
        
        RETURNS:
        --------
        str or None
            One of the following action strings:
            - 'w'  : Rotate piece clockwise
            - 'a'  : Move piece left
            - 's'  : Soft drop (move down faster)
            - 'd'  : Move piece right
            - ' '  : Hard drop (instant drop to bottom)
            - None : Do nothing this frame
        
        ====================================================================
        GAME STATE STRUCTURE (obs dictionary):
        ====================================================================
        
        obs = {
            "grid": List[List[int]],        # The game board
            "current_piece": dict,          # Currently falling piece
            "next_piece": dict,             # Next piece in queue
            "level": int                    # Current difficulty level
        }
        
        --------------------------------------------------------------------
        1. GRID (obs["grid"])
        --------------------------------------------------------------------
        A 20x10 matrix representing the game board (20 rows, 10 columns).
        - Index [0][0] is top-left corner
        - Index [19][9] is bottom-right corner
        - Values:
            0 = Empty cell
            1-7 = Occupied cell (different colors/piece types)
        
        Example access:
            grid = obs["grid"]
            top_row = grid[0]           # First row (list of 10 values)
            bottom_row = grid[19]       # Last row
            cell = grid[row][col]       # Individual cell value
            
        Example usage:
            # Check if bottom row is full
            if all(cell != 0 for cell in grid[19]):
                return ' '  # Hard drop!
                
            # Count empty cells in column 5
            empty_in_col5 = sum(1 for row in grid if row[5] == 0)
        
        --------------------------------------------------------------------
        2. CURRENT PIECE (obs["current_piece"])
        --------------------------------------------------------------------
        The piece currently falling. None if no piece is active.
        
        Structure:
            {
                "type": int,            # Piece type (0-6)
                                        # 0=I, 1=O, 2=T, 3=S, 4=Z, 5=J, 6=L
                
                "x": int,               # Column position (0-9)
                "y": int,               # Row position (0-19)
                
                "rotation": int,        # Rotation state (0-3)
                                        # 0=0°, 1=90°, 2=180°, 3=270°
                
                "color": int,           # Color code (1-7)
                
                "cells": List[tuple]    # Occupied cells as (row, col) pairs
                                        # Example: [(5,3), (5,4), (6,3), (6,4)]
            }
        
        Example usage:
            current = obs["current_piece"]
            if current is not None:
                # Check if piece is in danger zone (top rows)
                if current["y"] < 5:
                    return ' '  # Drop it fast!
                
                # Check if piece is too far right
                if current["x"] > 6:
                    return 'a'  # Move left
                
                # Rotate if it's an I-piece
                if current["type"] == 0:
                    return 'w'
        
        --------------------------------------------------------------------
        3. NEXT PIECE (obs["next_piece"])
        --------------------------------------------------------------------
        The next piece that will appear after current piece is placed.
        Useful for planning ahead!
        
        Structure:
            {
                "type": int,            # Piece type (0-6)
                "rotation": int,        # Initial rotation (usually 0)
                "color": int            # Color code (1-7)
            }
        
        Example usage:
            next_p = obs["next_piece"]
            if next_p["type"] == 0:  # Next is I-piece
                # Save space for vertical placement
                return 'd'  # Move to right side
        
        --------------------------------------------------------------------
        4. LEVEL (obs["level"])
        --------------------------------------------------------------------
        Current game level (difficulty increases with level).
        Higher levels = pieces fall faster
        
        Example usage:
            if obs["level"] > 5:
                # High speed - make quick decisions
                return ' '  # Hard drop
        
        ====================================================================
        EXAMPLE IMPLEMENTATIONS:
        ====================================================================
        
        Example 1: Simple rule-based bot
        ---------------------------------
        def decide(self, obs):
            if obs is None:
                return None
            
            current = obs["current_piece"]
            if current is None:
                return None
            
            # Move pieces to the left side
            if current["x"] > 3:
                return 'a'
            
            # Drop when in position
            return ' '
        
        Example 2: Grid analysis bot
        -----------------------------
        def decide(self, obs):
            if obs is None:
                return None
            
            grid = obs["grid"]
            current = obs["current_piece"]
            
            # Find the emptiest column
            col_heights = []
            for col in range(10):
                height = sum(1 for row in range(20) if grid[row][col] != 0)
                col_heights.append(height)
            
            best_col = col_heights.index(min(col_heights))
            
            # Move toward the best column
            if current["x"] < best_col:
                return 'd'
            elif current["x"] > best_col:
                return 'a'
            else:
                return ' '  # Drop!
        
        Example 3: ML model bot
        -----------------------
        def decide(self, obs):
            if obs is None:
                return None
            
            # Convert grid to numpy array
            grid_array = np.array(obs["grid"])
            
            # Get model prediction
            action_probs = self.model.predict(grid_array)
            action_idx = np.argmax(action_probs)
            
            # Map to action
            actions = ['w', 'a', 's', 'd', ' ', None]
            return actions[action_idx]
        
        ====================================================================
        TIPS & STRATEGIES:
        ====================================================================
        
        1. Start Simple: Begin with basic rules before adding ML
        2. Test Incrementally: Print debug info to see what's happening
        3. Consider Speed: Your code runs every ~120ms, keep it fast
        4. Plan Ahead: Use next_piece to inform your strategy
        5. Avoid Gaps: Try to minimize holes in your grid
        6. Clear Lines: Prioritize completing rows when possible
        7. Think Vertical: Keep some columns clear for I-pieces
        
        ====================================================================
        """
        
        # Safety check
        if obs is None:
            return None
        
        # ================================================================
        # IMPLEMENT YOUR BOT LOGIC BELOW THIS LINE
        # ================================================================
        
        # Extract game state components
        grid = obs["grid"]                    # 20x10 board
        current_piece = obs["current_piece"]  # Currently falling piece
        next_piece = obs["next_piece"]        # Next piece coming
        level = obs["level"]                  # Current difficulty
        
        # TODO: Add your decision logic here
        # Example: return 'a' to move left, 'd' to move right, etc.
        
        return None  # Replace with your logic
        
        # ================================================================
        # END OF YOUR IMPLEMENTATION
        # ================================================================
