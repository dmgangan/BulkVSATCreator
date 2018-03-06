from requests import Session
import requests
from requests.auth import HTTPBasicAuth  # or HTTPDigestAuth, or OAuth1, etc.
from zeep import *
from zeep.transports import Transport
import ast


class NbiFunction(object):
    nbi_user='admin'
    nbi_password='manager'
    clinet = None
    nbi_session = None

    def __init__(self):
        self.nbi_session = requests.Session()
        self.nbi_session.auth = HTTPBasicAuth(self.nbi_user, self.nbi_password)
        self.client = Client('cpeService.xml',transport=Transport(session=self.nbi_session))

    def crt(self, cpeq):
        try:
            response = self.client.service.createCPE(**cpeq)
        except exceptions.Fault as error:
            print(ValueError(error.message))


    def addRoute(self, cpe_rtq):
        try:
            response = self.client.service.cpeAddStaticRouteIPv4(**cpe_rtq)
        except exceptions.Fault as error:
            print(ValueError(error.message))

    def showCPE(self, CPEID):
        try:
            response = self.client.service.getCPEbyID(**CPEID)
        except exceptions.Fault as error:
            print(ValueError(error.message))
        return response
def main():
    cpe_rt= {'cpeId': {
                    'managedGroupId': 2,
                    'subscriberId': 123456789},
                    'vlanId': '24',
                    'IPv4StaticRoute': {
                    'network': '8.8.8.8',
                    'subnetMask': '255.255.255.255',
                    'nextHop': '10.10.10.10',
                    'ipV4Interface': 'LAN',
                    'redistribute': 'RIPv2',
                    'distributedMetric': '1',
                    }
            }
    cpe_id = {
        'id': {
            'managedGroupId': 2,
            'subscriberId': 1002,
        }}

    with open('vsat.json', 'r') as f:
        cpe_str = f.read()
    cpes = ast.literal_eval(cpe_str)
    vsat_obj = NbiFunction()
    #vsat_obj.addRoute(cpe_rt)
    vsat_obj.crt(cpes)

if __name__ == '__main__':
    main()
