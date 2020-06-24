import os
import base64
import json
import requests
from sikuli import *

def solve(host,site) :
    test_url = 'http://'+host+':5000/predict?site=' + site
    currentPath = os.path.dirname(__file__)
    if site == "BeobWon" :
        m = find(r'{}{}'.format(currentPath,"\BeobWonRefreshButton.png"))
        loc = (m.x ,m.y)
        path = capture(loc[0]-151,loc[1]-11,120,40)
    elif site == "MinWon24" :
        m = find(r'{}{}'.format(currentPath,"\MinWon24RefreshButton.png"))
        loc = (m.x ,m.y)
        path = capture(loc[0]-106,loc[1]-5,100,40)

    with open(path, "rb") as img_file:
        base64Encoded = base64.b64encode(img_file.read())
    response = requests.post(test_url, data=base64Encoded)

    os.remove(path)
    
    result = json.loads(response.text)
    return result["answer"]
