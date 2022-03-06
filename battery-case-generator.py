#!/usr/bin/env python3

import math
import sys
import argparse
import svgturtle

parser = argparse.ArgumentParser(description='Generate a hexagonal battery case',
                                 epilog="""
Most arguments have sensibly tuned defaults, so you'll probably only need
to specify --dimension, --hole, --thickness, and possibly --kerf.
""")
parser.add_argument('--dimension', default=5, type=int, help='Grid dimension')
parser.add_argument('--height', type=float, help='Height of battery')
parser.add_argument('--hole', default='AA', help='Hole diameter (mm or D, C, AA, AAA)')
parser.add_argument('--kerf', default=.1, type=float, help='Kerf')
parser.add_argument('--corner-length', default=4, help='Length of stretch corner in material thicknesses')
parser.add_argument('--stretch', default=1.05, type=float, help='Reduction factor of stretch material')
parser.add_argument('--horizontal-finger', default=5.0, type=float, help='Width of horizontal fingers')
parser.add_argument('--vertical-finger', default=15.0, type=float, help='Width of vertical fingers')
parser.add_argument('--padding', default=1.5, type=float, help='Padding around holes')
parser.add_argument('--outside-padding', default=4.0, type=float, help='Extra padding between holes and wall')
parser.add_argument('--extra-height', default=2.0, type=float, help='Extra vertical space')
parser.add_argument('--thickness', default=3.0, type=float, help='Thickness of material')
parser.add_argument('--lid', default=0.2, type=float, help='How much extra play to give the lid')
parser.add_argument('--tooth', default=0.8, type=float, help='How much to round the edges of the teeth')
parser.add_argument('--flex-width', default=.5, type=float, help='Spacing (in material thickness) between flex lines')
parser.add_argument('--flex-cut', default=5.0, type=float, help='Length (in material thickness) of flex cuts')
parser.add_argument('--flex-gap', default=1.0, type=float, help='Gap (in material thickness) between flex cuts')
parser.add_argument('--plug-play', default=0.8, type=float, help='How much smaller to make the plug than the hole')
parser.add_argument('--verbose', action='store_true', help='Print computed parameter values')
args = parser.parse_args()
assert (args.dimension % 2) == 1

BATTERY = {
    'AAA': [10.5, 44.5],
    'AA':  [14.5, 50.5],
    'C':   [26.2, 50.0],
    'D':   [34.2, 61.5],
}

if args.hole in BATTERY:
    dim = BATTERY[args.hole]
    args.hole = dim[0]
    if args.height == None:
        args.height = dim[1]
else:
    args.hole = float(args.hole)
    assert(args.height != None)

SUITABLE = False
while not SUITABLE:
    args.kerf2         = args.kerf/2
    args.grid          = args.hole+args.padding
    args.radius        = args.hole/2
    args.corner        = args.corner_length*args.thickness
    args.corner_s      = args.corner*args.stretch
    args.corner_radius = 3*args.corner_s/math.pi
    args.plug_radius   = args.corner_radius-args.thickness
    args.corner_inset  = args.corner_s*math.sqrt(3)/math.pi
    args.plug_inset    = args.plug_radius/math.sqrt(3)
    args.interior_edge = args.grid*args.dimension*0.5+args.outside_padding
    args.opening_edge  = args.interior_edge-args.thickness
    args.plug_edge     = min(args.opening_edge, .5*math.sqrt(3)*args.interior_edge)-args.plug_play
    args.disc_radius   = 0.45*(math.sqrt(3)-1)*args.plug_edge+args.plug_inset
    args.exterior_edge = args.interior_edge+2.0*args.thickness
    args.interior_leg  = (args.interior_edge-args.horizontal_finger-args.kerf)/2-args.corner_inset
    finger_length      = args.interior_edge-2.0*args.corner_inset
    args.n_hor_fingers = max(int(finger_length/args.horizontal_finger/2), 1)
    args.exterior_leg  = (finger_length-(2*args.n_hor_fingers-1)*args.horizontal_finger+args.kerf)/2
    args.wall_leg      = (args.interior_edge-args.corner-(2*args.n_hor_fingers-1)*args.horizontal_finger+args.kerf)/2
    args.exterior_slot = (args.interior_edge-args.horizontal_finger+args.kerf)/2
    args.n_ver_fingers = int((args.height+args.extra_height)/args.vertical_finger)
    top_slot           = args.extra_height+args.thickness+0.45*args.height
    args.slots         = [top_slot, top_slot+15.0]
    if args.exterior_leg > 2:
        SUITABLE=True
    else:
        args.outside_padding += .5
        args.padding         += .2 # Try again with more padding

if args.verbose:
    print(args, file=sys.stderr)

BOX    = 2.0*args.exterior_edge+5.0
DIMX   = 3.0*BOX
DIMY   = 2.0*BOX+args.height+args.extra_height+3.0*args.thickness+5.0
PI3    = math.pi/3

HOLES  = ''
SHAPES = ''
MARKS  = ''

def draw_grid(cx, cy):
    global HOLES
    for row in range(-int(args.dimension/2), int((args.dimension+1)/2)):
        cyr = cy+args.grid*row*math.sin(PI3)
        num_col = args.dimension-abs(row)
        cxr = cx-.5*args.grid*(num_col-1.0)
        for col in range(num_col):
            HOLES += '<circle cx="%.2f" cy="%.2f" r="%.2f"/>\n' % (cxr+col*args.grid, cyr, args.radius)

def draw_disc(cx, cy, layer):
    global HOLES, SHAPES, MARKS
    turtle       = svgturtle.SvgTurtle(cx, cy)
    turtle.penup()
    turtle.forward(args.disc_radius)
    turtle.pendown()
    turtle.left(90)
    turtle.circle(args.disc_radius)
    turtle.penup()
    turtle.home()
    if layer=='disc':
        HOLES += '<path d="%s"/>\n' % turtle.to_s()
    else:
        MARKS += '<path d="%s"/>\n' % turtle.to_s()

def draw_plane(cx, cy, layer):
    global HOLES, SHAPES, MARKS
    if layer=='interior':
        edge = args.interior_edge
    elif layer=='opening':
        edge = args.opening_edge
    elif layer=='plug' or layer=='plug_mark':
        edge = args.plug_edge
    else:
        edge = args.exterior_edge
    turtle       = svgturtle.SvgTurtle(cx, cy)
    turtle.penup()
    if layer=='plug_mark':
        turtle.right(30)
    turtle.forward(edge)
    turtle.right(120)
    if layer=='interior':
        turtle.forward(args.corner_inset)
        turtle.pendown()
        for side in range(5):
            turtle.forward(args.interior_leg)
            turtle.left(90)
            turtle.forward(args.thickness)
            turtle.right(90)
            turtle.forward(args.horizontal_finger+args.kerf)
            turtle.right(90)
            turtle.forward(args.thickness)
            turtle.left(90)
            turtle.forward(args.interior_leg)
            turtle.circle(-args.corner_radius, 60)
        turtle.forward(edge-2.0*args.corner_inset)
        turtle.circle(-args.corner_radius, 60)
    elif layer=='plug' or layer=='plug_mark':
        turtle.pendown()
        for side in range(3):
            turtle.forward(0.5*edge)
            turtle.right(90)
            turtle.circle(0.5*edge, 120)
            turtle.right(90)
            turtle.forward(0.5*edge)
            turtle.right(60)
    else:
        turtle.pendown()
        for side in range(6):
            turtle.forward(edge)
            turtle.right(60)
    if layer=='plug':
        HOLES += '<path d="%s"/>\n' % turtle.to_s()
    elif layer=='plug_mark':
        MARKS += '<path d="%s"/>\n' % turtle.to_s()
    else:
        SHAPES += '<path d="%s"/>\n' % turtle.to_s()
    turtle.reset()
    turtle.penup()
    if layer=='bottom' or layer=='rim':
        turtle.forward(args.interior_edge)
        turtle.right(120)
        turtle.forward(args.corner_inset)
        for side in range(5):
            for finger in range(args.n_hor_fingers):
                turtle.forward(args.exterior_leg if finger == 0 else args.horizontal_finger+args.kerf)
                turtle.pendown()
                turtle.left(90)
                turtle.forward(args.thickness)
                turtle.right(90)
                turtle.forward(args.horizontal_finger-args.kerf)
                turtle.right(90)
                turtle.forward(args.thickness)
                turtle.right(90)
                turtle.forward(args.horizontal_finger-args.kerf)
                turtle.penup()
                turtle.right(180)
                turtle.forward(args.horizontal_finger-args.kerf)
            turtle.forward(args.exterior_leg)
            turtle.pendown()
            turtle.left(90)
            turtle.forward(args.thickness)
            turtle.right(90)
            turtle.circle(-args.corner_radius-args.thickness, 60)
            turtle.right(90)
            turtle.forward(args.thickness)
            turtle.right(90)
            turtle.circle(args.corner_radius, 60)
            turtle.penup()
            turtle.right(180)
            turtle.circle(-args.corner_radius, 60)
        turtle.forward(args.interior_edge-2*args.corner_inset)
        turtle.pendown()
        turtle.left(90)
        turtle.forward(args.thickness)
        turtle.right(90)
        turtle.circle(-args.corner_radius-args.thickness, 60)
        turtle.right(90)
        turtle.forward(args.thickness)
        turtle.right(90)
        turtle.circle(args.corner_radius, 60)
        HOLES += '<path d="%s"/>\n' % turtle.to_s()

def draw_flex(t, h):
    global HOLES
    turtle = svgturtle.SvgTurtle(t.x, t.y)
    gap    = args.flex_gap*args.thickness
    ncut   = max(int((h-gap) // (args.flex_cut*args.thickness)), 1)
    cut    = ((h-gap) / ncut) - gap
    dx     = args.flex_width*args.thickness
    nlines = int(args.corner // dx)
    x0     = .5*(args.corner - (nlines-1)*dx)

    turtle.forward(x0)
    for line in range(nlines):
        turtle.pendown()
        if (line % 2) == 0:
            turtle.right(90)
            turtle.forward(gap+cut)
            for section in range(ncut-2):
                turtle.penup()
                turtle.forward(gap)
                turtle.pendown()
                turtle.forward(gap+2*cut)
            turtle.penup()
            turtle.forward(gap)
            if (ncut % 2) == 0:
                turtle.pendown()
                turtle.forward(gap+cut)
                turtle.penup()
            turtle.left(90)
        else:
            turtle.left(90)
            if (ncut % 2) == 1:
                turtle.forward(gap+cut)
            for section in range(ncut-1-(ncut % 2)):
                turtle.penup()
                turtle.forward(gap)
                turtle.pendown()
                turtle.forward(gap+2*cut)
            turtle.penup()
            turtle.forward(gap)
            turtle.right(90)
        turtle.forward(dx)
    HOLES += '<path d="%s"/>\n' % turtle.to_s()

def draw_case_h(turtle, h, top):
    turtle.forward(0.5*args.interior_edge-0.5*args.corner)
    for side in range(6):
        turtle.left(90)
        turtle.forward(args.thickness)
        turtle.right(90)
        if top:
            draw_flex(turtle, h+2*args.thickness)
        turtle.forward(args.corner)
        turtle.right(90)
        turtle.forward(args.thickness)
        turtle.left(90)
        if side == 5:
            break
        turtle.forward(args.wall_leg-0.5*args.kerf)
        for finger in range(args.n_hor_fingers):
            if finger > 0:
                turtle.forward(args.horizontal_finger-args.kerf)
            turtle.left(90)
            turtle.forward(args.thickness)
            turtle.right(90)
            turtle.forward(args.horizontal_finger+args.kerf)
            turtle.right(90)
            turtle.forward(args.thickness)
            turtle.left(90)
        turtle.forward(args.wall_leg-0.5*args.kerf)
    turtle.forward(0.5*args.interior_edge-0.5*args.corner)

def draw_case_v(turtle, h):
    ey = turtle.y+h
    leg = (h-(args.n_ver_fingers-0.66)*args.vertical_finger)/2.0
    slope = args.vertical_finger/math.sqrt(18)
    turtle.forward(leg)
    for finger in range(args.n_ver_fingers):
        ty = ey if finger==args.n_ver_fingers-1 else turtle.y+args.vertical_finger
        turtle.circle(args.tooth, 135)
        turtle.forward(slope)
        turtle.circle(-args.tooth, 135)
        turtle.forward(0.66*args.vertical_finger)
        turtle.circle(-args.tooth, 135)
        turtle.forward(slope)
        turtle.circle(args.tooth, 135)
        turtle.forward(ty-turtle.y)

def draw_case(x0, y0, h, slots):
    global HOLES, SHAPES
    turtle = svgturtle.SvgTurtle(x0, y0+args.thickness)
    draw_case_h(turtle, h, True)
    turtle.right(90)
    draw_case_v(turtle, h)
    turtle.right(90)
    draw_case_h(turtle, h, False)
    turtle.penup()
    turtle.left(90)
    turtle.back(h)
    turtle.pendown()
    draw_case_v(turtle, h)
    SHAPES += '<path d="%s"/>\n' % turtle.to_s()
    for slot in slots:
        for side in range(5):
            x = x0+(side+.5)*args.interior_edge+args.exterior_slot
            y = y0+slot
            w = args.horizontal_finger-args.kerf
            h = args.thickness-args.kerf
            HOLES += '<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f"/>\n' % (x, y, w, h)

print('<svg viewBox="0 0 %.2f %.2f" width="%.2fmm" height="%.2fmm" stroke-width="0.1" xmlns="http://www.w3.org/2000/svg">' % (DIMX, DIMY, DIMX, DIMY))
draw_grid(0.5*BOX, 0.5*BOX)
draw_plane(0.5*BOX, 0.5*BOX, 'interior')
draw_grid(1.5*BOX, 0.5*BOX)
draw_plane(1.5*BOX, 0.5*BOX, 'interior')
draw_plane(0.5*BOX, 1.5*BOX, 'bottom')
draw_plane(1.5*BOX, 1.5*BOX, 'rim')
draw_plane(1.5*BOX, 1.5*BOX, 'opening')
draw_disc(1.5*BOX, 1.5*BOX, 'disc')
draw_plane(2.5*BOX, 0.5*BOX, 'plug')
draw_plane(2.5*BOX, 1.5*BOX, 'lid')
draw_plane(2.5*BOX, 1.5*BOX, 'plug_mark')
draw_disc(2.5*BOX, 1.5*BOX, 'disc_mark')
draw_case(0.05*args.grid*args.dimension, 2.0*BOX, args.height+args.extra_height+args.thickness, args.slots)
print('<g fill="none" stroke="black">', SHAPES, '</g>', '<g fill="none" stroke="red">', HOLES, '</g>', '<g fill="none" stroke="blue">', MARKS, '</g>', sep='\n')
print('</svg>')
