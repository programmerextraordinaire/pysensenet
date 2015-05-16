#
# pysensenet.py
#
# by Thane Plummer
#
# Distribution
#    CodePlex: pysensenet.codeplex.com
#    GitHub: github.com/programmerextraordinaire/pysensenet
#
# License: Apache v2.0
#


from __future__ import print_function

import clr
import os
import sys


__title__ = 'pysensenet'
__version__ = '0.1.4'
__build__ = 0x000104
__author__ = 'Thane Plummer'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright (C) 2014 Thane Plummer'



from config import websitepath # Default is r"C:\inetpub\sensenet"
from config import referencepath # Default is r"C:\inetpub\sensenet\bin"

clr.AddReference("System.Configuration")
clr.AddReferenceToFileAndPath(os.path.join(referencepath, "Microsoft.Practices.Unity.dll"))
clr.AddReferenceToFileAndPath(os.path.join(referencepath, "SenseNet.ContentRepository.dll"))
clr.AddReferenceToFileAndPath(os.path.join(referencepath, "SenseNet.CorePortlets.dll"))
clr.AddReferenceToFileAndPath(os.path.join(referencepath, "SenseNet.Messaging.dll"))
clr.AddReferenceToFileAndPath(os.path.join(referencepath, "SenseNet.Portal.dll"))
clr.AddReferenceToFileAndPath(os.path.join(referencepath, "SenseNet.Storage.dll"))
clr.AddReferenceToFileAndPath(os.path.join(referencepath, "SenseNet.Workflow.dll"))
clr.AddReferenceToFileAndPath(os.path.join(referencepath, "SenseNet.Workflow.Definitions.dll"))


import System
from System import Array
from System.Configuration import *
from System.IO import StreamReader
import SenseNet.Search as SNS
import SenseNet.ContentRepository as SNCR
import SenseNet.ContentRepository.Storage as SNCRS
import SenseNet.ContentRepository.Storage.Security as SNCRSS

from system_configuration import ConfigurationProxy



# create configuration proxy/redirection to custom config    
proxy = None
try:
    # Look for web.config file in the following order:
    # - Look in current directory i.e. as shown by os.getcwd()
    # - Look in the pysensenet folder
    # - Look in the websitepath
    import site
    pkgpath = site.getsitepackages()[-1]
    configpath = "web.config"
    if not os.path.isfile(configpath):
        configpath = os.path.join(pkgpath, "pysensenet", configpath)
        if not os.path.isfile(configpath):
            configpath = os.path.join(websitepath, configpath)
    proxy = ConfigurationProxy(configpath)
    proxy.InjectToConfigurationManager()
except SystemError:
    print("Cannot find web.config.")
    print("Please change to the correct path and reimport, or")
    print("specify the full path (including web.config) and run:")
    print(" ")
    print("proxy = pysensenet.ConfigurationProxy(path_to_web.config)")
    print("proxy.InjectToConfigurationManager()")


def snversion():
    fullpath = os.path.join(referencepath, "SenseNet.ContentRepository.dll")
    if os.path.exists(fullpath):
        version = System.Diagnostics.FileVersionInfo.GetVersionInfo(fullpath)
        return version.ProductVersion
    return "unknown version"



# A class instance is used to connect to Sense/Net, so that a user
# could potentially have different simultaneous connections each
# with different configuration values.
class PySenseNet:
    def __init__(self, settings=None, querysettings=None, snpath=None):
        print("Connecting to SenseNet...")
        # Repository settings
        if settings is None:
            settings = SNCR.RepositoryStartSettings()
            settings.StartLuceneManager = True
            settings.StartWorkflowEngine = False
            settings.IndexPath = os.path.join(websitepath, "App_Data")
        self.repository_settings = settings
        # Default query settings
        if querysettings is None:
            querysettings = SNS.QuerySettings()
            querysettings.EnableAutofilters = SNS.FilterStatus.Enabled
            querysettings.EnableLifespanFilter = SNS.FilterStatus.Default
        self.query_settings = querysettings
        if snpath is None:
            snpath = "/Root"
        self.snpath = snpath
        # try to connect
        ss = SNCR.Repository.Start(settings)
        try:
            ss = SNCR.Repository.Start(settings)
            print("Connected to SenseNet v{0}".format(self.version()))
        except:
            print("Failed to connect to SenseNet.")


    def version(self):
        return snversion()


    #-------------- UTILITIES
    def binaryDataFromFile(self, filename):
        """binaryDataFromFile(filename)

        Open the file specified and return a binary data object.

        """
        # Create binary data
        binarydata = SNCRS.BinaryData()
        binarydata.FileName = filename
        sr = StreamReader(filename)
        binarydata.SetStream(sr.BaseStream)
        return binarydata


    def chgsnpath(self, snpath):
        """chgsnpath(snpath)

        Change the snpath (Sense/Net path) for this class instance.
        The snpath can be used as a convenience so that you do not
        have to pass the path into a function.

        Many PySenseNet functions that only require one path variable
        will use the "snpath" variable if the path is not specified.
        Example:
        >>> sn = pysensenet.PySenseNet(snpath='/Root/Sites')
        >>> sn.inTree()  # equivalent to sn.inTree('/Root/Sites')

        """
        if self.pathexists(snpath):
            self.snpath = snpath
        else:
            print("Failed to change snpath. Path does not exist: ", snpath)


    #-------------- WORKING WITH FOLDERS
    def pathexists(self, path):
        """pathexists(path)

        Check to see if a SenseNet node exists for this path.

        """
        node = SNCRS.Node.LoadNode(path)
        return node != None


    def combinepathexists(self, *args):
        """combinepathexists(*args)

        Combine args into a single path and check to see if a SenseNet node exists.

        """
        node = SNCRS.Node.LoadNode(self.sncombine(*args))
        return node != None


    def sncombine(self, *args):
        return SNCR.Storage.RepositoryPath.Combine(*args)


    def makefolder(self, parentpath, name='folder'):
        """makefolder(parentpath, name='folder')

        Make a SenseNet folder under the parentpath.

        """
        if not self.pathexists(parentpath):
            print("Error: parent path does not exist.")
            raise
        parent = SNCRS.Node.LoadNode(parentpath)
        folder = SNCR.Folder(parent)
        if folder is not None:
            folder.Name = name
            try:
                folder.Save()
            except SystemError as err:
                errmsg = " Unable to make folder: " + SNCR.Storage.RepositoryPath.Combine(parentpath, name)
                print(errmsg)
                err.message = err.message + errmsg
                raise


    def makefolders(self, name):
        """makefolders(name)

        Super-makefolder; create a leaf directory and all intermediate ones.
        Works like makefolder, except that any intermediate path segment (not
        just the rightmost) will be created if it does not exist.  This is
        recursive.

        """
        head, tail = os.path.split(name)
        if not tail:
            head, tail = pkgpath.split(head)
        if head and tail and not self.pathexists(head):
            try:
                self.makefolders(head)
            except:
                # be happy if someone already created the path
                if self.pathexists(head):
                    raise
            if tail == name:           
                return
        self.makefolder(head, tail)



    def deleteChildren(self, nodepath, bypassTrash=False):
        """deleteChildren(nodepath)

        Loads the child nodes beneath nodepath and deletes them.

        WARNING: if bypassTrash is set to True, this operation
        permanently deletes Content and cannot be undone.

        """
        # Sanity check
        if not self.pathexists(nodepath):
            return
        nodes = self.inFolder(nodepath)
        for node in nodes:
            node.Delete(bypassTrash)



    def getXml(self, nodepath=None, withChildren=False):
        """getXml(nodepath, withChildren=False)

        Loads the Content at the node path and returns XML STREAM.
        If nodepath is None, the class snpath is used.
        To get a string, call getXmlStr()

        """
        if nodepath is None:
            nodepath = self.snpath
        content = self.createContent(nodepath)
        if content is not None:
            return content.GetXml(withChildren)
        return None


    def getXmlStr(self, nodepath=None, withChildren=False):
        """getXmlStr(nodepath, withChildren=False)

        Loads the Content at the node path and returns XML string.
        If nodepath is None, the class snpath is used.

        """
        stream = self.getXml(nodepath=nodepath, withChildren=withChildren)
        if stream is not None:
            sr = StreamReader(stream, "utf-8")
            return sr.ReadToEnd()
        return None


    def createContent(self, nodepath=None):
        """createContent(nodepath=None)

        Convenience function to get the Content of a node.
        If nodepath is None, the class snpath is used.

        """
        if nodepath is None:
            nodepath = self.snpath
        parent = SNCRS.Node.LoadNode(nodepath)
        if parent is not None:
            return SNCR.Content.Create(parent)
        return None


    def createNewContent(self, name, sntype="GenericContent", parentpath=None):
        """createNewContent(name, sntype="GenericContent", parentpath=None)

        Convenience function to create new Content under a parent node.
        If parentpath is None, the class snpath is used.
        Note that this parameter order differs from Sense/Net, i.e.

            content = SNCR.Content.CreateNew("File", parent, name)

        """
        if parentpath is None:
            parentpath = self.snpath
        parent = SNCRS.Node.LoadNode(parentpath)
        if parent is not None:
            if not self.combinepathexists(parentpath, name):
                content = SNCR.Content.CreateNew(sntype, parent, name)
                content["Name"] = name;
                return content
            else:
                print("Error: file(s) already exists.")
                raise 
        return None


    def loadNode(self, nodepath=None):
        """loadNode(nodepath=None)

        Convenience function to load a Node.
        If nodepath is None, the class snpath is loaded.

        """
        if nodepath is None:
            nodepath = self.snpath
        return SNCRS.Node.LoadNode(nodepath)


    #-------------- QUERIES
    # From the SenseNet.ContentRepository.SafeQueries class

    ## Only SafeQueries will work in this mode.
    #def query(self, **kwargs):
    #    pass

    def _get_query_settings(self, **kwargs):
        qs = self.query_settings
        allowed = ['top', 'reversesort', 'sort', 'skip', 'enableautofilters', 'enablelifespanfilter']
        for k, v in kwargs.items():
            key = k.lower()
            if key not in allowed:
                print("Error: unknown Query Setting. Allowed values are: {0}".format(",".join(allowed)))
                raise
            if key == 'top':
                qs.Top = v
            if key == 'sort' or key == 'reversesort':
                qs.Sort = SNS.SortInfo()
                qs.Sort.FieldName = v
                qs.Reverse = True if key == 'reversesort' else False
            if key == 'skip':
                qs.Skip = v
            if key == 'enableautofilters':
                qs.EnableAutofilters = v
            if key == 'enablelifespanfilter':
                qs.EnableLifespanFilter = v
        return qs


    def allDevices(self):
        results = SNS.ContentQuery.Query(SNCR.SafeQueries.AllDevices, None)
        if results is not None:
            return results.Nodes
        return None


    def aspectExists(self):
        results = SNS.ContentQuery.Query(SNCR.SafeQueries.AspectExists, None)
        return results

    # -------- FOLDERS

    def inFolder(self, path=None, **kwargs):
        """
        inFolder(path=None, **kwargs)

        Returns an iterator of Nodes in the folder of the input path.
        kwargs: top, reversesort, sort, skip, enableautofilters, and enablelifespanfilter. 
        Default QuerySettings are used if kwargs is empty unless overridden in the query.
        Example: 
        sn = pysensenet.PySenseNet()
        mypath = '/Root/Sites/Default_Site/workspaces/Document'
        results = sn.inFolder(mypath)

        If path is None, the class snpath is loaded.

        """
        if path is None:
            path = self.snpath
        qs = self._get_query_settings(**kwargs)
        results = SNS.ContentQuery.Query(SNCR.SafeQueries.InFolder, qs, path)
        if results is not None:
            return results.Nodes
        return None


    def inFolderCountOnly(self, path=None, **kwargs):
        """
        inFolderCountOnly(path=None, **kwargs)

        Returns a count of Nodes in the folder of the input path.
        kwargs: top, reversesort, sort, skip, enableautofilters, and enablelifespanfilter. 
        Default QuerySettings are used if kwargs is empty unless overridden in the query.
        Example: 
        sn = pysensenet.PySenseNet()
        mypath = '/Root/Sites/Default_Site/workspaces/Document'
        count = sn.inFolderCountOnly(mypath)

        If path is None, the class snpath is loaded.

        """
        if path is None:
            path = self.snpath
        qs = self._get_query_settings(**kwargs)
        results = SNS.ContentQuery.Query(SNCR.SafeQueries.InFolderCountOnly, qs, path)
        if results is not None:
            return results.Count
        return None


    def inFolderAndTypeIs(self, path, sntype, **kwargs):
        """
        inFolderAndTypeIs(path, sntype, **kwargs)

        Returns an iterator of Nodes of Content Type in the folder of input path.
        kwargs: top, reversesort, sort, skip, enableautofilters, and enablelifespanfilter. 
        Default QuerySettings are used if kwargs is empty.
        Example: 
        sn = pysensenet.PySenseNet()
        workspaces = sn.inFolderAndTypeIs('/Root', 'workspace', top=10)

        """
        qs = self._get_query_settings(**kwargs)
        results = SNS.ContentQuery.Query(SNCR.SafeQueries.InFolderAndTypeIs, qs, path, sntype)
        if results is not None:
            return results.Nodes
        return None

    
    def inFolderAndTypeIsCountOnly(self, path, sntype, **kwargs):
        """
        inFolderAndTypeIsCountOnly(path, sntype, **kwargs)

        Returns a count of Nodes in the folder of the input path of the given Content Type.
        kwargs: top, reversesort, sort, skip, enableautofilters, and enablelifespanfilter. 
        Default QuerySettings are used if kwargs is empty unless overridden in the query.
        Example: 
        sn = pysensenet.PySenseNet()
        mypath = '/Root/Sites/Default_Site/workspaces'
        count = sn.inFolderAndTypeIsCountOnly(mypath, 'workspace')

        """
        qs = self._get_query_settings(**kwargs)
        results = SNS.ContentQuery.Query(SNCR.SafeQueries.InFolderAndTypeIsCountOnly, qs, path, sntype)
        if results is not None:
            return results.Count
        return None


    # -------- TREES

    def inTree(self, path=None, **kwargs):
        """
        inTree(path=None, **kwargs)

        Returns an iterator of Nodes in the tree of the input path.
        kwargs: top, reversesort, sort, skip, enableautofilters, and enablelifespanfilter. 
        Default QuerySettings are used if kwargs is empty unless overridden in the query.
        Example: 
        sn = pysensenet.PySenseNet()
        mypath = '/Root/Sites/Default_Site/workspaces/Document'
        results = sn.inTree(mypath)

        If path is None, the class snpath is loaded.

        """
        if path is None:
            path = self.snpath
        qs = self._get_query_settings(**kwargs)
        results = SNS.ContentQuery.Query(SNCR.SafeQueries.InTree, qs, path)
        if results is not None:
            return results.Nodes
        return None


    def inTreeCountOnly(self, path=None, **kwargs):
        """
        inTreeCountOnly(path=None, **kwargs)

        Returns a count of Nodes in the tree of the input path.
        kwargs: top, reversesort, sort, skip, enableautofilters, and enablelifespanfilter. 
        Default QuerySettings are used if kwargs is empty unless overridden in the query.
        Example: 
        sn = pysensenet.PySenseNet()
        mypath = '/Root/Sites/Default_Site/workspaces/Document'
        count = sn.inTreeCountOnly(mypath)

        If path is None, the class snpath is loaded.

        """
        if path is None:
            path = self.snpath
        qs = self._get_query_settings(**kwargs)
        results = SNS.ContentQuery.Query(SNCR.SafeQueries.InTreeCountOnly, qs, path)
        if results is not None:
            return results.Count
        return None



    def inTreeOrderByPath(self, path=None, **kwargs):
        """
        inTreeOrderByPath(path=None, **kwargs)

        Returns an iterator of Nodes for the input path and sorted by Path.
        kwargs: top, reversesort, sort, skip, enableautofilters, and enablelifespanfilter. 
        Default QuerySettings are used if kwargs is empty unless overridden in the query.
        Example: 
        sn = pysensenet.PySenseNet()
        mypath = '/Root/Sites/Default_Site/workspaces/Document'
        results = sn.inTreeOrderByPath(mypath)

        If path is None, the class snpath is loaded.

        """
        if path is None:
            path = self.snpath
        qs = self._get_query_settings(**kwargs)
        results = SNS.ContentQuery.Query(SNCR.SafeQueries.InTreeOrderByPath, qs, path)
        if results is not None:
            return results.Nodes
        return None


    def inTreeAndTypeIs(self, path, sntype, **kwargs):
        """
        inTreeAndTypeIs(path, sntype, **kwargs)

        Returns an iterator of Nodes for the input path and Content Type.
        kwargs: top, reversesort, sort, skip, enableautofilters, and enablelifespanfilter. 
        Default QuerySettings are used if kwargs is empty.
        Example: 
        sn = pysensenet.PySenseNet()
        workspaces = sn.inTreeAndTypeIs('/Root', 'workspace', top=10)

        """
        qs = self._get_query_settings(**kwargs)
        results = SNS.ContentQuery.Query(SNCR.SafeQueries.InTreeAndTypeIs, qs, path, sntype)
        if results is not None:
            return results.Nodes
        return None


    def inTreeAndTypeIsCountOnly(self, path, sntype, **kwargs):
        """
        inTreeAndTypeIsCountOnly(path, sntype, **kwargs)

        Returns a count of Nodes in the tree of the input path of the given Content Type.
        kwargs: top, reversesort, sort, skip, enableautofilters, and enablelifespanfilter. 
        Default QuerySettings are used if kwargs is empty unless overridden in the query.
        Example: 
        sn = pysensenet.PySenseNet()
        mypath = '/Root/Sites/Default_Site/workspaces'
        count = sn.inTreeAndTypeIsCountOnly(mypath, 'workspace')

        """
        qs = self._get_query_settings(**kwargs)
        results = SNS.ContentQuery.Query(SNCR.SafeQueries.InTreeAndTypeIsCountOnly, qs, path, sntype)
        if results is not None:
            return results.Count
        return None


    def inTreeAndTypeIsAndName(self, path, sntype, name, **kwargs):
        """
        inTreeAndTypeIsAndName(path, sntype, name, **kwargs)

        Returns an iterator of Nodes for the input path and Content Type and name.
        kwargs: top, reversesort, sort, skip, enableautofilters, and enablelifespanfilter. 
        Default QuerySettings are used if kwargs is empty.
        Example: 
        sn = pysensenet.PySenseNet()
        workspaces = sn.inTreeAndTypeIsAndName('/Root', 'workspace', top=10)

        """
        qs = self._get_query_settings(**kwargs)
        results = SNS.ContentQuery.Query(SNCR.SafeQueries.InTreeAndTypeIsAndName, qs, path, sntype, name)
        if results is not None:
            return results.Nodes
        return None


    def typeIsAndName(self, sntype, name, **kwargs):
        """
        typeIsAndName(sntype, name, **kwargs)

        Returns an iterator of Nodes for the Content Type and name entered.
        kwargs: top, reversesort, sort, skip, enableautofilters, and enablelifespanfilter. 
        Default QuerySettings are used if kwargs is empty.
        Example: 
        sn = pysensenet.PySenseNet()
        londonws = sn.typeIsAndName('workspace', 'londondocumentworkspace')

        """
        qs = self._get_query_settings(**kwargs)
        results = SNS.ContentQuery.Query(SNCR.SafeQueries.TypeIsAndName, qs, sntype, name)
        if results is not None:
            return results.Nodes
        return None

