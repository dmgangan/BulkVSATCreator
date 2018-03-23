from requests import Session
import requests, ast, time, datetime, getopt, sys, params
from requests.auth import HTTPBasicAuth
from zeep import *
from zeep.transports import Transport

class NbiFunction(object):
    nbi_user=params.nbi_user
    nbi_password=params.nbi_pass
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
        self.client = Client(params.wsdl_filename,transport=Transport(session=self.nbi_session))

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

    def CPEdesc(self, CPEdesc):
        try:
            response = self.client.service.setCPECustomerInformation(**CPEdesc)
        except exceptions.Fault as error:
            print(ValueError(error.message))


def opts(argv):
    backhaul = False
    info = False
    route = False
    opts, args = getopt.getopt(argv, 'bir',['route','info','backhauling'])
    for opt, arg in opts:
        if opt in ('-b','--backhauling'):
            backhaul = True
        if opt in ('-i','--info'):
            info = True
        if opt in ('-r','--route'):
            route = True
    return {'backhaul':backhaul,'info':info,'route':route}

def cpe_add(options):
    cpe_rt= {'cpeId': {
                    'managedGroupId': None,
                    'subscriberId': None},
                    'vlanId': None,
                    'IPv4StaticRoute': {
                    'network': None,
                    'subnetMask': None,
                    'nextHop': None,
                    'ipV4Interface': 'LAN',
                    'redistribute': 'RIPv2',
                    'distributedMetric': '1',}}

    cpe_id = {'id': {
                'managedGroupId': None,
                'subscriberId': None,}}

    cpe_desc = {'customerInformation' : {
            'cpeId': {
                'managedGroupId': None,
                'subscriberId': None},
                'cpeDescription': None,
                'companyName': None}}

    bch = {'Backhauling': [
                {
                'name': None,
                'cpeSideIPAddressSource': 'PROFILE',
                'cpeSideIPAddressValue': None}]}

    vsat_obj = NbiFunction()

    with open(params.req_template_name, 'r') as f:
        cpe_str = f.read()
    cpes = ast.literal_eval(cpe_str)

    with open(params.vsat_table_name, 'r') as m:
        cpe_cfg = m.read()

    for i in cpe_cfg.splitlines():
        now = datetime.datetime.now()
        cpe = i.split(',')
        cpes['cpe']['cpeId']['managedGroupId'] = cpe[0]
        cpes['cpe']['cpeId']['subscriberId'] = cpe[1]
        cpes['cpe']['clusterCode'] = cpe[2]
        cpes['cpe']['platform'] = cpe[3]
        cpes['cpe']['description'] = cpe[4]
        cpes['cpe']['slaName'] = cpe[5]
        cpes['cpe']['rtnClassifierName'] = cpe[6]
        cpes['cpe']['vrs']['VR'][0]['vlanId'] = cpe[7]
        cpes['cpe']['vrs']['VR'][0]['ipv4']['subscriberPublicIpAddress']=cpe[8]
        cpes['cpe']['vrs']['VR'][0]['ipv4']['ipv4Prefix']=cpe[9]
        if options['backhaul']:
            bch['Backhauling'][0]['name'] = cpe[10]
            cpes['cpe']['vrs']['VR'][0]['backhaulings'] = bch
        print ('\n{:10}: CPE:  {:10}'.format(now.strftime("%H:%M:%S"), cpe[1]))
        vsat_obj.createCpe(cpes)
        time.sleep(0.1)

        if options['route']:
            cpe_rt['cpeId']['managedGroupId'] = cpe[0]
            cpe_rt['cpeId']['subscriberId'] = cpe[1]
            cpe_rt['vlanId'] = cpe[7]
            cpe_rt['IPv4StaticRoute']['network'] = cpe[11]
            cpe_rt['IPv4StaticRoute']['subnetMask'] = cpe[12]
            cpe_rt['IPv4StaticRoute']['nextHop'] = cpe[13]
            print ('{:5}ROUTE: {:7} : < {} : {} : {} >'.format('--->', cpe[1], cpe[11], cpe[12], cpe[13]))
            vsat_obj.addRoute(cpe_rt)
            time.sleep(0.1)
            
        if options['info']:
            cpe_desc['customerInformation']['cpeId']['managedGroupId'] = cpe[0]
            cpe_desc['customerInformation']['cpeId']['subscriberId'] = cpe[1]
            cpe_desc['customerInformation']['cpeDescription'] = cpe[14]
            cpe_desc['customerInformation']['companyName'] = cpe[15]
            print ('{:5}DESCR: {:7} : < {} : {} >'.format('--->', cpe[1], cpe[14], cpe[15]))
            vsat_obj.CPEdesc(cpe_desc)
            time.sleep(0.1)

    print ('\n\n{}\nCPEs:\n\tSUCCESS: {}\n\tFAILURE: {} -> {}'.format('-'*23,vsat_obj.add_succ,vsat_obj.add_fail,vsat_obj.add_fail_l))

    if options['route']:
        print('\nROUTE:\n\tSUCCESS: {}\n\tFAILURE: {} -> {}'.format(vsat_obj.rt_succ,vsat_obj.rt_fail,vsat_obj.rt_fail_l))


def main():
    ops = opts(sys.argv[1:])
    print ('time: {}\noptions: {}\n'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),ops))
    start = time.time()
    cpe_add(ops)
    end = time.time()
    spent = end-start
    print('\nSpent: {}'.format(spent))
    input()

if __name__ == '__main__':
    main()
