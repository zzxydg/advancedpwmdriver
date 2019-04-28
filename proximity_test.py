#!/usr/bin/python

try:
    import os.path
    import sys
    import curses
    import time
    import logging
    import logging.config
    import industrialboarddriver
#endtry    
except Exception as e:
    logging.error("main::Unable to load import '%s'" % str(e))
#endexcept

# load the logging configuration
logging.config.fileConfig("debuglogfile.cfg")
logging.debug("main::logging file configuration loaded from 'debuglogfile.cfg'")

def fnPaintProximityStatus(scr, bdproximity, thecurses):
    logging.debug("main::fnPaintProximityStatus")
    ypos = 10; xpos = 1

    scr.addstr(ypos,xpos, "+-----+-----+-----+-----+-----+-----+-----+-----+", thecurses.color_pair(3))
    ypos += 1
    scr.addstr(ypos,xpos, "| --- | --- | --- | --- | --- | --- | --- | --- |", thecurses.color_pair(3))
    ypos += 1
    scr.addstr(ypos,xpos, "+-----+-----+-----+-----+-----+-----+-----+-----+", thecurses.color_pair(3))
    ypos += 1
    scr.addstr(ypos,xpos, "| --- | --- | --- | --- | --- | --- | --- | --- |", thecurses.color_pair(3))
    ypos += 1
    scr.addstr(ypos,xpos, "+-----+-----+-----+-----+-----+-----+-----+-----+", thecurses.color_pair(3))
    ypos += 1

    ypos = 11; xpos = 3
    for x in range(1, 9):

        if (bdproximity.fngetproximitysensorstatus(x) == True):
            scr.addstr(ypos,xpos, "-Y-", thecurses.color_pair(1))
        else:
            scr.addstr(ypos,xpos, "-N-", thecurses.color_pair(2))
        #endif
        xpos += 6
        #endif                
    #endfor
            
    ypos +=2; xpos = 3
    for x in range(9, 17):

        if (bdproximity.fngetproximitysensorstatus(x) == True):
            scr.addstr(ypos,xpos, "-Y-", thecurses.color_pair(1))
        else:
            scr.addstr(ypos,xpos, "-N-", thecurses.color_pair(2))
        #endif
        xpos += 6
        #endif                
    #endfor

    scr.refresh()
 
#enddef

def fndrawborder(scr, thecurses):
    logging.debug("main::fndrawborder")
    
    xpos=0
    ypos=0
    scr.addstr(ypos,xpos, "+-------------------------------------------------+", thecurses.color_pair(3))
    ypos += 1
    
    for x in range(20):
        scr.addstr(ypos,xpos, "|" + " " * 49 + "|", thecurses.color_pair(3))
        ypos += 1

    # adjust the ypos to print the next four lines
    ypos -= 4

    scr.addstr(ypos,xpos+3, "Esc=Exit", thecurses.color_pair(3))
    
    ypos += 1    
    
    xpos=0
    scr.addstr(ypos,xpos, "+-------------------------------------------------+", thecurses.color_pair(3))

    scr.refresh()
#enddef


def main():
    logging.debug("main(): begin")

    # Init the pygame engine
    logging.debug("main(): Starting curses")
    stdscr = curses.initscr()

    curses.noecho()
    curses.cbreak()
    stdscr.keypad(1)
    stdscr.nodelay(True)
    
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_GREEN)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)

    fndrawborder(stdscr, curses)
    
    logging.debug("main(): Starting up the IndustrialBoardDriver")
    bdproximity = industrialboarddriver.ProximitySensors()

    logging.debug("main(): IndustrialBoardDriver initialised, version '%s'" % industrialboarddriver.VERSION)

    # Main application loop
    going = True
    while going:

        # key the key stroke
        c = stdscr.getch()

        if c != -1:

            if c == 27:  # Esc pressed, exit
                going = False
                stdscr.addstr(1,12, "- Exiting application. -", curses.color_pair(3))
                stdscr.refresh()
                time.sleep(0.5)
            #endif
        #endif

        bdproximity.fnreadproximitysensors()
        fnPaintProximityStatus(stdscr, bdproximity, curses)
        time.sleep(1.0)

    #endwhile
   
    logging.debug("main(): Cleaning up")
    curses.nocbreak()
    stdscr.keypad(0)
    curses.echo()
    curses.endwin()

#enddef

if __name__ == '__main__':
    main()
#endif
        
#EOF
