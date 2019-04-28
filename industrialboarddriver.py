#!/usr/bin/python3

try:
    import time
    import logging
    import MCP23017
    import Adafruit_ADS1x15
    import Adafruit_PCA9685
#endtry    
except Exception as e:
    logging.error("Unable to load import '%s'" % str(e))
#endexcept

VERSION = "1.4.0_20190427_python3"

class channel(object):

    CH_FWD = 1
    CH_OFF = 0
    CH_REV = -1
    
    def __init__(self, number=0, logger=None):        
        self.number = number
        self.speed = 0
        self.previousdirection = self.CH_OFF
        self.direction = self.CH_OFF
        self.directionchangedsincelastcall = False
        self.segments = []
        self.readspeedfromadc = True
        self.logger = logger or logging.getLogger(__name__)
        self.logger.debug("channel[%d]::__init__" % self.number)

    def setreadspeedfromadc(self, thevalue):
        if self.readspeedfromadc != thevalue:
            self.directionchangedsincelastcall = True
        #endif
        self.readspeedfromadc = thevalue
        self.logger.debug("channel[%d]::setreadspeedfromadc=%s" % (self.number, self.readspeedfromadc))

    def getreadspeedfromadc(self):
        self.logger.debug("channel[%d]::getreadspeedfromadc=%s" % (self.number, self.readspeedfromadc))
        return self.readspeedfromadc
    
    def setspeed(self, thespeed):
        self.speed = thespeed
        self.logger.debug("channel[%d]::setspeed=%s" % (self.number, self.speed))

    def getspeed(self):
        self.logger.debug("channel[%d]::getspeed=%s" % (self.number, self.speed))
        return self.speed

    def toggledirection(self):

        if self.previousdirection == self.CH_FWD and self.direction == self.CH_OFF:
            self.previousdirection = self.direction
            self.direction = self.CH_REV

        elif self.previousdirection == self.CH_REV and self.direction == self.CH_OFF:
            self.previousdirection = self.direction
            self.direction = self.CH_FWD

        elif self.previousdirection == self.CH_OFF and self.direction == self.CH_FWD:
            self.previousdirection = self.direction
            self.direction = self.CH_OFF

        elif self.previousdirection == self.CH_OFF and self.direction == self.CH_REV:
            self.previousdirection = self.direction
            self.direction = self.CH_OFF

            
        elif self.previousdirection == self.CH_OFF and self.direction == self.CH_OFF:
            self.previousdirection = self.CH_OFF
            self.direction = self.CH_FWD
        #endif

        self.logger.debug("channel[%d]::toggledirection (self.previousdirection=%s; self.direction=%s" % (self.number, self.previousdirection, self.direction ))
    
        self.directionchangedsincelastcall = True
    #enddef

    def setdirection(self, thedirection):
        self.previousdirection = self.direction
        self.direction = thedirection
        self.directionchangedsincelastcall = True
        self.logger.debug("channel[%d]::setdirection=%s" % (self.number, self.direction))

    def getdirection(self):
        self.logger.debug("channel[%d]::getdirection=%s" % (self.number, self.direction))
        return self.direction

    def hasdirectionchangedsincelastcall(self):
        thevalue = self.directionchangedsincelastcall
        self.directionchangedsincelastcall = False
        return thevalue

    def addsegment(self, thesegmentnumber):
        if thesegmentnumber >= 0 and thesegmentnumber <= 7:
            self.segments.append(thesegmentnumber)
        else:
            self.logger.error('thesegmentnumber must be between 0 and 7)')
            raise ValueError('thesegmentnumber must be between 0 and 7)')
        #endif
        self.logger.debug("channel[%d]::addsegment[%s]" % (self.number, thesegmentnumber))

    def delsegment(self, thesegmentnumber):
        if thesegmentnumber >= 0 and thesegmentnumber <= 7:
            self.segments.remove(thesegmentnumber)
        else:
            self.logger.error('thesegmentnumber must be between 0 and 7)')
            raise ValueError('thesegmentnumber must be between 0 and 7)')
        #endif            
        self.logger.debug("channel[%d]::delsegment=%s" % (self.number, thesegmentnumber))

    def getsegments(self):
        self.logger.debug("channel[%d]::getsegments=%s" % (self.number, list(self.segments)))
        return list(self.segments)
        
class PowerDriver(object):

    MAX_PWM_VALUE = 4095
    MIN_PWM_VALUE = 0
    PWM_FREQ = 50

    CH_FWD = 1
    CH_OFF = 0
    CH_REV = -1    

    def __init__(self, logger=None):

        self.logger = logger or logging.getLogger(__name__)
        self.thechannelist = [ channel(i, logger) for i in range(4)]

        try:
            self.adc = Adafruit_ADS1x15.ADS1115()
            self.pwm = Adafruit_PCA9685.PCA9685()
            self.pwm.set_pwm_freq(self.PWM_FREQ)
        #endtry
        except Exception as e:
            self.logger.error("Unable to load import '%s'" % str(e))
        #endexcept    
                         
        self.ADCgain = 1        # default to 1, don't change
        self.adcmin = 0         # minimum value returned by ASS1115 simpletest.py example application run on RaspberryPi
        self.adcmax = 26449     # maximum value returned by ASS1115 simpletest.py example application run on RaspberryPi
        self.adcminchange = 10  # tweak this value if the system responds too slowly to a speed change
        
        self.logger.debug("PowerDriver::__init__")

    def POST(self):
        self.logger.debug("PowerDriver::POST")

    def setadcminchange(self, thevalue):
        self.adcminchange = thevalue
        self.logger.debug("PowerDriver::adcminchange=%s" % self.adcminchange)

    def setadcmin(self, thevalue):
        self.adcmin = thevalue
        self.logger.debug("PowerDriver::setadcmin=%s" % self.adcmin)

    def setadcmax(self, thevalue):
        self.adcmax = thevalue
        self.logger.debug("PowerDriver::setadcmax=%s" % self.adcmax)

    def addsegmenttochannel(self, channel, segment):
        self.thechannelist[channel].addsegment(segment-1)
        self.logger.debug("PowerDriver::addsegmenttochannel[%s]=%s" % (channel,segment))
        
    def removesegmentfromchannel(self, channel, segment):
        self.thechannelist[channel].delsegment(segment-1)
        self.logger.debug("PowerDriver::removesegmentfromchannel[%s]=%s" % (channel,segment))
        
    def removeallsegmentsfromchannel(self, channel):
        self.logger.debug("PowerDriver::removeallsegmentsfromchannel=%s" % channel)
    
    def listsegmentsforchannel(self, channel):
        self.logger.debug("PowerDriver::listsegmentsforchannel=%s" % channel)
        return self.thechannelist[channel].getsegments()
        	
    def ischannellinkedtosegment(self, channel, segment):
        self.logger.debug("PowerDriver::ischannellinkedtosegment[%s]=%s" % (channel,segment))

    def setchannelspeedfromadc(self, channel, thevalue):
        self.thechannelist[channel].setreadspeedfromadc(thevalue)
        self.logger.debug("PowerDriver::setchannelspeedfromadc[%s]=%s" % (channel,thevalue))        

    def getchannelspeedfromadc(self, channel):
        self.logger.debug("PowerDriver::getchannelspeedfromadc[%s]" % channel)
        return self.thechannelist[channel].getreadspeedfromadc()
    
    def setchannelspeed(self, channel, speed):
        self.thechannelist[channel].setspeed(int(speed))
        self.logger.debug("PowerDriver::setchannelspeed[%s]=%s" % (channel,int(speed)))

    def decrementchannelspeed(self, channel):
        speed = self.thechannelist[channel].getspeed()
        if speed > self.MIN_PWM_VALUE:
            speed -= 256
        #endif
        if speed < self.MIN_PWM_VALUE:
            speed = self.MIN_PWM_VALUE
        #endif
        self.thechannelist[channel].setspeed(int(speed))
        self.logger.debug("PowerDriver::decrementchannelspeed[%s]=%s" % (channel,int(speed)))

    def incrementchannelspeed(self, channel):
        speed = self.thechannelist[channel].getspeed()
        if speed < self.MAX_PWM_VALUE:
            speed += 256
        #endif
        if speed > self.MAX_PWM_VALUE:
            speed = self.MAX_PWM_VALUE
        #endif
        self.thechannelist[channel].setspeed(int(speed))        
        self.logger.debug("PowerDriver::incrementchannelspeed[%s]=%s" % (channel,int(speed)))

    def getchannelspeed(self, channel):
        self.logger.debug("PowerDriver::getchannelspeed=%s" % channel)
        return self.thechannelist[channel].getspeed()

    def switchoffallchannels(self):
        for i in range(4):
            self.thechannelist[i].setdirection(self.CH_OFF)
            self.thechannelist[i].setdirection(self.CH_OFF)
        self.logger.debug("PowerDriver::switchoffallchannels[]")

    def togglechanneldirection(self, channel):
        self.thechannelist[channel].toggledirection()
        self.logger.debug("PowerDriver::togglechanneldirection[%s]" % channel)        
                
    def setchanneldirection(self, channel, direction):
        self.thechannelist[channel].setdirection(direction)
        self.logger.debug("PowerDriver::setchanneldirection[%s]=%s" % (channel,direction))

    def getchanneldirection(self, channel):
        self.logger.debug("PowerDriver::getchanneldirection=%s" % channel)
        return self.thechannelist[channel].getdirection()

    def stopallchannels(self):
        for i in range(4):
            self.thechannelist[channel].setspeed(0)
            self.thechannelist[channel].setreadspeedfromadc(False)
        self.processchanges()
        self.logger.debug("PowerDriver::stopallchannels")    
    
    def startallchannels(self):
        for i in range(4):
            self.thechannelist[channel].setreadspeedfromadc(True)
        self.processchanges()
        self.logger.debug("PowerDriver::startallchannels")
        
    def stopchannel(self, channel):
        self.thechannelist[channel].setspeed(0)
        self.thechannelist[channel].setreadspeedfromadc(False)
        self.processchanges()
        self.logger.debug("PowerDriver::stopchannel=%s" % channel)

    def startchannel(self, channel):
        self.thechannelist[channel].setreadspeedfromadc(True)
        self.processchanges()
        self.logger.debug("PowerDriver::startchannel=%s" % channel)        
        
    def convert_adc_to_pwm(self, adcmin, adcmax, adcvalue, pwmmin, pwmmax):

        self.logger.debug("PowerDriver::convert_adc_to_pwm(adcmin=%d, adcmax=%d, adcvalue=%d, pwmmin=%d, pwmmax=%d):" % (adcmin, adcmax, adcvalue, pwmmin, pwmmax))
            
        # clip the ADC value to be within the min/max range
        if adcvalue > adcmax:
            adcvalue = adcmax
            self.logger.debug("PowerDriver::convert_adc_to_pwm(): adcvalue(%d) clipped to adcmax(%d)" % (adcvalue, adcmax))
        elif adcvalue < adcmin:
            adcvalue = adcmin
            self.logger.debug("PowerDriver::convert_adc_to_pwm(): adcvalue(%d) clipped to adcmin(%d)" % (adcvalue, adcmin))
        #endif

        # if the adcmin is less than zero move to +ve range so the calcuation works correctly, need to adjust adcmin, adcmax and adcvalue 
        if adcmin < 0:
            adcmax = abs(adcmin) + abs(adcmax)
            adcvalue = abs(adcmin) + abs(adcvalue)
            adcmin = 0
        #endif

        # calculate the return value based on the percentage adcvalue is of adcmax factored against pwmmax
        retval = float(float(adcvalue) / float(adcmax - adcmin))
        retval = int(retval * (pwmmax - pwmmin)) + int(pwmmin)

        # clip the calculated PWM value to be within the range, should not be necessary as clipping the ADC value should stop overflows
        if retval > pwmmax:
            retval = pwmmax
            self.logger.debug("PowerDriver::convert_adc_to_pwm(): retval(%d) clipped to pwmmax(%d)" % (retval, pwmmax))
        elif retval < pwmmin:
            retval = pwmmin
            self.logger.debug("PowerDriver::convert_adc_to_pwm(): retval(%d) clipped to pwmmin(%d)" % (retval, pwmmin))                        
        #endif

        self.logger.debug("PowerDriver::convert_adc_to_pwm")

        return int(retval)
    #enddef

    def fnhasvaluechangedenough(self, a, b, delta):
        return (abs(a - b) >= delta)
    #enddef

    def processchanges(self):

        speedordirectionchanged = False
        returnvalue = False

        # process each of the channels
        for i in range(4):

            # default value
            adcvalue = 0

            # if needed: read the ADC, convert to PWM value
            if self.thechannelist[i].getreadspeedfromadc() == True:
                try:
                    adcvalue = self.adc.read_adc(i, gain=self.ADCgain)
                #endtry
                except Exception as e:
                    self.logger.error("Unable to read ADC '%s'" % str(e))
                #endexcept    
                
                self.logger.debug("PowerDriver::processchanges::i=%s; self.ADCgain=%s" % (i, self.ADCgain))              
                pwmvalue = self.convert_adc_to_pwm(self.adcmin, self.adcmax, adcvalue, self.MIN_PWM_VALUE, self.MAX_PWM_VALUE)

                if self.fnhasvaluechangedenough(self.thechannelist[i].getspeed(), pwmvalue, self.adcminchange) == True or self.thechannelist[i].hasdirectionchangedsincelastcall() == True:
                    speedordirectionchanged = True
                    returnvalue = True
                    self.thechannelist[i].setspeed(pwmvalue)
                else:                    
                    speedordirectionchanged = False
                #endif
                self.logger.debug("PowerDriver::processchanges::channel[%s]: speedordirectionchanged=%s" % (i, speedordirectionchanged))
                
            else:
                adcvalue = 0
                speedordirectionchanged = True
                returnvalue = True
                pwmvalue = self.thechannelist[i].getspeed()
            #endif
                
            thedirection = self.thechannelist[i].getdirection()
            thesegments = list(self.thechannelist[i].getsegments())

            self.logger.debug("PowerDriver::processchanges::channel[%s]: segments=%s" % (i, thesegments))
 
            # process each of the linked segments        
            for segment in thesegments:

                if speedordirectionchanged == True:
                    self.logger.debug("PowerDriver::processchanges::channel[%s]: segment=%s" % (i, segment))
                    
                    if thedirection == channel.CH_FWD:
                        cha_pwmvalue = pwmvalue
                        chb_pwmvalue = 0
                    elif thedirection == channel.CH_REV:
                        cha_pwmvalue = 0
                        chb_pwmvalue = pwmvalue             
                    elif thedirection == channel.CH_OFF:
                        cha_pwmvalue = 0
                        chb_pwmvalue = 0
                    else:
                        cha_pwmvalue = 0
                        chb_pwmvalue = 0                    
                    # endif

                    # work out which of the 16 PWM channels map to the segments
                    cha_number = segment * 2
                    chb_number = cha_number + 1

                    try:
                        # send the speed and direction to the PWM channels that represent the segment
                        self.pwm.set_pwm(cha_number, 0, cha_pwmvalue)              
                        self.logger.debug("PowerDriver::processchanges::cha_number=%s; cha_pwmvalue=%s" % (cha_number, cha_pwmvalue))

                        self.pwm.set_pwm(chb_number, 0, chb_pwmvalue)       
                        self.logger.debug("PowerDriver::processchanges::chb_number=%s; chb_pwmvalue=%s" % (chb_number, chb_pwmvalue))
                    #endtry
                    except Exception as e:
                        self.logger.error("Unable to set PWM values '%s'" % str(e))
                    #endexcept    

                else:
                    self.logger.debug("PowerDriver::processchanges::channel[%s]: speed or direction not changed, nothing to do!" % i)
                #endif

            # endfor
        # endfor                

        self.logger.debug("PowerDriver::processchanges()")

        return (returnvalue)
    #enddef

    def __del__(self):
        for i in range(16):
            self.pwm.set_pwm(i, 0, 0)
        self.logger.debug("PowerDriver::__del__")
    #enddef            

#endclass    

class PointDriver(object):

    POINT_POSA = 0x00
    POINT_POSB = 0x01
    POINT_DISABLED = 0xFF
    RELAY_DELAY = 0.25
    POST_RELAY_DELAY = 0.25
    CDU_RECHARGE_DELAY = 0.25

    LUDDITE_SWITCH_ON = True
    LUDDITE_SWITCH_OFF = False
    LudditeRelayMask = [0x00, 0x08, 0x10, 0x20, 0x40]

    # Declare array of 25 (24 points + blank) items and pre-int to zero
    bPointDirection = [
        0,
        POINT_POSA, POINT_POSA, POINT_POSA, POINT_POSA,
        POINT_POSA, POINT_POSA, POINT_POSA, POINT_POSA,
        POINT_POSA, POINT_POSA, POINT_POSA, POINT_POSA,
        POINT_POSA, POINT_POSA, POINT_POSA, POINT_POSA,
        POINT_POSA, POINT_POSA, POINT_POSA, POINT_POSA,
        POINT_POSA, POINT_POSA, POINT_POSA, POINT_POSA
    ]
        
    PointMask = [0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80]

    PointPairs = [0,
         0, #P01=OK
         3, #P02=OK
         2, #P03=OK
         5, #P04=OK
         4, #P05=OK
         7, #P06=OK
         6, #P07=OK                    
         0, #P08=OK                    
         0, #P09=OK
        11, #P10=OK
        10, #P11=OK
        13, #P12=OK
        12, #P13=OK
         0, #P14=OK
         0, #P15=OK
         0, #P16=OK
         0, #P17=OK
         0, #P18=OK
         0, #P19=N/A
         0, #P20=N/A
         0, #P21=N/A
         0, #P22=N/A
         0, #P23=N/A
         0  #P24=N/A
    ]

    def __init__(self, logger=None):

        self.logger = logger or logging.getLogger(__name__)
        self.DriveLinkedPoints = True
        self.pointbanka = 0x00
        self.pointbankb = 0x00
        self.ludditeswitch = 0x00
        
        try:
            # init the I2C board
            self.mcp23017 = MCP23017.MCP23017(0x20)
        except Exception as e:
            self.logger.error("Error unable to initialising the device [%s]" % str(e))
        #endexcept

        try:            
            self.mcp23017.setcontrolregister(self.mcp23017.BANKA, 0x00)
            self.mcp23017.setcontrolregister(self.mcp23017.BANKB, 0x00)
        #endtry
        except Exception as e:
            self.logger.error("Unable to write MCP23017 ports '%s'" % str(e))
        #endexcept           

        finally:
            self.logger.debug("PointDriver::__init__")
        #endfimally

        return
    #enddef

    def fnswitchludditerelays(self, relayid, onoff):

        try:
            if relayid >=1 and relayid <= 4:
                if onoff == True:
                    # add the relay bit mask to the master value
                    self.ludditeswitch = self.ludditeswitch + self.LudditeRelayMask[relayid]                    
                else:
                    # strip the relay bit mask from the master value (if on the Xor to switch off, if off then leave off)
                    if (self.ludditeswitch and self.LudditRelayMask[relayid]) == self.LudditRelayMask[relayid]:
                        # on so xor to switch off
                        self.ludditeswitch = self.ludditeswitch ^ self.LudditRelayMask[relayid]
                    #endif
                #endif

                # drive the relays with the mask
                self.logger.debug("PointDriver::fnswitchludditerelays(relayid=%d; onoff=%d; self.ludditeswitch=0x%02X" % (relayid, onoff, self.ludditeswitch))
                self.mcp23017.writetoportbank(self.mcp23017.BANKB, self.ludditeswitch)
                        
            else:
                self.logger.error('relayid must be between 1 and 4)')
                raise ValueError('PointDriver::relayid must be between 1 and 4)')
            #endif
        #endtry
        except Exception as e:
            self.logger.error("PointDriver::fnswitchludditerelays::Unable to write MCP23017 ports '%s'" % str(e))
        #endexcept
        self.logger.debug("PointDriver::fnswitchludditerelays")
    #enddef
        
    def fnresetpointboard(self):
        try:
            self.pointbanka = 0x00
            self.pointbankb = 0x00
            self.mcp23017.writetoportbank(self.mcp23017.BANKA, self.pointbanka)
            self.mcp23017.writetoportbank(self.mcp23017.BANKB, self.pointbankb)
        #endtry
        except Exception as e:
            self.logger.error("PointDriver::fnresetpointboard::Unable to write MCP23017 ports '%s'" % str(e))
        #endexcept    
            
        self.logger.debug("PointDriver::fnresetpointboard")
    #enddef

    def POST(self):        
        self.fnresetpointboard()
        self.fntestpointboard()
        self.fnresetpointboard()
        self.logger.debug("PointDriver::POST")
    #enddef

    def fntestpointboard(self):
        for x in range(1, len(self.bPointDirection)):
            if self.bPointDirections[x] != self.POINT_DISABLED:
                self.bPointDirection[x] = self.POINT_POSA
                self.fncommandpoints( x, self.POINT_POSB)
                time.sleep(self.POST_RELAY_DELAY)
                self.fncommandpoints( x, self.POINT_POSA)
                time.sleep(self.POST_RELAY_DELAY)
            #endif
        #endfor
        self.logger.debug("PointDriver::fntestpointboard")
    #endef

    def fngetlinkedpointstatus(self):
        return self.DriveLinkedPoints
    #enddef

    def fnsetlinkedpointstatus(self, thevalue):
        self.DriveLinkedPoints = thevalue
    #enddef

    def fncommandpoints(self, ThePoint, TheDirection):
        try:
            if ThePoint >= 1 and ThePoint <= 24:
                if self.bPointDirection[ThePoint] != self.POINT_DISABLED:
                    self.fndrivethepoint(ThePoint, TheDirection)        
                    if self.PointPairs[ThePoint] != 0 and self.DriveLinkedPoints == True:
                        self.fndrivethepoint(self.PointPairs[ThePoint], TheDirection)
                    #endif
                #endif
            else:
                self.logger.error('thepoint must be between 1 and 24)')
                raise ValueError('thepoint must be between 1 and 24)')
            #endif
        #endtry

        except Exception as e:
            self.logger.error("PointDriver::fncommandpoints -- Error unable to complete function: %s!" % str(e))
        #endexcept

        finally:
            self.logger.debug("PointDriver::fncommandpoints")
        #endfinally

        return
    #enddef            

    def fndrivethepoint(self, ThePoint, TheDirection):

        #|**************************************** POINT PATTERNS ***************************************|
	#+-------------------------------+-------------------------------+-------------------------------+
	#|************* A1 **************|************* A2 **************|************* A3 **************| BANKB[bit0,bit1,bit2]
	#+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
	#|D00|D01|D02|D03|D04|D05|D06|D07|D00|D01|D02|D03|D04|D05|D06|D07|D00|D01|D02|D03|D04|D05|D06|D07| BANKA[bit0,bit1,bit2,bit3,bit4,bit5,bit6,bit7]
	#+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
	#|P01|P02|P03|P04|P05|P06|P07|P08|P09|P10|P11|P12|P13|P14|P15|P16|P17|P18|P19|P20|P21|P22|P23|P24|
	#+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
	#
	# Added new logic to set self.pointbanka and self.pointbankb to the new values required to drive the point extender based on the value of "ThePoint"
	# "ThePoint" will contain values from 0 to 24, these need to be decoded correctly into "block" and "bit" (0 is to signal "all-off" so can be ignored)
	# self.pointbanka needs to contain the D0..D7 to drive the "bit"
	# self.pointbankb needs to contain A1..A3 to select the correct "block"
	# self.pointbankb already contains 0x80 if POINT_POSA is selected or 0x00 if POINT_POSB is selected, this should not be erased or the point won't fire correctly
	# in order to avoid relay contact arching the ports should be driven as follows:-
	# 1] self.pointbanka to set the "bit" of the "block"
	# 2] self.pointbankb (bit7) to select the position of the point (POINT_POSA or POINT_POSB)
	# 3] self.pointbankb (bit3,bit4,bit5,bit6) to control the luddite relays
	# 4] self.pointbankb (bit0,bit1,bit2) to fire the point bank
	# 5] self.pointbanka set to zero and all bit except bit3,bit4,bit5,bit6 set to zero on self.pointbankb
	#

        try:

            if self.bPointDirection[ThePoint] != self.POINT_DISABLED:

                # Update the internal direction for status reporting
                self.bPointDirection[ThePoint] = TheDirection
                        
                # clear out previous values
                self.pointbanka = 0x00

                # Set the relay on IO15 to drive the points through position A, or position B remembering to add in the state of the luddite relays
                if TheDirection == self.POINT_POSA:
                    self.pointbankb = self.ludditeswitch + 0x80
                else:
                    self.pointbankb = self.ludditeswitch
                #endif

                # Setup the relay (DIR) first as this takes time to move to the new position and this must be in place before the dalingtons fire
                if TheDirection == self.POINT_POSA:
                    try:
                        self.mcp23017.writetoportbank(self.mcp23017.BANKB, self.pointbankb)
                        self.logger.debug("PointDriver::fndrivethepoint::self.pointbankb=0x%02X" % self.pointbankb)
                        time.sleep(0.1)
                    #endtry
                    except Exception as e:
                        self.logger.error("PointDriver::fndrivethepoint::Unable to write MCP23017 ports '%s'" % str(e))
                    #endexcept      
                #endif                

                if (ThePoint >= 1) and (ThePoint <=8):
                    self.pointbanka = self.PointMask[ThePoint]   # PointMask[] contains the banka bitmask the point
                    self.pointbankb = self.pointbankb + 0x01
                #endif

                if (ThePoint >= 9) and (ThePoint <=16):
                    self.pointbanka = self.PointMask[ThePoint-8]
                    self.pointbankb = self.pointbankb + 0x02
                #endif

                if (ThePoint >= 17) and (ThePoint <=24):
                    self.pointbanka = self.PointMask[ThePoint-16]
                    self.pointbankb = self.pointbankb + 0x04
                #endif
                
                # Sets the relays (banka) and Darlington (bankb) drivers in the right order to pulse the right point
                try:
                    self.mcp23017.writetoportbank(self.mcp23017.BANKA, self.pointbanka)
                    self.logger.debug("PointDriver::fndrivethepoint::self.pointbanka=0x%02X" % self.pointbanka)
                    time.sleep(0.01)        
                    self.mcp23017.writetoportbank(self.mcp23017.BANKB, self.pointbankb)
                    self.logger.debug("PointDriver::fndrivethepoint::self.pointbankb=0x%02X" % self.pointbankb)
                    time.sleep(self.RELAY_DELAY) # Hold the darlington (bankb) closed to allow maximum charge from the CDU to be dumped to the point

                    # Switch all outputs off and allow time for the CDU to re-charge
                    self.pointbanka = 0x00
                    self.pointbankb = self.ludditrswitch
                    self.mcp23017.writetoportbank(self.mcp23017.BANKA, self.pointbankb)
                    self.logger.debug("PointDriver::fndrivethepoint::self.pointbankb=0x%02X" % self.pointbankb)
                    time.sleep(0.01)
                    self.mcp23017.writetoportbank(self.mcp23017.BANKB, self.pointbanka)
                    self.logger.debug("PointDriver::fndrivethepoint::self.pointbanka=0x%02X" % self.pointbanka)
                    time.sleep(self.CDU_RECHARGE_DELAY)
                #endtry
                except Exception as e:
                    self.logger.error("PointDriver::fndrivethepoint::Unable to write MCP23017 ports '%s'" % str(e))
                #endexcept

            #endif
                
        #endtry

        except Exception as e:
            self.logger.error("PointDriver::fndrivethepoint::Error unable to complete function: %s" % str(e))
        #endexcept            

        finally:
            self.logger.debug("PointDriver::fndrivethepoint")
        #endfinally
        
    #enddef

    def togglepoint(self, ThePoint):
        try:
            if ThePoint >= 1 and ThePoint <= 24:
                if self.bPointDirection[ThePoint] != self.POINT_DISABLED:
                    
                    self.fncommandpoints(ThePoint, self.bPointDirection[ThePoint])
                    if self.bPointDirection[ThePoint] == self.POINT_POSA:
                        self.bPointDirection[ThePoint] = self.POINT_POSB
                    else:
                        self.bPointDirection[ThePoint] = self.POINT_POSA
                    #endif

                    # also update the point pair if there is one
                    if self.PointPairs[ThePoint] != 0 and self.DriveLinkedPoints == True:
                        self.bPointDirection[self.PointPairs[ThePoint]] = self.bPointDirection[ThePoint]
                    #endif
                #endif
                    
            else:
                self.logger.error('ThePoint must be between 1 and 24)')
                raise ValueError('ThePoint must be between 1 and 24)')
            #endif
        #endtry

        except Exception as e:
            self.logger.error("PointDriver::togglepoint -- Error unable to complete function: %s!" % str(e))
        #endexcept

        finally:
            self.logger.debug("PointDriver::togglepoint")
        #endfinally

        return
    #enddef

    def disablepoints(self, ThePoint):
        try:
            if ThePoint >= 1 and ThePoint <= 24:
                self.bPointDirection[ThePoint] = self.POINT_DISABLED                
            else:
                self.logger.error('ThePoint must be between 1 and 24)')
                raise ValueError('ThePoint must be between 1 and 24)')
            #endif
        #endtry

        except Exception as e:
            self.logger.error("PointDriver::disablepoints -- Error unable to complete function: %s!" % str(e))
        #endexcept

        finally:
            self.logger.debug("PointDriver::disablepoints")
        #endfinally

        return
    #enddef    

    def clearallpoints(self):
        self.fnresetpointboard()
        for x in range(1, len(self.bPointDirection)):
            if self.bPointDirection[x] != self.POINT_DISABLED:
                self.bPointDirection[x] = self.POINT_POSA
            #endif
        #endfor
        self.logger.debug("PointDriver::clearallpoints")
    #endif
    
    def getpointstatus(self, ThePoint):
        self.logger.debug("PointDriver::getpointstatus")
        return self.bPointDirection[ThePoint]
    #enddef
    
    def __del__(self):
        self.fnresetpointboard()
        self.logger.debug("PointDriver::__del__")
    #enddef

#endclass

class ProximitySensors(object):

    InputMask = [0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80]

    bHasStatusChanged = False

    # sixteen proximity sensors can be sensed
    bProximitySensors = [0,
                         False, False, False, False, False, False, False, False,
                         False, False, False, False, False, False, False, False
    ]

    def __init__(self, logger=None):

        self.logger = logger or logging.getLogger(__name__)
        try:
            # init the I2C board
            self.mcp23017 = MCP23017.MCP23017(0x27)
        except Exception as e:
            self.logger.error("Error unable to initialising the device [%s]" % str(e))
        #endexcept

        try:

            # configure PORTA and PORTB as input and set the weak pull-up resistors to stop floating inputs
            self.mcp23017.setcontrolregister(self.mcp23017.BANKA, 0xFF)
            self.mcp23017.setcontrolregister(self.mcp23017.BANKB, 0xFF)
            self.mcp23017.setcontrolregister(self.mcp23017.GPPUA, 0xFF)
            self.mcp23017.setcontrolregister(self.mcp23017.GPPUB, 0xFF)

            # to improve performance for short detections setup interupts to capture the bit changes
            self.mcp23017.setcontrolregister(self.mcp23017.GPINTENA, 0xFF)
            self.mcp23017.setcontrolregister(self.mcp23017.DEFVALA, 0x00)
            self.mcp23017.setcontrolregister(self.mcp23017.INTCONA, 0x00)
            self.mcp23017.setcontrolregister(self.mcp23017.GPINTENB, 0xFF)
            self.mcp23017.setcontrolregister(self.mcp23017.DEFVALB, 0x00)
            self.mcp23017.setcontrolregister(self.mcp23017.INTCONB, 0x00)
            
        #endtry
        except Exception as e:
            self.logger.error("Unable to write MCP23017 ports '%s'" % str(e))
        #endexcept           

        finally:
            self.logger.debug("ProximitySensors::__init__")
        #endfimally

        return
    #enddef

    def fnhasanyproximitystatuschanged(self):
        return self.bHasStatusChanged
    #enddef

    def fnreadproximitysensors(self):

        banka_inputs = 0
        bankb_inputs = 0

        self.bHasStatusChanged = False
        
        try:
            # read the data, then populate the status
            banka_inputs = self.mcp23017.readfromportbank(self.mcp23017.BANKA, True) # read via interrupt
            bankb_inputs = self.mcp23017.readfromportbank(self.mcp23017.BANKB, True) # read via interrupt

            self.logger.debug("ProximitySensors::fnreadproximitysensors(): banka=%02X; bankb=%02X" % (banka_inputs, bankb_inputs))

            # bProximitySensors[1..8] map to PORTA and bProximitySensors[9..16] map to PORTB
            for x in range(1, len(self.bProximitySensors)):
                if x >= 1 and x <=8:

                    self.logger.debug("ProximitySensors::fnreadproximitysensors(): banka_inputs=%02X; self.InputMask[%d]=%02X]" % (banka_inputs, x, self.InputMask[x]))
                        
                    if (self.InputMask[x] & banka_inputs) == self.InputMask[x]:
                        if self.bProximitySensors[x] == True:
                            self.bHasStatusChanged = True
                        #endif
                        self.bProximitySensors[x] = False
                    else:
                        if self.bProximitySensors[x] == False:
                            self.bHasStatusChanged = True
                        #endif                        
                        self.bProximitySensors[x] = True
                    #endif
                        
                else:

                    self.logger.debug("ProximitySensors::fnreadproximitysensors(): bankb_inputs=%02X; self.InputMask[%d]=%02X]" % (bankb_inputs, x-8, self.InputMask[x-8]))

                    if (self.InputMask[x-8] & bankb_inputs) == self.InputMask[x-8]:
                        if self.bProximitySensors[x] == True:
                            self.bHasStatusChanged = True
                        #endif                                                
                        self.bProximitySensors[x] = False
                    else:
                        if self.bProximitySensors[x] == False:
                            self.bHasStatusChanged = True
                        #endif                                                
                        self.bProximitySensors[x] = True
                    #endif
                #endif

                self.logger.debug("ProximitySensors::fnreadproximitysensors(): self.bProximitySensors[%d]=%s" % (x, self.bProximitySensors[x]))
                        
            #endfor
        #endtry

        except Exception as e:
            self.logger.error("ProximitySensors::fnreadproximitysensors(): **** Error unable to complete function: %s ****" % str(e))            
        #endexcept            

        finally:
            self.logger.debug("ProximitySensors::fnreadproximitysensors():")
        #endfinally
    #enddef

    def fngetproximitysensorstatus(self, TheSensorID):
        try:
            thevalue = False
            if TheSensorID >= 1 and TheSensorID <= 16:
                thevalue = self.bProximitySensors[TheSensorID]
                self.logger.debug("ProximitySensors::fngetproximitysensorstatus(): self.bProximitySensors[%d]=%s" % (TheSensorID, self.bProximitySensors[TheSensorID]))
            else:
                self.logger.error('TheSensorID must be between 1 and 16')
            #endif

        except Exception as e:
            self.logger.error("ProximitySensors::fngetproximitysensorstatus(): **** Error unable to complete function: %s ****" % str(e))
        #endexcept

        finally:
            self.logger.debug("ProximitySensors::fngetproximitysensorstatus():")
            return thevalue
        #endfinally
    #enddef

    def __del__(self):
        self.logger.debug("ProximitySensors::__del__")
    #enddef

#endclass

