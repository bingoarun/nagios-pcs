"""
Nagios / Icinga plugin to check the status of PCS cluster.

TODO:
    Get number of nodes and resources via command line. 
    Check for STONITH
    check for error count
    Check for DRBD status and roles of DRBD
    Appropriate message if the node is in standby mode
"""
#!\bin\python

from __future__ import print_function
from bs4 import BeautifulSoup
import os
import argparse

class PCSParser:
    
    def __init__(self):
        #fd = open("newtest","r")
        #pcs_xml = fd.read().replace('\n','')
        fd = os.popen("/usr/sbin/crm_mon -1 -r -f  -X").read()
        pcs_xml = fd.replace('\n','')
        pcs_xml = pcs_xml.replace('<?xml version="1.0"?>','')
        self.pcs = BeautifulSoup(pcs_xml,"lxml")
    
    def getOnlineNodes(self):
        nodes = self.pcs.find('nodes').find_all('node')
        online_nodes = []
        for node in nodes:
            if node['online'] == 'true':
                online_nodes.append(node['name'])
        return online_nodes

    def getOnlineResources(self):
        resources = self.pcs.find('resources').find_all('resource')
        online_resources = []
        for resource in resources:
            #print(resource)
            if ( resource['active'] == 'true' and 
                 resource['orphaned'] == 'false' and 
                 resource['blocked'] == 'false' and 
                 resource['failed'] == 'false' and 
                 int(resource['nodes_running_on']) > 0) :
                online_resources.append(resource['id'])
        return online_resources

class NagiosCheck:
    
    status = None
    message = ''

    def __init__(self,pcsobj,args):
        self.pcs = pcsobj
        self.args = args

    def validateNodes(self,pcs):
        if len(pcs.getOnlineNodes()) != int(args.nodes_count):
            self.status = 'WARNING'
            self.message = self.message+"Number of online nodes is less than 2."
        else:
            self.status = 'OK'
            self.message = self.message+"All 2 nodes are up and running."
    
    def validateResources(self,pcs):
        if len(pcs.getOnlineResources()) != int(args.resources_count):
            self.status = 'WARNING'
            self.message = self.message+"Number of online resources is less than 7."
        else:
            self.status = 'OK'
            self.message = self.message+" All 7 resources are up and running."

    def checkStatus(self):
        self.validateNodes(self.pcs)
        self.validateResources(self.pcs)
        print(("%s - %s")% (self.status,self.message))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("nodes_count", help="Number of active nodes expected")
    parser.add_argument("resources_count",help="Number of active resources expected")
    args = parser.parse_args()
    pcsobj = PCSParser()
    nagioschk = NagiosCheck(pcsobj,args)
    nagioschk.checkStatus()
    
