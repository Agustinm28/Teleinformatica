from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.node import OVSKernelSwitch

def network():
    net = Mininet(topo=None, build=False, ipBase='192.168.100.0/24')

    info('Generate main router\n')
    main_router = net.addHost('r0', ip=None)

    info('Generate switches\n')
    s1, s2, s1b, s2b = [
        net.addSwitch(s, cls=OVSKernelSwitch, failMode='standalone')
        for s in ('s1', 's2', 's1b', 's2b')
    ]

    info('Generate building routers\n')
    r1 = net.addHost('r1', ip='192.168.100.1/29')
    r2 = net.addHost('r2', ip='192.168.100.9/29')

    info('Generate hosts\n')
    h1 = net.addHost('h1', ip='10.0.1.1/24', defaultRoute='via 10.0.1.254')
    h2 = net.addHost('h2', ip='10.0.2.1/24', defaultRoute='via 10.0.2.254')

    info('Generate links\n')
    net.addLink(s1, main_router, intfName2='r0-eth1', params2={'ip': '192.168.100.6/29'})
    net.addLink(s2, main_router, intfName2='r0-eth2', params2={'ip': '192.168.100.14/29'})

    net.addLink(s1, r1, intfName1='s1-eth2', intfName2='r1-eth1', params2={'ip': '192.168.100.1/29'})
    net.addLink(s2, r2, intfName1='s2-eth2', intfName2='r2-eth1', params2={'ip': '192.168.100.9/29'})

    net.addLink(r1, s1b, intfName1='r1-eth2', params1={'ip': '10.0.1.254/24'})
    net.addLink(r2, s2b, intfName1='r2-eth2', params1={'ip': '10.0.2.254/24'})

    net.addLink(s1b, h1)
    net.addLink(s2b, h2)

    info('*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info('*** Starting switches\n')
    for s in (s1, s2, s1b, s2b):
        s.start([])
    info('*** Post configure switches and hosts\n')

    net.start()

    # Rutas:
    # - Subred 10.0.2.0/24 enrutada a través del router r0 usando 192.168.100.9 como salto 
    # - Subred 10.0.1.0/24 enrutada a través del router r0 usando 192.168.100.1 como salto 
    main_router.cmd('sysctl net.ipv4.ip_forward=1')
    r0_cmd = 'ip route add 10.0.2.0/24 via 192.168.100.9 && \
                ip route add 10.0.1.0/24 via 192.168.100.1'
    main_router.cmd(r0_cmd)

    # - Subred 10.0.2.0/24 enrutada a través del router r1 usando 192.168.100.6 como salto
    # - Subred 192.168.100.8/29 enrutada a través del router r1 usando 192.168.100.6 como salto
    r1.cmd('sysctl net.ipv4.ip_forward=1')
    r1_cmd = 'ip route add 10.0.2.0/24 via 192.168.100.6 && \
               ip route add 192.168.100.8/29 via 192.168.100.6'
    r1.cmd(r1_cmd)

    # - Subred 10.0.1.0/24 enrutada a través del router r2 usando 192.168.100.14 como salto
    # - Subred 192.168.100.0/29 enrutada a través del router r2 usando 192.168.100.14 como salto
    r2.cmd('sysctl net.ipv4.ip_forward=1')
    r2_cmd = 'ip route add 10.0.1.0/24 via 192.168.100.14 && \
               ip route add 192.168.100.0/29 via 192.168.100.14'
    r2.cmd(r2_cmd)

    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    network()



    