import time
from zipfile import ZipFile

prev = time.time()

zip = ZipFile('zip.zip')

print('Please wait... ', end='')
zip.extractall('zip')
print('Completed in %.2fs' %(time.time() - prev))
