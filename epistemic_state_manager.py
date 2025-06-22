class EpistemicStateManager:
    """Modeling Player Knowledge Map
    
    argument: player's userId->solvedLandmarkId
    Return: player's knowledge 
    """
    
    def __init__(self, userId) -> None:
        self.playerId = userId
        self.solved_landmarkId = []
        self.knownledge = {}
        self.previous_riddles = []
        pass

    def load_player_history(self):
        """
        Load User's known landmarks and their metadata.
        Build knowledge state + theme.
        """
        pass

    def get_state(self):
        return self.knownledge
    
    def get_previous_context(self):
        return {
            "previous_riddle": self.previous_riddles[-1] if self.previous_riddles else None,
        }