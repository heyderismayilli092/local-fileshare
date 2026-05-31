# local-fileshare
Software for Linux operating systems that enables easy browser-based file sharing over a local network among other devices

### Features
1. You can share the folder you want by selecting it from your Linux computer
2. Ability to wirelessly upload and download files from a device connected to the shared folder
3. Quickly access the link by scanning the QR code

### **Dependencies**

This application is developed based on Python3 and GTK+ 3. Dependencies:
```bash
python3-flask
python3-segno
gunicorn
```

Clone the repository
```bash
git clone https://github.com/heyderismayilli092/local-fileshare ~/local-fileshare
```

Run application
```bash
python3 ~/local-fileshare/src/main.py
```

### Build .deb package
```bash
sudo apt install devscripts git-buildpackage
sudo mk-build-deps -ir
gbp buildpackage --git-export-dir=/tmp/build/local-fileshare -us -uc
```

### **Screenshots**

![local-fileshare 1](screenshots/local-fileshare-1.png)
![local-fileshare 2](screenshots/local-fileshare-2.png)
![local-fileshare 3](screenshots/local-fileshare-3.png)
![local-fileshare 4](screenshots/local-fileshare-4.png)
![local-fileshare 5](screenshots/local-fileshare-5.png)


### Phone Screenshot
![local-fileshare 5](screenshots/local-fileshare-6.png)


NOTE: This software was prepared as part of the "Teknofest 2026 Pardus Bug Finding and Suggestion Competition"

