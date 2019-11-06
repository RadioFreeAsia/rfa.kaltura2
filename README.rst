.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

============
rfa.kaltura2
============

For creating video content in Plone CMS while leveraging the Kaltura Video Platform

Features
--------

- Add and Upload videos through the Plone CMS
- Use Kaltura Players for displaying videos
- Use Kaltura as a Video DAM (Digital Asset Manager)
- Syncronize video metadata between Kaltura KMC and Plone
- Plone 5.2 and Python 3 compatable


Examples
--------

Most video content at www.rfa.org is stored on Kaltura but rendered through Plone CMS.
New Videos can be created in Plone and Videos can be treated like any other content type in Plone, yet the storage, transcoding, and html5/flash/js players are configured in Kaltura.

Documentation
-------------

Full documentation for end users can be found in the "docs" folder, and is also available online at http://docs.plone.org/foo/bar


Translations
------------

This product has yet to be translated to any language.


Installation
------------

Install rfa.kaltura2 by adding it to your buildout::

    [buildout]

    ...

    eggs =
        rfa.kaltura2


and then running ``bin/buildout``


Contribute
----------

- Issue Tracker: https://github.com/RadioFreeAsia/rfa.kaltura2/issues
- Source Code: https://github.com/RadioFreeAsia/rfa.kaltura2
- Documentation: https://docs.plone.org/totallymissinghostingdocsatmsorry


Support
-------

If you are having issues, please let us know through the plone community forums.


License
-------

The project is licensed under the GPLv2.
