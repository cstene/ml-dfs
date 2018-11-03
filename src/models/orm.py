from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Sequence, Float, Boolean, Table, ForeignKey
from sqlalchemy.orm import relationship
from terminaltables import AsciiTable

Base = declarative_base()
lineup_player_association = Table('lineup_player_association', Base.metadata,
                                  Column('lineup_id', Integer,
                                         ForeignKey('lineup.id')),
                                  Column('player_id', Integer,
                                         ForeignKey('player.id'))
                                  )


class lineup(Base):
    __tablename__ = 'lineup'

    #Columns
    id = Column(Integer, Sequence('lineup_id_seq'), primary_key=True)
    league = Column(String(10))
    league_year = Column(Integer)
    league_game = Column(Integer)
    projected = Column(Float(4))
    actual = Column(Float(4))
    salary = Column(Integer)
    projection_source = Column(String(50))
    cash_line = Column(Float(4))
    is_winner = Column(Boolean)
    solution_index = Column(Integer)
    num_of_zero = Column(Integer)
    players = relationship("player", secondary=lineup_player_association,
                           back_populates="lineups", cascade="all,delete")
    
    #Props
    sort_order = {}
    sort_func = None

    def __init__(
        self,
        league,
        league_year,
        league_game,
        projection_source,
        solution_index,
        sort_func,
        projected=0.0,
        salary=0,
        actual=0.0,
        cash_line=0.0,
        is_winner=False,
        num_of_zero=0
    ):
        self.league = league
        self.league_year = league_year
        self.league_game = league_game
        self.projected = projected
        self.salary = salary
        self.sort_func = sort_func
        self.projection_source = projection_source
        self.solution_index = solution_index
        self.actual = actual
        self.cash_line = cash_line
        self.is_winner = is_winner
        self.num_of_zero = num_of_zero

    def run_init_calc(self):
        self.salary = sum(p.salary for p in self.players)
        self.projected = sum(p.projected for p in self.players)

    def run_results_calc(self):
        self.actual = sum(p.actual for p in self.players)
        self.is_winner = self.actual > float(self.cash_line)
        self.num_of_zero = len([p for p in self.players if p.actual == 0.0])

    def sorted_players(self):
        return self.sort_func(self.players)
        # return sorted(
        #     self.players,
        #     key=lambda p: self.sort_order[p.position]
        # )

    def __repr__(self):
        table_data = []
        headers = [
            'Position',
            'Player',
            'Team',
            'Salary',
            'Projection'
        ]

        if(self.actual > 0):
            headers.append('Actual')
        else:
            headers.append('Value')

        table_data.append(headers)
        #self.players.sort(key=lambda p: p.salary, reverse=True)

        for x in self.sorted_players():
            table_data.append([
                x.position,
                x.name,
                x.team,
                x.salary,
                x.projected,
                x.actual if self.actual > 0 else x.get_value()
            ])

        table = AsciiTable(table_data).table

        aggregate_info = '\nProjected Score: {} \t Cost: ${}'.format(
            str(self.projected),
            str(self.salary))

        aggregate_info += '\nActual Score: {} \t Winner: {}'.format(
            str(self.actual), self.is_winner)

        source = '\nProjection Source: {} \t Solution: {}'.format(
            self.projection_source, self.solution_index)

        return table + aggregate_info + source + '\n'


class player(Base):
    __tablename__ = 'player'

    # SQL lite table definitions
    id = Column(Integer, Sequence('player_id_seq'), primary_key=True)
    name = Column(String(100))
    position = Column(String(10))
    projected = Column(Float(4))
    actual = Column(Float(4))
    salary = Column(Integer)
    team = Column(String(100))
    lineups = relationship(
        "lineup", secondary=lineup_player_association, back_populates="players")

    def __init__(
        self,
        name,
        position,
        salary,
        projected=0.0,
        actual=0.0,
        team=None,
        possible_positions=None,
        multi_position=False,
        matchup=None,
        player_id=0
        #average_score, lock
    ):
        self.name = name
        self.position = position
        self.salary = salary
        self.projected = projected
        self.actual = actual
        self.team = team
        self.possible_positions = possible_positions
        self.multi_position = multi_position
        self.matchup = matchup
        self.player_id = player_id

    def solver_id(self):
        return '{} {} {}'.format(self.name, self.position, self.team)

    def get_value(self):
        return round(self.projected / self.salary * 1000.0, 2)

    def to_proj_player(self, percentage):
        return proj_player(self.name, self.projected, self.team, percentage)

class proj_player():
    def __init__(self, 
        name,
        projection,
        team,
        percentage=100
    ):
        self.playername = name
        self.projection = projection
        self.team = team
        self.percentage = percentage



def gen_player(pos, row):
    return player(
        row['Name'],
        pos,
        int(row['Salary']),
        possible_positions=row['Position'],
        multi_position=('/' in row['Position']),
        team=row.get('teamAbbrev') or row.get('TeamAbbrev'),
        matchup=row.get('GameInfo') or row.get('Game Info'),
        player_id=int(row['ID'])
        # average_score=avg,
        #lock=(args.locked and row[name_key] in args.locked)
    )


