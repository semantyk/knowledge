# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# # `.gitignore`
# @organization: Semantyk
# @project: knowledge
#
# @file: This file is used to generate random fragment identifiers for URIs.
#
# @created: Nov 27, 2024
# @modified: Nov 27,2024
#
# @author: Semantyk Team
# @maintainer: Daniel Bakas <https://id.danielbakas.com>
#
# @copyright: Copyright © Semantyk 2024. All rights reserved.
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

import random
import re
import string
import uuid


def main():
    f = open("fragments.txt", "a")
    for _ in range(10000):
        identifier = uuid.uuid4().hex
        identifier = random.choice(string.ascii_letters[0:6]) + identifier[1:8] + '_' + identifier[8:12] + '_' + \
            identifier[12:16] + '_' + identifier[16:20] + \
            '_' + identifier[20:] + '\n'
        f.write(identifier)
    f.close()


main()
