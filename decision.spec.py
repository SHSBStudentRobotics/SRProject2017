import decide from decision

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

def test():
    markers = [
        Marker(
            MarkerInfo(0, "arena"),
            MarkerPoint(
                Polar(
                    1,
                    0,
                    0
                )
            ),
            Orientation(
                0,
                20,
                0
            )
        ),
        Marker(
            MarkerInfo(31, "token-a"),
            MarkerPoint(
                Polar(
                    0.5,
                    0,
                    0
                )
            ),
            Orientation(
                0,
                0,
                0
            )
        )
    ]
    print("Result : ")
    data = decide(markers, [])
    result = data.action
    print("type : "+str(result.type))
    print("dist : "+str(result.distance))
    print("angle : "+str(result.angle))