import argparse
import os

OPTIMIZE_COMMAND_LINE = [ 
    ['-test', 'my first commandline arg', False],
    ['-l', 'league ex: NFL, MLB', 'MLB'],
    ['-g', 'game number ex NFL Week 7 is the game number', 0],
    ['-y', 'league year', 2018],
    ['-commit', 'commit lineup to db.', False],
    ['-env', 'What environment to save to?', 'dev'],
    ['-clp', 'Cash line pts for 50/50', 0.0],
    ['-upload', 'Produce upload files', False],
    ['-gpp', 'Generates gpp lineups. If 0 generates optimal lu.', 0]
    # ['-game', 'game to play', 'draftkings'],
    # ['-w', 'current week', None],
    # ['-season', 'current season', None],
    # ['-historical', 'fetch historical data', 'n'],
    # [
    #     '-historical_date',
    #     'day from history to optimize on (use YYYY-MM-DD)',
    #     None
    # ],
    # ['-mp', 'missing players to allow', 100],
    # ['-sp', 'salary threshold to ignore', 0],
    # ['-ms', 'max salary for player on roster', 100000],
    # ['-v_avg', 'projections must be within points v avg', 100000],
    # ['-i', 'iterations to run', 1],
    # ['-lp', 'lowest acceptable projection', 0],
    # ['-po', 'highest acceptable ownership', 100],
    # ['-limit', 'disallow more than 1 player per team sans QB', 'n'],
    # ['-home', 'only select players playing at home', None],
    # ['-duo', 'force a QB + WR/TE duo on specific team', 'n'],
    # ['-no_double_te', 'disallow two tight end lineups', 'n'],
    # ['-teams', 'player must be on specified teams', None],
    # ['-locked', 'player must be in final lineup', None],
    # ['-banned', 'player cannot be named players', None],
    # ['-dtype', 'specify WR or TE in combo', 'wr'],
    # ['-league', 'league', 'NFL'],
    # ['-pids', 'player id file (create upload file)', None],
    # ['-keep_pids', 'Keep current upload file', None],
    # ['-po_location', 'projected ownership percentages file location', None],
    # ['-salary_file', 'file location for salaries',
    #  os.getcwd() + '/data/current-salaries.csv'],
    # ['-projection_file', 'file location for projections',
    #  os.getcwd() + '/data/current-projections.csv'],
    # ['-flex_position', 'force player to have FLEX position', None],
    # ['-randomize_projections', 'use random projection factor', None],
    # ['-min_avg', 'player must exceed average points', None],
]


MULTIPLE_ARGS_COMMAND = [
    # '-teams',
    # '-banned',
    # '-locked'
]

PARSER = argparse.ArgumentParser()


def get_args():
    for opt in OPTIMIZE_COMMAND_LINE:
        nargs = '?'
        if opt[0] in MULTIPLE_ARGS_COMMAND:
            nargs = '+'
        PARSER.add_argument(
            opt[0],
            nargs=nargs,
            help=opt[1],
            default=opt[2]
        )
    return PARSER.parse_args()
