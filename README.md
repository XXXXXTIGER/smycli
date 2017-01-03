# smycli

Base on the cli tool *mycli* (HomePage: [http://mycli.net](http://mycli.net) ),
add additional secure manner via proxy



Quick Start
-----------

If you already know how to install python packages, then you can install it via pip:

You might need sudo on linux.

```
$ sudo pip install smycli
```

### Usage

    $ smycli --help
    Usage: smycli [OPTIONS] [DATABASE]

    Options:
      --ssh-host TEXT               Ssh host of the proxy,spicify this option to
                                    indcate use ssh tunnel;if not spicified,use
                                    mycli directly
      --ssh-port INTEGER            Ssh port of the proxy.
      --ssh-user TEXT               Ssh user of the proxy.
      --ssh-pkey TEXT               Ssh pravite key
      --ssh-password TEXT           the password for pravite key or password auth
      -h, --host TEXT               Host address of the database.
      -P, --port INTEGER            Port number to use for connection. Honors
                                    $MYSQL_TCP_PORT
      -u, --user TEXT               User name to connect to the database.
      -S, --socket TEXT             The socket file to use for connection.
      -p, --password TEXT           Password to connect to the database
      --pass TEXT                   Password to connect to the database
      --ssl-ca PATH                 CA file in PEM format
      --ssl-capath TEXT             CA directory
      --ssl-cert PATH               X509 cert in PEM format
      --ssl-key PATH                X509 key in PEM format
      --ssl-cipher TEXT             SSL cipher to use
      --ssl-verify-server-cert      Verify server's "Common Name" in its cert
                                    against hostname used when connecting. This
                                    option is disabled by default
      -v, --version                 Version of mycli.
      -D, --database TEXT           Database to use.
      -R, --prompt TEXT             Prompt format (Default: "\t \u@\h:\d> ")
      -l, --logfile FILENAME        Log every query and its results to a file.
      --defaults-group-suffix TEXT  Read config group with the specified suffix.
      --defaults-file PATH          Only read default options from the given file
      --auto-vertical-output        Automatically switch to vertical output mode
                                    if the result is wider than the terminal
                                    width.
      -t, --table                   Display batch output in table format.
      --warn / --no-warn            Warn before running a destructive query.
      --local-infile BOOLEAN        Enable/disable LOAD DATA LOCAL INFILE.
      --login-path TEXT             Read this path from the login file.
      -e, --execute TEXT            Execute query to the database.
      --help                        Show this message and exit.

### Examples
    #connect mydb on localhost user mycli directly
    $ smycli -h localhost -u root mydb 

    #connect mydb on dbhost but via the tunnel "localhost->sshhost" which is encrypted,then "sshhost->dbhost" is not encrypted.
    $ smycli -u admin -h dbhost -P 3306 --ssh-user=root --ssh-host sshhost  mydb 

    #connect mydb on dbhost but via the tunnel "localhost->dbhost" which is encrypted on the whole traffic.
    $ smycli -u admin -h dbhost -P 3306 --ssh-user=root --ssh-host dbhost   mydb 

Features
--------

except the excillent features of cli tool `mycli`,smycli has additional ones:
* encrypt the traffic data via ssh
* via the "proxy node" ,connect to DB hosts from anywhere, safely

Copyright:
--------------
All rights of `mycli` is reserved BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS,the license is [here](https://github.com/dbcli/mycli/blob/master/LICENSE.txt),and other rights is reserved by the BY THE COPYRIGHT HOLDERS .
All rights of `smycli` is reserved .
Email:xgtiger@163.com

## Detailed Install Instructions:
you can install mycli as follows:

```
$ sudo pip install mycli
```

### Thanks:
Thanks to all the ones who made this excellent tool `mycli`.

### Compatibility

Tests have been run on OS X and Linux.

THIS HAS NOT BEEN TESTED IN WINDOWS, but the libraries used in this app are Windows compatible. This means it should work without any modifications. 


