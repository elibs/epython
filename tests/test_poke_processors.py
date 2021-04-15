# -*- coding: utf-8 -*-
"""
Description:
    Tests around Poke processors

Author:
    Ray

Date:
    4/15/21
"""

from requests import Response
from epython.poke.processors import PokeResponse


def test_poke_response():
    """ Simple test that verifies PokeResponse has the same attributes as a requests.Response """

    rsp = Response()
    poke_rsp = PokeResponse(rsp)

    for key, val in rsp.__dict__.items():
        poke_rsp.__dict__[key] == val
