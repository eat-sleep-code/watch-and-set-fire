# Watch and Set Fire
This Python-based service will watch a specific folder.   When new or modified files are detected they will be uploaded to the specified bucket in Firebase Storage.

---
## Getting Started

- Use [raspi-config](https://www.raspberrypi.org/documentation/configuration/raspi-config.md) to:
  - Set up your WiFi connection

## Installation

Installation of the program, as well as any software prerequisites, can be completed with the following two-line install script.

```
wget -q https://raw.githubusercontent.com/eat-sleep-code/watchandsetfire/main/install-watchandsetfire.sh -O ~/install-watchandsetfire.sh
sudo chmod +x ~/install-watchandsetfire.sh && ~/install-watchandsetfire.sh
```

### Setup Your API Key

To use this application, you will need to:
+ Provision and download your `firebase_admin` API key from the [Google Cloud Platform Console](https://console.cloud.google.com/iam-admin/serviceaccounts)
+ Rename the downloaded file to `firebase-key.json` and place the file within the `\home\pi\watchandsetfire` directory

---

## Usage
```
watchandsetfire <options>
```

### Options

+ _--interval_ : Set the timelapse interval    *(default: 10)*
+ _--path'_ : Set the path that will be watched for changes    *(required)*
+ _--recursive_ : Set whether sub directories will also be watched    *(default: True)*
+ _--includePattern_ : Set the pattern of files to watch    *(default: all files are included)*
+ _--ignorePattern_ : Set the pattern of files to be ignored    *(default: no files are ignored)*
+ _--bucket_ : Set the Firebase storage bucket URI    *(required)*
+ _--destination_ : Set the destination within the Firebase storage bucket     *(default: root of the storage bucket)*

---
## Example

The following will watch the *cucumbers* folder for new or modified files.   When detected, they will be uploaded to *example.appspot.com/pickles/[filename].[ext]*
```
watchandsetfire --path '/home/pi/cucumbers' --bucket 'example.appspot.com' --destination 'pickles/'
```
---

## Autostart
Want to start the watch every time you boot your Raspberry Pi?  Here is how!

* Review `/etc/systemd/system/watchandsetfire.service`
   * If you would like to add any of aforementioned options you may do so by editing the service file.
* Run `~/watchandsetfire/install-watchandsetfire.service.sh`

---

:information_source: *This application was developed and tested using Raspberry Pi OS running on Raspberry Pi Zero W, Raspberry Pi 3B+, and Raspberry Pi 4B boards.   Issues may arise if you are using either older hardware or other Linux distributions.*
