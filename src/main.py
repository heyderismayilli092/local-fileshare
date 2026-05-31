#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GObject

import os
import socket
import subprocess
import locale
import segno
import bcrypt
from locale import gettext as _
from network import find_active_interface

locale.bindtextdomain('local-fileshare', '/usr/share/locale')
locale.textdomain('local-fileshare')

GLADE_FILE = os.path.dirname(os.path.abspath(__file__)) + "/../ui/MainWindow.glade"
fileserver = os.path.dirname(os.path.abspath(__file__)) + "/fileserver.py"


class LocalFileShare:
    def __init__(self):
        self.flask_process = None
        self.passhash_file = "/tmp/local-fileshare_passhash"

        self.builder = Gtk.Builder()
        self.builder.add_from_file(GLADE_FILE)

        # -------Widget referansları-------

        # Main Window
        self.mainwindow   = self.builder.get_object("mainwindow")  # home window
        self.directory    = self.builder.get_object("directory")  # selected directory
        self.share_button = self.builder.get_object("share_button")  # share button
        self.stopshare    = self.builder.get_object("stopshare")  # share stop button
        self.message      = self.builder.get_object("message")  # message label
        self.error_label   = self.builder.get_object("error_label")  # error output label
        self.sharefolder_text = self.builder.get_object("sharedfolder_text")  # shared directory label
        self.processbox   = self.builder.get_object("processbox")  # box of objects to be displayed after sharing
        self.qrwindow_button = self.builder.get_object("qrwindow_button")  # qr code window
        self.description  = self.builder.get_object("description")  # description label
        self.password_box = self.builder.get_object("password_box")  # password box
        self.aboutbtn     = self.builder.get_object("aboutbtn")  # about dialog button

        # About Window
        self.about_dialog = self.builder.get_object("about_dialog")  # about screen

        # QR Code Window
        self.qrcode_window  = self.builder.get_object("qrcode_window")  # qr code screen
        self.qrwindow_close = self.builder.get_object("qrwindow_close") # qr code window close button
        self.qr_image = self.builder.get_object("qr_image")  # qr code image
        # --------------


        # -------Signals-------
        # Main Window
        self.mainwindow.connect("destroy", self._on_destroy)
        self.share_button.connect("clicked", self._on_share_clicked)
        self.stopshare.connect("clicked", self._on_stop_clicked)
        self.aboutbtn.connect("clicked", self._on_aboutdialog)

        # QR Code Window
        self.qrwindow_button.connect("clicked", self._on_qrwindow)
        self.qrwindow_close.connect("clicked", self._on_qrwindow_close)
        # --------------

        # Önce pencereyi göster, SONRA başlangıç görünümünü ayarla
        # (show_all'dan önce hide() çağırmak işe yaramaz)
        self.mainwindow.show_all()
        self._set_initial_state()

    # ------------------------------------------------------------------
    # Durum yönetimi
    # ------------------------------------------------------------------

    # Uygulama ilk açıldığında / paylaşım durduğunda görünüm
    def _set_initial_state(self):
        self.directory.show()
        self.share_button.show()
        self.processbox.hide()
        self.message.hide()
        self.stopshare.hide()
        self.error_label.hide()
        self.qrwindow_button.hide()

    def _set_sharing_state(self, ip: str, sharedfolder: str):
        # Paylaşım başladığında görünüm
        self.directory.hide()
        self.share_button.hide()
        self.error_label.hide()
        self.password_box.hide()

        self.processbox.show()
        self.message.set_uri(f"http://{ip}:9339")  # linkbutton url
        self.message.set_label(f"http://{ip}:9339")  # linkbutton label

        self.ipaddr = f"http://{ip}:9339"
        self.description.set_label(_("🟢  Open your browser on your other device connected to the same network\n🌎  Enter the following address exactly as it is into the browser that opens:"))
        self.sharefolder_text.set_text(_("Shared folder:")+sharedfolder)
        self.message.show()
        self.stopshare.show()
        self.qrwindow_button.show()
        self.password_box.show()

    # ------------------------------------------------------------------
    # Functions triggered by signals

    # share process
    def _on_share_clicked(self, widget):
        raw_password = self.password_box.get_text()
        if len(raw_password) == 0:
          self.error_label.show()
          self.error_label.set_label(_("For security purposes, you will first need to enter a password.\nYou will use this password to access the interface."))
          return False

        folder_path = self.directory.get_filename()
        iface, host_ip = find_active_interface()

        env = os.environ.copy()
        env["MOD"] = folder_path

        if host_ip == "127.0.0.1":
          self.error_label.show()
          self.error_label.set_label(_("Connect to a network and try again !"))
          return False
        else:
          password_bytes = raw_password.encode('utf-8')  # convert string password to bytes
          salt = bcrypt.gensalt()  # generate a secure random salt (Default work factor is 12)
          hashed_password = bcrypt.hashpw(password_bytes, salt)  # hash the password
          # write hash password
          tmpfile = open(self.passhash_file, "wb")
          tmpfile.write(hashed_password)
          tmpfile.close()

          self._set_sharing_state(host_ip, folder_path)

        self.flask_process = subprocess.Popen(
            ["gunicorn", "--chdir", "/usr/share/local-fileshare/src", "-b", host_ip+":9339", "fileserver:app"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    # stop process
    def _on_stop_clicked(self, widget):
        if self.flask_process and self.flask_process.poll() is None:
            self.flask_process.terminate()
            os.remove(self.passhash_file)  # remove tmp hash info file
            try:
                self.flask_process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.flask_process.kill()
        self.flask_process = None
        self._set_initial_state()

    # about screen
    def _on_aboutdialog(self, widget):
      self.about_dialog.run()
      self.about_dialog.hide()
      return

    # qr code window show
    def _on_qrwindow(self, widget):
      self.create_qrcode()
      self.qr_image.set_from_file("/tmp/qrcode.png")
      self.qrcode_window.show_all()
      return

    # qr code window close
    def _on_qrwindow_close(self, widget):
      self.qrcode_window.hide()
      os.remove("/tmp/qrcode.png")
      return

    def _on_destroy(self, widget):
        self._on_stop_clicked(None)
        Gtk.main_quit()


    # ----- other functions -----
    # qr code create
    def create_qrcode(self):
      qrcode = segno.make_qr(self.ipaddr)
      qrcode.save(
        f"/tmp/qrcode.png",
        scale=10,
        light="lightblue",
        dark="darkblue",
        data_dark="green",
        data_light="lightgreen",
      )


app = LocalFileShare()
Gtk.main()

