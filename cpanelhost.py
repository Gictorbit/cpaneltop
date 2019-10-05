import requests
import json
from requests.auth import HTTPBasicAuth

class CpanelHost:
    
    def __init__(self,username,domain,password,port='2082'):
        self.__username = username
        self.__domain = domain
        self.__password = password
        self.__port = port
        self.__url = self.__makePrimaryURL()

    def __makePrimaryURL(self):
        PrimaryURL = 'http://'+self.__domain+':'+self.__port
        return PrimaryURL

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
    

