from os import path
import datetime
from configparser import ConfigParser
from shutil import copyfile
from sys import platform

def getwd(filename):
    return path.abspath(path.join(path.dirname(__file__), filename))


def getOSMods():
    if "linux" or "darwin" in platform:
        dirmark = "/"
        h5drv = "H5FD_SEC2"
        newLine = "\n"
    elif "win" in platform:
        dirmark = r"\ "
        h5drv = "H5FD_WINDOWS"
        newLine = "\n\r"
    return dirmark, h5drv, newLine
        
    
class datetools:

    def daycount(self, dtobj_start, dtobj_end):
        return (dtobj_end + datetime.timedelta(days=1) - dtobj_start).days 
        
    def genDates(self, dtobj_start, dtobj_end):
        return [dtobj_start + datetime.timedelta(days=i) for i in range((dtobj_end + datetime.timedelta(days=1) - dtobj_start).days)]
            
    def calcStart(self, dtobj_end, ndays):
        return dtobj_end - datetime.timedelta(days=ndays)
    
    def calcEnd(self, dtobj_start, ndays):
        return dtobj_start + datetime.timedelta(days=ndays)
        
    def dt2str(self, dtobj, tofmt="%Y%m%d"):
        return dtobj.strftime(tofmt)
    
    def str2dt(self, datestr, fromfmt):
        return datetime.datetime.strptime(datestr, fromfmt)
    
    def refmt_datestr(self, datestr, fromfmt, tofmt="%Y%m%d"):
        return datetime.datetime.strptime(datestr, fromfmt).strftime(tofmt)
  
class conftools:
    
    def __init__(self, filename):
        self.file = getwd("".join(["/configs/", filename]))
        self.cfg = ConfigParser()
        self.conf = self.cfg.read(self.file)
    
    def getValue(self, section, option):
        try:
            self.conf[section][option]
        except Exception as err:
            print("Error!: %s" % err)
        else:
            
            if self.conf[section][option] == "0":
                pass
            else:
                return self.conf[section][option]
    
    def updateValue(self, section, option, newValue, rmbackup=True):
        try:
            self.cfg[section][option] = newValue
        except Exception as err:
            print(err)
        else:
            print("Creating Backup File...")
            
            copyfile(self.file, os.splitext(self.file)[0]+".bak")
            
            with open(self.file, mode='w') as f:
                try:
                    print("Updating Config...")
                    self.cfg.write(f)
                except IOError as err:
                    print("IOError: %s" % err)
                    print("Falling back to original file")
                    os.remove(self.file)
                    os.rename("".join([os.splitext(self.file)[0]+".bak"]), self.file)
                    print("Done. Please manually update 'last_date' to %s in the config\
                     file before running again to prevent duplicate records" % datetime.date.today().strftime("%Y-%m-%d"))
                    
                else:
                    f.close()
                    print("Config File Updated.")
        
        if rmbackup is True:
            print("Erasing backup...")
            os.remove(os.splitext(self.file)[0]+".bak")
            print("Done.")
        else:
            print("Done.")
    
    def listSections(self):
        return self.conf.sections()
    
    def listOptions(self, sections):
        if type(sections) is list:
            d = dict(map(lambda x: self.conf[x].items(), [s for s in sections]))
            return d.items()
        else:
            return self.conf[sections].items()
    
