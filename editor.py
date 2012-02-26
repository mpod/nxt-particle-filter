#!/usr/bin/env python

import pygame
from pygame.locals import *
import pickle, os.path, sys, argparse

SCREENRECT = Rect(0, 0, 640, 480)

def main():
    parser = argparse.ArgumentParser(description='Map editor.')
    parser.add_argument('-f', default='model.out', dest='file',
            help='file name of the map from models folder')
    parser.add_argument('-n', type=int, dest='n',
            default=100, help='number of columns')
    parser.add_argument('-m', type=int, dest='m',
            default=80, help='number of rows')
    parser.add_argument('-e', nargs='?', const='True', help='erase the map')
    args = parser.parse_args()

    n = args.n
    m = args.m
    file_name = 'models/' + args.file

    pygame.init()
    clock = pygame.time.Clock()
    winstyle = 0  # |FULLSCREEN
    bestdepth = pygame.display.mode_ok(SCREENRECT.size, winstyle, 32)
    screen = pygame.display.set_mode(SCREENRECT.size, winstyle, bestdepth)
    pygame.display.set_caption('Editor')

    white_color = pygame.Color(255, 255, 255)
    black_color = pygame.Color(183, 183, 183)


    if args.e is not True and os.path.isfile(file_name):
        f = open(file_name, 'r+')
        model = pickle.load(f)
        f.close()
        m = model[0]
        n = model[1]
    else:
        model = [0] * (m * n + 2)  # m x n matrix
        model[0] = m
        model[1] = n
        print(model[0])
        print(model[1])

    draw_flag = False
    delta = 0
    dx = SCREENRECT.width * 1.0 / n
    dy = SCREENRECT.height * 1.0 / m

    while True:
        screen.fill(white_color);
        for i in range(n):
            x = dx * i
            pygame.draw.line(screen, black_color, (x, 0), (x, SCREENRECT.height), 1) 
        for j in range(m):
            y = dy * j
            pygame.draw.line(screen, black_color, (0, y), (SCREENRECT.width, y), 1) 
            for i in range(n):
                if model[j * n + i + 2] != 0:
                    pygame.draw.rect(screen, black_color, Rect(i * dx + 1, j * dy + 1, dx, dy), 0)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit(1)
            elif event.type == MOUSEMOTION:
                if draw_flag:
                    mousex, mousey = event.pos
                    i = int(mousex / dx)
                    j = int(mousey / dy)
                    model[j * n + i + 2] = delta
            elif event.type == MOUSEBUTTONDOWN:
                mousex, mousey = event.pos
                i = int(mousex / dx)
                j = int(mousey / dy)
                delta = event.button == 1 and 1 or 0
                model[j * n + i + 2] = delta
                draw_flag = True
            elif event.type == MOUSEBUTTONUP:
                draw_flag = False
            elif event.type == KEYDOWN:
                if event.key == K_s and event.mod & KMOD_CTRL:
                    f = open(file_name, 'w')
                    pickle.dump(model, f)
                    f.close()
                    print('Model saved to %s...' % file_name)
                elif event.key == K_r and event.mod & KMOD_CTRL:
                    model = [0] * (m * n + 2)   # m x n matrix
                    model[0] = m
                    model[1] = n
                elif event.key == K_ESCAPE:
                    pygame.event.post(pygame.event.Event(QUIT))

        pygame.display.update()
        clock.tick(40)


if __name__ == '__main__': main()


