# Copyright 2018-2024 Lausanne University Hospital and University of Lausanne,
# Switzerland & Contributors

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This module contains pacsifier package information."""

import datetime


__version__ = "1.0.0.dev0"

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
__email__ = "translationalML@gmail.com"
__status__ = "Beta"

__packagename__ = "pacsifier"
__container_name__ = "pacsifier"

__url__ = "https://github.com/TranslationalML/{name}/tree/{version}".format(
    name=__packagename__, version=__version__
)

DOWNLOAD_URL = "https://github.com/TranslationalML/{name}/archive/{ver}.tar.gz".format(
    name=__packagename__, ver=__version__
)

DOCKER_HUB = "TO_BE_COMPLETED_ONCE_IT_IS_DEPLOYED"
