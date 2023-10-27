# Copyright (C) 2018-2023, University Hospital Center and University of Lausanne (UNIL-CHUV)
# and Contributors, All rights reserved.
#  This software is distributed under the open-source Apache 2.0 license.

"""This file contains pacsman package information."""

import datetime


__version__ = "0.3.0"

__current_year__ = datetime.datetime.now().strftime("%Y")

__release_date__ = "DD.MM.{}".format(__current_year__)

__author__ = "Translational Machine Learning Lab"

__copyright__ = (
    "Copyright (C) 2018-{}, ".format(__current_year__)
    + "University Hospital Center and University of Lausanne (UNIL-CHUV) and Contributors, All rights reserved."
)

__credits__ = (
    "Contributors: please check the ``.zenodo.json`` file at the top-level folder"
    "of the repository"
)
__license__ = "Apache 2.0"
__maintainer__ = "Translational Machine Learning Lab"
__email__ = "sebastien.tourbier1@gmail.com"
__status__ = "Beta"

__packagename__ = "pacsman"

__url__ = "https://github.com/TranslationalML/{name}/tree/{version}".format(
    name=__packagename__, version=__version__
)

DOWNLOAD_URL = "https://github.com/TranslationalML/{name}/archive/{ver}.tar.gz".format(
    name=__packagename__, ver=__version__
)

DOCKER_HUB = "TO_BE_COMPLETED_ONCE_IT_IS_DEPLOYED"
