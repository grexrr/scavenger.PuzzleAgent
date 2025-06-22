class EpistemicPlanner:

    def __init__(self, player_state) -> None:
        self.player_state = player_state

    def evaluate_landmark(self, target_meta:dict) -> dict:
        """
        Compare target landmark keywords and player familiar landmark types(player knowledge)
        Return difficulty + epistemic hint
        """
        novelty_score = self._compute_novelty(target_meta)
        hint = None
        
        if novelty_score > 0.75:
            difficulty = "easy"
            hint = "Player is unfamiliar with: " + self._unfamiliar_keywords(target_meta)
        elif novelty_score > 0.4:
            difficulty = "medium"
        else:
            difficulty = "hard" 

        return {
            "difficulty": difficulty,
            "hint": hint,
            "novelty_score": novelty_score
        }
    
    def _compute_novelty(self, meta):
        pass

    def _unfamiliar_keywords(self, meta):
        """Return unfamiliar keyword (for hinting purpose)"""
        pass