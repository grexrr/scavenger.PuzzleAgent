class eloCalculatorDemo():

    def __init__(self) -> None:
        pass

    def calculateElo(self, player, landmark):
        """sumary_line
        
        q^_player = q_player + K_player(S_hshs - E(S_hshs))
        q^_riddle = q_riddle + K_riddle(E(S_hshs) - S_hshs)

        Keyword arguments:
        argument: description
        Return: return_description
        """
        
        return

    def dynamicK(self):
        """
        Glickman's K factor in CAP system calculates the rating uncertainty U of the player and the item 

        K_player = K(1 + K_+ * U_player - K_- * U_riddle)
        K_riddle = K(1 + K_+ * U_riddle - K_- * U_player)
        
        Keyword arguments:
        argument: description
        Return: return_description
        """
        
        return
    
    def updateUncertainty(self, current_U, day_since_last_play):
        """
        
        Update uncertainty based on last interaction time and total sessions
        
        U = U - 1/40 + 1/30 * D

        Keyword arguments:
            current_U (float): Current uncertainty lev [0, 1]
            day_since_last_play (int): inactivity time 

        Return: 
            update uncertainty (float)
        """

        U_new = current_U - (1/40.0) + (1/30.0) * day_since_last_play
        return max(0, min(1, U_new))
        

    def hshs(self, time_used_seconds, time_limit=20, correct=True):
        """
        Comupute High-Speed High-Stakes(HSHS) score.

        s_ij = (2 * x_ij - 1) * (a_i * d_i - a_i * t_ij)
        
        Keyword arguments:
            time_limit(float): Max allowed minutes for the riddle(d_i)
            time_used(float): Actual response seconds(t_ij)
            correct(bool): Whether the answer is correct (x_ij) = 1 if correct else 0

        Return: 
            hshs (float) 
        """
        
        time_limit_seconds = time_limit * 60

        # discrimination a_i = 1 / d_i (d_i is time_limit)
        discrimination = 1.0 / time_limit_seconds
        
        # calculate (a_i * d_i - a_i * t_ij) = a_i * (d_i - t_ij)
        time_component = discrimination * (time_limit_seconds - time_used_seconds)
        
        # apply(2 * x_ij - 1) factor
        hshs = time_component if correct else -time_component
        
        return hshs
    
class testPlayer():
    def __init__(self, playerId) -> None:
        self.playerId = playerId
        self.rating = 10 # placeholder, not sure
        self.uncertainty = 1.0

class testLandmark():
    def __init__(self, landmarkId) -> None:
        self.landmarkId = landmarkId
        self.rating = 10 # placeholder, not sure
        self.uncertainty = 1.0


if __name__ == "__main__":
    print("hello world")