import os
import sys
from glob import glob

currentPath = os.path.dirname(__file__)

jars = glob(currentPath+'/poi-4.1.2/*') + glob(currentPath+'/poi-4.1.2/*/*')

print(jars)

for jar in jars :
    sys.path.append(jar)
