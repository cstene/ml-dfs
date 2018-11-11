class player_ownership_service(object):
    players = []
    def __init__(self, num_of_lu):
        self.num_of_lu = num_of_lu

    def add(self, lu):
        for p in lu.players:
            p.gpp_usage += 1
            if p not in self.players:                
                self.players.append(p)   
                
    def get_used_players_by_name(self):
        return [p.name for p in self.players if (p.gpp_usage/self.num_of_lu) >= p.gpp_percent]