# !/usr/bin/python
from mininet.net import Mininet
from mininet.node import Node
from mininet.link import TCLink
from mininet.log import setLogLevel, info
from mininet.util import quietRun

from time import sleep


def scratchNet(cname='controller', cargs='-v ptcp:'):
    "Create network from scratch using Open vSwitch."

    info("*** Creating nodes\n")
    controller = Node('c0', inNamespace=False)
    switch0 = Node('s0', inNamespace=False)
    switch1 = Node('s1', inNamespace=False)
    h0 = Node('h0')
    h1 = Node('h1')

    info("*** Creating links\n")

    linkopts0 = dict(bw=10)
    linkopts1 = dict(bw=10, delay='5ms', loss=5)
    TCLink(h0, switch0, **linkopts0)
    TCLink(h1, switch1, **linkopts0)
    TCLink(switch0, switch1, **linkopts1)

    info("*** Configuring hosts\n")
    h0.setIP('192.168.123.1/24')
    h1.setIP('192.168.123.2/24')
    #info(str(h0) + '\n')
    #info(str(h1) + '\n')

    info("*** Starting network using Open vSwitch\n")
    controller.cmd(cname + ' ' + cargs + '&')
    switch0.cmd('ovs-vsctl del-br dp0')
    switch0.cmd('ovs-vsctl add-br dp0')
    switch1.cmd('ovs-vsctl del-br dp1')
    switch1.cmd('ovs-vsctl add-br dp1')

    for intf in switch0.intfs.values():
        print(intf)
        print(switch0.cmd('ovs-vsctl add-port dp0 %s' % intf))

    for intf in switch1.intfs.values():
        print(intf)
        print(switch1.cmd('ovs-vsctl add-port dp1 %s' % intf))

    switch0.cmd('ovs-vsctl set-controller dp0 tcp:127.0.0.1:6633')
    switch1.cmd('ovs-vsctl set-controller dp1 tcp: 127.0.0.1:6633')
    switch0.cmd('ovs-ofctl add-flow dp0 \"in_port=1 actions=output:2\"')
    switch0.cmd('ovs-ofctl add-flow dp0 \"in_port=2 actions=output:1\"')
    switch1.cmd('ovs-ofctl add-flow dp1 \"in_port=1 actions=output:2\"')
    switch1.cmd('ovs-ofctl add-flow dp1 \"in_port=2 actions=output:1\"')

    info('*** Waiting for switch to connect to controller')
    while 'is_connected' not in quietRun('ovs-vsctl show'):
        sleep(1)
        info('.')
    info('\n')
    print(switch0.cmd('ovs-ofctl show dp0'))
    print(switch1.cmd('ovs-ofctl show dp1'))

    info("*** Running test\n")
    h0.cmdPrint('ping -c10 -i0.5 -s128 ' + h1.IP())
    info('\n')
    h1.cmdPrint('ping -c10  ' + h0.IP())

    info("*** Stopping network\n")
    controller.cmd('kill %' + cname)
    switch0.cmd('ovs-vsctl del-br dp0')
    switch0.deleteIntfs()
    switch1.cmd('ovs-vsctl del-br dp1')
    switch1.deleteIntfs()
    info('\n')


if __name__ == '__main__':
    setLogLevel('info')
    info('*** Scratch network demo (kernel datapath)\n')
    Mininet.init()
    scratchNet()

