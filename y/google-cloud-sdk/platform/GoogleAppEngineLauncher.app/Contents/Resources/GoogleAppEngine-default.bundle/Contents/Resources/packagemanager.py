#!/usr/bin/python
#
# Copyright 2008 Google Inc.

"""
There are three packages of Python we need to extract for
dev_appserver.py to work: Django, YAML, and (of course) the
dev_appserver.zip itself.  This script is an attempt at extracting
these packages in a version-independent manner.

This script assumes the current directory contains the packages
(e.g. /Applications/Matchbook.app/Contents/Resources/DevAppServer-1.0.bundle/
       Contents/Resources)

There are no unit tests.  It is expected that changes to the
google_appengine.zip package will make MOST of this obsolete.
(Perhaps --extract and --clean for google_appengine.zip itself will
remain.)

4/1/08: Much already happened; WebOb/Django/YAML now included in
google_appengine.zip.

"""

import os
import sys
import stat
import glob
import posix
import getopt

class Package(object):
  """Base class of noops.  A poackage is a group of python files
  packaged for use in Matchbook.  This group may need extraction and
  cleanup to be useful.  Packages can be queried; i.e. how to extend
  PYTHONPATH to find them."""

  class Problem(Exception):
    """Generic exception for package problems, initialized with a
    filename or globname which choked us."""
    def __init__(self, file):
      self.file = file
    def __str__(self):
      return repr(self.file)

  def FindOneFile(self, globname):
    """Internal method.  If |globname| matches exactly one file,
    return it.  Else raise PackageManager.Problem()."""
    namearray = glob.glob(globname)
    if len(namearray) != 1:
      raise Package.Problem(globname)
    return namearray[0]

  def Extract(self):
    """Extract the package."""
    pass

  def Clean(self):
    """Remove extracted files"""
    pass

  def Query(self):
    """Ask if the package needs to be extracted"""
    return False

  def Path(self):
    """Print a string to add to our PYTHONPATH if relevant."""
    return None


class EggPackage(Package):
  """An egg package (e.g. WebOb-0.8.5-py2.5.egg).  No
  extraction/cleanup needed.  The PYTHONPATH points to the egg
  itself."""

  def __init__(self, eggglob):
    self.filename = self.FindOneFile(eggglob)

  def Path(self):
    return self.filename


class ArchivePackage(Package):
  """An archive (.zip, .tgz, .tar.gz) package.  Extraction et al is needed."""

  def __init__(self, fileglob, pathglob):
    """|fileglob| is a glob.glob() expression for finding the filename
    of the package (e.g. foo*.zip).  |pathglob| is a glob.glob()
    expression for finding a path suitable for PYTHONPATH.  Throws
    Package.Problem if name is unsuitable (e.g. doesn't end with
    a known extension like .zip, or doesn't exist on disk)."""
    self.fileglob = fileglob
    self.pathglob = pathglob
    self.filename = self.FindOneFile(self.fileglob)
    self.rootname = self.GetRootName(self.filename)

  def GetRootName(self, name):
    """Internal routine.  Return the root of the filename of the file
    (no "packaged" extension).
         foo.zip    --> foo
         foo.tar.gz --> foo
         foo.tgz    --> foo"""
    for ext in ('.zip', '.tar.gz', '.tgz'):
      if name.endswith(ext):
        return name[0:-len(ext)]
    raise Package.Problem(name)

  def ExtractCmd(self, filename):
    """Return the extraction command for |filename|.  |filename| is
    expected to be a real filename, not a glob filename."""
    if filename.endswith('.zip'):
      cmd = 'unzip -qq ' + filename + ' ; touch ' + filename.split('.')[0]
    elif filename.endswith('.tar.gz') or filename.endswith('.tgz'):
      cmd = 'tar -mxzf ' + filename
    else:
      raise Package.Problem(name)
    return cmd

  def ExtractedDir(self):
    """Return the directory which contains the extracted package."""
    return self.rootname

  def Extract(self):
    """Extract the package.  Does not check if this is needed or will
    work."""
    cmd = self.ExtractCmd(self.filename)
    if cmd != None:
      os.system(cmd)

  def Clean(self):
    """Cleanup; Remove files from an extracted package if they exist."""
    dir = self.ExtractedDir()
    if os.access(dir, posix.R_OK) == True:
      os.system('rm -rf ' + dir)

  def Query(self):
    """Return True if we need to extract by comparing the timestamp of
  an extracted directory with the package itself, or by checking if it
  exists at all.  If the directory is older than the package or
  doesn't exist, we do need to extract.  Else return False."""
    dir = self.ExtractedDir()
    if os.access(dir, posix.R_OK) == False:
      return True
    if os.stat(dir)[stat.ST_MTIME] < os.stat(self.filename)[stat.ST_MTIME]:
      return True
    return False

  def Path(self):
    """Print a string to add to our PYTHONPATH, or None of none is
    needed."""
    if self.pathglob == None:
      return None
    p = self.FindOneFile(self.pathglob)
    return p;


def PrintUseAndExit():
  print 'Use: '
  print '  [--extract] if anything needs extracting, delete all and extract'
  print '  [--clean]   delete all extracted files'
  print '  [--query]   ask what needs to be extracted'
  print '  [--path]    print the PYTHONPATH we\'ll need for this extraction'
  print '  [--help]    this message'
  sys.exit(2)

def main():
  try:
    # packages = [ArchivePackage('*YAML*.zip', '*YAML*/lib'),
    #             ArchivePackage('Django-*.tar.gz', None),
    #             EggPackage('WebOb-*.egg'),
    #             GAEArchivePackage('dev_appserver.zip', None)]
    packages = []
  except Package.Problem, inst:
    print 'Cannot create package for ' + inst.file
    sys.exit(2)

  try:
    opts, args = getopt.getopt(sys.argv[1:], "ecqhp",
                               ["extract", "clean", "query", "help", "path"])
  except getopt.GetoptError:
    PrintUseAndExit()

  if len(sys.argv) == 1:
    opts = [("-e", "")]

  for o, a in opts:
    if o in ("-e", "--extract"):
      for p in packages:
        if p.Query():
          p.Clean()
          p.Extract()
    if o in ("-c", "--clean"):
      for p in packages:
        p.Clean()
    if o in ("-q", "--query"):
      packs = []
      for p in packages:
        if p.Query():
          packs.append(p.filename)
      if len(packs) > 0:
        print ' '.join(packs)
    if o in ("-p", "--path"):
      paths = []
      for p in packages:
        path = p.Path()
        if path != None:
          paths.append(path)
      print 'PYTHONPATH=' + ':'.join(paths)
    if o in ("-h", "--help"):
      PrintUseAndExit()
  sys.exit(0)

if __name__ == '__main__':
  main()
