#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import os
import socket
import subprocess

GLADE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui/MainGlade.glade")

# Flask uygulamasının yolu — kendi flask script'inin adını buraya yaz
FLASK_APP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")


def get_local_ip():
    """Makinenin yerel IP adresini döndürür."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


class PardusFileShare:
    def __init__(self):
        self.flask_process = None

        self.builder = Gtk.Builder()
        self.builder.add_from_file(GLADE_FILE)

        # Widget referansları
        self.mainwindow   = self.builder.get_object("mainwindow")
        self.direntry      = self.builder.get_object("directory_entry")
        self.share_button = self.builder.get_object("share_button")
        self.stopshare    = self.builder.get_object("stopshare")
        self.message      = self.builder.get_object("message")
        self.processbox   = self.builder.get_object("processbox")
        self.error_dialog = self.builder.get_object("directory_check")

        # Referans kontrolü — None gelirse sebebini hemen anlarsın
        widgets = {
            "mainwindow":   self.mainwindow,
            "directory_entry":      self.direntry,
            "share_button": self.share_button,
            "stopshare":    self.stopshare,
            "message":      self.message,
            "processbox":   self.processbox,
            "error_dialog": self.error_dialog,
        }
        for name, obj in widgets.items():
            if obj is None:
                raise RuntimeError(
                    f"Glade'den '{name}' widget'ı yüklenemedi. "
                    f"Glade dosyasındaki id ile eşleştiğinden emin ol."
                )

        # Sinyaller
        self.mainwindow.connect("destroy", self._on_destroy)
        self.share_button.connect("clicked", self._on_share_clicked)
        self.stopshare.connect("clicked", self._on_stop_clicked)
        self.error_dialog.connect("response", lambda d, r: d.hide())

        # Önce pencereyi göster, SONRA başlangıç görünümünü ayarla
        # (show_all'dan önce hide() çağırmak işe yaramaz)
        self.mainwindow.show_all()
        self._set_initial_state()

    # ------------------------------------------------------------------
    # Durum yönetimi
    # ------------------------------------------------------------------

    def _set_initial_state(self):
        """Uygulama ilk açıldığında / paylaşım durduğunda görünüm."""
        self.direntry.set_placeholder_text("Klasör yolunu girin:")
        self.direntry.set_text("")
        self.direntry.show()
        self.share_button.show()
        """Paylaşım başladığında görünüm."""

        self.processbox.hide()
        self.message.hide()
        self.stopshare.hide()

    def _set_sharing_state(self, ip: str, port: int = 9339):
        """Paylaşım başladığında görünüm."""
        self.direntry.hide()
        self.share_button.hide()

        self.processbox.show()
        self.message.set_uri(f"http://{ip}:{port}")  # linkbutton url
        self.message.set_label(f"http://{ip}:{port}")  # linkbutton label
        self.message.show()
        self.stopshare.show()

    # ------------------------------------------------------------------
    # Sinyal işleyicileri
    # ------------------------------------------------------------------

    def _on_share_clicked(self, widget):
        folder_path = self.direntry.get_text().strip()

        if not folder_path or not os.path.isdir(folder_path):
            self.error_dialog.run()
            self.error_dialog.hide()
            return

        env = os.environ.copy()
        env["SHARE_FOLDER"] = folder_path

        try:
            self.flask_process = subprocess.Popen(
                ["python3", "fileserver.py", folder_path],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except FileNotFoundError:
            self._show_custom_error("Flask Hatası: Uygulama bulunamadı:")
            return

        ip = get_local_ip()
        self._set_sharing_state(ip)

    def _on_stop_clicked(self, widget):
        if self.flask_process and self.flask_process.poll() is None:
            self.flask_process.terminate()
            try:
                self.flask_process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.flask_process.kill()
        self.flask_process = None
        self._set_initial_state()

    def _on_destroy(self, widget):
        self._on_stop_clicked(None)
        Gtk.main_quit()

    # ------------------------------------------------------------------
    # Yardımcı
    # ------------------------------------------------------------------

    def _show_custom_error(self, title: str, body: str):
        dlg = Gtk.MessageDialog(
            transient_for=self.mainwindow,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.CLOSE,
            text=title,
        )
        dlg.format_secondary_text(body)
        dlg.run()
        dlg.destroy()


if __name__ == "__main__":
    app = PardusFileShare()
    Gtk.main()
