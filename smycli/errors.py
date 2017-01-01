from __future__ import print_function


class SSHConnectionError(Exception):
    '''connection error via ssh'''
    pass


class SSHConnectionTimeout(Exception):
    '''connection timeout error'''
    message = "*** Timeout occured while open ssh tunnel"


class SSHPasswordNotProvided(Exception):
    '''ssh password not provided error'''
    message = "*** SSH Password Must be Provided when ssh key not provided "
