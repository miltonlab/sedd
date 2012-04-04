#!/usr/bin/env python
#-*-coding:utf-8-*-
from SOAPpy import Config, HTTPTransport, SOAPAddress, WSDL
class myHTTPTransport (HTTPTransport):
    username = None
    passwd = None

    @classmethod
    def setAuthentication(cls,u,p):
        cls.username = u
        cls.passwd = p
          
    def call(self, addr, data, namespace, soapaction=None, encoding=None,http_proxy=None, config=Config):
        if not isinstance(addr, SOAPAddress):
            addr=SOAPAddress(addr, config)
        if self.username != None:
            addr.user = self.username+":"+self.passwd
        return HTTPTransport.call(self, addr, data, namespace, soapaction,encoding, http_proxy, config)

if __name__ == '__main__':
    #wsdlFile = 'http://miltonlab:1000lab@ws.unl.edu.ec/sgaws/wspersonal/soap/api.wsdl'
    wsdlFile = 'http://ws.unl.edu.ec/sgaws/wspersonal/soap/api.wsdl'
    myHTTPTransport.setAuthentication('miltonlab', '1000lab')
    server = WSDL.Proxy(wsdlFile, transport=myHTTPTransport)
    print server.sgaws_datos_docente(cedula='1103499966')
   
