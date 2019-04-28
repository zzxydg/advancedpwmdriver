#!/usr/bin/python

try:
    import os.path
    import sys
    import curses
    import time
    import logging
    import logging.config
    import configparser
    import industrialboarddriver
#endtry    
except Exception as e:
    logging.error("main::Unable to load import '%s'" % str(e))
#endexcept

# load the logging configuration
logging.config.fileConfig("debuglogfile.cfg")
logging.debug("main::logging file configuration loaded from 'debuglogfile.cfg'")

# lookup power (channel) keycodes
PowerKeycodes = [ord("0"),
    ord("1"), ord("2"), ord("3"), ord("4")
]

# lookups for points keycodes
PointKeycodes = [ord("z"),
    ord("q"), ord("w"), ord("e"), ord("r"), ord("t"), ord("y"), ord("u"), ord("i"),
    ord("o"), ord("p"), ord("a"), ord("s"), ord("d"), ord("f"), ord("g"), ord("h"),
    ord("j"), ord("k")
]

def fnprocesskeypress(thekeycode):
    logging.debug("main::fnprocesskeypress")
    
    try:
        h = list(PointKeycodes)
        thepoint = h.index(thekeycode)
    #endtry
    except:
        thepoint = -1
    #endexcept

    try:
        j = list(PowerKeycodes)
        thepower = j.index(thekeycode)
    #endtry        
    except:
        thepower = -1
    #endexcept        

    return [thepoint, thepower]    
#enddef

def fnPaintPointStatus(scr, bdpoints, thecurses, pointkeycodes):
    logging.debug("main::fnPaintPointStatus")
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
    scr.addstr(ypos,xpos, "| --- | --- | --- | --- | --- | --- | --- | --- |", thecurses.color_pair(3))
    ypos += 1
    scr.addstr(ypos,xpos, "+-----+-----+-----+-----+-----+-----+-----+-----+", thecurses.color_pair(3))

    ypos = 11; xpos = 3
    for x in range(1, 9):

        if (bdpoints.getpointstatus(x) == bdpoints.POINT_POSA):
            scr.addstr(ypos,xpos, "P%02d" % x, thecurses.color_pair(1))
        #endif
                
        if (bdpoints.getpointstatus(x) == bdpoints.POINT_POSB):
            scr.addstr(ypos,xpos, "P%02d" % x, thecurses.color_pair(2))    
        #endif

        xpos += 6
    #endfor
            
    ypos +=2; xpos = 3
    for x in range(9, 17):

        if (bdpoints.getpointstatus(x) == bdpoints.POINT_POSA):
            scr.addstr(ypos,xpos, "P%02d" % x, thecurses.color_pair(1))
        #endif
                
        if (bdpoints.getpointstatus(x) == bdpoints.POINT_POSB):
            scr.addstr(ypos,xpos, "P%02d" % x, thecurses.color_pair(2))
        #endif

        xpos += 6            
    #endfor

    ypos +=2; xpos = 3
    for x in range(17, len(pointkeycodes)):

        if (bdpoints.getpointstatus(x) == bdpoints.POINT_POSA):
            scr.addstr(ypos,xpos, "P%02d" % x, thecurses.color_pair(1))
        #endif
                
        if (bdpoints.getpointstatus(x) == bdpoints.POINT_POSB):
            scr.addstr(ypos,xpos, "P%02d" % x, thecurses.color_pair(2))
        #endif

        xpos += 6
    #endfor

    scr.refresh()
 
#enddef

def increment(value):
    return int(value+1)
#enddef

def fnPaintChannelTableStatus(scr, bdpower, thecurses, powerkeycodes):
    logging.debug("main::fnPaintChannelTableStatus")

    segments = []
    direction = []
    speed = []

    for i in range(4):
        segments.append(bdpower.listsegmentsforchannel(i))
        direction.append(bdpower.getchanneldirection(i))
        speed.append(int(float(bdpower.getchannelspeed(i)) / float(bdpower.MAX_PWM_VALUE) * float(100)))
    #nextfor
    
    xpos = 9
    ypos = 2

    scr.addstr(ypos,xpos, "+---+--------------+-----+------+", thecurses.color_pair(3))

    ypos +=1
    scr.addstr(ypos,xpos, "+ # + segments     + dir + smps +", thecurses.color_pair(3))

    ypos += 1
    scr.addstr(ypos,xpos, "+---+--------------+-----+------+", thecurses.color_pair(3))
    
    for i in range(4):

        if direction[i] == bdpower.CH_FWD:
            directionlabel = "FWD"
        elif direction[i] == bdpower.CH_REV:
            directionlabel = "REV"
        else:
            directionlabel = "OFF"
        #endif

        segments[i] = list(map(increment, segments[i]))

        ypos += 1
        scr.addstr(ypos,xpos, "| %d | %12s | %3s | %3d%% |" % ((i+1), segments[i], directionlabel, speed[i]), thecurses.color_pair(3))
    #endfor

    ypos += 1
    scr.addstr(ypos,xpos, "+---+--------------+-----+------+", thecurses.color_pair(3))

    scr.refresh()
        
#enddef

def fnUpdateScreenwithStatus(scr, bdpoints, bdpower, thecurses, powerkeycodes, pointkeycodes):    
    logging.debug("main::fnUpdateScreenwithStatus")
    fnPaintChannelTableStatus(scr, bdpower, thecurses, powerkeycodes)
    fnPaintPointStatus(scr, bdpoints, thecurses, pointkeycodes)
#enddef

def fngetvaluefromconfigurationfile(config, valuetype, sectionname, keyname, defaultreturnvalue):
    logging.debug("main::fngetvaluefromconfigurationfile")    

    try:
        logging.debug("main::fngetvaluefromconfigurationfile - attempting to read [valuetype=%s; sectionname=%s; keyname=%s]" % (valuetype, sectionname, keyname))
        if valuetype == "integer":
            return config.getint(sectionname, keyname)
        elif valuetype == "boolean":
            return config.getboolean(sectionname, keyname)
        else:
            return config.get(sectionname, keyname)
        #endif
    #endtry

    except Exception as e:
        logging.debug("main::fngetvaluefromconfigurationfile - failed to read [defaultreturnvalue=%s]" % defaultreturnvalue)
        return defaultreturnvalue
    #endexcept
#enddef

def fnExecuteAutoSequence(scr, bdpoints, bdpower, thecurses, powerkeycodes, pointkeycodes, config):
    logging.debug("main::fnExecuteAutoSequence")    

    numsteps=fngetvaluefromconfigurationfile(config, "integer", "general", "numsteps", 0)
    defaultstepdelayseconds=fngetvaluefromconfigurationfile(config, "integer", "general", "defaultstepdelayseconds", 1)
    numtimetorepeatsteps=fngetvaluefromconfigurationfile(config, "integer", "general", "numtimetorepeatsteps", 1)
    verbosestepexecution=fngetvaluefromconfigurationfile(config, "boolean", "general", "verbosestepexecution", False)

    # turn off the channel speed from the ADC so we have control!
    for channelnum in range(0, len(powerkeycodes)-1):
        bdpower.setchannelspeedfromadc(channelnum, False)
    #endfor

    sequenceaborted = False
    for stepnum in range(1, numsteps+1):
        sectionname="step%d" % stepnum

        steptitle=fngetvaluefromconfigurationfile(config, "string", sectionname, "title", "no title")
        scr.addstr(1,0, "|" + " " * 49 + "|", thecurses.color_pair(3))
        scr.addstr(1,3, "#%d: %s" % (stepnum, steptitle[:40]), thecurses.color_pair(4))
        scr.refresh()

        for channelnum in range(0, len(powerkeycodes)-1):
            # get channel speed and directions from the file
            channelspeedpercent=fngetvaluefromconfigurationfile(config, "integer", sectionname, "channel%dspeedpercent" % (channelnum+1), -1) 
            channelspeeddirection=fngetvaluefromconfigurationfile(config, "string", sectionname, "channel%ddirection" % (channelnum+1), "NOP")

            # set the channel speed, only if not the default value is returned
            if channelspeedpercent != -1:
                bdpower.setchannelspeed(channelnum, float(channelspeedpercent) / float(100) * float(bdpower.MAX_PWM_VALUE))
            #endif

            # set the channel direction, only if not the default value is returned
            if channelspeeddirection == "FWD":
                bdpower.setchanneldirection(channelnum, bdpower.CH_FWD)
            elif channelspeeddirection == "REV":
                bdpower.setchanneldirection(channelnum, bdpower.CH_REV)
            elif channelspeeddirection == "OFF":
                bdpower.setchanneldirection(channelnum, bdpower.CH_OFF)
            else:
                pass # NOP
            #endif
            
        #endfor

        for pointnum in range(0, len(pointkeycodes)):
            pointdirection=fngetvaluefromconfigurationfile(config, "string", sectionname, "point%ddirection" % (pointnum+1), "NOP")

            if bdpoints.getpointstatus(pointnum+1) != bdpoints.POINT_DISABLED:

                if pointdirection == "POSA":
                    bdpoints.fncommandpoints(pointnum+1, bdpoints.POINT_POSA)
                elif pointdirection == "POSB":
                    bdpoints.fncommandpoints(pointnum+1, bdpoints.POINT_POSB)
                else:
                    pass # NOP
                #endif
            #endif
        #endfor

        # invoke power handler to read ADC and send signals to PWM, then update the screen with data
        bdpower.processchanges()
        fnUpdateScreenwithStatus(scr, bdpoints, bdpower, thecurses, powerkeycodes, pointkeycodes)            

        stepdelayseconds=fngetvaluefromconfigurationfile(config, "integer", sectionname, "stepdelayseconds", defaultstepdelayseconds)
        time.sleep(stepdelayseconds)

        # Esc to abort the sequence
        c = scr.getch()
        if c == 27:
            sequenceaborted = True
            break
        #endif
        
    #endfor

    # reset thw power and the points
    if sequenceaborted == True:
        scr.addstr(1,3, "Sequence ABORTED: resetting power and points", thecurses.color_pair(4))
    else:
        scr.addstr(1,3, "Sequence complete: resetting power and points", thecurses.color_pair(4))
    #endif
    scr.refresh()

    # turn on the channel speed from the ADC so user has control!
    for channelnum in range(0, 4):
        bdpower.setchanneldirection(channelnum, bdpower.CH_OFF)
        bdpower.setchannelspeedfromadc(channelnum, True)
    #endfor

    bdpower.processchanges()

    # for pointnum in range(0, len(pointkeycodes)):
    #     bdpoints.fncommandpoints(pointnum+1, bdpoints.POINT_POSA)
    # #endfor
        
    scr.addstr(1,0, "|" + " " * 49 + "|", thecurses.color_pair(3))
    scr.refresh()

#enddef

def fndrawborder(scr, thecurses, powerkeycodes, pointkeycodes):
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

    xpos=2
    scr.addstr(ypos,xpos, "Channel:", thecurses.color_pair(3))
    xpos=11
    for x in range(1, len(powerkeycodes)):
        scr.addstr(ypos,xpos, "'%s' " % chr(powerkeycodes[x]), thecurses.color_pair(3))
        xpos += 4
    ypos += 1

    xpos=2
    scr.addstr(ypos,xpos, "Points :", thecurses.color_pair(3))
    xpos=11
    for x in range(1, 9):
        scr.addstr(ypos,xpos, "'%s' " % chr(pointkeycodes[x]), thecurses.color_pair(3))
        xpos+= 4
    ypos += 1

    xpos=2
    scr.addstr(ypos,xpos, "Points :", thecurses.color_pair(3))
    xpos=11
    for x in range(9, 17):
        scr.addstr(ypos,xpos, "'%s' " % chr(pointkeycodes[x]), thecurses.color_pair(3))
        xpos+= 4
    ypos += 1

    xpos=2
    scr.addstr(ypos,xpos, "Points :", thecurses.color_pair(3))
    xpos=11
    for x in range(17, len(pointkeycodes)):
        scr.addstr(ypos,xpos, "'%s' " % chr(pointkeycodes[x]), thecurses.color_pair(3))
        xpos+= 4

    scr.addstr(ypos,xpos+3, "F8=Auto; F9=Linked; Esc=Exit", thecurses.color_pair(3))
    
    ypos += 1    
    
    xpos=0
    scr.addstr(ypos,xpos, "+-------------------------------------------------+", thecurses.color_pair(3))

    scr.refresh()
#enddef

def main(configfilename):
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

    fndrawborder(stdscr, curses, PowerKeycodes, PointKeycodes)

    # open the configuration parser
    config = configparser.ConfigParser()

    logging.debug("main(): Starting up the IndustrialBoardDriver")
    bdpoints = industrialboarddriver.PointDriver()
    bdpower = industrialboarddriver.PowerDriver()

    logging.debug("main(): Settings channels")
    # channel 0
    bdpower.addsegmenttochannel(0, 1)
    bdpower.addsegmenttochannel(0, 2)
    bdpower.addsegmenttochannel(0, 3)
    bdpower.addsegmenttochannel(0, 4)
    bdpower.setchanneldirection(0, bdpower.CH_OFF)

    # channel 1
    bdpower.addsegmenttochannel(1, 5)
    bdpower.addsegmenttochannel(1, 6)
    bdpower.setchanneldirection(1, bdpower.CH_OFF)

    # channel 2
    bdpower.addsegmenttochannel(2, 7)
    bdpower.setchanneldirection(2, bdpower.CH_OFF)

    # channel 3
    bdpower.addsegmenttochannel(3, 8)
    bdpower.setchanneldirection(3, bdpower.CH_OFF)

    # disable points
    logging.debug("main(): disable redundant points")
    bdpoints.disablepoints(1)
    bdpoints.disablepoints(8)
    
    # Purge the command window buffer
    logging.debug("main(): Initialisation Complete")

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
                
            elif c == 272: # F8 to invoke autosequence
                
                stdscr.addstr(1,12, "-Invoking auto sequence-", curses.color_pair(3))
                stdscr.refresh()

                config.read(configfilename)
                fnExecuteAutoSequence(stdscr, bdpoints, bdpower, curses, PowerKeycodes, PointKeycodes, config)

                stdscr.addstr(1,12, "-auto sequence complete-", curses.color_pair(3))
                stdscr.refresh()
                
            elif c == 273: # F9 to toggle linked points
                
                DriveLinkedPoints = not bdpoints.fngetlinkedpointstatus()
                bdpoints.fnsetlinkedpointstatus(DriveLinkedPoints)
                
                stdscr.addstr(1,12, "DriveLinkedPoints=%5s" % DriveLinkedPoints , curses.color_pair(3))
                stdscr.refresh()
            else:
                ThePointPower = fnprocesskeypress(c)

                if ThePointPower[0] != -1:
                    if ThePointPower[0] == 0:
                        bdpoints.clearallpoints()
                        stdscr.addstr(1,12, "-- clearing all points --", curses.color_pair(3))
                        stdscr.refresh()
                        logging.debug("main(): KeyPress::Clearing all points")
                    else:
                        # Drive the point (and any pair if needed)
                        bdpoints.togglepoint(ThePointPower[0])

                        stdscr.addstr(1,12, "-- toggling point [%02d] --" % ThePointPower[0], curses.color_pair(3))
                        stdscr.refresh()                        
                        
                    #endif
                        
                    # update screen based on any changes
                    fnUpdateScreenwithStatus(stdscr, bdpoints, bdpower, curses, PowerKeycodes, PointKeycodes)

                #endif

                if ThePointPower[1] != -1:
                    if ThePointPower[1] == 0:
                        bdpower.switchoffallchannels()
                        stdscr.addstr(1,12, "- clearing all channels -", curses.color_pair(3))
                        stdscr.refresh()
                        logging.debug("main(): KeyPress::switching off all channels")
                    else:
                        bdpower.togglechanneldirection((ThePointPower[1]-1))
                        stdscr.addstr(1,12, "- toggling channel [%02d] -" % ThePointPower[1], curses.color_pair(3))
                        stdscr.refresh()
                        logging.debug("main(): KeyPress::toggling channel [%s] direction" % ThePointPower[1])
                    #endif

                    # update screen based on any changes
                    fnUpdateScreenwithStatus(stdscr, bdpoints, bdpower, curses, PowerKeycodes, PointKeycodes)
                        
                #endif

                if ThePointPower[0] == -1 and ThePointPower[1] == -1:
                    stdscr.addstr(1,12, "--invalid keypress [%d]--" % c, curses.color_pair(1))
                    stdscr.refresh()
                #endif                                
            #endif                                        
        #endfor

        # invoke power handler to read ADC and send signals to PWM        
        if bdpower.processchanges() == True:

            # update screen based on any changes
            fnUpdateScreenwithStatus(stdscr, bdpoints, bdpower, curses, PowerKeycodes, PointKeycodes)
        #endif

        # wait a bit to reduce CPU load                     
        time.sleep(0.25)
    #endwhile

    # Clear all points to allow the CDU to reset, then exit
    logging.debug("main(): Cleaning up")
    curses.nocbreak()
    stdscr.keypad(0)
    curses.echo()
    curses.endwin()
#enddef

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("ERROR: You must specify the demo sequence configuration file on the command line\ne.g. python %s demo-sequence.cfg" % sys.argv[0])
        exit(1)
    else:
        # get the config name from the command line and pass in
        main(sys.argv[1])
    #endif
#endif
        
#EOF
