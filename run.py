from requests import Session
import requests
from requests.auth import HTTPBasicAuth  # or HTTPDigestAuth, or OAuth1, etc.
from zeep import *
from zeep.transports import Transport
import ast
import time
import datetime


class NbiFunction(object):
    nbi_user='nbi'
    nbi_password='$SatCom$'
    clinet = None
    nbi_session = None
    add_succ=0
    add_fail=0
    rt_succ=0
    rt_fail=0
    add_succ_l=[]
    add_fail_l=[]
    rt_succ_l=[]
    rt_fail_l=[]

    def __init__(self):
        self.nbi_session = requests.Session()
        self.nbi_session.auth = HTTPBasicAuth(self.nbi_user, self.nbi_password)
        self.client = Client('cpeService.xml',transport=Transport(session=self.nbi_session))

    def createCpe(self, cpeq):
        try:
            response = self.client.service.createCPE(**cpeq)
            self.add_succ+=1
            self.add_succ_l.append(cpeq['cpe']['cpeId']['subscriberId'])
        except exceptions.Fault as error:
            self.add_fail+=1
            self.add_fail_l.append(cpeq['cpe']['cpeId']['subscriberId'])
            print(ValueError(error.message))


    def addRoute(self, cpe_rtq):
        try:
            response = self.client.service.cpeAddStaticRouteIPv4(**cpe_rtq)
            self.rt_succ+=1
            self.rt_succ_l.append(cpe_rtq['cpeId']['subscriberId'])
        except exceptions.Fault as error:
            self.rt_fail+=1
            self.rt_fail_l.append(cpe_rtq['cpeId']['subscriberId'])
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
    with open('vsats.csv', 'r') as m:
        cpe_cfg = m.read()

    for i in cpe_cfg.splitlines():
        now = datetime.datetime.now()
        cpe = i.split(',')
        cpes['cpe']['cpeId']['managedGroupId'] = cpe[0]
        cpes['cpe']['cpeId']['subscriberId'] = cpe[1]
        cpes['cpe']['description'] = cpe[2]
        cpes['cpe']['vrs']['VR'][0]['vlanId'] = cpe[3]
        cpes['cpe']['vrs']['VR'][0]['ipv4']['subscriberPublicIpAddress']=cpe[4]
        cpes['cpe']['vrs']['VR'][0]['ipv4']['ipv4Prefix']=cpe[5]
        cpes['cpe']['vrs']['VR'][0]['backhaulings']['Backhauling'][0]['name'] = cpe[6]
        print ('\n{:10}: CPE:  {:10}'.format(now.strftime("%Y-%m-%d %H:%M"), cpe[1]))
        vsat_obj.createCpe(cpes)
        time.sleep(1)

        cpe_rt['cpeId']['managedGroupId'] = cpe[0]
        cpe_rt['cpeId']['subscriberId'] = cpe[1]
        cpe_rt['vlanId'] = cpe[3]
        cpe_rt['IPv4StaticRoute']['network'] = cpe[7]
        cpe_rt['IPv4StaticRoute']['subnetMask'] = cpe[8]
        cpe_rt['IPv4StaticRoute']['nextHop'] = cpe[9]
        print ('{:5}ROUTE: {:7} : < {} : {} : {} >'.format('--->', cpe[1], cpe[7], cpe[8], cpe[9]))
        vsat_obj.addRoute(cpe_rt)
        time.sleep(1)

    print ('\nCPEs:\n\tSUCCESS: {}\n\tFAILURE: {} -> {}\nROUTE:\n\tSUCCESS: {}\n\tFAILURE: {} -> {}'.format(vsat_obj.add_succ,vsat_obj.add_fail,vsat_obj.add_fail_l,vsat_obj.rt_succ,vsat_obj.rt_fail,vsat_obj.rt_fail_l))
if __name__ == '__main__':
    main()
