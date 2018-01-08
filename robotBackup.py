import decision , time
from action import Action
from hardware import *
from sr.robot import * 

CAMERARES = (800,600)


def main():
    robot = Robot()
    state = decision.State([], "search")
    
    #robot.ruggeduinos[0].pin_mode(2,OUTPUT)
    #robot.ruggeduinos[0].digital_write(2, True)
    print("Robot started: ")
    
    #move(robot,Action("move",0,100))
    while True:
        
        startTime = time.time()
        #robot.motors[0].m0.power = 0
        #robot.motors[0].m1.power = 0
        #time.sleep(0.2)
        markers = robot.see(res = CAMERARES)
        print("Camera: ")
        print(",".join(map(lambda x: str(x.info.code) + " : " + str(x.info.marker_type),markers)))
        print()
        print("Camera update took {0} seconds".format(time.time()-startTime))
        result = decision.decide(markers, state,robot.zone)
        data = result.action
        state = result.state
        move(robot,data,state.tokens)
        #move(robot,Action("move",0,200),0)
        print("Action type: {0} distance: {1} angle: {2}".format(data.type,data.dist,data.angle))
        print("State mode: {0} code: {1} counter: {2}".format(state.mode,state.code,state.count))
        
        time.sleep(0.4)
        
main()
        