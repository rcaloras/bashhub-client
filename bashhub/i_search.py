#!/usr/bin/python
import cli.app
from time import *
import readline
import getch
import rest_client

@cli.app.CommandLineApp
def interactive_search(app):
    inp = raw_input("> ")
    x = rest_client.search(query=inp, limit=3)
    size = len(x)

    for y in x:
        print y

    while True:
        key = ord(getch())
        if key == 27: #ESC
            break
        elif key == 13: #Enter
            select()
        elif key == 224: #Special keys (arrows, f keys, ins, del, etc.)
            key = ord(getch())
            if key == 80: #Down arrow
                moveDown()
            elif key == 72: #Up arrow
                moveUp()

def main():
    try:
        interactive_search.run()
    except Exception as e:
        print "Oops, look like an exception occured: " + str(e)

main()
