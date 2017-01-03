#!/usr/bin/python
# coding:utf8
from __future__ import absolute_import
from __future__ import print_function
import re
import time
import sys
import click
from getpass import getpass
import functools
import paramiko
from .__init__ import __version__
from . import utils
from .utils import getfunctionbyname, failed
from .errors import *
from .forward import Forwarder as forwarder
cli = getfunctionbyname('mycli.main', 'cli')
MyCli = getfunctionbyname('mycli.main', 'MyCli')


def __cli(database, user, host, port, socket, password, dbname,
          version, prompt, logfile, defaults_group_suffix, defaults_file,
          login_path, auto_vertical_output, local_infile, ssl_ca, ssl_capath,
          ssl_cert, ssl_key, ssl_cipher, ssl_verify_server_cert, table, warn,
          execute):

    mycli = MyCli(prompt=prompt, logfile=logfile,
                  defaults_suffix=defaults_group_suffix,
                  defaults_file=defaults_file, login_path=login_path,
                  auto_vertical_output=auto_vertical_output, warn=warn)

    # Choose which ever one has a valid value.
    database = database or dbname

    ssl = {
        'ca': ssl_ca and os.path.expanduser(ssl_ca),
        'cert': ssl_cert and os.path.expanduser(ssl_cert),
        'key': ssl_key and os.path.expanduser(ssl_key),
        'capath': ssl_capath,
        'cipher': ssl_cipher,
        'check_hostname': ssl_verify_server_cert,
    }

    # remove empty ssl options
    ssl = dict((k, v) for (k, v) in ssl.items() if v is not None)
    if database and '://' in database:
        mycli.connect_uri(database, local_infile, ssl)
    else:
        mycli.connect(database, user, password, host, port, socket,
                      local_infile=local_infile, ssl=ssl)

    mycli.logger.debug('Launch Params: \n'
                       '\tdatabase: %r'
                       '\tuser: %r'
                       '\thost: %r'
                       '\tport: %r', database, user, host, port)

    #  --execute argument
    if execute:
        try:
            mycli.run_query(execute, table_format=table)
            exit(0)
        except Exception as e:
            click.secho(str(e), err=True, fg='red')
            exit(1)

    if sys.stdin.isatty():
        mycli.run_cli()
    else:
        stdin = click.get_text_stream('stdin')
        stdin_text = stdin.read()

        try:
            sys.stdin = open('/dev/tty')
        except FileNotFoundError:
            mycli.logger.warning('Unable to open TTY as stdin.')

        if (mycli.destructive_warning and
                confirm_destructive_query(stdin_text) is False):
            exit(0)
        try:
            mycli.run_query(stdin_text, table_format=table)
        except Exception as e:
            click.secho(str(e), err=True, fg='red')
            exit(1)


@click.command()
@click.option('--ssh-host', 'ssh_host', envvar='SSH_HOST', default=None, help='Ssh host of the proxy,spicify this option to indcate use ssh tunnel;if not spicified,use mycli directly')
@click.option('--ssh-port', 'ssh_port', envvar='SSH_PORT', default=22, help='Ssh port of the proxy.')
@click.option('--ssh-user', 'ssh_username', envvar='SSH_USERNAME', default='root', help='Ssh user of the proxy.')
@click.option('--ssh-pkey', 'ssh_pkey', envvar='SSH_PKEY', default=None, help='Ssh pravite key')
@click.option('--ssh-password', 'ssh_password', envvar='SSH_PASSWORD', default=None, help='the password for pravite key or password auth')
@click.option('-h', '--host', envvar='MYSQL_HOST', help='Host address of the database.')
@click.option('-P', '--port', 'port', envvar='MYSQL_TCP_PORT', type=int, help='Port number to use for connection. Honors '
              '$MYSQL_TCP_PORT')
@click.option('-u', '--user', help='User name to connect to the database.')
@click.option('-S', '--socket', 'sock', envvar='MYSQL_UNIX_PORT', help='The socket file to use for connection.')
@click.option('-p', '--password', 'password', envvar='MYSQL_PWD', type=str,
              help='Password to connect to the database')
@click.option('--pass', 'password', envvar='MYSQL_PWD', type=str,
              help='Password to connect to the database')
@click.option('--ssl-ca', help='CA file in PEM format',
              type=click.Path(exists=True))
@click.option('--ssl-capath', help='CA directory')
@click.option('--ssl-cert', help='X509 cert in PEM format',
              type=click.Path(exists=True))
@click.option('--ssl-key', help='X509 key in PEM format',
              type=click.Path(exists=True))
@click.option('--ssl-cipher', help='SSL cipher to use')
@click.option('--ssl-verify-server-cert', is_flag=True,
              help=('Verify server\'s "Common Name" in its cert against '
                    'hostname used when connecting. This option is disabled '
                    'by default'))
@click.option('-v', '--version', is_flag=True, help='Version of smycli.')
@click.option('-D', '--database', 'dbname', help='Database to use.')
@click.option('-R', '--prompt', 'prompt',
              help='Prompt format (Default: "{0}")'.format(
                  MyCli.default_prompt))
@click.option('-l', '--logfile', type=click.File(mode='a', encoding='utf-8'),
              help='Log every query and its results to a file.')
@click.option('--defaults-group-suffix', type=str,
              help='Read config group with the specified suffix.')
@click.option('--defaults-file', type=click.Path(),
              help='Only read default options from the given file')
@click.option('--auto-vertical-output', is_flag=True,
              help='Automatically switch to vertical output mode if the result is wider than the terminal width.')
@click.option('-t', '--table', is_flag=True,
              help='Display batch output in table format.')
@click.option('--warn/--no-warn', default=None,
              help='Warn before running a destructive query.')
@click.option('--local-infile', type=bool,
              help='Enable/disable LOAD DATA LOCAL INFILE.')
@click.option('--login-path', type=str,
              help='Read this path from the login file.')
@click.option('-e', '--execute',  type=str,
              help='Execute query to the database.')
@click.argument('database', default='', nargs=1)
def scli(ssh_host, ssh_port, ssh_username, ssh_pkey, ssh_password, database, user, host, port, sock, password, dbname,
         version, prompt, logfile, defaults_group_suffix, defaults_file,
         login_path, auto_vertical_output, local_infile, ssl_ca, ssl_capath,
         ssl_cert, ssl_key, ssl_cipher, ssl_verify_server_cert, table, warn,
         execute):
    if version:
        print('Version:', __version__)
        sys.exit(0)
    ret = None
    server = None
    # ssh_host = ssh_host or host
    ssh_port = ssh_port or 22
    ssh_username = ssh_username or 'root'
    ssh_password = ssh_password or ''
    host = host or '127.0.0.1'
    port = port or 3306

    if prompt is None:
        prompt = "mysql \u@\h:\d> "
    if prompt.find(r'\h') != -1:
        prompt = prompt.replace('\h', host)
    if ssh_host is not None and (ssh_password is None or not ssh_password.strip()):
        ssh_username=ssh_username or 'root'
        ssh_password = getpass('SSH PASSWORD(%s):' % ssh_username.encode('utf8'))

    if password is None or not password.strip():
        user=user or 'root'
        password = getpass('MYSQL PASSWORD(%s):' % user.encode('utf8'))

    try:
        if ssh_host is not None and not ssh_password.strip() and ssh_pkey is None:
            raise SSHPasswordNotProvided()
        if ssh_host:
            server = forwarder(
                ssh_host=ssh_host,
                ssh_port=ssh_port,
                ssh_username=ssh_username,
                ssh_private_key=ssh_pkey,
                ssh_password=ssh_password,
                local_bind_address=None,
                remote_bind_address=(host, port),
            )
            server.start()
            _, local_bind_port = server.local_address()
            print('****************************')
            print('SMYCLI Version: ' + __version__)
            print('****************************')
            time.sleep(2)
            ret = __cli(database, user, '127.0.0.1', local_bind_port, sock, password, dbname,
                        version, prompt, logfile, defaults_group_suffix, defaults_file,
                        login_path, auto_vertical_output, local_infile, ssl_ca, ssl_capath,
                        ssl_cert, ssl_key, ssl_cipher, ssl_verify_server_cert, table, warn,
                        execute)
        else:
            ret = __cli(database, user, host, port, sock, password, dbname,
                        version, prompt, logfile, defaults_group_suffix, defaults_file,
                        login_path, auto_vertical_output, local_infile, ssl_ca, ssl_capath,
                        ssl_cert, ssl_key, ssl_cipher, ssl_verify_server_cert, table, warn,
                        execute)
    except paramiko.ssh_exception.SSHException, e:

        message = "*** Failed to connect to %s:%d->%s" % (
            host, port, e.message)
        ret = failed(SSHConnectionError(message))
    except Exception, e:
        ret = failed(e)
    finally:
        if isinstance(server, forwarder):
            server.stop()
            del server
    if ret == 1:
        exit(ret)
    return ret

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(scli())
