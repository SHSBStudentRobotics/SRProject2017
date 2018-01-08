import math

def filterForPlayer(markers,zone): #Finds all markers in the given players zone
    if zone == 0:
        return filter(lambda x: (x.x + x.y) < 100,markers)
    if zone == 1:
        return filter(lambda x: (x.y - x.x) > 700,markers)
    if zone == 2:
        return filter(lambda x: (x.x + x.y) < 1500,markers)
    if zone == 3:
        return filter(lambda x: (x.y - x.x) < -750,markers)

def findClosestCube(targets):
    return min(filter(lambda x: x.code >= 32,targets) , key = lambda x: x.distance)
    
def findPlayerScores(targets):
    return [score(filterForPlayer(targets,0)),score(filterForPlayer(targets,1)),score(filterForPlayer(targets,2)),score(filterForPlayer(targets,3))]
    
def score(markers): #Sums up the scores for the given markers. (Does not check positiom)
    aMarkers = filter(lambda x: x.code >= 32 and x.code <= 35,markers)
    bMarkers = filter(lambda x: x.code >= 36 and x.code <= 39,markers)
    cMarkers = filter(lambda x: x.code >= 32 and x.code <= 35,markers)
    ans = len(markers)
    if len(aMarkers):
        return ans + len(bMarkers)
    if len(aMarkers) and len(bMarkers) and len(cMarkers):
        return ans + len(bMarkers) + 2*len(cMarkers)
    
def getDiffToBestOpponent(markers,zone):    #Calculates score advantage from markers , for the player of a given zone
    player0Score = score(filterForPlayer(markers,0))
    player1Score = score(filterForPlayer(markers,1))
    player2Score = score(filterForPlayer(markers,2))
    player3Score = score(filterForPlayer(markers,3))
    if zone == 0:
        return player0Score - max([player1Score,player2Score,player3Score])
    if zone == 1:
        return player1Score - max([player0Score,player2Score,player3Score])
    if zone == 2:
        return player2Score - max([player0Score,player1Score,player3Score])
    if zone == 3:
        return player3Score - max([player0Score,player1Score,player2Score])
        
def getScoreAfterCube(markers,movedMarker,playerZone):
    tempList = markers[:]
    tempList[tempList.index(movedMarker)].x = 0 if playerZone == 0 or playerZone == 1 else 800
    tempList[tempList.index(movedMarker)].y = 0 if playerZone == 0 or playerZone == 3 else 800
    return getDiffToBestOpponent(tempList,playerZone)
    
def getDistFromMarkerHome(marker,zone):
    if zone == 0:
        return math.sqrt((marker.x - 0)**2 + (marker.y - 0)**2)
    if zone == 1:
        return math.sqrt((marker.x - 0)**2 + (marker.y - 800)**2)
    if zone == 2:
        return math.sqrt((marker.x - 800)**2 + (marker.y - 800)**2)
    if zone == 3:
        return math.sqrt((marker.x - 800)**2 + (marker.y - 0)**2)
    
def findBestCubes(markers,playerZone):
    currentScore = getDiffToBestOpponent(markers,playerZone)
    otherMarkers = sum(map(lambda x : filterForPlayer(markers,x) , [0,1,2,3].remove(playerZone)))
    return sorted(otherMarkers , key = lambda x: (getScoreAfterCube(markers,x,playerZone) - currentScore)/(x.distance + getDistFromMarkerHome(x,playerZone)),reverse=True)
    