from os import path, getcwd, pardir

#TODO: this some ass
# Also add some fallback paths don't rely on drive letters
def get_local_net_drives():
    """
    Makes a dict with all the local network drives and their paths.

    Returns:
        dict : {"Drive Name": "E:/", "Drive 2 Name": "X:/"}
    """
    drives, total, resume = win32net.NetUseEnum(None, 0)

    net_drives = {}
    
    for drive in drives:
        for key in drive:
            if key == 'local':
                net_drives[drive['remote'].split('\\')[-1]] = drive[key]
                
    return net_drives

#drives = get_local_net_drives()

#This is a really bad way to handle paths, i get that i wanted to use this to save time when opening the same paths over and over, but hardcoding these with
#a windows spesifi libary is not great

PROJECT = path.join(getcwd())
ASSETS = path.join(PROJECT, 'assets')
SCHEMES = path.join(PROJECT, 'schemes')
STYLE = ''
with open(path.join( ASSETS, 'stylesheet', 'Combinear.qss'), 'r') as style:
    STYLE = style.read()
LOGO = path.join(ASSETS, 'abf_logo.png')


'''
LOC_DOCUMENTS = path.expanduser('~') + "\\Documents\\"
LOC_2016 = f"{drives['2016']}\\"
LOC_SKOLE = LOC_2016 + "Skole 2022\\"
LOC_BESTELLINGS = f"{drives['Bestellings']}\\BESTELLINGS\\"
LOC_SCHEMES = f"{LOC_DOCUMENTS}brenda\\schemes\\"
STYLE = ""
LOC_ASSETS = f"{LOC_DOCUMENTS}brenda\\assets\\"
LOGO = f"{LOC_ASSETS}logo\\abf_logo.png"

with open(f"{LOC_ASSETS}stylesheet\\Combinear.qss", 'r') as style:
    STYLE = style.read()
'''
