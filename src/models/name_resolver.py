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
    'Nick Delmonico' : 'Nicky Delmonico',
    'Yulieski Gurriel' : 'Yuli Gurriel',
    'Jakob Bauers' : 'Jake Bauers',
    'Jackie Bradley' : 'Jackie Bradley Jr.',
    'Lourdes Gurriel' : 'Lourdes Gurriel Jr.',
    'Willie Snead' : 'Willie Snead IV',
    'Duke Johnson' : 'Duke Johnson Jr.',
    'Will Fuller' : 'Will Fuller V',
    'D.J. Chark' : 'D.J. Chark Jr.',
    'Melvin Gordon' : 'Melvin Gordon III',
    'AJ Derby' : 'A.J. Derby',
    'CJ Ham' : 'C.J. Ham',
    'Ted Ginn' : 'Ted Ginn Jr.',
    'Wayne Gallman' : 'Wayne Gallman Jr.',
    'Odell Beckham' : 'Odell Beckham Jr.',
    'Juju Smith-Schuster' : 'JuJu Smith-Schuster',
    'Ronald Jones' : 'Ronald Jones II',
    'Robert Kelley' : 'Rob Kelley',
    'Paul Richardson' : 'Paul Richardson Jr.',
    'Todd Gurley' : 'Todd Gurley II',
    'Marvin Jones' : 'Marvin Jones Jr.',
    'Ray-Ray McCloud' : 'Ray-Ray McCloud III',
    'Allen Robinson' : 'Allen Robinson II',
    'Dwayne Washington' : 'Deandre Washington',
    'Sammie Coates' : 'Sammie Coates Jr.',
    'Khadarel Hodge' : 'KhaDarel Hodge'
}

TEAM_NAMES = {
    'NEP' : 'NE',
    'NOS' : 'NO',
    'JAC' : 'JAX',
    'GBP' : 'GB',
    'SFO' : 'SF',
    'TBB' : 'TB',
    'KCC' : 'KC'
}

def resolve_name(name):
    if name in RENAMES:
        return RENAMES[name]
    return name

def resolve_team(name):
    if name in TEAM_NAMES:
        return TEAM_NAMES[name]
    return name

