
OVERVIEW
This package is ONLY for IronPython v2.7.

It is intended to make it easy to connect to a Sense/Net CMS
instance, test queries, create content, and build simple programs.


INSTALLATION
You have to install this package to your IronPython instance by 
calling IronPython. For example, if IronPython is found in the 
install path shown below, installation coud be done as follows:

IronPython Install Path
=======================
C:\Python\IronPython27

Unzip the Package
=================
unzip C:\Users\Hackfest\Downloads\pysensenet-0.1.1.zip
cd C:\Users\Hackfest\Downloads\pysensenet-0.1.1

Install Using IronPython
========================
C:\Python\IronPython27\ipy64.exe setup.py install


USAGE
Using the package involves three steps:
1. Locate the Sense/Net DLLs. Edit the websitepath
   variable in config.py to point the path where the
   Sense/Net website is located.
   Optionally edit the referencepath variable. By default 
   this uses the "bin" folder beneath the websitepath.
2. Import pysensenet
   >>> import pysensenet
3. Connect to SenseNet. To do this, the package must
   find the "web.config" file for your SenseNet instance.
   It looks first in the current directory, and then
   in the package installation directory, and finally
   in the websitepath directory. If it is not found in
   any of these locations it gracefully fails and tells 
   you how to resolve the problem.

Although not required, it may be helpful to import the 
PySenseNet class separately. 


SAMPLE SESSION
C:\Python\IronPython27\ipy64.exe

IronPython 2.7.4 (2.7.0.40) on .NET 4.0.30319.34014 (64-bit)
Type "help", "copyright", "credits" or "license" for more information.
>>> import pysensenet
Validated Sense/Net referencepath.
referencepath=C:\Projects\Aztech\Source\AztechWeb\bin
>>> sn = pysensenet.PySenseNet()
Connecting to SenseNet...
Connected to SenseNet v6.3.1.6838
>>>
>>> sn.version()
'6.3.1.6838'
>>>
>>> path = '/Root/Sites/Default_Site/workspaces'
>>> wsfolders = sn.inTreeAndTypeIs(path, 'folder')
>>> wsfolders.Count
71
>>>


Hopefully this Python package makes you more productive
and gives you more free time.


--Thane Plummer
