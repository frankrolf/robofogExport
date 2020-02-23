# remove the .finf folders, equivalent to .DS_Store on Mac OS 9

import os
import sys
import shutil


input_folder = os.path.normpath(sys.argv[-1])

for root, folders, files in os.walk(input_folder):
    for folder in folders:
        if folder == '.finf':
            shutil.rmtree(os.path.join(root, folder))

print('done')
