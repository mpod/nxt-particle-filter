import random
import pickle
import copy
import math

class Direction:
    FORWARD = 1
    RIGHT = 2
    BACK = 3
    LEFT = 4

class Orientation:
    NORTH = 1
    EAST = 2
    SOUTH = 3
    WEST = 4

    @staticmethod
    def get_list():
        return [Orientation.NORTH, Orientation.SOUTH, Orientation.WEST, Orientation.EAST]

    @staticmethod
    def get_orientation(orientation, direction):
        return (direction - 1 + orientation - 1) % 4 + 1

    @staticmethod
    def get_delta(orientation):
        di = 0
        dj = 0
        if orientation == Orientation.NORTH:
            dj = -1
        elif orientation == Orientation.SOUTH:
            dj = 1
        elif orientation == Orientation.EAST:
            di = 1
        elif orientation == Orientation.WEST:
            di = -1
        return (di, dj)


class Particle:
    def __init__(self, world, weight, position, orientation):
        self.world = world
        self.weight = weight
        self.position = position
        self.orientation = orientation
        self.noise = 1
        self.sigma_move = 1.5
        self.sigma_measure = 1.5

    def get_coordinates(self):
        return self.world.get_coordinates(self.position)

    def move(self, direction, mode = 'direction'):
        if mode == 'orientation':
            new_orientation = direction
        else:
            new_orientation = Orientation.get_orientation(self.orientation, direction)
        (di, dj) = Orientation.get_delta(new_orientation)
        (i, j) = self.get_coordinates()
        # Add noise
        i += di + self.noise * int(random.normalvariate(0, self.sigma_move))
        j += dj + self.noise * int(random.normalvariate(0, self.sigma_move))
        if not self.world.is_border(i, j):
            self.position = self.world.get_index(i, j)
        self.orientation = new_orientation 

    def measure(self):
        res = []
        orientations = Orientation.get_list()
        while orientations[0] != self.orientation:
            o = orientations.pop()
            orientations.insert(0, o)
        for o in orientations:
            m = 0
            (di, dj) = Orientation.get_delta(o)
            (i, j) = self.get_coordinates()
            while not self.world.is_border(i + m * di, j + m * dj):
                m += 1
            res.append(m + self.noise * int(random.normalvariate(0, self.sigma_measure)))
        return res

    def __str__(self):
        return '(p: %s, %s, %s)' % (self.weight, self.position, self.orientation)

class Robot(Particle):
    def __init__(self, world, position, orientation):
        Particle.__init__(self, world, 1.0, position, orientation)
        self.noise = 0

class World:
    def __init__(self, world):
        self.world = world
        self.m = world[0]
        self.n = world[1]

    def is_border(self, i, j):
        if i<0 or i>=self.n or j<0 or j>=self.m:
            return True
        else:
            return  self.world[self.get_index(i, j)] == 1

    def get_value_by_index(self, idx):
        return self.world[indx]

    def get_coordinates(self, index):
        j = (index - 2) / self.n
        i = (index - 2) % self.n
        return (i, j)

    def get_index(self, i, j):
        return self.n * j + i + 2

    def get_free_cells(self):
        res = []
        map(lambda x: self.world[x] == 0 and res.append(x), range(2, len(self.world)))
        return res

def init_particles(world, N):
    particles = []
    free_cells = world.get_free_cells()
    while len(free_cells) < N:
        free_cells += free_cells
    for i in random.sample(free_cells, N):
        particles.append(Particle(world, 1.0 / N, i, random.choice(Orientation.get_list())))
    return particles

def particle_filter(particles, world, measured_value, action, action_mode='direction'):
    new_particles = []
    N = len(particles)
    weight_sum = 0
    weight_sums = map(lambda x: reduce(lambda z, y: z + y.weight, particles[:x], 0), range(1, N + 1))
    for i in range(N):
        # resampling
        r = random.uniform(0, weight_sums[-1])
        for i, v in enumerate(weight_sums):
            if v > r:
                p = copy.copy(particles[i])
                break
        
        # perform action
        p.move(action, action_mode)

        # recalculate weight
        m = p.measure()
        m_diff = sum(map(lambda x: (x[0] - x[1])**2, zip(measured_value, m)))
        sigma = 2.0
        p.weight = max(0.0001, 1.0 / (sigma * math.sqrt(2 * math.pi)) * math.exp(-m_diff / (2 * sigma ** 2)))

        weight_sum += p.weight
        new_particles.append(p)

    # normalize
    for p in new_particles:
        p.weight /= weight_sum

    return new_particles

def print_particles(particles):
    for p in particles:
        print(p),
    print('')

def main():
    f = open('worlds/model.out', 'r')
    world = World(pickle.load(f))
    f.close()
    particles = init_particles(world, 20)
    #particles = particle_filter(particles, world, 1)

if __name__ == '__main__': main()
