Title: Case sensitive MySQL on OS X
Date: 2016-04-30 11:30:00
Modified: 2016-04-30 11:30:00
Category: MySQL, OSX

## Why

I've recently moved from Arch Linux to an OS X desktop, and one of my projects, powered by MySQL, broke when doing an atomic rename of a table (`RENAME TABLE snapshot TO snapshot_old, snapshot_new TO snapshot`) with a cryptic error of "Table already exists". No it doesn't.

Apparently the HFS filesystem on OS X is case-sensitive _internally_, but exposes a case-insensitive interface to userland programs, by default. And the MySQL support story of almost-case-sensitive file systems is sad.

It is possible to create a case-sensitive volume in which to store the MySQL datafiles and avoid random "Table already exists" errors.

**Note:** I've been on OS X for a couple of weeks now, there's probably a better way to do it, please let me know.

## What

I'm actually using MariaDB installed from Homebrew, it is 100% compatible with MySQL and unless you need support from Oracle, I encourage you to switch to it. These instructions should (not tested) work with upstream MySQL.

## How

Like on Linux, on OS X it is possible to create a filesystem (or volume), format and mount it.
First, dump all your databases. We'll be recreating the data directory from scratch.

    mysqldump -u root --all-databases > backup.sql
    mysql.server stop

Now, let's create an empty case-sensitive volume and mount it in place of the default data directory at `/usr/local/var/mysql`. We'll create a sparse 20GB volume, which will grow incrementally as data is written to it.

    cd /usr/local/var
    mv mysql mysql_backup
    hdiutil create -size 20g -type SPARSEBUNDLE -fs JHFS+X -volname mysql mysql
    hdiutil attach -nobrowse -mountpoint mysql mysql.sparsebundle/

Start MySQL, make sure everything is OK, and load the dump.

    mysql_install_db
    mysql.server start
    mysql -u root < backup.sql

That's it. But we want the volume to be mounted automatically at boot. Let's create a _launch daemon_, at `/Library/LaunchDaemons/cc.combo.mysql-sparsebundle.plist`, with the following contents:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
          <key>RunAtLoad</key>
          <true/>
          <key>Label</key>
          <string>cc.combo.mysql-sparsebundle</string>
          <key>ProgramArguments</key>
          <array>
                    <string>hdiutil</string>
                    <string>attach</string>
                    <string>-nobrowse</string>
                    <string>-mountpoint</string>
                    <string>/usr/local/var/mysql</string>
                    <string>/usr/local/var/mysql.sparsebundle</string>
          </array>
</dict>
</plist>
```

Let's fix the permissions and load it into launchd.

    sudo chown root:wheel /Library/LaunchDaemons/cc.combo.mysql-sparsebundle.plist
    launchctl load -w /Library/LaunchDaemons/cc.combo.mysql-sparsebundle.plist

Your MySQL installation should now behave exactly as if it were installed on a Linux server.
