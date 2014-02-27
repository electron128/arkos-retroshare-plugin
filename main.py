from genesis.ui import *
from genesis.api import *

import retroshare_mmi

RETROSHARE_OS_USER = "retroshare"
RETROSHARE_NOGUI = "/home/vagrant/retroshare-git/retroshare-nogui/src/retroshare-nogui"

# what about translation???
# better have profile on external harddrive
# but how?
# the downloads dir has to be on a external drive, because of the size
# what about ports and port-forwarding?
# ports are the user-nighmare.

# now we have hardcoded /home/user/.retroshare directories even here
# have to remove this

class RetrosharePlugin(CategoryPlugin):
	text = "Retroshare"
	iconfont = "gen-bubbles"# don't know whta this is good for, icon from __init__.py is used
	folder = "apps"
	
	# in which order are init and session start called?
	# livetime of object?
	# textinput: what is name, and what is id?
	def on_session_start(self):
		print "on_session_start()"
		print self
		self._add_location = False
		self._identity_mode = "" # new, import or existing
		self._pgp_id = None
		self._name = None
		
		self._export_identity = False
		self._edit_location = None
		
		self._ask_for_password = False
		
		self._current_ssl_id = None
	
	def on_init(self):
		print "on_init()"
		print self
		self.rs = retroshare_mmi.RetroshareMMI(os_user=RETROSHARE_OS_USER, retroshare_nogui=RETROSHARE_NOGUI)

	def get_ui(self):
		print "get_ui()"
		print self
		ui = self.app.inflate("retroshare:main")
		
		location_list = ui.find("location-list")
		
		if not self._add_location and not self._edit_location and not self._ask_for_password:
			ok, locations, error_string = self.rs.get_locations()
			
			print "ok:"
			print ok
			print "locations:"
			print locations
			print "error_string:"
			print error_string
		
			if ok:
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
						UI.Label(text="/home/"+RETROSHARE_OS_USER+"/.retroshare/"+location.ssl_id)
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
								id='add-location')
							)
						for identity in identities:
							ui.find("name").append(UI.SelectOption(text=identity.name+"("+identity.pgp_id+")", value=identity.pgp_id))
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
						id='add-location')
					)
			if self._identity_mode == "import":
				# we have to show a box here to upload a file
				ui.append("main",UI.Label(text="Error: upload of keyfile not implemented. No import possible."))
				self._identity_mode = ""
		
		if self._edit_location:
			ui.append('main',
				UI.DialogBox(
					UI.Label(text="Settings"),
					UI.FormLine(
						UI.TextInput(name='name', id='name'),
						text='TODO'
					).append(
						UI.Button(id="import-identity", text="Import Identity")
					).append(
						UI.Button(id="existing-identity", text="Select existing Identity")
					),
					UI.FormLine(
						UI.TextInput(id='password', value='Click to add password', password="True"),
						text='TODO'
					),
					UI.FormLine(
						UI.TextInput(name='location-name', id='location-name'),
						text='TODO'
					),
					id='edit-location')
				)
		
		if self._ask_for_password:
			ui.append('main',
				UI.DialogBox(
					UI.Label(text="Enter your password"),
					UI.FormLine(
						UI.TextInput(id='password', name='password', password="True"),
						text='Password'
					),
					id='ask-for-password')
				)
		return ui

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
			self._edit_location = params[1]
		elif params[0] == "start-location":
			self._current_ssl_id = params[1]
			self._ask_for_password = True
		elif params[0] == "stop-location":
			location = params[1]
			self.rs.stop(location)

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
					
					if ok:
						pass
					else:
						print "ERROR ERROR ERROR ERROR ERROR ERROR ERROR"
						print "create_identity_and_location failed:"
						print error_string
			
			self._add_location = False
			self._identity_mode = "existing"
		
		elif params[0] == "edit-location":
			self._edit_location = None
			
		elif params[0] == "ask-for-password":
			if vars.getvalue("action","")=="OK":
				self.rs.start(vars.getvalue("password",""), self._current_ssl_id)
			self._ask_for_password = False


