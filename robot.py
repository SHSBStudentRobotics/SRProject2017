import decisionBackup as decision , time, math
from action import Action
from hardware import *
from sr.robot import * 

CAMERARES = (800,600)


def main():
    robot = Robot()
    state = decision.State([], [], time.time())
    
    print("MODE : "+str(robot.mode))
    
    #robot.ruggeduinos[0].pin_mode(2,OUTPUT)
    #robot.ruggeduinos[0].digital_write(2, True)
    print("Robot started: ")
    
    move(robot,Action("move",0,1000), 1)
    time.sleep(1)
    
    while True:
        print("TIME : "+str(time.time()))
        startTime = time.time()
        #robot.motors[0].m0.power = 0
        #robot.motors[0].m1.power = 0
        #time.sleep(0.2)
        markers = robot.see(res = CAMERARES)
        print("Camera: ")
        print(",".join(map(lambda x: str(x.info.code) + " : " + str(x.info.marker_type),markers)))
        print()
        print("Camera update took {0} seconds".format(time.time()-startTime))
        
        try:
            result = decision.decide(markers, state,robot.zone)
            data = result.action
            state = result.state
            print("Action")
            print("Type : "+data.type+", Distance : "+str(data.dist)+", Angle : "+str(data.angle))
            print("Tokens : "+str(len(state.tokens)))
            ROBOTS = filter(lambda x: x.info.marker_type == "robot", markers)
            BAD_ROBOTS = filter(lambda robot: nearlyEqual(data, robot))
            if len(BAD_ROBOTS) >= 1:
                move(robot, Action("move", 0, 100), len(state.tokens))
            else:
                move(robot,data,len(state.tokens))
            
            time.sleep(0.3)
        
            if data.type == "turn":
                move(robot,Action("stop",500),0)
            time.sleep(0.1)
        
        except Exception as error:
            print("ERROR!")
            print(error)
            time.sleep(0.4)
            
        # move(robot,Action("move",0,200),0)
                    
            
        
main()
        
def nearlyEqual(a,b):
    if math.fabs(a.dist - b.dist) < 0.5 and math.fabs(a.angle - b.rot_y) < 10:
        return True
    return False
    
    
    
    