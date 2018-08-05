import os.path

base_path = os.path.dirname(os.path.abspath(__file__))
FILEPATHS = {
    'salaries' : base_path + "/data/current-salaries.csv",
    'template' : base_path + "/data/template.csv",
    'results' : base_path + "/data/results.csv"
}

DIRPATHS = {
    'projections' : base_path + "/data/projections"
}

DB = {
    'dfs': "sqlite:///{}/data/dfs-".format(base_path)
}

POSITIONS = {
    'MLB' : [
        ['SP', 2, 2],
        ['C', 1, 1],
        ['1B', 1, 1],
        ['2B', 1, 1],
        ['3B', 1, 1],
        ['SS', 1, 1],
        ['OF', 3, 3],
    ]
}