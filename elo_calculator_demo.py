import math

class testPlayer():
    def __init__(self, playerId,  lastPlay, uncertainty=0.5) -> None:
        self.playerId = playerId
        self.rating = 10 # placeholder, not sure
        self.uncertainty = uncertainty
        self.lastPlayed = lastPlay

class testLandmark():
    def __init__(self, landmarkId, lastAnswered, uncertainty=0.5) -> None:
        self.landmarkId = landmarkId
        self.rating = 10 # placeholder, not sure
        self.uncertainty = uncertainty
        self.lastAnswered = lastAnswered


class testEloCalculator():

    def __init__(self, players, landmarks) -> None:
        self.players = players
        self.landmarks = landmarks

    def calculateElo(self, player:testPlayer, landmark:testLandmark, minutes_used, time_limit_minutes=20, correct=True):
        """sumary_line
        
        q^_player = q_player + K_player(S_hshs - E(S_hshs))
        q^_riddle = q_riddle + K_riddle(E(S_hshs) - S_hshs)

        Keyword arguments:
        argument: description
        Return: return_description
        """
        
    
        K_player, K_riddle = self._dynamicK(player, landmark)
        hshs, expectation = self._hshs(minutes_used *  60, player.rating, landmark.rating, time_limit_minutes * 60, correct)

        player.rating += K_player * (hshs - expectation)
        landmark.rating -= K_riddle * (hshs - expectation)

        return

    def _dynamicK(self, player: testPlayer, landmark:testLandmark, test_mode=True):
        """
        Glickman's K factor in CAP system calculates the rating uncertainty U of the player and the item 

        K_player = K(1 + K_+ * U_player - K_- * U_riddle)
        K_riddle = K(1 + K_+ * U_riddle - K_- * U_player)
        """
        
        K, K_plus, K_minus = 0.0075, 4, 0.5 

        player.uncertainty = self._updateUncertainty(player.uncertainty, test_mode)
        landmark.uncertainty = self._updateUncertainty(landmark.uncertainty, test_mode)

        K_player = K * (1 + K_plus * player.uncertainty - K_minus * landmark.uncertainty)
        K_riddle = K * (1 + K_plus * landmark.uncertainty - K_minus * player.uncertainty)
        
        return K_player, K_riddle
    
    def _updateUncertainty(self, current_U, day_since_last_play=30, test_mode=False):
        """
        
        Update uncertainty based on last interaction time and total sessions
        
        U = U - 1/40 + 1/30 * D

        Keyword arguments:
            current_U (float): Current uncertainty lev [0, 1]
            day_since_last_play (int): inactivity time 

        Return: 
            update uncertainty (float)
        """
        if test_mode:
            return current_U
        else:
            U_new = current_U - (1/40.0) + (1/30.0) * day_since_last_play
            return max(0, min(1, U_new))
        

    def _hshs(self, seconds_used, player_rating, landmark_rating, time_limit, correct):
        """
        Comupute High-Speed High-Stakes(HSHS) score and Expectation .

        HSHS: s_ij = (2 * x_ij - 1) * (a_i * d_i - a_i * t_ij)

        E(HSHS): a_i * d_i * (
            (e^ (2 * a_i * d_i) * (theta_j - beta_i) + 1)/
            (e^ (2 * a_i * d_i) * (theta_j - beta_i) - 1)
            ) - (1 / (theta_j - beta_i))
        
        Keyword arguments:
            time_limit(float): Max allowed seconds for the riddle(d_i)
            time_used(float): Actual response seconds(t_ij)
            correct(bool): Whether the answer is correct (x_ij) = 1 if correct else 0
            player_rating (float): Player's skill level (theta_j)
            landmark_rating (float): Landmark's difficulty level (beta_i)

        Return: 
            hshs (float) 
        """

        ### HSHS
        # discrimination a_i = 1 / d_i (d_i is time_limit)
        discrimination = self._discrimination(time_limit)
        
        # calculate (a_i * d_i - a_i * t_ij) = a_i * (d_i - t_ij)
        time_component = discrimination * (time_limit - seconds_used)
        
        # apply(2 * x_ij - 1) factor
        hshs = time_component if correct else -time_component

        ### Expectation
        delta = player_rating - landmark_rating
        if abs(delta) < 1e-6:
            delta = 1e-6

        weight_ability_difference = 2 * discrimination * time_limit * (delta)
        exp_term = math.exp(weight_ability_difference)
        expectation = discrimination * time_limit * ((exp_term + 1) / (exp_term - 1)) - (1 / delta)

        return hshs, expectation
    
    def _discrimination(self, time_limit, mode="default"):   
        
        """
        Allowing mode="default" and fallback 1/10, expandable for future work like “different judgement rate for different riddle types”
        """
        
        return 1.0/time_limit if mode == "default" else 1/10
        

# class testSession():
#     def __init__(self, player, landmark, minutes_used, minutes_limit = 20, is_correct=True) -> None:
#         self.player = player
#         self.landmark = landmark
#         self.time_limit_seconds = minutes_limit * 60
#         self.seconds_used = minutes_used * 60
#         self.correct = is_correct


if __name__ == "__main__":
    print("hello world")