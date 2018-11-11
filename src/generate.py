import csv
import os.path
import constants as c
import datetime
import models.constraint_defs as constraint_defs
import models.ignore_player as ip

import models.solver as lu_solver


from command_line import get_args
from sqlalchemy import create_engine
from models.orm import lineup, player, gen_player, Base, proj_player
from sqlalchemy.orm import sessionmaker
from csv_parse import mlb_upload
from ortools.linear_solver import pywraplp
from ortools.constraint_solver import pywrapcp, solver_parameters_pb2
from helper.file_helper import rename_file
from models.name_resolver import resolve_name, resolve_team

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

    proj_dir = c.DIRPATHS['proj-gpp'] if args.gpp > 0 else c.DIRPATHS['projections']
    full_file_path = proj_dir + file_name
    with open(full_file_path, 'rb') as csv_file:
        csv_data = csv.DictReader(csv_file)
        player_not_found = []
        duplicate_found = []

        # hack for weird defensive formatting
        def name_match(row):
            def match_fn(p):
                if p.position == 'DST':
                    return p.name.strip() in row['playername']
                return p.name in resolve_name(row['playername']) and p.team == resolve_team(row['team'])
            return match_fn

        for row in csv_data:
            matching_players = filter(name_match(row), all_players)

            if len(matching_players) == 0 and resolve_team(row['team']) in (o.team for o in all_players):
                player_not_found.append(row)                
                continue

            if len(matching_players) > 1:
                duplicate_found.append(row)                
                continue

            for p in matching_players:
                p.projected = float(row['points'])
                p.gpp_percent = int(row['percentage']) if 'percentage' in row.keys() else 0
                

                
    player_not_found.sort(key=lambda pl: pl['team'])
    for pl in player_not_found:
         print('Projection not applied for player {} {}'.format(pl['team'], pl['playername']))

    for dup in duplicate_found:
        print('Duplicate found for player {} {}'.format(dup['team'], dup['playername']))

    missing_projections = [
        p for p in all_players if p.projected == 0.0 or p.salary < 1]
    with_projections = [
        p for p in all_players if p.projected > 0.0 and p.salary > 0 and p.name not in ip.ignore_player_list]
    print('Total Players missing projections: {}'.format(len(missing_projections)))
    print('Total Players with projections: {}'.format(len(with_projections)))
    return with_projections

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

def create_gpp_projection(lu, source):
    print('Building GPP list.')
    player_list = []
    add_list = []
    gpp_file = c.DIRPATHS['proj-gpp'] + c.FILEPATHS['gpp-file'].format(source, args.l, args.g)  
    with open(gpp_file, 'ab+') as gpp_csv:
        csv_data = csv.DictReader(gpp_csv)
        
        header = ['playername', 'points', 'team', 'percentage']
        
        for row in csv_data:
            player_list.append(proj_player(row['playername'], float(row['points']), row['team'], float(row['percentage'])))

        writer = csv.writer(gpp_csv)
        if gpp_csv.tell() == 0:        
            writer.writerow(header)
        
        for lup in lu.players:
            if not any(p.playername == lup.name and p.team == lup.team for p in player_list):                
                writer.writerow([lup.name, lup.projected, lup.team, 60])       
        
        
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
    proj_dir = c.DIRPATHS['proj-gpp'] if args.gpp > 0 else c.DIRPATHS['projections']
    for i, proj_file in enumerate(os.listdir(proj_dir)):
        info = proj_file.split('_')
        source = info[0]
        constraint_def = constraint_defs.set_constraints(info[1])

        # map to players
        players_with_projections = apply_projections(all_players, proj_file)                

        try:
            s = lu_solver.multi_solver_v_2()
            lups.extend(s.solve(players_with_projections, constraint_def, info, args))
        except Exception, e:
            print('Lineup solver failed: {0}'.format(str(e)))
    
    if(args.commit):
        print('Saving LUs.')
        session.add_all(lups)
        session.commit()        
        clean_files()

    if(args.gpp == 0):   
        create_gpp_projection(lups[0], source)
        
    if(args.upload):
        create_dk_upload(lups, constraint_def.export_order)
            
    for l in sorted(lups, key=lambda ls: ls.projected, reverse=True):
        print l   

    

print('Complete.')

