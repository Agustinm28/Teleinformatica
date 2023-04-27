from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.node import OVSKernelSwitch

def network():
    #? Crea una red con un router principal, dos routers secundarios y dos hosts.

    #? La red usa Mininet para crear un escenario con cuatro switches y tres routers.
    #? Los routers se conectan entre sí mediante subredes /29 y los hosts se conectan
    #? a los routers secundarios mediante subredes /24. Se configuran las rutas
    #? necesarias para que los hosts puedan comunicarse entre sí.

    #! IMPORTANTE para la consigna:
    #* Red 192.168.100.0/24 dividida en subredes con máscara /29
    #* La Dirección IP del enlace wan del router de la sucursal será la primera dirección utilizable de la red /29 su contraparte en la casa matríz será la última dirección utilizable de la red /29.
    #* La dirección IP privada del router de la sucursal será la primer dirección utilizable de la red 10.0.n.0/24.
    #* El router [primer IP] y un puesto de trabajo de la sucursal [última IP]

    # Crea una instancia de Mininet con la configuración predeterminada y establece la dirección IP base de la red.
    net = Mininet(topo=None, build=False, ipBase='192.168.100.0/24')

    # Agrega un host llamado r0 a la red, correspondiente al router matriz, y le asigna la dirección IP 192.168.100.6/29.
    info('Generate main router\n')
    main_router = net.addHost('r0', ip='192.168.100.6/29')

    # Agrega cuatro switches llamados s1, s2, s3 y s4 a la red
    info('Generate switches\n')
    s1, s2, s3, s4 = [
        net.addSwitch(s, cls=OVSKernelSwitch, failMode='standalone')
        for s in ('s1', 's2', 's3', 's4')
    ]

    info('Generate building routers\n')
    # Agrega un host llamado r1 a la red y le asigna la dirección IP 192.168.100.1/29.
    r1 = net.addHost('r1', ip='192.168.100.1/29')
    # Agrega un host llamado r2 a la red y le asigna la dirección IP 192.168.100.9/29
    r2 = net.addHost('r2', ip='192.168.100.9/29')

    info('Generate hosts\n')
    # Agrega un host llamado h1 a la red, le asigna la dirección IP 10.0.1.1/24 y establece su ruta predeterminada a través de 10.0.1.254
    h1 = net.addHost('h1', ip='10.0.1.1/24', defaultRoute='via 10.0.1.254')
    # Agrega un host llamado h2 a la red, le asigna la dirección IP 10.0.2.1/24 y establece su ruta predeterminada a través de 10.0.2.254.
    h2 = net.addHost('h2', ip='10.0.2.1/24', defaultRoute='via 10.0.2.254')

    #? Cuando se establece una ruta predeterminada (default route) en un host, 
    #? significa que cualquier tráfico de red que no esté destinado a una dirección IP específica en la misma red o en subredes conectadas directamente, 
    #? se enviará a través del enrutador o gateway predeterminado.

    #? En otras palabras, cualquier tráfico que no esté destinado a otra dirección en la subred 10.0.1.0/24 se enviará a través del switch s3 
    #? y su puerto conectado a h1 con dirección IP 10.0.1.1, y cualquier tráfico que no esté destinado a otra dirección en la subred 10.0.2.0/24 se enviará a través del switch s4 
    #? y su puerto conectado a h2 con dirección IP 10.0.2.1.

    info('Generate links\n')
    # Se definen las interfaces de red, que vendrian a asemejar a "puertos" en los cuales se conectaran entre si
    #? La diferencia entre params1 y params2 es que params1 se refiere a la interfaz de red del primer nodo enlazado al link, 
    #? mientras que params2 se refiere a la interfaz de red del segundo nodo enlazado. 
    # Agrega un enlace entre el switch s1 y el enrutador principal r0 y le asigna la dirección IP `192.168.100.6/29
    net.addLink(s1, main_router, intfName2='r0-eth1', params2={'ip': '192.168.100.6/29'})
    net.addLink(s2, main_router, intfName2='r0-eth2', params2={'ip': '192.168.100.14/29'})
    #? intfName1 se refiere al nombre de la interfaz de red en el primer nodo (o dispositivo) del enlace, 
    #? mientras que intfName2 se refiere al nombre de la interfaz de red en el segundo nodo (o dispositivo) del enlace.

    # Agrega un enlace entre el switch s1 y el enrutador r1 y le asigna la dirección IP 192.168.100.1/29
    net.addLink(s1, r1, intfName1='s1-eth2', intfName2='r1-eth1', params2={'ip': '192.168.100.1/29'})
    # Agrega un enlace entre el switch s2 y el enrutador r2 y le asigna la dirección IP 192.168.100.9/29
    net.addLink(s2, r2, intfName1='s2-eth2', intfName2='r2-eth1', params2={'ip': '192.168.100.9/29'})

    # Agrega un enlace entre el enrutador r1 y el switch s3 y le asigna la dirección IP 10.0.1.254/24
    net.addLink(r1, s3, intfName1='r1-eth2', params1={'ip': '10.0.1.254/24'})
    # Agrega un enlace entre el enrutador r2 y el switch s4 y le asigna la dirección IP 10.0.2.254/24
    net.addLink(r2, s4, intfName1='r2-eth2', params1={'ip': '10.0.2.254/24'})

    net.addLink(s3, h1)
    net.addLink(s4, h2)

    info('*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info('*** Starting switches\n')
    for s in (s1, s2, s3, s4):
        s.start([])
    info('*** Post configure switches and hosts\n')

    net.start()

    # Rutas: 

    #? se establecen las rutas utilizando comandos de shell en cada router, mediante el método cmd(). 
    #? Estas rutas indican qué subredes deben ser enrutadas a través de cada router, especificando la dirección IP del siguiente salto. 
    #? Por ejemplo, la línea r1_cmd = 'ip route add 10.0.2.0/24 via 192.168.100.6 && ip route add 192.168.100.8/29 via 192.168.100.6' establece que la subred 10.0.2.0/24 y 
    #? la subred 192.168.100.8/29 deben ser enrutadas a través del router r1, usando la dirección IP 192.168.100.6 como siguiente salto.

    # - Subred 10.0.2.0/24 enrutada a través del router r0 usando 192.168.100.9 como salto 
    # - Subred 10.0.1.0/24 enrutada a través del router r0 usando 192.168.100.1 como salto 
    #? Podria leerse como: Quiero que el router matriz haga ping con la subred 10.0.2.0/24 (que contiene host 2) a traves de 192.168.100.9 (enlace de switch 2 a router 2)
    #?                     Quiero que el router matriz haga ping con la subred 10.0.1.0/24 (que contiene host 1) a traves de 192.168.100.1 (enlace de switch 1 a router 1)
    main_router.cmd('sysctl net.ipv4.ip_forward=1')
    r0_cmd = 'ip route add 10.0.2.0/24 via 192.168.100.9 && \
                ip route add 10.0.1.0/24 via 192.168.100.1'
    main_router.cmd(r0_cmd)

    # - Subred 10.0.2.0/24 enrutada a través del router r1 usando 192.168.100.6 como salto
    # - Subred 192.168.100.8/29 enrutada a través del router r1 usando 192.168.100.6 como salto
    #? Podria leerse como: Quiero que el router 1 haga ping con la subred 10.0.2.0/24 (que contiene host 2) a traves de 192.168.100.6 (enlace de r0 a red 1)
    #?                     Quiero que el router 1 haga ping con la subred 192.168.100.8/29 (que contiene router 2) a traves de 192.168.100.6 (enlace de r0 a red 1)
    r1.cmd('sysctl net.ipv4.ip_forward=1')
    r1_cmd = 'ip route add 10.0.2.0/24 via 192.168.100.6 && \
               ip route add 192.168.100.8/29 via 192.168.100.6'
    r1.cmd(r1_cmd)

    # - Subred 10.0.1.0/24 enrutada a través del router r2 usando 192.168.100.14 como salto
    # - Subred 192.168.100.0/29 enrutada a través del router r2 usando 192.168.100.14 como salto
    #? Podria leerse como: Quiero que el router 2 haga ping con la subred 10.0.1.0/24 (que contiene host 1) a traves de 192.168.100.14 (enlace de r0 a red 2)
    #?                     Quiero que el router 2 haga ping con la subred 192.168.100.0/29 (que contiene router 1) a traves de 192.168.100.14 (enlace de r0 a red 2)
    r2.cmd('sysctl net.ipv4.ip_forward=1')
    r2_cmd = 'ip route add 10.0.1.0/24 via 192.168.100.14 && \
               ip route add 192.168.100.0/29 via 192.168.100.14'
    r2.cmd(r2_cmd)

    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    network()



    