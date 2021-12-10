#Invoke Sonatype Nexus IQ scan using CLI
"""Invoke Sonatype Nexus IQ scan using CLI"""

import os
import sys

#Import creds
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from creds import stlabcred, stlabserver, stentcred, stentserver

#manual def
name = "cagantest"
cli = "/users/mm67226/nexus-iq-cli-1.114.0-01.jar"
scandir = "/users/mm67226/nexusscan"
output = "$scandir/output.json"
env = "ent"

#env variables
if env == "lab":
    nexusserver = stlabserver
    nexuscred = stlabcred
elif env == "ent":
    nexusserver = stentserver
    nexuscred = stentcred


os.system("java -jar {0} -i {1} -s {2} -a {3} {4}".format(cli, name, nexusserver, nexuscred, scandir))

