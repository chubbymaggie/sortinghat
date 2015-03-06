#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2014-2015 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors:
#     Santiago Dueñas <sduenas@bitergia.com>
#

import sys
import unittest

if not '..' in sys.path:
    sys.path.insert(0, '..')

from sortinghat.db.model import UniqueIdentity, Identity
from sortinghat.matching.email_name import EmailNameMatcher


class TestEmailNameMatcher(unittest.TestCase):

    def test_match(self):
        """Test match method"""

        # Let's define some identities first
        jsmith = UniqueIdentity(uuid='jsmith')
        jsmith.identities = [Identity(name='John Smith', email='jsmith@example.com', source='scm'),
                             Identity(name='John Smith', source='scm'),
                             Identity(username='jsmith', source='scm'),
                             Identity(email='', source='scm')]

        john_smith = UniqueIdentity(uuid='js')
        john_smith.identities = [Identity(name='J. Smith', username='john_smith', source='scm'),
                                 Identity(username='john_smith', source='scm'),
                                 Identity(name='Smith. J', source='mls'),
                                 Identity(name='Smith. J', email='JSmith@example.com', source='mls')]

        jsmith_alt = UniqueIdentity(uuid='J. Smith')
        jsmith_alt.identities = [Identity(name='J. Smith', username='john_smith', source='alt'),
                                 Identity(name='John Smith', username='jsmith', source='alt'),
                                 Identity(email='', source='alt'),
                                 Identity(email='jsmith', source='alt')]

        jsmith_not_email = UniqueIdentity(uuid='John Smith')
        jsmith_not_email.identities = [Identity(email='jsmith', source='mls')]

        jrae = UniqueIdentity(uuid='jrae')
        jrae.identities = [Identity(name='Jane Rae', source='scm'),
                           Identity(name='Jane Rae Doe', email='jane.rae@example.net', source='mls')]

        jrae_doe = UniqueIdentity(uuid='jraedoe')
        jrae_doe.identities = [Identity(name='Jane Rae Doe', email='jrae@example.com', source='mls'),
                               Identity(name='jrae', source='scm')]

        jrae_no_name = UniqueIdentity(uuid='Jane Rae')
        jrae_no_name.identities = [Identity(name='jrae', source='scm')]

        # Tests
        matcher = EmailNameMatcher()

        # First two unique identities must match
        result = matcher.match(jsmith, john_smith)
        self.assertEqual(result, True)

        result = matcher.match(john_smith, jsmith)
        self.assertEqual(result, True)

        # Comparing with the third only the first one
        # produces a match because of "John Smith" name
        result = matcher.match(jsmith, jsmith_alt)
        self.assertEqual(result, True)

        result = matcher.match(jsmith_alt, jsmith)
        self.assertEqual(result, True)

        result = matcher.match(john_smith, jsmith_alt)
        self.assertEqual(result, False)

        result = matcher.match(jsmith_alt, john_smith)
        self.assertEqual(result, False)

        # Jane Rae matches Jane Rae Doe because they share
        # the same name "Jane Rae Doe"
        result = matcher.match(jrae, jrae_doe)
        self.assertEqual(result, True)

        result = matcher.match(jrae, jrae_doe)
        self.assertEqual(result, True)

        # No match with Jane Rae
        result = matcher.match(jsmith, jrae)
        self.assertEqual(result, False)

        result = matcher.match(jsmith, jrae_doe)
        self.assertEqual(result, False)

        result = matcher.match(john_smith, jrae)
        self.assertEqual(result, False)

        result = matcher.match(john_smith, jrae_doe)
        self.assertEqual(result, False)

        result = matcher.match(jsmith_alt, jrae)
        self.assertEqual(result, False)

        result = matcher.match(jsmith_alt, jrae_doe)
        self.assertEqual(result, False)

        # This two unique identities have the same email address
        # but due to 'jsmith' is not a valid email address, they
        # do not match
        result = matcher.match(jsmith_alt, jsmith_not_email)
        self.assertEqual(result, False)

        # This two do not match although they share the same name.
        # In this case the name is invalid because is not formed
        # like "firstname lastname"
        result = matcher.match(jrae_doe, jrae_no_name)
        self.assertEqual(result, False)

    def test_match_same_identity(self):
        """Test whether there is a match comparing the same identity"""

        uid = UniqueIdentity(uuid='John Smith')

        matcher = EmailNameMatcher()
        result = matcher.match(uid, uid)

        self.assertEqual(result, True)

    def test_match_same_uuid(self):
        """Test if there is a match when compares identities with the same UUID"""

        uid1 = UniqueIdentity(uuid='John Smith')
        uid2 = UniqueIdentity(uuid='John Smith')

        matcher = EmailNameMatcher()

        result = matcher.match(uid1, uid2)
        self.assertEqual(result, True)

        result = matcher.match(uid2, uid1)
        self.assertEqual(result, True)

    def test_identities_instances(self):
        """Test whether it raises an error when ids are not UniqueIdentities"""

        uid = UniqueIdentity(uuid='John Smith')

        matcher = EmailNameMatcher()

        self.assertRaises(ValueError, matcher.match, 'John Smith', uid)
        self.assertRaises(ValueError, matcher.match, uid, 'John Smith')
        self.assertRaises(ValueError, matcher.match, None, uid)
        self.assertRaises(ValueError, matcher.match, uid, None)
        self.assertRaises(ValueError, matcher.match, 'John Smith', 'John Doe')


if __name__ == "__main__":
    unittest.main()
