import os
import sys
from glob import glob

currentPath = os.path.dirname(__file__)

jars = glob(currentPath+'/jdbc_driver/*')

print(jars)

for jar in jars :
    sys.path.append(jar)
