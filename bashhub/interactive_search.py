#!/usr/bin/python
"""
Sampled from Lyle Scott scrolling curses
"""
from __future__ import print_function
import curses
import sys
import random
import time
import locale


class InteractiveSearch:
    DOWN = 1
    UP = -1
    SPACE_KEY = 32
    ESC_KEY = 27
    ENTER_KEY = 10

    PREFIX_SELECTED = '_X_'
    PREFIX_DESELECTED = '___'

    outputLines = []
    commands = []
    screen = None

    def __init__(self, commands):

        self.commands = commands
        # Parse out our input
        self.outputLines = [x.__str__() for x in commands]
        self.nOutputLines = len(self.outputLines)

        self.topLineNum = 0
        self.highlightLineNum = 0
        self.markedLineNums = []

    def run(self):
        # Locale set to support utf-8 characters.
        locale.setlocale(locale.LC_ALL, "")
        return curses.wrapper(self._run)

    def _run(self, screen):
        self.screen = screen
        curses.cbreak()
        curses.start_color()
        curses.use_default_colors()
        self.screen.border(0)
        while True:
            self.displayScreen()
            # get user command
            c = self.screen.getch()
            if c == curses.KEY_UP or c == ord('k'):
                self.updown(self.UP)
            elif c == curses.KEY_DOWN or c == ord('j'):
                self.updown(self.DOWN)
            elif c == self.ENTER_KEY:
                return self.selectLine()
            elif c == self.ESC_KEY or c == ord('q'):
                sys.exit()

    def markLine(self):
        linenum = self.topLineNum + self.highlightLineNum
        if linenum in self.markedLineNums:
            self.markedLineNums.remove(linenum)
        else:
            self.markedLineNums.append(linenum)

    def selectLine(self):
        linenum = self.topLineNum + self.highlightLineNum
        self.screen.erase()
        self.restoreScreen()
        return self.commands[linenum]

    def displayScreen(self):
        # clear screen
        self.screen.erase()

        # now paint the rows
        top = self.topLineNum
        bottom = self.topLineNum + curses.LINES
        for (index, line, ) in enumerate(self.outputLines[top:bottom]):
            line = '%s' % (line, )

            # highlight current line
            if index != self.highlightLineNum:
                self.screen.addstr(index, 0, line)
            else:
                self.screen.addstr(index, 0, line, curses.A_STANDOUT)
        self.screen.refresh()

    # move highlight up/down one line
    def updown(self, increment):
        nextLineNum = self.highlightLineNum + increment

        # paging
        if increment == self.UP and self.highlightLineNum == 0 and self.topLineNum != 0:
            self.topLineNum += self.UP
            return
        elif increment == self.DOWN and nextLineNum == curses.LINES and (
                self.topLineNum + curses.LINES) != self.nOutputLines:
            self.topLineNum += self.DOWN
            return

        # scroll highlight line
        if increment == self.UP and (self.topLineNum != 0 or
                                     self.highlightLineNum != 0):
            self.highlightLineNum = nextLineNum
        elif increment == self.DOWN and (
                self.topLineNum + self.highlightLineNum + 1
        ) != self.nOutputLines and self.highlightLineNum != curses.LINES:
            self.highlightLineNum = nextLineNum

    def restoreScreen(self):
        curses.nocbreak()
        curses.echo()
        curses.endwin()

    # catch any weird termination situations
    def __del__(self):
        self.restoreScreen()
