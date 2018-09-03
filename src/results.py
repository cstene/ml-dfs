import os.path
import csv
import datetime
from helper.file_helper import rename_file
from command_line import get_args
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.orm import lineup, player, gen_player, Base
from models.name_resolver import resolve_name
import models.constraint_defs as constraint_defs

import constants as c

def load_results():
    print('Retrieve player results')
    player_results = {}
    with open(c.FILEPATHS['results'], 'rb') as csv_file:        
        csv_data = csv.DictReader(csv_file)

        for row in csv_data:
            player_results[resolve_name(row['Player'])] = row['Fpts']         

    print('Player count: {}'.format(len(player_results)))
    return player_results

def init_db():
    global engine
    global session
    engine = create_engine(c.DB['dfs'] + '{}.db'.format(args.env))
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

def pre_req_check():
    print('Check pre reqs...')

    preReqs = [
        c.FILEPATHS['results']        
    ]

    for pr in preReqs:
        if not os.path.isfile(pr):
            raise Exception('File not found {}'.format(pr))

    if(args.g == 0):
        msg = '''Game number (-g) must be specified.
                 -l is {} -y is {}'''.format(args.l, args.y)
        raise Exception(msg)

    if(args.clp == 0):
        msg = 'Plese indicate the cash_line points.'
        raise Exception(msg)

def clean_files():
    print('Moving results to history.')
    #create history folder 
    date_str = datetime.datetime.today() - datetime.timedelta(days=1)
    dir_name = "g{} {}-{}-{}".format(args.g, date_str.month, date_str.day, date_str.year) + '/'
    dir_path = c.DIRPATHS['history'] + dir_name
    proj_path = dir_path + 'projections/'

    if not os.path.exists(proj_path):
        raise Exception("History path not found. Please resolve manually")
   
    #move salaries    
    rename_file(c.FILEPATHS['results'], dir_path + 'results.csv')
    
if __name__ == '__main__':
    args = get_args() 
    pre_req_check()
    
    init_db()

    results = load_results()

    constraint_def = constraint_defs.set_constraints(args.l)

    current_lus = session.query(lineup).filter_by(league=args.l, league_year=args.y, league_game=int(args.g))
    for cl in current_lus:
        cl.cash_line = float(args.clp)        
        for p in cl.players:
            if(p.name in results):
                p.actual = float(results[p.name])
            else:
                p.actual = 0.0
                print('{} had no results'.format(p.name))
        
        cl.run_results_calc()
    
    for l in sorted(current_lus, key=lambda ls: ls.actual, reverse=True):
        l.sort_func = constraint_def.sort_func
        print l

    if(args.commit):
        print("Saving results")
        session.commit()
        clean_files()
    else:
        print("Results were NOT saved.")

        
    



    


    #Fetch Players from db.
    

    #Fetch results from csv.

    #Show report and save back to db.
    