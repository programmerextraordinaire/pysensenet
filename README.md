# pysensenet
#### A Python Library for SenseNet (IronPython)

pysensenet is a Python library that provides connections and useful wrappers to the SenseNet framework. It is limited to IronPython 2.7.

The goal of pysensenet is to make interacting with Sense/Net more productive. Sometimes you need to quickly create content, or query and analyze data. Pysensenet aims to make that easy.

For example, you might need to create a long list of nested folders in your Sense/Net repository.

```
>>> import pysensenet
Validated Sense/Net referencepath.
referencepath=C:\Projects\Aztech\Source\AztechWeb\bin
>>> sn = pysensenet.PySenseNet()
Connecting to SenseNet...
Connected to SenseNet v6.3.1.6838
>>> s = "wow this is a very long folder structure"
>>> crazypath = sn.sncombine('/Root', *s.split())
>>> crazypath
'/Root/wow/this/is/a/very/long/folder/structure'
>>> sn.pathexists(crazypath)
False
>>> sn.makefolders(crazypath)
>>> sn.pathexists(crazypath)
True
>>> sn.deleteChildren('/Root/wow/this/is')
>>> sn.pathexists(crazypath)
False
>>> sn.pathexists('/Root/wow/this/is')
True
```
