# -*- coding: utf-8 -*-
"""
Description:
     Post Processors for the Poke module. The intention is to have helper methods that
     speed up the testing of an API.

Author:
    Ray Gomez

Todo:
    * Add callback processors that would help with API validation

Date:
    3/16/21
"""

from requests import Response


class PokeResponse(Response):
    """ A subclassed version of requests.Response, wrapped to help with ease of use."""

    def __init__(self, response):

        # Hacky way to copy the response values
        for k, v in response.__dict__.items():
            self.__dict__[k] = v

##############################################################
# Generic mechanism that allows easy validation of api calls #
##############################################################
