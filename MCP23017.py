#!/usr/bin/python

import time
import logging

class MCP23017(object):

    # Registers/etc:
    MCP23017_ADDRESS = 0x20    
    BANKA = 0x00
    BANKB = 0x01
    
    IODIRA = 0x00
    IODIRB = 0x01    
    GPINTENA = 0x04
    GPINTENB = 0x05    
    DEFVALA = 0x06
    DEFVALB = 0x07    
    INTCONA = 0x08
    INTCONB = 0x09
    GPPUA = 0x0C
    GPPUB = 0x0D    
    INTCAPA = 0x10
    INTCAPB = 0x11    
    GPIOA = 0x12    
    GPIOB = 0x13
    
    VERSION = "1.2.0_20181028"

    def __init__(self, address=MCP23017_ADDRESS, logger=None, i2c=None, **kwargs):

        try:
            self.logger = logger or logging.getLogger(__name__)
            self.logger.debug("MCP23017::__init__")
            # Setup I2C interface for the device.
            if i2c is None:
                import Adafruit_GPIO.I2C as I2C
                i2c = I2C
            self._device = i2c.get_i2c_device(address, **kwargs)
            
            # set both porta (0x00) and portb (0x01) to input "1" to stop hardware errors
            self.setcontrolregister(self.IODIRA, 0xFF)
            self.setcontrolregister(self.IODIRB, 0xFF)

            self.logger.debug("MCP23017::__init__ (version=%s" % self.VERSION)
            
        #endtry
        except Exception as e:
            self.logger.error("__init__(): error writing to the device [%s]" % str(e))
        #endexcept            
    #enddef
	
    def setcontrolregister(self, theregister, thevalue):
        self.logger.debug("MCP23017::setcontrolregister")
        try:
            self._device.write8(theregister, thevalue)
        #endtry

        except Exception as e:
            self.logger.error("setcontrolregister(): error writing to the device [%s]" % str(e))
        #endexcept            
    #enddef
	
    def readfromportbank(self, thebank, readviaintcap = False):
        self.logger.debug("MCP23017::readfromportbank(readviaintcap=%s)" % readviaintcap )
        result = 0
        theregister = 0x00
        
        try:
            if thebank == self.BANKA:
                if readviaintcap == False:
                    theregister = self.GPIOA
                else:
                    theregister = self.INTCAPA
                #endif
                result = self._device.readU8(theregister)
            elif thebank == self.BANKB:
                if readviaintcap == False:
                    theregister = self.GPIOB
                else:
                    theregister = self.INTCAPB
                #endif
                result = self._device.readU8(theregister)
            else:
                self.logger.error('Invalid bank value, only BANKA or BANKB permitted!')
                raise ValueError('Invalid bank value, only BANKA or BANKB permitted!')
            #endif
        #endtry

        except Exception as e:
            self.logger.error("readfromportbank(): error reading to the device [%s]" % str(e))
        #endexcept

        return result
        
    #enddef
		
    def writetoportbank(self, thebank, thevalue):
        self.logger.debug("MCP23017::writetoportbank")
        try:
            if thebank == self.BANKA:
                self._device.write8(self.GPIOA,thevalue)
            elif thebank == self.BANKB:
                self._device.write8(self.GPIOB,thevalue)
            else:
                self.logger.error('Invalid bank value, only BANKA or BANKB permitted!')
                raise ValueError('Invalid bank value, only BANKA or BANKB permitted!')
            #endif
        #endtry

        except Exception as e:
            self.logger.error("writetoportbank(): error writing to the device [%s]" % str(e))
        #endexcept
        
        return
    #enddef

    # POST, set ports as output, set all bit on, wait 2 seconds, set all bits off, set ports as imputs
    def post(self):
        self.logger.debug("MCP23017::post")
        self.setcontrolregister(self.BANKA, 0x00) # "0" = output
        self.setcontrolregister(self.BANKB, 0x00) # "0" = output
        self.writetoportbank(self.BANKA, 0xFF) # all on
        self.writetoportbank(self.BANKB, 0xFF) # all on
        time.sleep(2)
        self.writetoportbank(self.BANKA, 0x00) # all off
        self.writetoportbank(self.BANKB, 0x00) # all off
        self.setcontrolregister(self.BANKA, 0xFF) # "1" = input
        self.setcontrolregister(self.BANKB, 0xFF) # "1" = input
    #enddef

#endclass
