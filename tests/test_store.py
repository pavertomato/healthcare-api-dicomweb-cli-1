# -*- coding: utf-8 -*-
"""Store method tests
"""
import httpretty
import pytest_check as check
from dcmweb import dcmweb


FILE_PATH_CASES = {"./cloudBuild/**.dcm": 3,
                   "./cloudBuild/dcms/*": 1,
                   "./cloudBuild/dcms/1.dcm": 1,
                   "./cloudBuild/dcms/**": 3}


@httpretty.activate
def test_store():
    """files should be uploaded correctly"""
    requests_counter = RequestsCounter()
    httpretty.register_uri(
        httpretty.POST,
        "https://dicom.com/studies",
        body=requests_counter.request_callback
    )

    for multithreading in (True, False):
        dcmweb_cli = dcmweb.Dcmweb("https://dicom.com/", multithreading, None)
        for mask, amount in FILE_PATH_CASES.items():
            dcmweb_cli.store(mask)
            check.equal(requests_counter.requests, amount,\
            "incorrect amount of uploaded files for {} mask in {} mode, should be {}"\
            .format(mask, "parallel" if multithreading else "sequential", amount))
            requests_counter.reset()


class RequestsCounter:
    """Counts requests"""

    def __init__(self):
        self.reset()

    def reset(self):
        """resets counter"""
        self.requests = 0

    def request_callback(self, request, uri, response_headers):
        """Counts requests and checks headers"""
        assert request.headers.get('Content-Type') == 'application/dicom'
        assert uri == "https://dicom.com/studies"
        self.requests += 1
        return [200, response_headers, ""]