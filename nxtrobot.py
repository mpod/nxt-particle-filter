from localization import Robot, Direction, Orientation, World, Particle 
import time, threading
from nxt.brick import Brick
from nxt.locator import find_one_brick
from nxt.motor import Motor, SynchronizedMotors, PORT_A, PORT_B, PORT_C
from nxt.sensor import Light, Sound, Touch, Ultrasonic
from nxt.sensor import PORT_1, PORT_2, PORT_3, PORT_4


class NxtRobot(Robot):
    FULL_ROTATE_FACTOR = 5.5
    CELL_MOVE_FACTOR = 2.35

    def __init__(self, world):
        Robot.__init__(self, world, 2, Orientation.NORTH)
        self.noise = 0
        self.brick = find_one_brick()
        self.motor1 = Motor(self.brick, PORT_B)
        self.motor2 = Motor(self.brick, PORT_C)
        self.ultrasonic = Ultrasonic(self.brick, PORT_4)
        self.motor1.reset_position(False)
        self.motor2.reset_position(False)

    def move(self, direction):
        if direction == Direction.FORWARD:
            pass
        elif direction == Direction.RIGHT:
            self._rotate(-0.25)
            pass
        elif direction == Direction.BACK:
            self._rotate(0.5)
            pass
        elif direction == Direction.LEFT:
            self._rotate(0.25)
            pass
        m = self.ultrasonic.get_sample()
        if m > 26:
            t1 = threading.Thread(target=self.motor1.turn, args=(50, self.CELL_MOVE_FACTOR * 360))
            t2 = threading.Thread(target=self.motor2.turn, args=(50, self.CELL_MOVE_FACTOR * 360))
            t1.start()
            t2.start()
            t1.join()
            t2.join()

    def measure(self):
        m = []
        for i in range(4):
            m.append(self.ultrasonic.get_sample())
            self._rotate(0.25)
        return m

    def sync(self):
        m = self.ultrasonic.get_sample()
        while m == 255:
            self._rotate(0.17)
            m = self.ultrasonic.get_sample()

    def _rotate(self, degree):
        if degree == 0:
            return
        sign = 1
        if degree < 0:
            sign = -1
            degree = abs(degree)
        t1 = threading.Thread(target=self.motor1.turn, args=(sign * 50, self.FULL_ROTATE_FACTOR * 360 * degree))
        t2 = threading.Thread(target=self.motor2.turn, args=(sign * -50, self.FULL_ROTATE_FACTOR * 360 * degree))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

def main():
    robot = NxtRobot(None)
    while True:
        s = raw_input('--> ');
        if s == 'm':
            print('robot measurement: %s' % robot.measure())  
        elif s == 'a':
            robot.move(Direction.LEFT)
        elif s == 'd':
            robot.move(Direction.RIGHT)
        elif s == 'w':
            robot.move(Direction.FORWARD)
        elif s == 's':
            robot.move(Direction.BACK)
        elif s == 'n':
            print('ultrasonic sensor: %d' % robot.ultrasonic.get_sample())
        elif s == 'x':
            robot.sync()
        else:
          break

if __name__ == '__main__': main()



