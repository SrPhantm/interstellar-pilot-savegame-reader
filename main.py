import json
import copy
from tools import SaveReader

save_file = [
    'saves/051_Pixelfactor_002.dat',
    'saves/AutoSave0.dat',
    'saves/Player_Shuttle.dat',
    'saves/055_Player_001.dat'
][3]

with open(save_file, 'rb') as f:
    reader = SaveReader(f.read())

save = {}
save['header'] = reader.readHeader()
save['seconds_eslapsed'] = reader.readDouble()
save['sectors'] = reader.readSectors()
save['factions'] = reader.readFactions()
save['patrol_paths'] = reader.readPatrolPaths()
save['faction_relations'] = reader.readFactionRelations()
save['faction_opinions'] = reader.readFactionOpinions()

print(save)

with open('data.json', 'w') as f:
    json.dump(save, f, indent=2)
