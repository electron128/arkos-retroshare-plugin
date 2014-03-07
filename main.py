from genesis.ui import *
from genesis.api import *

import retroshare_mmi
import os
import pwd
import stat

RETROSHARE_OS_USER = "retroshare"
#RETROSHARE_NOGUI = "/home/vagrant/retroshare-git/retroshare-nogui/src/retroshare-nogui"
RETROSHARE_NOGUI = "retroshare-nogui"

'''
what about translation???
peakwinter: There will be a translation system introduced in 0.7 and a system will be made available at that time

better have profile on external harddrive
but how?
peakwinter: The best way is to leave it as-is, to include a function/configuration for changing a data directory,
and in the future when the boot/data split is complete, this will be much easier to do from the start.
the downloads dir has to be on a external drive, because of the size

what about ports and port-forwarding?
ports are the user-nighmare.
peakwinter: There is a  SERVICES  directive in  __init__.py

todo: read in tramsmission plugin about service and ports

problem: want different firewall rules for different ports

# now we have hardcoded /home/user/.retroshare directories even here
# have to remove this


Todo:
- add logging
- decide about retroshare-nogui startup, fork to background?
  (proof-of-concept code is already working)
- put data directory on external harddrive?
- integrate into ArkOS port managment

'''

class RetrosharePlugin(CategoryPlugin, URLHandler, IURLHandler):
	text = "Retroshare"
	iconfont = "gen-bubbles"# don't know whta this is good for, icon from __init__.py is used
	folder = "apps"
	'''
	in which order are init and session start called?
	on_session_start()  is called when the user successfully logs in. It is called for all plugins, whether they are in focus or not.
	This is a good place to get connections to other frameworks and plugins for later use in your plugin.
	on_init()  is called when you view your plugin, in preparation for displaying the page.

	livetime of object?

	textinput: what is name, and what is id?
	The  name  is how you retrieve values, like with 
	 vars.getvalue(name) . This is what is passed in the POST request. 
	 id  is only used for manipulating the XML (like with 
	 ui.find()  or 
	 ui.remove() ), and not for retrieving values
	'''
	
	def on_session_start(self):
		print "on_session_start()"
		print self
		self._add_location = False
		self._identity_mode = "" # new, import or existing
		self._pgp_id = None
		self._name = None
		
		# status of dialog windows
		self._export_identity = False
		self._edit_location = None
		self._ask_for_password = False
		self._ask_for_restart = False
		self._current_ssl_id = None
		self._last_error = ""
		
		self._selected_pgp_id = None
		
		self._cached_locations = []
		
		self._mmi_data_directory = "/home/"+RETROSHARE_OS_USER+"/.retroshare_arkos_settings"
		if not os.path.exists(self._mmi_data_directory):
			os.mkdir(self._mmi_data_directory)
			# rw for user
			os.chmod(self._mmi_data_directory, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
			passwd = pwd.getpwnam(RETROSHARE_OS_USER)
			os.chown(self._mmi_data_directory, passwd[2], passwd[3])
	
	def on_init(self):
		print "on_init()"
		print self
		self.rs = retroshare_mmi.RetroshareMMI(mmi_data_directory=self._mmi_data_directory, os_user=RETROSHARE_OS_USER, retroshare_nogui=RETROSHARE_NOGUI)

	def get_ui(self):
		print "get_ui()"
		print self
		ui = self.app.inflate("retroshare:main")
		
		ui.find("retroshare-nogui").set("text", "retroshare-nogui command: "+RETROSHARE_NOGUI)
		ui.find("os-user").set("text", "RETROSHARE_OS_USER: "+RETROSHARE_OS_USER)
		ui.find("data-directory").set("text", "Data Directory: "+"/home/"+RETROSHARE_OS_USER+"/.retroshare")
		
		if not self._add_location and not self._edit_location and not self._ask_for_password:
			# load all locations an display in a table
			ok, locations, error_string = self.rs.get_locations()
			
			print "ok:"
			print ok
			print "locations:"
			print locations
			print "error_string:"
			print error_string
		
			if ok:
				location_list = ui.find("location-list")
				
				self._cached_locations = locations
				for location in locations:
					pid_ok, pid, error_string = self.rs.get_pid(location.ssl_id)
					if pid_ok and pid:
						status = "running"
						button_label = "stop"
						button_action = "stop-location/"+location.ssl_id
					elif pid_ok:
						status = "stopped"
						button_label = "start"
						button_action = "start-location/"+location.ssl_id
					else:
						status = "Error: "+error_string
						button_label = "Error"
						button_action = "nop"
					location_list.append(UI.DTR(
						UI.Label(text=(location.identity.name+"("+location.name+")")),
						UI.Label(text=status),
						UI.Button(id=button_action, text=button_label),
						UI.Button(id=("edit-location/"+location.ssl_id), text="Settings"),
						UI.Label(text=location.ssl_id)
					))
			else:
				ui.append("main",UI.Label(text="could not get location list. Error:"+error_string))
		
		if self._add_location:
			print "self._add_loaction=True"
			print "self._identity_mode=\""+self._identity_mode+"\""
			if self._identity_mode == "" or self._identity_mode == "existing":
				ok, identities, error_string = self.rs.get_identities()
				if ok:
					if len(identities)>0:
						print "diaolog for existign identity"
						ui.append('main',
							UI.DialogBox(
								UI.Label(text="Create new Location"),
								UI.FormLine(
									UI.SelectInput(name='name', id='name'),
									text='Select Identity'
								).append(
									UI.Button(id="import-identity", text="Import Identity")
								).append(
									UI.Button(id="new-identity", text="Create new Identity")
								),
								UI.FormLine(
									UI.TextInput(id='password', name="password", password="True"),
									text='Password'
								),
								UI.FormLine(
									UI.TextInput(name='location-name', id='location-name'),
									text='Location'
								),
								id='add-location'
							)
						)
						for identity in identities:
							ui.find("name").append(UI.SelectOption(text=identity.name+"("+identity.pgp_id+")", value=identity.pgp_id, id=identity.pgp_id))
						if self._selected_pgp_id:
							ui.find(self._selected_pgp_id).set("selected", "True")
					else:
						# no existing identities, show new identity dialog
						print "no identities switching to new identity"
						self._identity_mode = "new"
				else:
					ui.append("main",UI.Label(text="Error: "+error_string))
			
			if self._identity_mode == "new":
				print "dialog new identity"
				ui.append('main',
					UI.DialogBox(
						UI.Label(text="Create new Identity and Location"),
						UI.FormLine(
							UI.TextInput(name='name', id='name'),
							text='Name'
						).append(
							UI.Button(id="import-identity", text="Import Identity")
						).append(
							UI.Button(id="existing-identity", text="Select existing Identity")
						),
						UI.FormLine(
							UI.TextInput(id='password', name='password', password="True"),
							text='Password'
						),
						UI.FormLine(
							UI.TextInput(name='location-name', id='location-name'),
							text='Location'
						),
						id='add-location'
					)
				)
			if self._identity_mode == "import":
				# we have to show a box here to upload a file
				ui.append("main",
					UI.UploadBox(id='upload-key',
						text="Select Identity file for import",
						multiple=False)
					)
				self._identity_mode = "existing"
		
		if self._edit_location:
			location = self._edit_location
			
			if location.ssh_enabled:
				ssh_enabled = "True"
			else:
				ssh_enabled = "False"
				
			if location.ssh_rpc_enabled:
				ssh_rpc_enabled = "True"
			else:
				ssh_rpc_enabled = "False"
				
			ui.append('main',
				UI.DialogBox(
					UI.Label(text="Settings for "+location.identity.name+"("+ location.name+")"),
					UI.FormLine(
						UI.TextInput(name='port', id='port', value=location.port),
						text='Port'
					),
					UI.FormLine(
						UI.CheckBox(name='ssh_enabled', id='ssh_enabled', checked=ssh_enabled),
						text='enable ssh'
					),
					UI.FormLine(
						UI.CheckBox(name='ssh_rpc_enabled', id='ssh_rpc_enabled', checked=ssh_rpc_enabled),
						text='enable ssh rpc'
					),
					UI.FormLine(
						UI.TextInput(id='ssh_user', name='ssh_user', value=location.ssh_user),
						text='ssh user'
					),
					UI.FormLine(
						UI.TextInput(name='ssh_password', id='ssh_password', password="True"),
						text='ssh password'
					),
					UI.FormLine(
						UI.TextInput(name='ssh_port', id='ssh_port', value=location.ssh_port),
						text='ssh port'
					),
					id='edit-location')
				)
		
		if self._ask_for_password:
			ui.append('main',
				UI.DialogBox(
					UI.Label(text="Enter your Retroshare password"),
					UI.FormLine(
						UI.TextInput(id='password', name='password', password="True"),
						text='Password'
					),
					id='ask-for-password')
				)
		
		if self._export_identity:
			ok, identities, error_string = self.rs.get_identities()
			if ok:
				table = UI.DT(
							UI.DTR(
								UI.DTH(UI.Label(text="Identity")),
								UI.DTH(UI.Label(text="PGP-ID")),
								UI.DTH(UI.Label(text="export it")),
								header="True"
							)
						)
				for identity in identities:
					table.append(
						UI.DTR(
							UI.Label(text=identity.name),
							UI.Label(text=identity.pgp_id),
							UI.CustomHTML(html="<a href='retroshare/export_identity/"+identity.pgp_id+"'>download keyfile</a>")
						)
					)
				ui.append("main",UI.DialogBox(UI.Label(text="Export Identity"), table, id="export-identity"))
			else:
				self._export_identity = False
				last_error = "could not get lits of identites: " + error_string
		ui.append("main",UI.Label(text=self._last_error))
		return ui

	@url("^/retroshare/export_identity.*$")
	def download_identity(self, req, start_response):
		self.on_init()
		pgp_id = req["PATH_INFO"].split("/")[3]
		print "download identity() pgp_id:"+pgp_id
		
		keyfile_path = self._mmi_data_directory + "/genesis_identity_export_tmp"
		ok, nothing, error_string = self.rs.export_identity(pgp_id, keyfile_path)
		if ok:
			self._export_identity = False
			size = os.path.getsize(keyfile_path)
			file = open(keyfile_path, "rb")
			data = file.read()
			file.close()
			os.remove(keyfile_path)
			start_response('200 OK', [
				('Content-length', str(size)),
				('Content-Disposition', 'attachment; filename=%s' % pgp_id+'_retroshare_private_key.asc')
			])
			return data
		else:
			msg = "failed to export Retroshare identity\n"+error_string
			start_response('200 OK', [
				('Content-length', str(size)),
				('Content-type', 'text/plain')
			])
			return msg

	@event('button/click')
	def on_click(self, event, params, vars = None):
		print "on_click()"
		print self
		print "on_click params:"
		print params
		if params[0] == "add-location":
			print "setting self._add_loaction=True"
			self._add_location = True
		elif params[0] == "import-identity":
			print "import-identity button clicked"
			self._identity_mode = "import"
		elif params[0] == "existing-identity":
			print "existing-identity button clicked"
			self._identity_mode = "existing"
		elif params[0] == "new-identity":
			print "new-identity button clicked"
			self._identity_mode = "new"
		elif params[0] == "edit-location":
			ssl_id = params[1]
			for location in self._cached_locations:
				if location.ssl_id == ssl_id:
					self._edit_location = location
		elif params[0] == "start-location":
			self._current_ssl_id = params[1]
			self._ask_for_password = True
		elif params[0] == "stop-location":
			location = params[1]
			self.rs.stop(location)
			self._last_error = ""
		elif params[0] == "export-identity":
			self._export_identity = True

	@event('dialog/submit')
	def on_submit(self, event, params, vars = None):
		print "on_submit()"
		print self
		if params[0] == 'add-location':
			print "add-location submitted"
			print event
			print params
			print vars
			
			if vars.getvalue("action","")=="OK":
				if self._identity_mode == "new":
					name = vars.getvalue("name","")
					password = vars.getvalue("password","")
					location_name = vars.getvalue("location-name","")
					
					ok, location, error_string = self.rs.create_identity_and_location(name, password, location_name)
					
					if not ok:
						self._last_error = "Error creating location: "+ error_string
					else:
						self._last_error = ""
			else:
				self._last_error = ""
			self._add_location = False
			self._identity_mode = "existing"
		
		elif params[0] == "edit-location":
			print "edit-location submitted"
			print event
			print params
			print vars
			
			if vars.getvalue("action","")=="OK":
				location = self._edit_location
				changed = False
				
				port = vars.getvalue("port", "")
				if location.port != port:
					changed = True
					location.port = port
					
				ssh_enabled = vars.getvalue("ssh_enabled", "")
				if ssh_enabled == "0":
					ssh_enabled = False
				else:
					ssh_enabled = True
				if location.ssh_enabled != ssh_enabled:
					changed = True
					location.ssh_enabled = ssh_enabled
				
				ssh_rpc_enabled = vars.getvalue("ssh_rpc_enabled", "")
				if ssh_rpc_enabled == "0":
					ssh_rpc_enabled = False
				else:
					ssh_rpc_enabled = True
				if location.ssh_rpc_enabled != ssh_rpc_enabled:
					changed = True
					location.ssh_rpc_enabled = ssh_rpc_enabled
					
				ssh_user = vars.getvalue("ssh_user", "")
				if location.ssh_user != ssh_user:
					changed = True
					location.ssh_user = ssh_user
					
				ssh_password = vars.getvalue("ssh_password", "")
				if ssh_password != "":
					changed = True
					location.ssh_password = ssh_password
					
				ssh_port = vars.getvalue("ssh_port", "")
				if location.ssh_port != ssh_port:
					changed = True
					location.ssh_port = ssh_port
					
				if changed:
					ok, error_string = self.rs.set_location(location)
					if ok:
						self._ask_for_restart = True
						self._current_ssl_id = location.ssl_id
						self._last_error = ""
					else:
						self._last_error = "Error editing location: "+error_string
			else:
				self._last_error = ""
			self._edit_location = None
			
		elif params[0] == "ask-for-password":
			if vars.getvalue("action","")=="OK":
				ok, error_string = self.rs.start(vars.getvalue("password",""), self._current_ssl_id)
				if ok:
					self._last_error = ""
				else:
					self._last_error = "Error starting location: "+error_string
			else:
				self._last_error = ""
			self._ask_for_password = False
		
		elif params[0] == "upload-key":
			if vars.getvalue('action', '') == 'OK' and vars.has_key('file'):
				upf = vars['file']
				print "got uploaded file"
				print str(upf)
				
				filepath = self._mmi_data_directory + "/genesis_identity_import_tmp"
				
				import pdb; pdb.set_trace()
				
				# first create a file
				file = open(filepath, "w")
				file.close()
				# then change permissions to not allow anyone else to read it
				os.chmod(filepath, stat.S_IRUSR | stat.S_IWUSR)
				
				# open file again and write data to it
				file = open(filepath, "w")
				file.write(upf.value)
				file.close()
				
				# change ownership of file to RETROSHARE_OS_USER
				passwd = pwd.getpwnam(RETROSHARE_OS_USER)
				os.chown(filepath, passwd[2], passwd[3])
				
				ok, pgp_id, error_string = self.rs.import_identity(filepath)
				
				if ok:
					self._selected_pgp_id = pgp_id
					self._add_location = True
					self._last_error = ""
				else:
					self._add_location = False
					self._last_error = "Import of identity failed: " + error_string
				
				os.remove(filepath)
			else:
				self._last_error = ""
				self._add_location = False
			self._identity_mode = "existing"
		elif params[0] == "export-identity":
			self._export_identity = False
			self._last_error = ""

