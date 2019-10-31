#!/usr/bin/python3
from beautifultable import BeautifulTable
from cpanelhost import CpanelHost
from cpanelhost import netIsOn
from threading import Thread
from getpass import getpass
from curses import textpad
import validators
import curses
import sys
import re


class NoArgumen(ValueError):
    def __init__(self,messeage):
        self.msg = messeage

class InvalidArgumen(ValueError):
    def __init__(self,messeage):
        self.msg = messeage

class NoUserHost(KeyError):
    def __init__(self,messeage):
        self.msg = messeage

class UnknownParameter(ValueError):
    def __init__(self,messeage):
        self.msg = messeage

class CantConnect(ValueError):
    def __init__(self,messeage):
        self.msg = messeage


def main():
    #check argument validation
    try:
        userInput=checkArg()
    except InvalidArgumen as ea:
        print(ea.msg)
        print("try cpaneltop --help ")
        sys.exit()
    except NoUserHost as eu:
        print(eu.msg)
        print("try cpaneltop --help ")
        sys.exit()
    except UnknownParameter as ep:
        print(ep.msg)
        print("try cpaneltop --help ")
        sys.exit()


    #store user password and add this key/value to userInput Dictionary
    userInput['password'] = getpass("enter your password: ")
    print("Connecting...")

    """
    userInput is like this:
    {
        'user@host': 'asd@sad.com',
        'port': 0, #alwayze str
        'time': 1, #alwayze integer
        'help': 0,
        'user': 'username',
        'host': 'domain',
        'password' : 'getpass' //initial in main and add to perv dictionary
    }
    """

    #if user didnt use to time argument we set default period to 10 second
    if userInput['time']==0:
        userInput['time']+=10

    if userInput['ssl']==0:
        userInput['ssl']='no'

    #find out wheter user entered port or not
    if userInput['port']=='0':
        host1 = CpanelHost(username=userInput['user'],domain=userInput['host'],\
            password=userInput['password'],period=userInput['time'],ssl=userInput['ssl'])
    else:
        host1 = CpanelHost(username=userInput['user'],domain=userInput['host'],\
            password=userInput['password'],period=userInput['time'],port=userInput['port'],ssl=userInput['ssl'])

    #check internet connection is avaible
    if netIsOn() == False:
        print("there is no Internet Connection")
        sys.exit()

    #initialize resource information with 1 requests
    primaryTime=host1.period
    host1.period=1

    try:
        host1.checkStatus()
        print("OK")
    except KeyError :
        print("can't connect to Host! :(")
        sys.exit()

    if 'data' not in host1.getResource(justData=False):
        raise CantConnect("cant connect and fetch resource usage Information")

    #check resource detail in background every X second with below thread
    host1.period = primaryTime
    checkStatusOnlineThread = Thread(target=host1.checkStatus,args=(),daemon=True)
    checkStatusOnlineThread.start()

    def __windowShow(topWindow):

        curses.curs_set(0)
        h,w = topWindow.getmaxyx()

        if h<24 or w<78:
            topWindow.addstr(0,0,'console size is not enough must be greater than 24*78')
            topWindow.getch()
            sys.exit()

        topWindow.nodelay(True)
        topWindow.timeout(500)
        curses.init_pair(1,curses.COLOR_BLACK,curses.COLOR_YELLOW)
        curses.init_pair(2,curses.COLOR_YELLOW,curses.COLOR_BLACK)

        while True:
            topWindow.clear()
            topWindow.refresh()

            table = createTable(host1.getResource())
            lineStr = str(table).split("\n")

            headStr = "  CpanelTop >>> "+"Host: "+host1.getDomain()+"   "+"user: "+host1.getUserName()\
                +"   "+"port: "+str(host1.getPort())+"   "+'request: '+str(host1.getRequestNumber())+"  "

            topWindow.attron(curses.color_pair(1))
            topWindow.addstr(0,0,headStr)
            topWindow.attroff(curses.color_pair(1))

            tableWidth =  len(lineStr[0])
            tableHeight = len(lineStr)

            for index ,row in enumerate(lineStr,1):
                topWindow.addstr(index,2,row)

            topWindow.refresh()
            topWindow.attron(curses.color_pair(2))
            textpad.rectangle(topWindow,1,2,tableHeight,tableWidth+1)
            topWindow.attron(curses.color_pair(2))
            topWindow.refresh()

            key = topWindow.getch()

            if str(key)=="113" or str(key)=="813":
                sys.exit()

        topWindow.nodelay(False)
        curses.curs_set(1)
        sys.exit()

    curses.wrapper(__windowShow)
    sys.exit()



def getInfoBox(resource:dict):

    def __hasHumanRead(resource:dict):
        hasSizeListId = ["disk_usage","cachedmysqldiskusage",\
            "bandwidth","lvememphy","lveio"]

        if resource['id'] in hasSizeListId:
            return True
        else:
            return False

    finalString = ''
    finalString += resource['description']+'\n'

    if resource['maximum'] == None :
        finalString += str(resource['usage'])+'/∞'
        return finalString

    if __hasHumanRead(resource):
        finalString += humanReadableSize(float(resource['usage']))+' / '+humanReadableSize(float(resource['maximum']))+"\n"
        finalString += getStatusBar(calculatePercent(float(resource['usage']),float(resource['maximum'])))
    else:
        finalString += str(resource['usage'])+' / '+str(resource['maximum'])+"\n"
        finalString += getStatusBar(calculatePercent(float(resource['usage']),float(resource['maximum'])))

    return finalString

def humanReadableSize(byteSize:float):

    def __sizeFormat(size,listIndex:int):
        if not size:
            return '0'
        elif listIndex == 0:
            return str(size)
        else:
            return '{:.2f}'.format(size)

    sizeList = ['B','KiB','MiB','GiB','TiB','PiB','EiB','ZiB','YiB']
    listIndex = 0
    finalSize = byteSize

    while finalSize >= 1024.00 and listIndex<len(sizeList):
        finalSize/=1024.0
        listIndex+=1

    endSize = __sizeFormat(finalSize,listIndex)
    suffixSize = sizeList[listIndex]

    if float(endSize)- int(float(endSize)) == 0.0:
        endSize = str(int(float(endSize)))

    return endSize+' '+suffixSize

def getStatusBar(percent:int,barSize=10):
    bar="|"
    percentString = str(percent)+'/100%'

    progressChar = percent*barSize//100

    for i in range(barSize):
        if(i<=progressChar and percent!=0):
            bar+='█'
        else:
            bar+=' '

    bar+='| '+percentString
    return bar

def calculatePercent(usage:float,maximum:float):
    percent = (usage*100)/maximum
    percentString = "{:.2f}".format(percent)
    return float(percentString)

def createTable(resource:list):
    #just take a list of dictionary , each dict contain one resource
    table = BeautifulTable()
    tempList = list()
    count=0
    for res in resource:
        count+=1
        tempList.append((getInfoBox(res)))
        if count==3:
            table.append_row(tempList)
            count=0
            tempList.clear()

    return table

def checkArg():

    argumentList = ('-h','--help','-p','--port','-t','--time','-s','--ssl')
    resultInit = {
        'user@host':0,
        'port':0,
        'time':0,
        'help':0,
        'ssl' :0,
    }
    def __fetchArgument():

        index=1
        while index < len(sys.argv):
            if '@'  in sys.argv[index]:
                #fetch user@host argument
                resultInit['user@host'] = sys.argv[index]
            elif  argumentList[0] == sys.argv[index] or argumentList[1] == sys.argv[index] :
                #fetch -h and --help argument
                resultInit['help']=1
                break
            elif argumentList[2] == sys.argv[index] or argumentList[3] == sys.argv[index] :
                #fetch -p --port argument
                if index+1 < len(sys.argv) :
                    resultInit['port'] = sys.argv[index+1]
                    index+=1
                else:
                    resultInit['port']=-1
            elif argumentList[4] == sys.argv[index] or  argumentList[5] == sys.argv[index]:
                #fetch -t --time argument
                if index+1 < len(sys.argv) :
                    resultInit['time'] = sys.argv[index+1]
                    index+=1
                else:
                    resultInit['time']=-1
            elif argumentList[6] == sys.argv[index] or argumentList[7] == sys.argv[index]:
                if index+1 < len(sys.argv) :
                    resultInit['ssl'] = sys.argv[index+1]
                    index+=1
                else:
                    resultInit['ssl']=-1
            else:
                raise InvalidArgumen('your argument is invalid')
            index+=1

        return resultInit

    #check help argument
    result = __fetchArgument()
    if result['help']==1:
        printHelp()
        sys.exit()

    #check user@host validation
    if result['user@host']==0:
        raise NoUserHost("no user@host selected")
    else:
        userHostList = str(result['user@host']).split('@')
        if validators.domain(userHostList[1]):
            result['user'] = userHostList[0]
            result['host']= userHostList[1]
        else:
            raise UnknownParameter("the domain is Invalid")

    #check time of requests
    if result['time']==-1:
        raise UnknownParameter("cant find refresh time parameter")
    elif str(result['time']).isnumeric():
        if int(result['time'])==1 or (int(result['time'])>=5 and int(result['time'])<=60) or int(result['time'])==0 :
            result['time'] = int(result['time'])
        else:
            raise UnknownParameter("the time parameter is invalid shoud be in 5-60 second or 1")
    else:
        raise UnknownParameter("Invalid input ,the time is not numeric ")

    #check port validation
    pattern=re.compile("^()([1-9]|[1-5]?[0-9]{2,4}|6[1-4][0-9]{3}|65[1-4][0-9]{2}|655[1-2][0-9]|6553[1-5])$")
    if result['port'] == -1:
        raise UnknownParameter("cant find port parameter")
    elif pattern.match(str(result['port'])) or result['port'] == 0:
        result['port']=str(result['port'])
    else:
        raise UnknownParameter("bad port for connection")

    #check ssl enable
    if result['ssl'] == -1:
        raise UnknownParameter("cant find ssl parameter ")
    elif result['ssl'] == 'yes' or result['ssl'] == 'no' or result['ssl']==0:
        pass
    else:
        raise UnknownParameter("bad ssl answer, should be yes or no")

    return result

def printHelp():
    helpString = "\n\tusername@host\tConnect to the host with specified username\
        \n\n\t-h\t--help\tprint this help\
        \n\t-t\t--time\tchange request time for refresh detail must be\t5 <t< 60\
        \n\t-p\t--port\tconnect to host with specified port\
        \n\t-s\t--ssl\trequest to host with https protocol\
        \n\n  exit from program with pressing q button\
        \n\n  for more information check https://github.com/Gictorbit/cpaneltop\n"

    print(helpString)

if __name__ == '__main__':
    main()

