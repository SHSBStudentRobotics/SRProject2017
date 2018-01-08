# Some Information
# The point (0,0) is the bottom left of the grid and is where zone 0 and arena markers 0 and 27 are
# All global angles are measured clockwise from north which is in the negative y direction or towards the wall that joins zones 1 and 2

#All commands must receive a list of markers and state

#The distance away from a marker when the robot wil start its final aproach
FINALMOVEDIST = 1.2
TURN_ANGLE = 80
TURNING_ITER = 50


import math, time, random
from action import Action

def decide(markers, state, zone):
    # Store only the arena markers in a constant
    ARENA_MARKERS = filter(lambda x: x.info.marker_type in ["arena", "MARKER_ARENA"], markers)
    # Store only the token markers in a constant
    TOKEN_MARKERS = filter(lambda x: "token" in x.info.marker_type, markers)
    NOT_CAPTURED = map(lambda x: x.info.code, TOKEN_MARKERS)
    CAPTURED = filter(lambda x: not x.info.code in NOT_CAPTURED, state.tokens)
    if len(CAPTURED) != len(state.tokens):
        return decide(markers, state.setTokens(CAPTURED), zone)
    # Store only the markers that are in the robot's zone
    ZONE_MARKERS = getZoneMarkers(zone, ARENA_MARKERS)
    #If there is a command, execute it
    
    if state.turnCounter >= 30:
        COMMANDS = [moveForward for x in range(3)]
        return Result(state.setCommands(COMMANDS).resetTurnCounter(), Action("move", 0, 200))
    
    if len(state.commands) > 0:
        return state.runCommand()(markers, state.dropCommand(), zone)
    
    #Run this if no commands are available
    TIME_UP = (time.time() - state.startTime) > 120
    if len(state.tokens) >= 2 or TIME_UP:
        print("RETURNING!!!")
        if len(ZONE_MARKERS) > 0:
            ZONE = ZONE_MARKERS[0]
            if ZONE.dist < FINALMOVEDIST and ZONE.rot_y < 40 and ZONE.rot_y > -40:
                COMMANDS = [moveTowardsZoneMarker for x in range(3)] + [stop]
                return Result(state.setCommands(COMMANDS).resetTurnCounter(), Action("move", ZONE.rot_y, ZONE.dist*100))
            return Result(state.resetTurnCounter(), Action("move", ZONE.rot_y, ZONE.dist*100))
        elif len(ARENA_MARKERS) > 0:
            print("No zone markers")
            ROBOT = getRobotEntity(ARENA_MARKERS)
            """
            if isInOwnZone(zone, ROBOT):
                print("I'm home")
                return Result(state.setCommands([stop]).resetTurnCounter(), Action("stop", 0))
            """
            print("ROBOT ANGLE : "+str(ROBOT.angle))
            return Result(state.resetTurnCounter(), getZoneAction(zone,ROBOT))
        else:
            DIRECTION = forwardsOrBack(markers, state, zone)
            COMMANDS = [turnUntilArena for i in range(TURNING_ITER)] + [lambda markers, state, zone: DIRECTION for i in range(5)]
            return Result(state.setCommands(COMMANDS), Action("turn", TURN_ANGLE))

    #To go to a token marker
    if len(TOKEN_MARKERS) > 0:
        print("GET MARKERS")
        CAPTURED_TYPES = map(lambda x: x.info.marker_type, state.tokens)
        if time.time() - state.startTime > 60:
            AVAILABLE = TOKEN_MARKERS
        else:
            AVAILABLE = filter(lambda x: not x.info.marker_type in CAPTURED_TYPES, TOKEN_MARKERS)
        TOKEN = findClosestCube(AVAILABLE)
        #If a marker is close enough that it can be grabbed
        if TOKEN.dist < FINALMOVEDIST and TOKEN.rot_y > -40 and TOKEN.rot_y < 40:
            #Move forward 3 times commands
            COMMANDS = [(lambda markers, state, zone: moveIfTokenGone(markers, state.resetTurnCounter(), zone, TOKEN)) for i in range(4)] + [lambda markers, state, zone: moveAndGetToken(markers, state.resetTurnCounter(), zone, TOKEN)]
            #Move forward for 3 iterations
            return Result(state.setCommands(COMMANDS).resetTurnCounter(), Action("move", TOKEN.rot_y, TOKEN.dist*100))
        else:
            return Result(state.resetTurnCounter(), Action("move", TOKEN.rot_y, TOKEN.dist*100))
    else:
        DIRECTION = forwardsOrBack(markers, state, zone)
        COMMANDS = [turnUntilAvailableToken for i in range(TURNING_ITER)] + [lambda markers, state, zone: DIRECTION for i in range(5)]
        return Result(state.setCommands(COMMANDS), Action("turn", TURN_ANGLE))

def getZoneAction(zone, robot):
    ZONES = [
        Point(50, 50),
        Point(50, 750),
        Point(750, 750),
        Point(750, 50)
    ]
    ZONE = ZONES[zone]
    DISTANCE = math.sqrt((robot.x-ZONE.x)**2 + (robot.y-ZONE.y)**2) * 100
    ANGLE = getAngleFromNorth(ZONE.x-robot.x, ZONE.y-robot.y) - robot.angle
    return Action("move" , ANGLE, DISTANCE)

def moveTowardsZoneMarker(markers, state, zone):
    ARENAS = getArenaTokens(markers)
    ZONES = getZoneMarkers(zone, ARENAS)
    if len(ZONES) >= 1:
        ANGLE = sum(map(lambda x: x.rot_y, ZONES))/len(ZONES)
        return Result(state, Action("move", ANGLE, ZONES[0].dist * 100))
    return Result(state, Action("move", 0, 100))

def forwardsOrBack (markers, state, zone):
    if random.randint(0,4) == 2:
        return moveBackward(markers, state, zone)
    else:
        return moveForward(markers, state, zone)

def turnSideways(state):
    return Result(state, Action("turn", TURN_ANGLE))

def moveForward(markers, state, zone):
    print("Forwards")
    return Result(state, Action("move", 0, 100))

def moveBackward(markers, state, zone):
    print("Forwards")
    return Result(state, Action("move", 0, -100))

def moveIfTokenGone(markers, state, zone, token):
    TARGETS = filter(lambda x: x.info.code == token.info.code, markers)
    if len(TARGETS) >= 1:
        TARGET = TARGETS[0]
        return Result(state, Action("move", TARGET.dist*100, TARGET.rot_y))
    else:
        return moveForward(markers, state, zone)

def moveAndGetToken(markers, state, zone, token):
    print("Getting token")
    return Result(state.addToken(token), Action("move", 0, 100))

def stop(markers, state, zone):
    return Result(state.setCommands([stop]), Action("stop", 0))

def turnUntilAvailableToken(markers, state, zone):
    AVAILABLE = getAvailableTokens(getTokensFromMarkers(markers), state)
    if len(AVAILABLE) >= 1:
        return decide(markers, state.setCommands([]), zone)
    return turn(markers, state, zone)

def turnUntilArena(markers, state, zone):
    ARENAS = getArenaTokens(markers)
    if len(ARENAS) >= 1:
        return decide(markers, state.setCommands([]), zone)
    return turn(markers, state, zone)

def turn(markers, state, zone):
    return Result(state, Action("turn", TURN_ANGLE))

def getAngleToZone(zone, robotAngle):
    print(zone)
    if zone == 0:
        return - robotAngle - 135
    if zone == 1:
        return - robotAngle - 45
    if zone == 2:
        return - robotAngle + 45
    if zone == 3:
        return - robotAngle + 135

def getTokensFromMarkers(markers):
    return filter(lambda x: "token" in x.info.marker_type, markers)

def getAvailableTokens(markers, state):
    CAPTURED_TYPES = map(lambda x: x.info.marker_type, state.tokens)
    return filter(lambda x: not x.info.marker_type in CAPTURED_TYPES, markers)

def getArenaTokens(markers):
    return filter(lambda x: x.info.marker_type in ["arena", "MARKER_ARENA"], markers)

def getZoneMarkers(zone, markers):
    if zone == 0:
        return filter(lambda x: x.info.code in [27,0], markers)
    if zone == 1:
        return filter(lambda x: x.info.code in [6,7], markers)
    if zone == 2:
        return filter(lambda x: x.info.code in [13,14], markers)
    if zone == 3:
        return filter(lambda x: x.info.code in [20,21], markers)

def isInOwnZone(zone, robot):
    if zone == 0:
        return robot.x + robot.y < 100
    if zone == 1:
        return robot.x - robot.y < -700
    if zone == 2:
        return robot.x + robot.y > 1500
    if zone == 3:
        return robot.x - robot.y > 700

def getAngleFromNorth(x, y):
    print(x)
    print(y)
    POSY = float(math.fabs(y))
    POSX = float(math.fabs(x))
    if x > 0 and y > 0:
        print(0)
        ANGLE_ANTI_FROM_EAST = toDegrees(math.atan(POSY / POSX))
    if x < 0 and y > 0:
        print(1)
        ANGLE_ANTI_FROM_EAST = 90 + toDegrees(math.atan(POSY / POSX))
    if x < 0 and y < 0:
        print(2)
        ANGLE_ANTI_FROM_EAST = 180 + toDegrees(math.atan(POSY / POSX))
    if x > 0 and y < 0:
        print(3)
        ANGLE_ANTI_FROM_EAST = 270 + toDegrees(math.atan(POSY / POSX))
    
    print(ANGLE_ANTI_FROM_EAST)
    print(-ANGLE_ANTI_FROM_EAST - 270)
    return -ANGLE_ANTI_FROM_EAST - 270

def getGlobalPos(marker):
    # This converts the marker into an entity with absolute x, y, and rotation from north
    ENTITY = markerToEntity(marker)
    # This is the angle from north that the robot is from the marker
    ANGLE = ENTITY.angle - marker.orientation.rot_y
    # This converts that angle from north into the robots position relative
    # to the marker and adds that to the markers position
    X = ENTITY.x + marker.centre.polar.length*100 * math.sin(toRadians(ANGLE))
    print(math.sin(toRadians(ANGLE)))
    print(ANGLE)
    Y = ENTITY.y + marker.centre.polar.length*100 * math.cos(toRadians(ANGLE))
    ROBOT_ANGLE = ANGLE-180
    print("ROBOT X : "+str(X))
    print("ROBOT Y : "+str(Y))
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

def toRadians(deg):
    return (deg/180.0)*math.pi

def toDegrees(rad):
    return (rad/math.pi)*180.0
    
def findClosestCube(cubes):
    return min(cubes , key = lambda x: x.dist)
    
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
class State:
    def __init__(self, commands, tokens, startTime,turnCount = 0):
        self.commands = commands
        self.tokens = tokens
        self.startTime = startTime
        self.turnCounter = turnCount
        
    def incTurnCounter(self):
        return State(self.commands, self.tokens, self.startTime,self.turnCounter + 1)
        
    def resetTurnCounter(self):
        return State(self.commands, self.tokens, self.startTime,self.turnCounter)
        
    def setCommands(self, commands):
        return State(commands, self.tokens, self.startTime,self.turnCounter)
    def runCommand(self):
        return self.commands[0]
    def dropCommand(self):
        return State(self.commands[1:], self.tokens, self.startTime,self.turnCounter)
    def addToken(self, marker):
        return State(self.commands, self.tokens + [marker], self.startTime,self.turnCounter)
    def setTokens(self, tokens):
        return State(self.commands, tokens, self.startTime, self.turnCounter)

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
        self.dist = self.centre.polar.length
        self.rot_y = self.centre.polar.rot_y

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
