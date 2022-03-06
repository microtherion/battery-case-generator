#!/usr/bin/env python3
"""svgturtle - simple library to generate SVG paths from turtle graphics style commands"""

import math
import sys

class SvgTurtle():
    def __init__(self, homex=0, homey=0):
        """Create a new turtle at the given home location, facing right"""
        self.homex    = homex
        self.homey    = homey
        self.cvtangle = math.tau/360
        self.reset()

    def penup(self):
        """Subsequent movements will be invisible and only affect location and heading"""
        self.pen      = False

    def pendown(self):
        """Subsequent movements will be visible and drawn"""
        self.pen      = True

    def forward(self, distance):
        """Move forward"""
        if self.pen and (self.path == ''):
            self.path = "M %.2f,%.2f" % (self.x,self.y)
        dx = distance*math.cos(self.heading)
        dy = distance*math.sin(self.heading)
        self.x += dx
        self.y += dy
        if self.pen:
            if abs(dy) < .01:
                self.path += " h %.2f" % dx
            elif abs(dx) < .01:
                self.path += " v %.2f" % dy
            else:
                self.path += " l %.2f,%.2f" % (dx, dy)
        elif self.path != '':
            self.path += " m %.2f, %.2f" % (dx, dy)

    def back(self, distance):
        """Move backward"""
        self.forward(-distance)

    def left(self, angle):
        """Turn left by angle specified in degrees"""
        self.right(-angle)

    def right(self, angle):
        """Turn right by angle specified in degrees"""
        self.heading = (self.heading + angle*self.cvtangle) % math.tau

    def circle(self, radius, extent=360, steps=None):
        """Draw a circle or arc spanning extent degrees around a center
           radius units to the left (if radius is positive) or right
           (if radius is negative). Use a polygon if steps is specified,
           otherwise a circle."""
        if steps:
            w  = 1.0*extent/steps
            w2 = 0.5*w
            l  = 2.0*radius*math.sin(w2*math.pi/180.0)
            if radius < 0:
                l, w, w2 = -l, -w, -w2
            self.left(w2)
            for i in range(steps):
                self.forward(l)
                self.left(w)
            self.right(w2)
        else:
            if extent>355:
                self.circle(radius, 355)
                extent -= 355
            ra  = self.cvtangle*(extent if radius < 0 else -extent)
            cx  = self.x+radius*math.cos(self.heading-.5*math.pi)
            cy  = self.y+radius*math.sin(self.heading-.5*math.pi)
            th  = self.heading+.5*math.pi+ra
            dx  = cx+radius*math.cos(th)-self.x
            dy  = cy+radius*math.sin(th)-self.y
            lg  = 1 if extent >= 180 else 0
            sw  = 0 if radius > 0 else 1
            if self.pen:
                if self.path == '':
                    self.path = "M %.2f,%.2f" % (self.x,self.y)
                self.path += " a %.2f %.2f %.2f %d %d %.2f %.2f" % (radius, radius, extent, lg, sw, dx, dy)
            elif self.path != '':
                self.path += " m %.2f, %.2f" % (dx, dy)
            self.x += dx
            self.y += dy
            self.heading = (self.heading + ra) % math.tau


    def to_s(self):
        """Return the generated path, suitable for the d attribute of an SVG <path> element"""
        return self.path

    def home(self):
        """Reset to the initial position and heading"""
        self.x        = self.homex
        self.y        = self.homey
        self.heading  = 0
        if self.path != '':
            self.path += " M %.2f, %.2f" % (self.x, self.y)

    def reset(self):
        """Clear the path and return home"""
        self.path = ''
        self.pen  = True
        self.home()

if __name__ == "__main__":
    turtle = SvgTurtle(50, 100)
    turtle.left(90)
    turtle.forward(50)
    turtle.left(30)
    turtle.forward(50)
    turtle.penup()
    turtle.back(50)
    turtle.right(60)
    turtle.pendown()
    turtle.forward(50)
    turtle.penup()
    turtle.back(50)
    turtle.left(30)
    turtle.back(50)
    turtle.right(90)
    turtle.forward(70)
    turtle.pendown()
    turtle.circle(25)
    print('<svg viewBox="0 0 170 110" xmlns="http://www.w3.org/2000/svg">')
    print('<path fill="none" stroke="blue" d="%s"/>' % turtle.to_s())
    print('</svg>')
