#!/usr/bin/env python3

import sys
import socket
import time

#time.sleep(10)

from ompl import base as ob
from ompl import control as oc
from ompl import util as ou

def list2vec(l, ret=None):
    """
    Convert a Python list into an ou.vectorDouble.
      l = the list
      ret = an existing ou.vectorDouble or None
    Returns a new vector if ret=None; modifies ret in place otherwise.
    """
    if not ret:
        ret = ou.vectorDouble()
        for e in l:
            ret.append(e)
        return ret
    else:
        for i in range(len(l)):
            ret[i] = l[i]
    
class MyEnvironment(ob.MorseEnvironment):
    """
    Represents the MORSE environment we will be planning in.
    Inherits from the C++ OMPL class ob.MorseEnvironment and
    implements pure virtual functions prepareStateRead(),
    finalizeStateWrite(), applyControl(), and worldStep().
    """
    
    def setSocket(self, comm_socket):
        """
        Use comm_socket for communication with the simulation.
        """
        self.sock = comm_socket
        
    def call(self, cmd):
        """
        Request a function call cmd from the simulation and
        return the result.
        """

        # submit cmd to socket; return eval()'ed response
        print('Calling %s' % cmd)
        if sock:
            self.sock.sendall(cmd.encode())
            return eval(sock.recv(1024))    # TODO: buffer size? states can get pretty big
    
    def prepareStateRead(self):
        """
        Get the state from the simulation and load it into
        the ou.vectorDoubles so OMPL can use it.
        """
        """state = self.call('extractState()')
        if not state:
            state = [((1.0,1.0,1.0),(1.0,1.0,1.0),(1.0,1.0,1.0),(1.0,1.0,1.0,1.0)),
                     ((1.0,1.0,1.0),(1.0,1.0,1.0),(1.0,1.0,1.0),(1.0,1.0,1.0,1.0)),
                    ]
        pos, lin, ang, quat = [],[],[],[]
        for obj in state:
            pos += obj[0]
            lin += obj[1]
            ang += obj[2]
            quat += obj[3]"""
        pos, lin, ang, quat = [], [], [], []
        for i in range(3*self.rigidBodies_):
            pos.append(1.0)
            lin.append(1.0)
            ang.append(1.0)
        for i in range(4*self.rigidBodies_):
            quat.append(1.0)
            if i%4:
                quat[i] = 0.0
        list2vec(pos, self.positions)
        list2vec(lin, self.linVelocities)
        list2vec(ang, self.angVelocities)
        list2vec(quat, self.quaternions)
        
    def finalizeStateWrite(self):
        """
        Compose a state string from the data in the
        ou.vectorDoubles and send it to the simulation.
        """
        """pos = list(self.positions)
        lin = list(self.linVelocities)
        ang = list(self.angVelocities)
        quat = list(self.quaternions)
        state = []
        for i in xrange(len(self.positions)/3):
            state.append((tuple(pos[3*i:3*i+3]),
                          tuple(lin[3*i:3*i+3]),
                          tuple(ang[3*i:3*i+3]),
                          tuple(quat[4*i:4*i+4])))
        self.call('submitState(%s)' % repr(state))"""
        
    def applyControl(self, control):
        """
        Tell MORSE to apply control to the robot.
        """
        """# TODO
        print("OMPL called applyControl(%s)" % repr(control))"""
        
    def worldStep(self, dur):
        """
        Run the simulation for dur seconds. World tick is 1/60 s.
        """
        """for i in range(int(round(dur/(1.0/60)))):
            self.call('nextTick()')"""
        
    def endSimulation(self):
        """
        Let the simulation know to shut down.
        """
        self.call('endSimulation()')
        
class MyGoal(ob.Goal):
    """
    The goal state of the simulation.
    """
    def __init__(self, si):
        super(MyGoal, self).__init__(si)
        self.c = 0
    
    def isSatisfied(self, state):
        self.c += 1
        if c==10:
            return True
        return false

def planWithMorse(sock):
    """
    Set up MyEnvironment, MorseStateSpace, and MorseSimpleSetup objects.
    Plan using sock as the communication socket to the simulation.
    """
    
    try:
        # create a MORSE environment representation
        # TODO get these numbers from the simulation
        env = MyEnvironment(2, 2, list2vec([-10,10,-1,1]), list2vec([-100,100,-100,100,-100,100]),
            list2vec([-10,10,-10,10,-10,10]), list2vec([-6,6,-6,6,-6,6]))
        env.setSocket(sock)

        # create a simple setup object
        ss = oc.MorseSimpleSetup(env)
        
        # get the state space
        space = ss.getStateSpace()
        
        # set up goal
        g = MyGoal(ob.SpaceInformation(space))
        ss.setGoal(g)
        
        print("Goal is set up.")
        
        # solve
        solved = ss.solve(1.0)
        print("Solve finished: %i", solved)
    
    finally:
        # tell simulation it can shut down
        env.endSimulation()
    
# set up the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 50007))
#sock = None

# plan
planWithMorse(sock)
sock.shutdown(socket.SHUT_RDWR)
sock.close()


