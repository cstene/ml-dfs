#The key is the projection name, the value is the draftkings name.
RENAMES = {
    'Eric Young': 'Eric Young Jr.',
    'Enrique Hernandez' : 'Kike Hernandez',
    'Nick Castellanos' : 'Nicholas Castellanos',
    'Shin-Soo Choo' : 'Shin-soo Choo',
    'J.T. Riddle' : 'JT Riddle',
    'Steven Souza' : 'Steven Souza Jr.',
    'Ronald Acuna' : 'Ronald Acuna Jr.',
    'Gregory Bird' : 'Greg Bird',
    'Nick Delmonico' : 'Nicky Delmonico'
}

def resolve_name(name):
    if name in RENAMES:
        return RENAMES[name]
    return name

