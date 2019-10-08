import requests
from requests.auth import HTTPBasicAuth
import json
from time import sleep

class CpanelHost:

    def __init__(self,username:str,domain:str,password:str,port='2082'):
        self.__username=username
        self.__domain = domain
        self.__password = password
        self.__port = port
        self.__url = self.__makeURL()
        self.__data = {
            'user': username,
            'pass' : password
        }
        self.__resourceUsage = {}
    
    def __makeURL(self):
        return 'http://'+self.__domain+':'+self.__port

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
    
    def checkStatus(self,time =10,once=False):
        with requests.session() as session:

            resourceUsageURL = self.__url+self.__getToken()+'/execute/ResourceUsage/get_usages'
            
            while(True):
                resourceResponce = session.post(resourceUsageURL,data=self.__data,auth=HTTPBasicAuth(self.__username,self.__password))
                usage = json.loads(resourceResponce.content)
                self.__resourceUsage = usage
                # print(json.dumps(self.__resourceUsage['data'][0],indent=4))
                if(once==True):
                    break
                sleep(time)
    
    def getResource(self):
        return self.__resourceUsage
    
    def __byteToMebi(self,byteValu):
        return byteValu/pow(1024,2)
    


