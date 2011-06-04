from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.Console import Console
from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap, HelpableActionMap
from Components.Label import Label
from Components.Language import language
from Components.Button import Button
from Components.MenuList import MenuList
from Components.Sources.List import List
from Screens.Standby import TryQuitMainloop
from Tools.Directories import resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS, SCOPE_CURRENT_SKIN
from os import listdir, remove, environ
import datetime, time, gettext

lang = language.getLanguage()
environ["LANGUAGE"] = lang[:2]
print "[IPKInstaller] set language to ", lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("enigma2")
gettext.bindtextdomain("IPKInstaller", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "SystemPlugins/ViX/locale"))

def _(txt):
	t = gettext.dgettext("IPKInstaller", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

class VIXIPKInstaller(Screen):
	skin = """<screen name="VIXIPKInstaller" position="center,center" size="560,400" title="IPK Installer" flags="wfBorder" >
		<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on" />
		<widget name="key_red" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
		<widget name="key_green" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
		<widget name="lab1" position="0,50" size="560,50" font="Regular; 20" zPosition="2" transparent="0" halign="center"/>
		<widget name="list" position="10,105" size="540,300" scrollbarMode="showOnDemand" />
		<applet type="onLayoutFinish">
			self["list"].instance.setItemHeight(25)
		</applet>
	</screen>"""


	def __init__(self, session):
		Screen.__init__(self, session)
		self["title"] = Label(_("IPK Installer"))
		self['lab1'] = Label()
		self.list = []
		self.populate_List()
		self['list'] = MenuList(self.list)
		self['myactions'] = ActionMap(['ColorActions', 'OkCancelActions', 'DirectionActions'],
			{
				'cancel': self.close,
				'red': self.close,
				'green': self.keyInstall,
				'ok': self.keyInstall,
			}, -1)

		self["key_red"] = Button(_("Close"))
		self["key_green"] = Button(_("Install"))
		
	def populate_List(self):
		self['lab1'].setText(_("Select a package to install:"))
		del self.list[:]
		f = listdir('/tmp')
		for line in f:
			parts = line.split()
			pkg = parts[0]
			if pkg.find('.ipk') >= 0:
				self.list.append(pkg)
		self.list.sort()	

	def keyInstall(self):
		message = _("Are you ready to install ?")
		ybox = self.session.openWithCallback(self.Install, MessageBox, message, MessageBox.TYPE_YESNO)
		ybox.setTitle(_("Install Confirmation"))

	def Install(self,answer):
		if answer is True:
			sel = self['list'].getCurrent()
			if sel:
				cmd1 = "/usr/bin/opkg install /tmp/" + sel
				self.session.openWithCallback(self.installFinished(sel), Console, title=_("Installing..."), cmdlist = [cmd1], closeOnSuccess = True)	

	def installFinished(self,sel):
		message = ("Do you want to restart GUI now ?")
		ybox = self.session.openWithCallback(self.restBox, MessageBox, message, MessageBox.TYPE_YESNO)
		ybox.setTitle(_("Restart Enigma2."))
					
	def restBox(self, answer):
		if answer is True:
			self.session.open(TryQuitMainloop, 3)
		else:
			self.populate_List()
			self.close()

	def myclose(self):
		self.close()
		