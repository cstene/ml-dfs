import os.path

base_path = os.path.dirname(os.path.abspath(__file__))
FILEPATHS = {
    'salaries' : base_path + "/data/current-salaries.csv",
    'lu_upload' : base_path + "/data/lu_upload.csv",
    'results' : base_path + "/data/results.csv",
    
}

DIRPATHS = {
    'projections' : base_path + "/data/projections/",
    'history' : base_path + "/history/"
}

DB = {
    'dfs': "sqlite:///{}/data/dfs-".format(base_path)
}

PROJECTED_URLS = {
    'MLB' :['https://rotogrinders.com/projected-stats/mlb-hitter.csv?site=draftkings',
            'https://rotogrinders.com/projected-stats/mlb-pitcher.csv?site=draftkings'],
    'NFL' :['https://rotogrinders.com/projected-stats/nfl-qb.csv?site=draftkings',
            'https://rotogrinders.com/projected-stats/nfl-rb.csv?site=draftkings',
            'https://rotogrinders.com/projected-stats/nfl-wr.csv?site=draftkings',
            'https://rotogrinders.com/projected-stats/nfl-te.csv?site=draftkings',
            'https://rotogrinders.com/projected-stats/nfl-defense.csv?site=draftkings'            
    ]
}

