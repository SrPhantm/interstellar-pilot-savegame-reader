from tools_v2 import SaveReader

save = [
    'saves/051_Pixelfactor_002.dat',
    'saves/AutoSave0.dat',
    'saves/Player_Shuttle.dat',
    'saves/055_Player_001.dat'
][3]

with open(save, 'rb') as f:
    save_reader = SaveReader(f.read())

save_reader.run()