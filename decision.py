# Some Information
# The point (0,0) is the bottom left of the grid and is where zone 0 and arena markers 0 and 27 are
# All global angles are measured clockwise from north which is in the negative y direction or towards the wall that joins zones 1 and 2

import math, time
from action import Action

def decide(markers, state,zone):
    if state.mode == "done":
        return Result(state, Action("turn", 100))
    # Store only the arena markers in a constant
    ARENA_MARKERS = filter(lambda x: x.info.marker_type in ["arena", "MARKER_ARENA"], markers)
    # Store only the token markers in a constant
    TOKEN_MARKERS = filter(lambda x: "token" in x.info.marker_type, markers)
    print("TOKENS : "+", ".join(map(lambda x: str(x.info.code)+" : "+str(x.rot_y), TOKEN_MARKERS)))
    #CAN_SEE_TARGET = (len(filter(lambda x: x.info.code==state.code, TOKEN_MARKERS)) >= 1) * int(state.code != 0)       
    
    CAN_SEE_ARENA_MARKERS = len(ARENA_MARKERS) != 0
    
    if CAN_SEE_ARENA_MARKERS:
        # Get the robot as an entity
        ROBOT = getRobotEntity(ARENA_MARKERS)        
    else:
        print("Can't find arena markers")
    
    CAN_SEE_TARGET = (len(filter(lambda x: x.info.code==state.code, TOKEN_MARKERS)) >= 1)
    
    if state.mode == "search":
        if state.code != 0:
            if CAN_SEE_TARGET:
                return checkIsClose(getIndependantAction(markers,state))         
            elif state.isClose:
                return Result(state.setMode("collecting").setCount(3), Action("move", 0, 100))
            else:
                return Result(state, Action("turn", 40))
        else:
            return getIndependantAction(markers,state)
            
    elif state.mode == "collecting":
        #If the code needs to be reset to 0 afterwards 
        lastCollect = False 
        if state.count == 1:
            state = state.setMode("return").incTokens()
            lastCollect = True
        if CAN_SEE_TARGET:
            state = state.setState("search")
            return checkIsClose(getIndependantAction(markers,state))
        else:
            result = Result(state.setCount(state.count-1), Action("move", 0, 100))
            if lastCollect:
                return result.resetCode()
            else:
                return result          
            
    elif state.mode == "return":
        if CAN_SEE_ARENA_MARKERS:
            ZONE_TARGET = getZoneTarget(zone, ROBOT)
            ANGLE_TO_BASE = ZONE_TARGET.angleFromRobot
            
            if ZONE_TARGET.distance < 200:
                state = state.setIsClose(True)
            else:
                state = state.setIsClose(False)
                
            if ANGLE_TO_BASE > 180 or ANGLE_TO_BASE < -180:
                return Result(state.setCount(3), Action("turn", ANGLE_TO_BASE))
                
            return Result(state.setCount(3), Action("move", ANGLE_TO_BASE, ZONE_TARGET.distance))
            
        elif state.isClose:
            if state.count == 1:
                state.setMode("done")
            return Result(state.setCount(state.count-1), Action("move", 0, 100))
                 
        else:
            return Result(state, Action("turn", 40))
    
def checkIsClose(result):
    if result.action.dist < 200:
        return Result(result.state.setIsClose(True),result.action)
    else:
        return Result(result.state.setIsClose(False),result.action)
    
def getIndependantAction(markers, state):
    TOKEN_MARKERS = filter(lambda x: "token" in x.info.marker_type, markers)
    print(", ".join(map(lambda x: str(x.info.code)+" : "+str(x.rot_y), TOKEN_MARKERS)))
    if len(TOKEN_MARKERS) == 0:
        return Result(state, Action("turn", 40))
    TARGET_TOKEN = findClosestCubeFromMarker(TOKEN_MARKERS)
    return Result(state.setCode(TARGET_TOKEN.info.code), Action("move", TARGET_TOKEN.rot_y, TARGET_TOKEN.dist*100+100))

def isInOwnZone(zone, robot):
    if zone == 0:
        return robot.x + robot.y < 100
    if zone == 1:
        return robot.x - robot.y < -700
    if zone == 2:
        return robot.x + robot.y > 1500
    if zone == 3:
        return robot.x - robot.y > 700

def getPointFromMarker(marker, robot_angle):
    DISTANCE = marker.centre.polar.length * 100
    ANGLE_FROM_ROBOT = marker.centre.polar.rot_y
    # Get the angle from east anticlockwise from the robot to the marker
    ANGLE_ANTI_FROM_EAST = 90-(robot_angle + ANGLE_FROM_ROBOT)
    # Use trig to get the X and Y
    Y = math.sin(toRadians(ANGLE_ANTI_FROM_EAST)) * DISTANCE
    X = math.cos(toRadians(ANGLE_ANTI_FROM_EAST)) * DISTANCE
    return Point(X, Y)

def getTargetFromMarker(marker, robot_angle):
    CODE = marker.info.code
    TYPE = marker.info.marker_type
    ANGLE_FROM_ROBOT = marker.centre.polar.rot_y
    DISTANCE = marker.centre.polar.length * 100
    POINT = getPointFromMarker(marker, robot_angle)
    Y = POINT.y
    X = POINT.x
    return Target(X, Y, DISTANCE, ANGLE_FROM_ROBOT, CODE, TYPE)

def getTargetFromMap(mapping, ROBOT):
    if time.time()-mapping.marker.timestamp < 10:
        return getTargetFromMarker(mapping.marker, ROBOT.angle)
    else:
    
        CODE = mapping.marker.info.code
        TYPE = mapping.marker.info.marker_type
        
        X = mapping.point.x
        Y = mapping.point.y
        
        DISTANCE = math.sqrt(X**2+Y**2)
        
        ANGLE = getAngleFromNorth(X-ROBOT.x, Y-ROBOT.y) - ROBOT.angle
        
        return Target(X, Y, DISTANCE, ANGLE, CODE, TYPE)

def getAngleFromNorth(x, y):
    DIST = math.sqrt(x**2+y**2)
    SIN_1 = round(toDegrees(math.asin(y/DIST)), 1)
    print("SIN 1 : " + str(SIN_1))
    SINS = [SIN_1, 180-SIN_1]
    COS_1 = round(toDegrees(math.acos(x/DIST)), 1)
    print("COS 1 : " + str(COS_1))
    COSS = [COS_1, 360-COS_1]
    SIN = filter(lambda x: x in COSS, SINS)
    COS = filter(lambda x: x in SINS, COSS)
    if len(SIN) == 1 and len(COS) == 1:
        return 90-SIN[0]
    return 0

def getGlobalPos(marker):
    # This converts the marker into an entity with absolute x, y, and rotation from north
    ENTITY = markerToEntity(marker)
    # This is the angle from north that the robot is from the marker
    ANGLE = ENTITY.angle - marker.orientation.rot_y
    # This converts that angle from north into the robots position relative
    # to the marker and adds that to the markers position
    X = ENTITY.x + marker.centre.polar.length*100 * math.sin(toRadians(ANGLE))
    Y = ENTITY.y + marker.centre.polar.length*100 * math.cos(toRadians(ANGLE))
    ROBOT_ANGLE = ANGLE-180
    return Entity(X, Y, ROBOT_ANGLE)

def getRobotEntity(markers):
    POSITIONS = map(getGlobalPos, markers)
    # The mean of all of the x, y and angles
    X = sum(map(lambda x: x.x, POSITIONS))/len(POSITIONS)
    Y = sum(map(lambda x: x.y, POSITIONS))/len(POSITIONS)
    ANGLE = sum(map(lambda x: x.angle, POSITIONS))/len(POSITIONS)
    return Entity(X, Y, ANGLE)

def markerToEntity(marker):
    ARENA_ENTITIES = [
        Entity(0, 100, 90),
        Entity(0, 200, 90),
        Entity(0, 300, 90),
        Entity(0, 400, 90),
        Entity(0, 500, 90),
        Entity(0, 600, 90),
        Entity(0, 700, 90),
        Entity(100, 800, 180),
        Entity(200, 800, 180),
        Entity(300, 800, 180),
        Entity(400, 800, 180),
        Entity(500, 800, 180),
        Entity(600, 800, 180),
        Entity(700, 800, 180),
        Entity(800, 700, 270),
        Entity(800, 600, 270),
        Entity(800, 500, 270),
        Entity(800, 400, 270),
        Entity(800, 300, 270),
        Entity(800, 200, 270),
        Entity(800, 100, 270),
        Entity(700, 0, 0),
        Entity(600, 0, 0),
        Entity(500, 0, 0),
        Entity(400, 0, 0),
        Entity(300, 0, 0),
        Entity(200, 0, 0),
        Entity(100, 0, 0),
    ]
    # Return the entity that corresponds to which arena marker it is
    return ARENA_ENTITIES[marker.info.code]

def getZoneTarget(zone, robot):
    ZONES = [
        Point(50, 50),
        Point(50, 750),
        Point(750, 750),
        Point(750, 50)
    ]
    ZONE = ZONES[zone]
    DISTANCE = math.sqrt((robot.x-ZONE.x)**2 + (robot.y-ZONE.y)**2)
    ANGLE = getAngleFromNorth(ZONE.x-robot.x, ZONE.y-robot.y) - robot.angle
    print(getAngleFromNorth(ZONE.x-robot.x, ZONE.y-robot.y))
    return Target(ZONE.x, ZONE.y, DISTANCE, ANGLE, 0, "zone")

def findPlayerScores(targets):
    player0Markers = filter(lambda x: (x.x + x.y) < 100,targets)
    player1Markers = filter(lambda x: (x.y - x.x) > 700,targets)
    player2Markers = filter(lambda x: (x.x + x.y) < 1500,targets)
    player3Markers = filter(lambda x: (x.y - x.x) < -750,targets) 
    return [score(player0Markers),score(player1Markers),score(player2Markers),score(player3Markers)]

def score(markers):
    aMarkers = filter(lambda x: x.code >= 32 and x.code <= 35,markers)
    bMarkers = filter(lambda x: x.code >= 36 and x.code <= 39,markers)
    cMarkers = filter(lambda x: x.code >= 32 and x.code <= 35,markers)
    ans = len(markers)
    if len(aMarkers):
        ans += len(bMarkers)
    if len(aMarkers) and len(cMarkers):
        ans += 2 * len(cMarkers)
    return ans

def findClosestCube(cubes):
    return min(cubes , key = lambda x: x.distance)

def findClosestCubeFromMarker(cubes):
    return min(cubes , key = lambda x: x.dist)

def toRadians(deg):
    return (deg/180)*math.pi

def toDegrees(rad):
    return (rad/math.pi)*180

class State:
    def __init__(self, mapping, mode, count=0, code=0, tokens=0, isClose = False):
        self.mapping = mapping
        # Mode is one of "search", "collect", "return"
        self.mode = mode
        self.count = count
        self.code = code
        self.isClose = isClose
        self.tokens = tokens
    def setIsClose(self,isClose):
        return State(self.mapping, self.mode, self.count, self.code, self.tokens , isClose)
    def setMode(self, mode):
        return State(self.mapping, mode, self.count, self.code, self.tokens)
    def setMap(self, mapping):
        return State(mapping, self.mode, self.count, self.code, self.tokens)
    def setCount(self, count):
        return State(self.mapping, self.mode, count, self.code, self.tokens)
    def setCode(self, code):
        return State(self.mapping, self.mode, self.count, code, self.tokens)
    def incTokens(self):
        return State(self.mapping, self.mode, self.count, self.code, self.tokens + 1)

class MapItem:
    def __init__(self, point, marker):
        self.point = point
        self.marker = marker

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Entity:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle

class Target:
    def __init__(self, x, y, distance, angleFromRobot, code, markerType):
        self.x = x
        self.y = y
        self.distance = distance
        self.angleFromRobot = angleFromRobot
        self.code = code
        self.markerType = markerType

class Result:
    def __init__(self, state, action):
        self.state = state
        self.action = action
    def resetCode(self):
        return Result(self.state.setCode(0),self.action)

class Marker:
    def __init__(self, info, centre, orientation):
        self.info = info
        self.centre = centre
        self.orientation = orientation

class MarkerPoint:
    def __init__(self, polar):
        self.polar = polar
    
class Polar:
    def __init__(self, length, rot_x, rot_y):
        self.length = length
        self.rot_x = rot_x
        self.rot_y = rot_y

class Orientation:
    def __init__(self, rot_x, rot_y, rot_z):
        self.rot_x = rot_x
        self.rot_y = rot_y
        self.rot_z = rot_z

class MarkerInfo:
    def __init__(self, code, marker_type):
        self.code = code
        self.marker_type = marker_type
