"""
Group 3
1. Dipayan Deb , 2019H1030015G, h20190015@goa.bits-pilani.ac.in
2. Kumar Anand, 2019H1030500G, h20190500@goa.bits-pilani.ac.in
3. Bharath S, 2019H1030017G, h20190017@goa.bits-pilani.ac.in
4. Ghodke  Pratik Pravin, 2019H1030558G, h20190558@goa.bits-pilani.ac.in 


"""

from pox.core import core
import pox.openflow.libopenflow_01 as of


class LearningSwitch (object):

  def __init__ (self, connection):
    self.connection = connection

    self.macToPort = {}
    connection.addListeners(self)

  def _handle_PacketIn (self, event):
    packet = event.parsed
    def flood ():
      msg = of.ofp_packet_out()
      msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
      msg.data = event.ofp
      msg.in_port = event.port
      self.connection.send(msg)

    def drop (duration = None):
      #Only adds flow table if time is given.
      if duration is not None:
        if not isinstance(duration, tuple):
          duration = (duration,duration)
        msg = of.ofp_flow_mod()
        msg.match = of.ofp_match.from_packet(packet)
        msg.idle_timeout = duration[0]
        msg.hard_timeout = duration[1]
        msg.buffer_id = event.ofp.buffer_id
        self.connection.send(msg)
      elif event.ofp.buffer_id is not None:
        msg = of.ofp_packet_out()
        msg.buffer_id = event.ofp.buffer_id
        msg.in_port = event.port
        self.connection.send(msg)

    self.macToPort[packet.src] = event.port 

    if packet.dst.is_multicast:
      flood() 
    else:
      if packet.dst not in self.macToPort: 
        flood() 
      else:
        port = self.macToPort[packet.dst]
        if port == event.port: 
          drop(10)
          return
        l = packet.find('tcp')
        if event.port == 3 and port == 1 and  l!=None and l.dstport == 80:
           drop(100)
        else:
           msg = of.ofp_flow_mod()
           msg.match = of.ofp_match.from_packet(packet, event.port)
           msg.idle_timeout = 10
           msg.hard_timeout = 30
           msg.actions.append(of.ofp_action_output(port = port))
           msg.data = event.ofp
           self.connection.send(msg)


class l2_learning (object):
  def __init__ (self):
    core.openflow.addListeners(self)
  def _handle_ConnectionUp (self, event):
    LearningSwitch(event.connection)


def launch():
  core.registerNew(l2_learning)