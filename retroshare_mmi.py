# -*- coding: utf-8 -*-
'''

Functions for simple managment of retroshare identities and locations
(using retroshare-nogui)
Identity: a public/private PGP keypair
Location: a ssl-keypair, signed by a PGP key

functions return:
(ok, result, error_string)

ok: True or False
result: depends on the function, could be a list, dictionary or whatever
        some functions don't return a result
error_string: a human readable error string

notes:
- what about different os users? need to run retroshare-nogui with different user?
- how to handle webinterface/android/...?
- want to hide complexity from the user
- create a ssh-key
- translate the error strings?

where to store the settings?
we have some data which has to be set from outside of retroshare
we need this data before rs starts
what about the port in rswebui?

code in this file should stay generic as possible, to allow different frontends like ArkOS-genesis and Freedombox-Plinth


idea:
send messages through stdin/stdout as long as possible to know if start is ok
need to take care to not lock rs-nogui

info needed from outside:
- did start suceed?
- why did start fail?

info needed by rs-nogui
- password
- enable plugins?
- ssh-rpc settings
- rswebui-port

rs can't wait for input on stdin
-> outside has to wait for rs to send request and has to answer immediately

which webui?
- rswebui-plugin
- pyrs
- retroflux


'''

import platform
import subprocess
import os

import signal
import struct
import fcntl

# command line switch of rs-nogui to enable mmi
RS_MMI_SWITCH = "--mmi"

class Identity:
	name = ""
	pgp_id = ""

class Location:
	identity = None # an object of type Identity
	
	name = ""
	ssl_id = ""
	
	#-- currently unused --
	enabled = False # wheter this location should start on boot
	# running = False
	
	ssh_enabled = False # True or False
	ssh_user = ""
	ssh_password = ""
	ssh_port = ""
	
	ssh_rpc_enabled = False # True or False

class DummyIdentity(Identity):
	''' For testing without retroshare-nogui available. '''
	def __init__(self, name):
		self.name = name
		self.pgp_id = "dummy-pgp-id-of-" + name

class DummyLocation(Location):
	''' For testing without retroshare-nogui available. '''
	def __init__(self, name, location):
		self.identity = DummyIdentity(name)
		self.name = name + "(" + location + ")"
		self.ssl_id = "dummy-ssl-id-of-location-" + location

def runCommand(command, input):
	''' command is a list like ["executable","arg1","arg2"]. input is a string which will be passed to stdin of the command. Return (returncode, stdout, stderr).'''
	# universal_newlines = True is important for windows
	process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
	stdout, stderr = process.communicate(input)
	return process.returncode, stdout, stderr

# this is just a copy of the fn in retroshare-initscript-rev0.py
def getPidFromLockfile(filename):
    if not os.path.isfile(filename):
        return None
    
    # does not work
    # lockfile.lock packs the struct for fcntl wrong
    # see the original python source code
    #lockfile=posixfile.open(lockFileName)
    #lock=lockfile.lock("w?")
    #if lock!=None:
    #    mode, lenth, start, whence, pid=lock
    
    # see
    # /usr/include/i386-linux-gnu/bits/fcntl.h
    # fcntl.F_GETLK is 12, so we have to use struct flock64
    # (12=F_GETLK64, 5=F_GETLK in C)
    # i guess python uses fcntl.h with defined __USE_FILE_OFFSET64
    # i don't know if this will work on all linux platforms
    flock64=struct.pack('hhqql',fcntl.F_WRLCK,0,0,0,0)
    flock64=fcntl.fcntl(open(filename),fcntl.F_GETLK,flock64)
    l_type, l_whence, l_start, l_len, l_pid=struct.unpack('hhqql',flock64)
    if l_type==fcntl.F_UNLCK:
        return None
    else:
        return l_pid
	
class RetroshareMMI:
	def __init__(self, os_user = None, data_directory = None, retroshare_nogui = "retroshare-nogui"):
		''' Parameter os_user is only available on Linux. The current user needs the right to do "sudo --user" '''
		self.os_user = os_user
		self.data_directory = data_directory
		self.retroshare_nogui = retroshare_nogui
		
	def _check_sudo(self):
		if platform.system() == "Linux":
			if self.os_user:
				return ["sudo", "--user="+self.os_user]
			else:
				return []
		else:
			return []
		
	def create_identity_and_location(self, identity_name, password, location_name):
		''' Create a new identity and a new location. Return a Location object. '''
		print "create_identity_and_location()"
		print "identity_name=\""+identity_name+"\""
		print "password=\""+password+"\""
		print "location_name=\""+location_name+"\""
		
		ok = False
		result = None
		error_string = None
		command = self._check_sudo()
		
		command += [self.retroshare_nogui, RS_MMI_SWITCH, "generate-pgp-and-ssl-certificate"]
		input = identity_name + "\t" + password + "\t" + location_name +"\n"
		returncode, stdout, stderr = runCommand(command, input)
		
		if returncode == 0:
			ok = True
			pgp_id, ssl_id = stdout.split("\n")[0].split("\t")
			result = Location()
			result.identity = Identity()
			result.identity.name = identity_name
			result.identity.pgp_id = pgp_id
			result.name = location_name
			result.ssl_id = ssl_id
		else:
			error_string = stderr
		
		return ok, result, error_string

	def create_location(self, pgp_id, password, location_name):
		''' Create a new Location for the given identity. Return a Location object. '''
		ok = False
		result = None
		error_string = None
		command = self._check_sudo()
		
		command += [self.retroshare_nogui, RS_MMI_SWITCH, "generate-pgp-certificate"]
		input = pgp_id + "\t" + password + "\t" + location_name +"\n"
		returncode, stdout, stderr = runCommand(command, input)
		
		if returncode == 0:
			ok = True
			ssl_id = stdout.split("\n")[0]
			result = Location()
			result.identity = Identity()
			result.identity.name = None # not known at this point
			result.identity.pgp_id = pgp_id
			result.name = location_name
			result.ssl_id = ssl_id
		else:
			error_string = stderr
		
		return ok, result, error_string

	def import_identity(self, path_to_keyfile):
		''' Import a identity(=PGP-key). Return a Identiy object. '''
		ok = False
		result = None
		error_string = None
		command = self._check_sudo()
		
		command += [self.retroshare_nogui, RS_MMI_SWITCH, "import-pgp-key"]
		input = path_to_keyfile +"\n"
		returncode, stdout, stderr = runCommand(command, input)
		
		if returncode == 0:
			ok = True
			pgp_id = stdout.split("\n")[0]
			result = Identity()
			result.name = None # not known at this point
			result.pgp_id = pgp_id
		else:
			error_string = stderr
		
		return ok, result, error_string
		
	def export_identity(self, pgp_id, path_to_keyfile):
		''' Export a identity(=PGP-key). Return Tuple (ok, None, error_string)'''
		ok = False
		result = None
		error_string = None
		command = self._check_sudo()
		
		command += [self.retroshare_nogui, RS_MMI_SWITCH, "export-pgp-key"]
		input = pgp_id + "\t" + path_to_keyfile +"\n"
		returncode, stdout, stderr = runCommand(command, input)
		
		if returncode == 0:
			ok = True
		else:
			error_string = stderr
		
		return ok, result, error_string

	def get_identities(self):
		''' Return a list of Identity objects. '''
		ok = False
		result = None
		error_string = None
		command = self._check_sudo()
		
		command += [self.retroshare_nogui, RS_MMI_SWITCH, "list-pgp-private-keys"]
		input = ""
		returncode, stdout, stderr = runCommand(command, input)
		
		if returncode == 0:
			ok = True
			result = []
			for line in stdout.split("\n"):
				if line != "":
					identity = Identity()
					identity.pgp_id, identity.name = line.split("\t")
					result += [identity]
		else:
			error_string = stderr
		
		return ok, result, error_string

	def get_locations(self):
		''' Return a list of Location objects. '''
		ok = False
		result = None
		error_string = None
		command = self._check_sudo()
		
		command += [self.retroshare_nogui, RS_MMI_SWITCH, "list-accounts"]
		input = ""
		returncode, stdout, stderr = runCommand(command, input)
		
		if returncode == 0:
			ok = True
			result = []
			for line in stdout.split("\n"):
				if line != "":
					print line.split("\t")
					location = Location()
					location.identity = Identity()
					
					location.ssl_id, location.name,\
					location.identity.pgp_id, location.identity.name = line.split("\t")
					
					result += [location]
		else:
			error_string = stderr
		
		return ok, result, error_string

	def set_location(self, location):
		''' Set a locations settings. Parameter location is a Location object. '''
		ok = False
		error_string = "set_location() not implemented"
		return ok, error_string
	
	def start(self, password, ssl_id=None):
		''' Start retroshare-nogui for the given ssl_id. If ssl_id==None, then start all enabled locations. '''
		command = [self.retroshare_nogui]
		
		if ssl_id:
			command += ["--user-id", ssl_id]
			
		if platform.system() == "Windows":
			DETACHED_PROCESS = 0x00000008
			process = subprocess.Popen(command, close_fds=True, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP|DETACHED_PROCESS, stdin=subprocess.PIPE)
		if platform.system() == "Linux":
			command = self._check_sudo() + command
			# retroshare gets killed when this script dies
			#process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			
			# shared stddout/stderr for debugging
			process = subprocess.Popen(command, stdin=subprocess.PIPE)
		
		process.stdin.write(password+"\n")
		
		ok = False
		error_string = "We don't know if retroshare-nogui failed and if it failed we don't know why."
		return ok, error_string
	
	# we have hardcoded config dirs here
	# this is only a solution for testing
	def stop(self, ssl_id=None):
		''' Stop retroshare-nogui for the given ssl_id. If ssl_id==None, then stop all enabled locations. '''
		if platform.system() == "Linux":
			if ssl_id == None:
				return False, "stop(): currently not possible to stop many locations at once"
			if self.os_user:
				lockfilename = "/home/"+self.os_user+"/.retroshare/"+ssl_id+"/lock"
				pid = getPidFromLockfile(lockfilename)
				if pid:
					print "found lock on file "+lockfilename+" pid="+str(pid)
					os.kill(pid,signal.SIGINT)
				return True, None
			else:
				return False, "Error in stop(): no os_user given"
		else:
			return False, "Error in stop(): not implemented on Windows"
		
	def get_pid(self, ssl_id):
		if platform.system() == "Linux":
			if self.os_user:
				lockfilename = "/home/"+self.os_user+"/.retroshare/"+ssl_id+"/lock"
				pid = getPidFromLockfile(lockfilename)
				return True, pid, None
			else:
				return False, None, "Error in get_pid(): no os_user given"
		else:
			return False, None, "Error in get_pid(): not implemented on Windows"

	def status(self):
		''' Return the status of the locations.
		This is similar to get_locations,so maybe return the status in get_locations, and remove this.
		'''
		ok = True
		result = [DummyLocation("hans","home"),DummyLocation("hans","far away"),DummyLocation("fritz","laptop")]
		error_string = None
		
		ok = False
		result = None
		error_string = "status() currently not implemented. Try to start retroshare an see the output to check if retroshare-nogui is running. Or use another program to see if retroshare-nogui is running."
		
		return ok, result, error_string

if __name__ == "__main__":
	if platform.system() == "Windows":
		#data_directory = "Data"
		#print "data_directory = " + data_directory
		
		mmi = RetroshareMMI()
		print mmi.create_identity_and_location("python-test2-password","password","python-location")
		#print mmi.get_locations()
		mmi.start("no-passsword", "python-test2-password")
		
	elif platform.system() == "Linux":
		print "test on Linux not written yet. TODO: write test for Linux"