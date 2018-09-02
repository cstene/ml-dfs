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

