# Roman Joost - 2006
# this thingy here is public domain - do whatever you want with it, but
# don't cry if it doesn't work
# 
#    1. Create a directory python_plugins in your vim home and add the script.
#    2. Configure the script by setting the following python trickery up in
#    your $Home/.vimrc (thought thats an example!):
#
#      py << PY
#
#      import vim
#      import sys
#
#      # set the system path to the new directory
#      sys.path.append('/home/roman/.vim/python-plugins')
#
#      # now we can import the python module
#      from utils import *
#
#      # set the variables (you may want to leave alone the cvs_command and
#      # svn_command
#      name = "Roman Joost"
#      email = "<romanofski@gimp.org>"
#      cvs_command = 'cvs update -dP 2>&1 | grep -v "Updating"'
#      svn_command = 'svn st'
#
#      PY
#
#    3. You may want to bind the script to a key like:
#
#      map <F2> :py make_cl_entry(name, email, cvs_command, svn_command)<CR>
#
#    Btw. :help python-vim is worth to look at, if you want to writer your
#    own scripts.
#
# ver. 0.2

import vim
import os
import commands
import re

from datetime import datetime, date
from types import ListType

svn_regexp = re.compile('[GDMA].{,6}(.*)')
cvs_regexp = re.compile('[PAMR].{,1}(.*)')

# copied from vimdb written by Guido Wesdorp
def request_input(p=">> ", evaluate=1):
    command = "input('%s')" % p
    vim.command('call inputsave()')
    inp = vim.eval(command)
    vim.command('call inputrestore()')
    if evaluate:
        inp = eval(inp)
    return inp

class ChangeLog(object):

    def __init__(self, name, email, cvs_command=None, svn_command=None):
        self.name = name 
        self.email = email 
        if cvs_command is not None:
            self.cvs_command = cvs_command
        else:
            self.cvs_command = 'cvs update -dP 2>&1 | grep -v "Updating"'

        if svn_command is not None:
            self.svn_command = svn_command
        else:
            self.svn_command = 'svn st'

    def addChangeLogEntry(self):
        if not self.is_cvs() and not self.is_svn():
            print "You don't seem to be in a CVS or SVN directory."
            return
        
        vim.command('set noexpandtab')
        vim.command('set ts=8')
        vim.command('set enc=utf-8')
        # XXX the print to the buffer is currently reversed once someone
        # figured how this can be done in a better way
        self.print_to_buffer(['',])
        self.print_to_buffer(self.get_changes())
        self.print_to_buffer(["%s  %s  %s" %(self.get_changelog_date(),
                                      self.name,
                                      self.email),
                       ''])

        # set the cursor to the first entry line
        self.set_cursor()

    def get_changes(self):
        """returns a list of updated files"""
        if self.is_cvs():
            print "Note: Getting filelist from CVS. This can take a while."
            command = self.cvs_command
            regexp = cvs_regexp
        elif self.is_svn():
            command = self.svn_command
            regexp = svn_regexp
        else:
            print "You don't seem to be in a CVS or SVN directory"
            return 

        result = []
        changes = commands.getoutput(command).split('\n')
        for line in changes:
            try:
                result.append('\t* ' + regexp.match(line).group(1))
            except AttributeError:
                pass
        return result

    def print_to_buffer(self, strings_to_add):
        """prints string to buffer"""
        cb = vim.current.buffer
        if type(strings_to_add) == ListType:
            cb[0:0] = strings_to_add

    def set_cursor(self):
        """sets the cursor on the end of the first line"""
        # cursor(row, col)
        vim.current.window.cursor = (3, len(vim.current.buffer[3])+1)

    def get_changelog_date(self):
        """returns an iso formatted date (YYYY-MM-DD)"""
        return date.isoformat(datetime.today())

    def is_cvs(self):
        """checks if we're in a directory which has been checked out of an
           CVS repository
        """
        return os.path.exists(os.curdir + '/CVS')

    def is_svn(self):
        """checks if we're in a directory which has been checked out of an
           SVN repository
        """
        return os.path.exists(os.curdir + '/.svn')

def make_cl_entry(name, 
                  email, 
                  cvs_command=None,
                  svn_command=None):
    mail_addr = request_input('Enter your email or leave default: ', 0)
    if mail_addr:
        email = "<%s>" %mail_addr
    cl = ChangeLog(name, email, cvs_command, svn_command)
    cl.addChangeLogEntry()
