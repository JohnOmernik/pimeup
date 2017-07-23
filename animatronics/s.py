#!/usr/bin/python
import pygame
pygame.mixer.init()
pygame.mixer.music.load("whizzer.wav")
pygame.mixer.music.play()
tcnt = 0
while pygame.mixer.music.get_busy() == True:
    tcnt +=1
    print("We are in a loop: %s" % tcnt)
    continue


