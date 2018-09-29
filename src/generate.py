import csv
import os.path
import constants as c
import datetime
import models.constraint_defs as constraint_defs
import models.ignore_player as ip
import models.solver as lu_solver

from command_line import get_args
from sqlalchemy import create_engine
from models.orm import lineup, player, gen_player, Base
from sqlalchemy.orm import sessionmaker
from csv_parse import mlb_upload
from ortools.linear_solver import pywraplp
from ortools.constraint_solver import pywrapcp, solver_parameters_pb2
from helper.file_helper import rename_file
from models.name_resolver import resolve_name

args = None
engine = None
session = None

def retrieve_players_with_salaries():
    print('Retrieve players with salaries')
    all_players = []
    with open(c.FILEPATHS['salaries'], 'rb') as csv_file:
        csv_data = csv.DictReader(csv_file)

        for row in csv_data:
                for pos in row['Position'].split('/'):
                    all_players.append(gen_player(pos, row))

    print('Player count: {}'.format(len(all_players)))
    return all_players


def apply_projections(all_players, file_name):
    print('Apply projections from file {}'.format(file_name))

    full_file_path = c.DIRPATHS['projections'] + file_name
    with open(full_file_path, 'rb') as csv_file:
        csv_data = csv.DictReader(csv_file)
        player_not_found = []

        # hack for weird defensive formatting
        def name_match(row):
            def match_fn(p):
                if p.position == 'DST':
                    return p.name.strip() in row['playername']
                return p.name in resolve_name(row['playername'])
            return match_fn

        for row in csv_data:
            matching_players = filter(name_match(row), all_players)

            if len(matching_players) == 0:
                player_not_found.append(row)                
                continue

            for p in matching_players:
                p.projected = float(row['points'])

    player_not_found.sort(key=lambda pl: pl['team'])
    for pl in player_not_found:
         print('Projection not applied for player {} {}'.format(pl['team'], pl['playername']))

    missing_projections = [
        p for p in all_players if p.projected == 0.0 or p.salary < 1]
    with_projections = [
        p for p in all_players if p.projected > 0.0 and p.salary > 0 and p.name not in ip.ignore_player_list]
    print('Total Players missing projections: {}'.format(len(missing_projections)))
    print('Total Players with projections: {}'.format(len(with_projections)))
    return with_projections


def run_solver(solver, players):
    print('Running solver...')
    variables = []

    #Define the variables
    for p in players:
        variables.append(solver.IntVar(0, 1, p.solver_id()))

    #Define the constraints

    #todo come back to this one.
    # set multi-player constraint
    # multi_caps = {}
    # for i, p in enumerate(players):
    #      if not p.multi_position:
    #         continue

    #      if p.name not in multi_caps:
    #         multi_caps[p.name] = solver.Constraint(0, 1)

    #      multi_caps[p.name].SetCoefficient(variables[i], 1)

    # set salary cap constraint
    #salary_cap = solver.Constraint(
    #    0,
    #    50000,
    #)
    salaryConstraint = 0
    for i, p in enumerate(players):
        salaryConstraint += variables[i] * p.salary
    solver.Add(salaryConstraint < 50000)    
        #solver.Add(variables[i] * p.salary < 50000)
        #solver.Add(1 * variables[i] == 9)
        #solver.Add(constraints <= 50000)    
    
        
    #set roster size constraint
    #size_cap = solver.Constraint(
    #   constraint_def.num_of_players,
    #   constraint_def.num_of_players
    #)

    size_cap = 0 
    for variable in variables:
        size_cap += variable
    solver.Add(size_cap == constraint_def.num_of_players)
    #    solver.Add(1 * variable == constraint_def.num_of_players)
    #    #size_cap.SetCoefficient(variable, 1)

    #  # set position limit constraint    
    for position, min_limit, max_limit \
            in constraint_def.pos_def:
    
        position_cap = 0
    #     #position_cap = solver.Constraint(min_limit, max_limit)

        for i, player in enumerate(players):
            if position == player.position:
                position_cap += variables[i]
        
        solver.Add(position_cap >= min_limit)
        solver.Add(position_cap <= max_limit)
    #             solver.Add(1 * variables[i] >= min_limit)
    #             solver.Add(1 * variables[i] <= max_limit)
    #             #position_cap.SetCoefficient(variables[i], 1)

    #set objective
    #objective = solver.Objective()
    #objective.SetMaximization()

    obj_expr = solver.IntVar(50, 50, "obj_expr")
    objective = solver.Maximize(obj_expr, 1)
    
    # optimize on projected points
    obj = 0
    for i, p in enumerate(players):
        obj += variables[i] * int(p.projected * 100)
        #solver.Add(obj_expr == variables[i] * int(p.projected * 100))    
        #obj_eq += variables[i] * int(p.projected * 100)
        
        #objective.SetCoefficient(variables[i], p.projected)
    
    #solver.Add(obj_expr < obj)    
    decision_builder = solver.Phase(variables, solver.CHOOSE_FIRST_UNBOUND, solver.ASSIGN_MIN_VALUE)
    #decision_builder = solver.Phase(variables, solver.CHOOSE_LOWEST_MIN, solver.ASSIGN_MIN_VALUE)
    #decision_builder = solver.Phase(variables, solver.CHOOSE_RANDOM, solver.ASSIGN_RANDOM_VALUE)
    collector = solver.AllSolutionCollector()
    for v in variables:
        collector.Add(v)
    #collector.AddObjective(obj_expr)    

    print("Solve the problem")
    #solver.Solve(decision_builder, [objective,collector])
    solver.Solve(decision_builder, collector)

    print('Solutions found: {}'.format(collector.SolutionCount()))

    if(collector.SolutionCount() > 0):
        best_solution = collector.SolutionCount() - 1
        print("Objective value:", collector.ObjectiveValue(best_solution))
        
        for v in variables:
            if(collector.Value(best_solution, v) == 1):
                print(v)
     
    #print('x= ', collector.Value(best_solution, x))
    #print('y= ', collector.Value(best_solution, y))
    #return variable, collector.SolutionCount() - 1


def pre_req_check():
    print('Check pre reqs...')
    preReqs = [
        c.FILEPATHS['salaries']
    ]

    for pr in preReqs:
        if not os.path.isfile(pr):
            raise Exception('File not found {}'.format(pr))

    if(args.commit and args.g == 0):
        msg = '''Game number (-g) must be specified to save to database.
                 -l is {} -y is {}'''.format(args.l, args.y)
        raise Exception(msg)


def init_db():
    global engine
    global session
    engine = create_engine(c.DB['dfs'] + '{}.db'.format(args.env))
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()


def clean_lineups():
    current_lus = session.query(lineup).filter_by(
        league=args.l, league_year=args.y, league_game=int(args.g))
    for cl in current_lus:
        session.delete(cl)
    session.commit()


def clean_files():
    print('Moving salaries and projections to history.')
    # create history folder
    date_str = datetime.datetime.today()
    dir_name = "g{} {}-{}-{}".format(args.g, date_str.month,
                                     date_str.day, date_str.year) + '/'
    dir_path = c.DIRPATHS['history'] + dir_name
    proj_path = dir_path + 'projections/'

    if not os.path.exists(proj_path):
        os.makedirs(proj_path)

    # move salaries
    rename_file(c.FILEPATHS['salaries'], dir_path + 'current-salaries.csv')

    # move projections
    for i, file_name in enumerate(os.listdir(c.DIRPATHS['projections'])):
        rename_file(c.DIRPATHS['projections'] +
                    file_name, proj_path + file_name)


def create_dk_upload(lups, pos_order):
    print('Create lu_upload for DK.')
    with open(c.FILEPATHS['lu_upload'], 'wb') as lu_upload:
        lu_upload_writer = csv.writer(lu_upload)
        lu_upload_writer.writerow(pos_order)

        for lu in lups:
            sorted_players = lu.sorted_players()
            lu_upload_writer.writerow([
                p.player_id for p in sorted_players
            ])

if __name__ == '__main__':
    args = get_args()  

    pre_req_check()

    # Do we need a database?
    engine = None
    session = None
    
    if(args.commit):        
        init_db()
        clean_lineups()
    else:
        print('Nothing will be saved to database. Files will not be cleaned up.')


    all_players = retrieve_players_with_salaries()

    lups = []
    constraint_def = None
    for i, proj_file in enumerate(os.listdir(c.DIRPATHS['projections'])):        
        info = proj_file.split('_')
        source = info[0]
        constraint_def = constraint_defs.set_constraints(info[1])
        # solver = pywraplp.Solver(
        #     'FD',
        #     pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING
        # )
        params = pywrapcp.Solver.DefaultSolverParameters()
        solver = pywrapcp.Solver('FD', params)

        # map to players
        players_with_projections = apply_projections(all_players, proj_file)        

        # find optimized solution
        #variables, solution = run_solver(solver, players_with_projections)
        s = lu_solver.multi_solver()
        lups = s.solve(players_with_projections, constraint_def, info, args)

        # if solution == solver.OPTIMAL:            
        #     print("We have a solution for {} projections".format(source))
        #     # need to update index when we have multi solutions per projections, set to 0 for now
        #     lu = lineup(info[1],args.y,args.g,source,0,constraint_def.sort_func)

        #     for j, player in enumerate(players_with_projections):
        #         if variables[j].solution_value() == 1:                    
        #             lu.players.append(player)
            
        #     lu.run_init_calc()
        #     lups.append(lu)

        # else:
        #     print("No solution found for {} bro.".format(source))
    
    if(args.commit):
        print('Saving LUs.')
        session.add_all(lups)
        session.commit()        
        clean_files()   

    if(args.upload):
        create_dk_upload(lups, constraint_def.export_order)
            
    for l in sorted(lups, key=lambda ls: ls.projected, reverse=True):
        print l   

print('Complete.')

