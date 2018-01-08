import math
from action import *


MOTORRATIO = 1 #Speed of right wheel compared to left one.
BASESPEED = 40 #Speed of robot.
TURNSPEED = 1
MAXDIST = 200 #Distance that can be covered in between one camera update at full power.
MAXANGLE = 120 #Angle that can be convered between one camera update at full power.
    
def move(robot,action,tokens):
    
    CUBEMULTIPLIER = 1 + 0.5 * tokens
    #Generates leftSpeed and rightSpeed from motor ratio(To go straight)
    if MOTORRATIO < 1:
        leftSpeed = BASESPEED
        rightSpeed = BASESPEED * MOTORRATIO
    else:
        leftSpeed = BASESPEED / MOTORRATIO
        rightSpeed = BASESPEED
    
    if leftSpeed *  CUBEMULTIPLIER < 100 and rightSpeed * CUBEMULTIPLIER < 100:
        leftSpeed *= CUBEMULTIPLIER
        rightSpeed *= CUBEMULTIPLIER
    elif leftSpeed > rightSpeed:
        rightSpeed *= 100 / leftSpeed
        leftSpeed = 100
    elif rightSpeed > leftSpeed:
        leftSpeed *= 100 / rightSpeed
        rightSpeed = 100
    
    if action.type == "move":
        if action.dist < MAXDIST * (BASESPEED/100.0): #If distance is too short
            multiplier = action.dist / (MAXDIST * (BASESPEED/100.0))
            leftSpeed *= multiplier
            rightSpeed *= multiplier
            
        turn = clamp(float(action.angle)/ float(MAXANGLE),-1,1) #Proportion to turn
        if turn < 0: #Turn left
            print("Turn left")
            robot.motors[0].m0.power = leftSpeed * (1 + turn) / TURNSPEED
            robot.motors[0].m1.power = rightSpeed    
            print("left speed: " + str(leftSpeed * (1 + turn) / TURNSPEED))
            print("right speed: " + str(rightSpeed))
        elif turn > 0: #Turn right
            print("Turn right")
            robot.motors[0].m0.power = leftSpeed
            robot.motors[0].m1.power = rightSpeed * (1 - turn) / TURNSPEED
            print("left speed: " + str(leftSpeed * (1 + turn) / TURNSPEED))
            print("right speed: " + str(rightSpeed))
        else:
            robot.motors[0].m0.power = leftSpeed
            robot.motors[0].m1.power = rightSpeed
                
    elif action.type == "stop":
        robot.motors[0].m0.power = 0
        robot.motors[0].m1.power = 0
        
    elif action.type == "turn":
        
        if action.angle < 0:
            leftSpeed *= -1
        else:
            rightSpeed *= -1
        
        if action.angle < MAXANGLE:
            proportion = clamp(float(action.angle)/float(MAXANGLE) , -1 , 1) #Generate speed multiplier
            leftSpeed *= proportion
            rightSpeed *= proportion
            
        robot.motors[0].m0.power = leftSpeed 
        robot.motors[0].m1.power = rightSpeed
            
            
        
            
    
def clamp(val,min,max):
    if val < min:
        return min
    if val > max:
        return max
    return val

            
    