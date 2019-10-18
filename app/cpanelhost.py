import requests
from requests.auth import HTTPBasicAuth
import json
from time import sleep


class CpanelHost:

    def __init__(self,username:str,domain:str,password:str,period=10,port='2082'):
        self.__username=username
        self.__domain = domain
        self.__password = password
        self.__port = port
        self.__url = self.__makeURL()
        self.__data = {
            'user': username,
            'pass' : password
        }
        self.__resourceUsage = {'data':[]}
        self.__requestNumber=0
        self.period = period

    def __makeURL(self,https=False):
        url=''
        if https == False:
            url='http://'+self.__domain+':'+self.__port
        else:
            url ='https://'+self.__domain+':'+self.__port
        return url 

    def getUserName(self):
        return self.__username

    def getDomain(self):
        return self.__domain

    def getPassWord(self):
        return self.__password

    def getPort(self):
        return self.__port

    def getURL(self):
        return self.__url
    
    def getData(self):
        return self.__data

    def __getToken(self):

        with requests.session() as session :
            firstURL = self.__url+'/login/?login_only=1'
            response = session.post(
                firstURL, 
                data = self.__data,
                auth = HTTPBasicAuth(self.__username,self.__password),
                allow_redirects = False,
                stream = False,
            )
            response = json.loads(response.content)
            securityToken = response['security_token']

        return securityToken

    def checkStatus(self):
        with requests.session() as session:

            resourceUsageURL = self.__url+self.__getToken()+'/execute/ResourceUsage/get_usages'
            
            resCode =200
            while(resCode==200):
                resourceResponce = session.post(resourceUsageURL,data=self.__data,auth=HTTPBasicAuth(self.__username,self.__password))
                usage = json.loads(resourceResponce.content)
                self.__resourceUsage = usage
                resCode=resourceResponce.status_code
                self.__requestNumber+=1
                if(self.period == 1):
                    break
                sleep(self.period)
        return resCode

    def getResource(self,justData=True):
        if justData:
            #return a list of resource each reasource is a dictionary
            return self.__resourceUsage['data']
        else:
            #return whole content of host responce
            return self.__resourceUsage

    def __searchOnData(self,id:str):

        for resourceInfo in self.__resourceUsage['data']:
            if resourceInfo['id'] == id:
                return resourceInfo

        return None


    def diskUsage(self):
        return self.__searchOnData(id='disk_usage')

    def mySqlDiskUsage(self):
        return self.__searchOnData(id='cachedmysqldiskusage')

    def bandWidth(self):
        return self.__searchOnData(id='bandwidth')

    def addonDomain(self):
        return self.__searchOnData(id='addon_domains')

    def subDomains(self):
        return self.__searchOnData(id='subdomains')

    def aliases(self):
        return self.__searchOnData(id='aliases')

    def emailAccount(self):
        return self.__searchOnData(id='email_accounts')

    def autoresponders(self):
        return self.__searchOnData(id='autoresponders')

    def forwarders(self):
        return self.__searchOnData(id='forwarders')

    def emailFilters(self):
        return self.__searchOnData(id='email_filters')

    def ftpAccounts(self):
        return self.__searchOnData(id='ftp_accounts')

    def mySqlDatabases(self):
        return self.__searchOnData(id='mysql_databases')

    def cpuUsage(self):
        return self.__searchOnData(id='lvecpu')

    def entryProcesses(self):
        return self.__searchOnData(id='lveep')

    def physicalMemoryUsage(self):
        return self.__searchOnData(id='lvememphy')

    def IOPS(self):
        return self.__searchOnData(id='lveiops')

    def ioUsage(self):
        return self.__searchOnData(id='lveio')

    def numberOfProcesses(self):
        return self.__searchOnData(id='lvenproc')

    def getRequestNumber(self):
        return self.__requestNumber




