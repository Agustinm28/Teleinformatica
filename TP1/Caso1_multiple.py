from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.node import OVSKernelSwitch
import argparse

def gen_routers(net:Mininet, number:int):
    # Main router
    info('Generate main router\n')
    rm = net.addHost('rm', ip=None)
    rm.cmd('sysctl -w net.ipv4.ip_forward=1')

    # Building routers
    info('Generate building routers\n')
    r = [[] for l in range(number)]
    first_assignable = 1
    for i in range(number):
        if number <= 6:
            r[i] = net.addHost(f'r{i}', ip=f'192.168.100.{first_assignable}/29')
            r[i].cmd('sysctl -w net.ipv4.ip_forward=1')
            first_assignable += 8
        else:
            info('Max number of routers reached\n')
            break

    return rm, r

def gen_switches(net:Mininet, number:int):
    info( '*** Add switches\n')
    s_l = [[] for z in range(number)] # Para los switches entre el router central y los routers locales
    s_w = [[] for x in range(number)] # Para los switches entre los routers locales y los hosts locales
    for i in range(number):
        s_l[i] = net.addSwitch(f's{i}', cls=OVSKernelSwitch, failMode='standalone')
        s_w[i] = net.addSwitch(f'S{i}', cls=OVSKernelSwitch, failMode='standalone')

    return s_l, s_w


def gen_hosts(net, number):
    info('*** Add hosts\n')
    h = [[] for H in range(number)]
    for i in range(number):
        if number <= 253:
            h[i] = net.addHost(f'h{i}', ip=f'10.0.{i+1}.1/24', defaultRoute=f'via 10.0.{i+1}.254')
        else:
            info('Max number of hosts reached\n')
            break

    return h

def gen_links(net:Mininet, number:int, rm, s_w, s_l, r, h):
    info('*** Add links\n')

    # Para enlace rm - switch 1
    first_assignable = 1
    last_assignable = 6

    # Generacion de links
    for i in range(number):
        # /main router - entry switches/ links
        net.addLink(s_w[i], rm, intfName2=f'rm-eth{i}', params2={'ip': f'192.168.100.{last_assignable}/29'})
        # /entry switches - local routers/ links
        net.addLink(s_w[i], r[i], intfName1=f's{i}-eth0', params2={'ip': f'192.168.100.{first_assignable}/29'})
        # /local routers - local switches/ links
        net.addLink(r[i], s_l[i], intfName1=f'r{i}-eth1', params1={'ip': f'10.0.{i+1}.254/24'})
        # /local switches - hosts/ links
        net.addLink(s_l[i], h[i])

        first_assignable += 8
        last_assignable += 8

def start_network(net:Mininet, number:int):
    info('*** Starting network\n')
    net.build()

    info('*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info('*** Starting switches\n')
    for i in range(number):
        net.get(f's{i}').start([])
        net.get(f'S{i}').start([])

def post_configure(net:Mininet, number:int, rm, r):
    info('*** Post configure switches and hosts\n')

    first_assignable  = 1
    last_assignable  = 6

    rm.cmd('sysctl net.ipv4.ip_forward=1')

    for i in range(number):
        r[i].cmd('sysctl net.ipv4.ip_forward=1')
        rm_cmd = f'ip route add 10.0.{i+1}.0/24 via 192.168.100.{first_assignable}'
        rm.cmd(rm_cmd)
        for j in range(number):
            if j!= i:
                r_l_cmd = f'ip route add 10.0.{j+1}.0/24 via 192.168.100.{last_assignable}'
                r_w_cmd = f'ip route add 192.168.100.{8*j}/29 via 192.168.100.{last_assignable}'
                r[i].cmd(r_l_cmd)
                r[i].cmd(r_w_cmd)

        last_assignable += 8
        first_assignable += 8
    
def network(number):
    net = Mininet(topo=None, build=False, ipBase='192.168.100.0/24')

    # Generate main router and building routers
    try:
        rm, r = gen_routers(net, number)

        # Generate switches
        s_l, s_w = gen_switches(net, number)

        # Generate hosts
        h = gen_hosts(net, number)

        # Generate links
        gen_links(net, number, rm, s_w, s_l, r, h)

        # Start controllers
        start_network(net, number)

        net.start()

        # Post configure switches and hosts
        post_configure(net, number, rm, r)
    except AttributeError:
        print("No se pueden superar las 6 sucursales")
        net.stop()

    CLI(net)
    net.stop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', type=int, default=6,
                        help='Numero de sucursales')
    args = parser.parse_args()
    setLogLevel('info')
    if args.n <= 6:
        network(args.n)  
    else:
        print('No se pueden superar las 6 sucursales')