#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess

from setuptools import setup, find_packages


def create_mo_files():
    podir = "po"
    mo = []
    for po in os.listdir(podir):
        if po.endswith(".po"):
            os.makedirs("{}/{}/LC_MESSAGES".format(podir, po.split(".po")[0]), exist_ok=True)
            mo_file = "{}/{}/LC_MESSAGES/{}".format(podir, po.split(".po")[0], "pardus-fileshare.mo")
            msgfmt_cmd = 'msgfmt {} -o {}'.format(podir + "/" + po, mo_file)
            subprocess.call(msgfmt_cmd, shell=True)
            mo.append(("/usr/share/locale/" + po.split(".po")[0] + "/LC_MESSAGES",
                       ["po/" + po.split(".po")[0] + "/LC_MESSAGES/pardus-fileshare.mo"]))
    return mo


changelog = "debian/changelog"
if os.path.exists(changelog):
    head = open(changelog).readline()
    try:
        version = head.split("(")[1].split(")")[0]
    except:
        print("debian/changelog format is wrong for get version")
        version = "0.0.1"
    f = open("src/__version__", "w")
    f.write(version)
    f.close()

data_files = [
    ("/usr/bin", ["pardus-fileshare"]),

    ("/usr/share/applications",
     ["tr.org.pardus.fileshare.desktop"]),

    ("/usr/share/pardus/pardus-fileshare/ui",
     ["ui/MainWindow.glade"]),

    ("/usr/share/pardus/pardus-fileshare/src",
     ["src/main.py",
      "src/fileshare.py",
      "src/network.py"]),

    ("/usr/share/pardus/pardus-fileshare/src/templates", ["src/templates/index.html"]),

    ("/usr/share/pardus/pardus-fileshare/src/icons",
     ["src/icons/computer.png",
      "src/icons/csv.png",
      "src/icons/deb.png",
      "src/icons/docx.png",
      "src/icons/folder.png",
      "src/icons/jpg.png",
      "src/icons/mp3.png",
      "src/icons/mp4.png",
      "src/icons/pardus.png",
      "src/icons/pdf.png",
      "src/icons/png.png",
      "src/icons/pptx.png",
      "src/icons/svg.png",
      "src/icons/txt.png",
      "src/icons/unknown.png",
      "src/icons/xlsx.png",
      "src/icons/zip.png"]),

    ("/usr/share/icons/hicolor/scalable/apps/",
     ["pardus-fileshare.png"])
] + create_mo_files()

setup(
    name="pardus-fileshare",
    version=version,
    packages=find_packages(),
    scripts=["pardus-fileshare"],
    install_requires=["PyGObject"],
    data_files=data_files,
    author="Heydar Ismayilli",
    author_email="heyderismayilli092@gmail.com",
    description="Redshift based night light application",
    license="GPLv3",
    keywords="pardus-fileshare, fileshare, share",
    url="https://github.com/heyderismayilli092/pardus-fileshare",
)
