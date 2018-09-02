class NFL_constraints():
    num_of_players = 9
    pos_def = [
        ['QB', 1, 1],
        ['RB', 2, 3],
        ['WR', 3, 4],
        ['TE', 1, 1],
        ['DST', 1, 1]
    ]
    sort_order = {
        'QB': 0,
        'RB': 1,
        'WR': 2,
        'TE': 3,
        'FLEX' : 4,
        'DST': 5
    }
    export_order = [
        'QB', 
        'RB', 
        'RB',
        'WR', 
        'WR', 
        'WR', 
        'TE', 
        'FLEX', 
        'DST'
        ]
    

    def sort_func(self, players):
        #Find the flex and set the position.        
        rb_list = [p for p in players if p.position == 'RB'] 
        wr_list = [p for p in players if p.position == 'WR']
        te_list = [p for p in players if p.position == 'TE']

        if len(rb_list) > 2:
            rb_list[2].position = 'FLEX'
        elif len(wr_list) > 3:
            wr_list[3].position = 'FLEX'
        elif len(te_list) > 1:
            te_list[1].position = 'FLEX' 

        return sorted(
            players,
            key=lambda p: self.sort_order[p.position]
        )


class MLB_constraints():
    num_of_players = 10
    pos_def = [
        ['SP', 2, 2],
        ['C', 1, 1],
        ['1B', 1, 1],
        ['2B', 1, 1],
        ['3B', 1, 1],
        ['SS', 1, 1],
        ['OF', 3, 3],
    ]
    sort_order = {
        'P': 0,
        'SP': 0,
        'C': 1,
        '1B': 2,
        '2B': 3,
        '3B': 4,
        'SS': 5,
        'OF': 6,
        'RP': 7,
    }
    export_order = [
        'P',
        'P',
        'C',
        '1B',
        '2B',
        '3B',
        'SS',
        'OF',
        'OF',
        'OF',
    ]    
    
    def sort_func(self, players):
        return sorted(
            players,
            key=lambda p: self.sort_order[p.position]
        )


def set_constraints(game_type):
    if game_type.upper() == 'NFL':
        return NFL_constraints()
    elif game_type.upper() == 'MLB':
        return MLB_constraints()
    else:
        raise Exception(
            '{} is not a game type. Constraints cannot be set.'.format(game_type))
