class Action:
    def __init__(self,type,angle,dist = 0):
        self.type = type
        self.angle = clampAngle(angle)
        self.dist = dist

def clampAngle(angle):
    if angle > 180:
        return clampAngle(angle-360)
    if angle < -180:
        return clampAngle(angle+360)
    return angle
