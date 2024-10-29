.. PACSIFIER documentation master file, created by
   sphinx-quickstart on Mon Oct 23 12:16:21 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PACSIFIER's documentation!
=====================================

This radiological PACS data management software is developed by the Translational Machine Learning Lab team at the Lausanne University Hospital and University of Lausanne for use within the hospital, as well as for open-source software distribution.

.. image:: https://img.shields.io/github/v/release/TranslationalML/pacsifier
  :alt: Latest GitHub Release
.. image:: https://img.shields.io/github/release-date/TranslationalML/pacsifier
  :alt: GitHub Release Date


Introduction
-------------

`PACSIFIER` is an open-source tool written in Python and encapsulated in a Docker image to query, retrieve, and edit data  in DICOM format from a radiological PACS server.

Aknowledgment
--------------

If your are using `PACSIFIER` in your work, please acknowledge this software and its dependencies. See :ref:`Citing <citing>` for more details.

License information
--------------------

This software is distributed under the Apache 2 license. See :ref:`license <license>` for more details.

All trademarks referenced herein are property of their respective holders.

Help/Questions
---------------

If you run into any problems or have any code bugs or questions, please create a new `GitHub Issue <https://github.com/TranslationalML/pacsifier/issues>`_.

Eager to contribute?
---------------------

See :ref:`Contributing <contributing>` for more details.

Funding
--------

This project received funding from the Lausanne University Hospital and the Lundin Family Brain Tumour Research Center.

Contents
=========

.. _getting_started:

.. toctree::
   :maxdepth: 2
   :caption: Getting started

   installation

.. _user-docs:

.. toctree::
   :maxdepth: 2
   :caption: User Documentation

   usage

.. _developer-docs:

.. toctree::
   :maxdepth: 2
   :caption: Developer Documentation

   developer

.. _api-doc:

.. toctree::
   :maxdepth: 5
   :caption: API Documentation

   api/generated/modules
   api_cli_subpackage
   api_core_subpackage

.. _about-docs:

.. toctree::
   :maxdepth: 1
   :caption: About PACSIFIER

   license
   citing
   changes
   contributors
   contributing
