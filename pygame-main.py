#!/usr/bin/python3

try:
    from pygame import *
    import os.path
    import sys
    import pygame
    import time
    import logging
    import logging.config
    import configparser    
    import industrialboarddriver
#endtry    
except Exception as e:
    logging.error("Unable to load import '%s'" % str(e))
#endexcept

# load the logging configuration
logging.config.fileConfig("debuglogfile.cfg")
logging.debug("logging file configuration loaded from 'debuglogfile.cfg'")
Font = None
main_dir = os.path.dirname(sys.argv[0]) # absolute dir name

PowerKeycodes = [ord("0"),
    ord("1"), ord("2"), ord("3"), ord("4")
]

PointKeycodes = [ord("z"),
    ord("q"), ord("w"), ord("e"), ord("r"), ord("t"), ord("y"), ord("u"), ord("i"), ord("o"), ord("p"),
    ord("a"), ord("s"), ord("d"), ord("f"), ord("g"), ord("h"), ord("j"), ord("k")
]

PhyProximitySensors = [[0,0],
    [600,110],  # S01=OK
    [750,60],   # S02=OK
    [230,60],   # S03=OK
    [420,380],  # S04=OK
    [200,530],  # S05=OK
    [550,410],  # S06=OK
    [825,480],  # S07=OK
    [825,585],  # S08=OK
    [65,460],   # S09=OK
    [10,240],
    [10,260],
    [10,280],
    [10,300],
    [10,320],
    [10,340],
    [10,360]
]

PhyPointHotspots = [[0,0],
    [254, 50], #P01=OK
    [295, 50], #P02=OK
    [255,100], #P03=OK
    [541, 50], #P04=OK
    [500,100], #P05=OK
    [542,100], #P06=OK
    [500,150], #P07=OK                    
    [757, 50], #P08=OK                    
    [950,272], #P09=OK
    [720,500], #P10=OK
    [680,450], #P11=OK
    [460,550], #P12=OK
    [419,500], #P13=OK
    [248,550], #P14=OK
    [521,450], #P15=OK
    [474,401], #P16=OK
    [415,350], #P17=OK
    [310,250], #P18=OK
    [  0,  0], #P19=N/A
    [  0,  0], #P20=N/A
    [  0,  0], #P21=N/A
    [  0,  0], #P22=N/A
    [  0,  0], #P23=N/A
    [  0,  0]  #P24=N/A
]

ChannelSpeedIncrement = [[0,0],
    [791,228],
    [791,243],
    [791,251],
    [791,271]
]

ChannelSpeedDecrement = [[0,0],
    [719,228],
    [719,243],
    [719,251],
    [719,271]
]

ChannelDirectionHotspots = [[0,0],
    [640, 228],
    [640, 243],
    [640, 256],
    [640, 273]
]

SegmentOverlayPoints = [
    [[734,  50], [938,  50], [950,  62], [950, 538], [940, 550], [780, 550]], #0 - OK
    [[160,  50], [270,  50]], #1 - OK
    [[146,  50], [ 60,  50], [ 50,  63], [ 50, 537], [ 62, 550], [762, 550]], #2 - OK
    [[282,  50], [717,  50]], #3 - OK
    [[233, 100], [890, 100], [900, 112], [900, 485], [890, 500], [400, 500]], #4 - OK    
    [[217, 100], [112, 100], [100, 114], [100, 487], [111, 500], [385, 500]], #5 - OK
    [[161, 150], [150, 165], [150, 437], [163, 450], [838, 450], [850, 436], [850, 162], [838, 150], [160, 150]], #6 - OK
    [[498, 426], [255, 195]] #7 - OK
]

ChannelDirectionColours = [
    [[127, 127, 127], [63, 63, 0], [0, 63, 63]],
    [[127, 127, 127], [127, 127, 0], [0, 127, 127]],
    [[127, 127, 127], [191, 191, 0], [0, 191, 191]],
    [[127, 127, 127], [255, 255, 0], [0, 255, 255]]
]

def load_image(thefile):
    logging.debug("load_image")
    # loads an image, prepares it for play
    thefile = os.path.join(main_dir, thefile)
    try:
        surface = pygame.image.load(thefile)
    #endtry
    except pygame.error:
        logging.error('Could not load image "%s" %s' %(thefile, pygame.get_error()))
        return None
    #endexcept
    return surface.convert()
#enddef

def fndrawhistory(hWnd, thehistory):
    logging.debug("fndrawhistory")
    hWnd.blit(Font.render(
        "__ [COMMAND EVENT HISTORY] __ [Esc=Quit; F6=Luddite; F7=Mode; F8=Auto; F9=Toggle-Linked; 0=Channels off; z=Points off] _____ ",
        1, (155, 155, 155), (0,0,0)), (2, 600)
    )
    ypos = 680
    
    h = list(thehistory)
    h.reverse()
    for line in h:
        r = hWnd.blit(line, (0, ypos))
        hWnd.fill((0, 0, 0), (r.right, r.top, 700, r.height))
        ypos -= Font.get_height()
    #endfor
    display.flip()
    return
#enddef

def fnprintstatusmessage(message, hWnd, thehistory):
    logging.debug("fnprintstatusmessage")
    logging.debug("fnprintstatusmessage(): message=%s" % message)
    img = Font.render("%s: %s" % (time.asctime(), message), 1, (0, 255, 0), (0, 0, 0))
    thehistory.append(img)
    fndrawhistory(hWnd, thehistory)
    return
#enddef

def fnconvertmousetokeypress(mousex, mousey):
    logging.debug("fnconvertmousetokeypress")
    thekeycode = 0 # default to invalid

    # Test Physical point hotspots
    for i in range(len(PhyPointHotspots)):
        bytestream = PhyPointHotspots[i]

        if fnTestHotspot(bytestream[0], bytestream[1], mousex, mousey, 8) == True:
            thekeycode = PointKeycodes[i]
            break
        #endif
    #endfor        

    # Test Power hotspots
    for i in range(len(ChannelDirectionHotspots)):
        bytestream = ChannelDirectionHotspots[i]

        if fnTestHotspot(bytestream[0], bytestream[1], mousex, mousey, 8) == True:
            thekeycode = PowerKeycodes[i]
            break
        #endif
    #endfor

    return thekeycode
#enddef

def fnDecodeSpeedIncrementDecrement(mousex, mousey):

    thedecrementchannel=-1
    theincrementchannel=-1

    # Test Channel Speed Decrement hotspots
    for i in range(len(ChannelSpeedDecrement)):
        bytestream = ChannelSpeedDecrement[i]

        if fnTestHotspot(bytestream[0], bytestream[1], mousex, mousey, 8) == True:
            thedecrementchannel = i
            break
        #endif
    #endfor

    # Test Channel Speed Decrement hotspots
    for i in range(len(ChannelSpeedIncrement)):
        bytestream = ChannelSpeedIncrement[i]

        if fnTestHotspot(bytestream[0], bytestream[1], mousex, mousey, 8) == True:
            theincrementchannel = i
            break
        #endif
    #endfor
    
    return [thedecrementchannel, theincrementchannel]
#enddef

def fnTestHotspot(hotspotx, hotspoty, mousex, mousey, tolerance):
    logging.debug("fnTestHotspot")
    if ((mousex > (hotspotx - tolerance)) and (mousex < (hotspotx + tolerance))):
        if ((mousey > (hotspoty - tolerance)) and (mousey < (hotspoty + tolerance))):
            result = True
        else:
            result = False
        #endif
    else:
        result = False
    #endif 
                   
    return result
#enddef

def fnprocesskeypress(thekeycode):
    logging.debug("fnprocesskeypress")
    
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

def fnPaintProximitySensorStatus(hWnd, bdproximity):
    logging.debug("fnPaintProximitySensorStatus")

    for x in range(1,len(PhyProximitySensors)):

        # Paint the Physical point hotspots
        pos = PhyProximitySensors[x]

        # Skip if the (x, y) co-ordinates are zero, is will be an un-used point (Physical or Virtual)
        if (pos[0] != 0):
            if (pos[1] != 0):
        
                xpos = pos[0] # - 3
                ypos = pos[1] # - 3
                radius = 6

                if bdproximity.fngetproximitysensorstatus(x) == True:
                    R=255; G=0; B=0
                else:
                    R=0; G=255; B=0
                #endif

                pygame.draw.circle ( hWnd, (R,G,B), (xpos, ypos), radius, 0)
            #endif
        #endif
    #endfor

    # print last updated time
    line = Font.render("%s" % time.asctime() , 1, (0, 0, 0), (255, 255, 255))    
    hWnd.blit(line, (0, 0))

    display.flip()
#enddef

def fnPaintPointStatus(hWnd, bdpoints):
    logging.debug("fnPaintPointStatus")
    
    for x in range(1,len(PhyPointHotspots)):

        # Paint the Physical point hotspots
        pos = PhyPointHotspots[x]

        # Skip if the (x, y) co-ordinates are zero, is will be an un-used point (Physical or Virtual)
        if (pos[0] != 0):
            if (pos[1] != 0):
        
                xpos = pos[0] - 6
                ypos = pos[1] - 6
                width = 12
                height = 12

                # check for disabled points
                if bdpoints.getpointstatus(x) != bdpoints.POINT_DISABLED:

                    # POSa = Red
                    if (bdpoints.getpointstatus(x) == bdpoints.POINT_POSA):
                        R=255; G=0; B=0
                    #endif

                    # POSB = Green
                    if (bdpoints.getpointstatus(x) == bdpoints.POINT_POSB):
                        R=0; G=255; B=0
                    #endif

                    pygame.draw.rect ( hWnd, (R ,G,B), Rect(xpos, ypos, width, height), 0)

                #endif
            #endif
        #endif             
        
    #endfor
                
    # print last updated time
    line = Font.render("%s" % time.asctime() , 1, (0, 0, 0), (255, 255, 255))    
    hWnd.blit(line, (0, 0))

    display.flip()
#enddef

def increment(value):
    return int(value+1)
#enddef

def fnPaintChannelTableStatus(hWnd, bdpower):
    logging.debug("fnPaintChannelTableStatus")

    segments = []
    direction = []
    speed = []

    for i in range(4):
        segments.append(bdpower.listsegmentsforchannel(i))
        direction.append(bdpower.getchanneldirection(i))
        speed.append(int(float(bdpower.getchannelspeed(i)) / float(bdpower.MAX_PWM_VALUE) * float(100)))
    #nextfor
    
    xpos = 460
    ypos = 160

    line = Font.render("+---+--------------+-----+------------------+" , 1, (0, 0, 0), (255, 255, 255))
    ypos += Font.get_height()
    hWnd.blit(line, (xpos, ypos))

    line = Font.render("+ # + segments     + dir + [m] [  speed   ] +" , 1, (0, 0, 0), (255, 255, 255))
    ypos += Font.get_height()
    hWnd.blit(line, (xpos, ypos))

    line = Font.render("+---+--------------+-----+------------------+" , 1, (0, 0, 0), (255, 255, 255))
    ypos += Font.get_height()
    hWnd.blit(line, (xpos, ypos))    
    
    for i in range(4):

        if direction[i] == bdpower.CH_FWD:
            directionlabel = "--F"
        elif direction[i] == bdpower.CH_REV:
            directionlabel = "R--"
        else:
            directionlabel = "-N-"
        #endif

        segments[i] = list(map(increment, segments[i]))

        if bdpower.getchannelspeedfromadc(i) == True:
            channeladcmode ="A"
        else:
            channeladcmode = "G"
        #endif
        line = Font.render("| %d | %12s | %3s | [%s] [-] %03d%% [+] |" % ((i+1), segments[i], directionlabel, channeladcmode, speed[i]) , 1, (0, 0, 0), (255, 255, 255))
            
        ypos += Font.get_height()
        hWnd.blit(line, (xpos, ypos))

    line = Font.render("+---+--------------+-----+------------------+" , 1, (0, 0, 0), (255, 255, 255))
    ypos += Font.get_height()
    hWnd.blit(line, (xpos, ypos))

    # print last updated time
    line = Font.render("%s" % time.asctime() , 1, (0, 0, 0), (255, 255, 255))    
    hWnd.blit(line, (0, 0))

    display.flip()
#enddef

def fnconvertchanneldirectiontocolour(bdpower, channel, direction):
    logging.debug("fnconvertchanneldirectiontocolour")

    if direction == bdpower.CH_FWD:
        directionindex = 1
    elif direction == bdpower.CH_REV:
        directionindex = 2
    else:
        directionindex = 0

    return ChannelDirectionColours[channel][directionindex]
#enddef

def fnPaintSegmentStatus(hWnd, bdpower):
    logging.debug("fnPaintSegmentStatus")

    segments = []
    direction = []

    for i in range(4):
        segments.append(bdpower.listsegmentsforchannel(i))
        direction.append(bdpower.getchanneldirection(i))
    #endfor

    for i in range(4):                
        for segment in segments[i]:
            pointlist = SegmentOverlayPoints[segment]
            colour = fnconvertchanneldirectiontocolour(bdpower, i, direction[i])
            pygame.draw.lines(hWnd, colour, False, pointlist, 6)
        #endfor
    #endfor

    # print last updated time
    line = Font.render("%s" % time.asctime() , 1, (0, 0, 0), (255, 255, 255))    
    hWnd.blit(line, (0, 0))

    display.flip()
#enddef

def fnUpdateScreenwithStatus(hWnd, bdpoints, bdpower):
    logging.debug("fnUpdateScreenwithStatus")
    fnPaintChannelTableStatus(hWnd, bdpower)
    fnPaintSegmentStatus(hWnd, bdpower)
    fnPaintPointStatus(hWnd, bdpoints)
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

def fnExecuteAutoSequence(hWnd, bdpoints, bdpower, powerkeycodes, pointkeycodes, config):
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
    myhistory = []
    for stepnum in range(1, numsteps+1):
        sectionname="step%d" % stepnum

        steptitle=fngetvaluefromconfigurationfile(config, "string", sectionname, "title", "no title")

        txt = "#%d: %s" % (stepnum, steptitle[:40])
        fnprintstatusmessage(txt, hWnd, myhistory)
        myhistory=myhistory[-4:]                                        

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
        fnUpdateScreenwithStatus(hWnd, bdpoints, bdpower)      

        stepdelayseconds=fngetvaluefromconfigurationfile(config, "integer", sectionname, "stepdelayseconds", defaultstepdelayseconds)
        time.sleep(stepdelayseconds)

        for e in event.get():

            if e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    sequenceaborted = True
                #endif
            #endif
        #endfor

        if sequenceaborted == True:
            break
        #endif
        
    #endfor

    # reset thw power and the points
    if sequenceaborted == True:
        txt = "Sequence ABORTED: resetting power and points"
    else:
        txt = "Sequence complete: resetting power and points"
    #endif

    fnprintstatusmessage(txt, hWnd, myhistory)
    myhistory=myhistory[-4:]                                        

    # turn on the channel speed from the ADC so user has control!
    for channelnum in range(0, 4):
        bdpower.setchanneldirection(channelnum, bdpower.CH_OFF)
        bdpower.setchannelspeedfromadc(channelnum, True)
    #endfor

    bdpower.processchanges()

    # for pointnum in range(0, len(pointkeycodes)):
    #    bdpoints.fncommandpoints(pointnum+1, bdpoints.POINT_POSA)
    # #endfor

    fnUpdateScreenwithStatus(hWnd, bdpoints, bdpower, bdproximity)        

    # erase the status message to stop stale messages appearing
    hWnd.fill((0, 0, 0), (0, 600, 1000, 100))

#enddef

def main(configfilename):
    logging.debug("main(): begin")

    # Init the pygame engine
    logging.debug("main(): Starting Graphics Engine")
    pygame.init()

    logging.debug("main(): pygame version %s" % pygame.version.ver)

    # Check if pygame supports what we need
    logging.debug("main(): Checking pygame capabilities")
    if not pygame.image.get_extended():
        raise SystemExit("main(): Sorry, extended image module required")
    else:
        logging.debug("main(): Extended image capability present")
    #endif

    logging.debug("main(): Starting up the IndustrialBoardDriver")
    bdpoints = industrialboarddriver.PointDriver()
    bdpower = industrialboarddriver.PowerDriver()
    dbproximity = industrialboarddriver.ProximitySensors()

    logging.debug("main(): IndustrialBoardDriver version %s" % industrialboarddriver.VERSION)

    # open the configuration parser
    config = configparser.ConfigParser()
    
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

    # Set the window size
    logging.debug("main(): Switching to Graphics mode")
    win = display.set_mode((1000, 700))
    display.set_caption("BMRC Industrial Board Driver")

    # Set the font sizes
    logging.debug("main(): Loading font")
    global Font
    fontname = "freemono"
    fontsize = 14
    Font = font.SysFont(fontname, fontsize, bold=True, italic=False)

    # Load the background
    logging.debug("main(): Loading layout background image")
    thebackground = load_image("boardlayout.png")
    win.blit(thebackground, (0,0))

    # Switching on the luddite relays to return control to the PWM
    logging.debug("main(): Switching on the luddite relays to give control to the PWM")
    for i in range(4):
        bdpoints.fnswitchludditerelays(i+1, bdpoints.LUDDITE_SWITCH_ON)
    #endfor
    bLudditeRelaysEnabled = True

    # Purge the command window buffer
    logging.debug("main(): Initialisation Complete")
    myhistory = []    

    # Update screen status to initial values
    fnUpdateScreenwithStatus(win, bdpoints, bdpower)

    # Print out "ready" to signifigy init complete and ready for user command
    txt = "Ready"
    fnprintstatusmessage(txt, win, myhistory)

    # Main application loop
    going = True
    while going:
        for e in event.get():
            bValidCommand = False
            if e.type == QUIT:
                going = False
            #endif

            if e.type == KEYDOWN:
                
                if e.key == K_ESCAPE:
                    going = False
                #endif

                if e.key == K_F6:

                    bValidCommand = True
                    bLudditeRelaysEnabled = not bLudditeRelaysEnabled
                    txt = "main(): Luddite relays Enabled=%s" % bLudditeRelaysEnabled
                    fnprintstatusmessage(txt, win, myhistory)
                    myhistory=myhistory[-4:]                    
                    for i in range(4):
                        bdpoints.fnswitchludditerelays(i+1, bLudditeRelaysEnabled)
                    #endfor                
                    
                elif e.key == K_F7:

                    bValidCommand = True
                    txt = "main(): Toggle GUI / ADC speed control mode"
                    fnprintstatusmessage(txt, win, myhistory)
                    myhistory=myhistory[-4:]                    
                    for channelnum in range(0, 4):
                        thevalue = bdpower.getchannelspeedfromadc(channelnum)
                        bdpower.setchannelspeedfromadc(channelnum, not thevalue)
                    #endfor

                elif e.key == K_F8:
                    bValidCommand = True
                    txt = "main(): Starting Execute Auto Sequence"
                    fnprintstatusmessage(txt, win, myhistory)
                    myhistory=myhistory[-4:]

                    config.read(configfilename)
                    fnExecuteAutoSequence(win, bdpoints, bdpower, PowerKeycodes, PointKeycodes, config)

                    txt = "main(): Ready:"
                    fnprintstatusmessage(txt, win, myhistory)
                    myhistory=myhistory[-4:]

                elif e.key == K_F9:
                    bValidCommand=True
                    DriveLinkedPoints = not bdpoints.fngetlinkedpointstatus()
                    bdpoints.fnsetlinkedpointstatus(DriveLinkedPoints)                    

                    txt = "main(): KeyPress::F9 DriveLinkedPoints=%s" % DriveLinkedPoints
                    fnprintstatusmessage(txt, win, myhistory)
                    myhistory=myhistory[-4:]
                #endif
                    
                else:
                    TheKeyCode = e.key
                    ThePointPower = fnprocesskeypress(TheKeyCode)

                    if ThePointPower[0] != -1:
                        bValidCommand = True
                        if ThePointPower[0] == 0:
                            bdpoints.clearallpoints()
                            txt = "main(): KeyPress::Clearing all points"
                        else:
                            # Drive the point (and any pair if needed)
                            bdpoints.togglepoint(ThePointPower[0])
                            txt = "main(): KeyPress::Processed point [%s]" % ThePointPower[0]
                            #endif                                
                            
                        #endif                        
                        fnUpdateScreenwithStatus(win, bdpoints, bdpower)
                    #endif

                    if ThePointPower[1] != -1:
                        bValidCommand = True
                        if ThePointPower[1] == 0:
                            bdpower.switchoffallchannels()
                            txt = "main(): KeyPress::switching off all channels"
                        else:
                            bdpower.togglechanneldirection((ThePointPower[1]-1))
                            txt = "main(): KeyPress::toggling channel [%s] direction" % ThePointPower[1]                                                   
                        #endif
                        fnUpdateScreenwithStatus(win, bdpoints, bdpower)
                    #endif

                    if ThePointPower[0] == -1 and ThePointPower[1] == -1:
                        txt = "main(): KeyPress::Unknown command [%s]" % TheKeyCode
                    #endif                        

                    fnprintstatusmessage(txt, win, myhistory)
                    myhistory=myhistory[-4:]
                    
                #endif
                                        
            if e.type == MOUSEBUTTONDOWN and e.button == 1:

                # Get the mouse position and convert to "keypress"
                pos = pygame.mouse.get_pos()

                # print last updated time
                line = Font.render("[%03d, %03d]" % (pos[0], pos[1]) , 1, (0, 0, 0), (255, 255, 255))    
                win.blit(line, (0, 15))
                display.flip()

                logging.debug("main(): MouseClick::pos=%s" % list(pos))
                
                ThePointPower = fnprocesskeypress(fnconvertmousetokeypress(pos[0], pos[1]))

                if ThePointPower[0] != -1:
                    bValidCommand = True
                    if ThePointPower[0] == 0:
                        bdpoints.clearallpoints()
                        txt = "main(): MouseClick::Clearing all points"
                    else:

                        # Drive the point (and any pair if needed)
                        bdpoints.togglepoint(ThePointPower[0])
                        txt = "main(): MouseClick::Processed point [%s]" % ThePointPower[0]
                        #endif
                                
                    #endif                    
                    fnUpdateScreenwithStatus(win, bdpoints, bdpower)
                #endif

                if ThePointPower[1] != -1:
                    bValidCommand = True
                    if ThePointPower[1] == 0:
                        bdpower.switchoffallchannels()
                        txt = "main(): MouseClick::switching off all channels"
                    else:
                        bdpower.togglechanneldirection((ThePointPower[1]-1))
                        txt = "main(): MouseClick::toggling channel [%s] direction" % ThePointPower[1]                                                   
                    #endif
                    fnUpdateScreenwithStatus(win, bdpoints, bdpower)
                #endif                    
                if bValidCommand == True:    
                    fnprintstatusmessage(txt, win, myhistory)
                    myhistory=myhistory[-4:]
                #endif

                SpeedIncrementDecrement = fnDecodeSpeedIncrementDecrement(pos[0], pos[1])

                if SpeedIncrementDecrement[0] != -1:
                    bdpower.decrementchannelspeed(SpeedIncrementDecrement[0]-1)
                #endif
                    
                if SpeedIncrementDecrement[1]!= -1:
                    bdpower.incrementchannelspeed(SpeedIncrementDecrement[1]-1)
                #endif
                    
            #endif                    
        #endfor

        # invoke power handler to read ADC and send signals to PWM (True will be returned if something changed and needs updating)
        if bdpower.processchanges() == True:
            # update screen based on any changes
            fnPaintChannelTableStatus(win, bdpower)
        #endif

        # read the proximity sensors and paint to the screen, but only if something has changed
        dbproximity.fnreadproximitysensors()
        if dbproximity.fnhasanyproximitystatuschanged() == True:
            fnPaintProximitySensorStatus(win, dbproximity)
        #endif

        # wait a bit to reduce CPU load                     
        time.sleep(0.25)
    #endwhile

    txt = "main(): Shutdown"
    fnprintstatusmessage(txt, win, myhistory)
    myhistory=myhistory[-4:]

    # Clear all points to allow the CDU to reset, then exit
    logging.debug("main(): Cleaning up")
    pygame.quit()
#enddef

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("ERROR: You must specify the demo sequence configuration file on the command line for example: python3 %s demo-sequence.cfg" % sys.argv[0])
        exit(1)
    else:
        # get the config name from the command line and pass in
        main(sys.argv[1])
    #endif
#endif

#EOF
