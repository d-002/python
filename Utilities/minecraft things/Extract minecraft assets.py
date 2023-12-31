import json
import os
import shutil

MC_ASSETS = os.path.expandvars('%APPDATA%/.minecraft/assets')

_, _, filenames = next(os.walk('%s/indexes' %MC_ASSETS))
versions = ''
for file in filenames:
    versions += '%s, ' %file.split('.json')[0]
del _, filenames

print('Versions found: %s' %versions[:-2])
version = input('Enter one of these versions: ')
print()

path = 'Extracted - %s' %version

with open('%s/indexes/%s.json' %(MC_ASSETS, version)) as f:
    data = json.load(f)

    sounds = {}
    for (dest, src) in data['objects'].items():
        src = '%s/%s' %(src['hash'][:2], src['hash'])

        dest_path = os.path.dirname(dest)
        
        os.makedirs('%s/%s/%s' %(MC_ASSETS, path, dest_path), exist_ok=True)
        shutil.copyfile('%s/objects/%s' %(MC_ASSETS, src), '%s/%s/%s' %(MC_ASSETS, path, dest))

        print(dest)
