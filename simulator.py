#!/usr/bin/env python

import pygame
import pygame.gfxdraw
from pygame.locals import *
import pickle, os.path, sys, argparse, random, copy
from localization import Direction, Orientation, World, Particle, Robot, init_particles, print_particles, particle_filter
from nxtrobot import NxtRobot

SCREENRECT = Rect(0, 0, 640, 480)

def get_triangle(o, d, dx, dy, noise = (0,0)):
    (i, j) = o.get_coordinates()
    i += noise[0]
    j += noise[1]
    c = ((i + 0.5) * dx, (j + 0.5) * dy)
    (di, dj) = Orientation.get_delta(o.orientation)
    p1 = (c[0] + d * di, c[1] + d * dj)
    p2 = (c[0] + d * (di == 0 and 1 or -di), c[1] + d * (dj == 0 and 1 or -dj))
    p3 = (c[0] + d * (di == 0 and -1 or -di), c[1] + d * (dj == 0 and -1 or -dj))
    return (p1, p2, p3) 

def print_msg_in_cell(screen, msg, i, j, color, dx, dy):
    font_obj = pygame.font.Font('tahoma.ttf', 9)
    msg_surface = font_obj.render(msg, False, color) 
    msg_rect = msg_surface.get_rect()
    msg_rect.topleft = (int(i*dx), int(j*dy)) 
    screen.blit(msg_surface, msg_rect)


def main():
    parser = argparse.ArgumentParser(description='Particle filter simulator.')
    parser.add_argument('map', default='model.out', help='file name of the map from models folder')
    parser.add_argument('--nxt', action='store_true', default=False, help='use lego mindstorms nxt robot')
    args = parser.parse_args()

    file_name = 'models/' + args.map
    if not os.path.isfile(file_name):
        print('File doesn\'t exist')
        sys.exit(1)

    f = open(file_name, 'r')
    world = World(pickle.load(f))
    f.close()
    particles = init_particles(world, 1000)
    cell = random.choice(world.get_free_cells())

    if args.nxt:
        robot = NxtRobot(world)
    else:
        robot = Robot(world, cell, Orientation.NORTH)

    pygame.init()
    clock = pygame.time.Clock()
    winstyle = 0  # |FULLSCREEN
    bestdepth = pygame.display.mode_ok(SCREENRECT.size, winstyle, 32)
    screen = pygame.display.set_mode(SCREENRECT.size, winstyle, bestdepth)
    pygame.display.set_caption('Simulator')

    noise = [random.uniform(-0.4, 0.4) for x in range(2 * len(particles))]

    white_color = pygame.Color(255, 255, 255)
    black_color = pygame.Color(183, 183, 183)
    red_color = pygame.Color(197, 54, 52)
    blue_color = pygame.Color(42, 49, 255)

    dx = SCREENRECT.width * 1.0 / world.n
    dy = SCREENRECT.height * 1.0 / world.m

    print("""
    Controls:
    w - forward
    s - backward
    a - left 
    d - right

    up - go north
    down - go south
    left - go west
    right - go east

    esc - quit
    """)

    while True:
        # Draw world
        screen.fill(white_color);
        for i in range(world.n):
            x = dx * i
            pygame.draw.line(screen, black_color, (x, 0), (x, SCREENRECT.height), 1) 
        for j in range(world.m):
            y = dy * j
            pygame.draw.line(screen, black_color, (0, y), (SCREENRECT.width, y), 1) 
            for i in range(world.n):
                if world.is_border(i, j):
                    pygame.draw.rect(screen, black_color, Rect(i * dx + 1, j * dy + 1, dx, dy), 0)
                # print_msg_in_cell(screen, '%d,%d' % (i, j), i, j, blue_color, dx, dy)

        # Draw particles
        for i, p in enumerate(particles):
            n = (noise[2 * i], noise[2 * i + 1])
            points = get_triangle(p, 2, dx, dy, n)
            pygame.gfxdraw.filled_polygon(screen, points, red_color)

        # Draw robot
        if not isinstance(robot, NxtRobot):
            points = get_triangle(robot, 4, dx, dy)
            pygame.gfxdraw.filled_polygon(screen, points, blue_color)

        # Handle events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit(1)
            elif event.type == MOUSEBUTTONDOWN:
                mousex, mousey = event.pos
                i = int(mousex / dx)
                j = int(mousey / dy)
                if not isinstance(robot, NxtRobot): 
                    robot.position = world.get_index(i, j)
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.event.post(pygame.event.Event(QUIT))
                elif event.key == K_m:
                    print(robot.measure())
                elif event.key == K_UP:
                    robot.move(Orientation.NORTH, 'orientation')
                    particles = particle_filter(particles, world, robot.measure(), Orientation.NORTH, 'orientation')
                elif event.key == K_LEFT:
                    robot.move(Orientation.WEST, 'orientation')
                    particles = particle_filter(particles, world, robot.measure(), Orientation.WEST, 'orientation')
                elif event.key == K_DOWN:
                    robot.move(Orientation.SOUTH, 'orientation')
                    particles = particle_filter(particles, world, robot.measure(), Orientation.SOUTH, 'orientation')
                elif event.key == K_RIGHT:
                    robot.move(Orientation.EAST, 'orientation')
                    particles = particle_filter(particles, world, robot.measure(), Orientation.EAST, 'orientation')
                elif event.key == K_w:
                    robot.move(Direction.FORWARD)
                    particles = particle_filter(particles, world, robot.measure(), Direction.FORWARD)
                elif event.key == K_s:
                    robot.move(Direction.BACK)
                    particles = particle_filter(particles, world, robot.measure(), Direction.BACK)
                elif event.key == K_a:
                    robot.move(Direction.LEFT)
                    particles = particle_filter(particles, world, robot.measure(), Direction.LEFT)
                elif event.key == K_d:
                    robot.move(Direction.RIGHT)
                    particles = particle_filter(particles, world, robot.measure(), Direction.RIGHT)

        pygame.display.update()
        clock.tick(40)


if __name__ == '__main__': main()

 
