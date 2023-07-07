#!/usr/bin/env python3
###################################################################################################
# MIT License
#
# Copyright (c) 2023 The Water Institute
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Author: Zach Cobell
# Contact: zcobell@thewaterinstitute.org
# Organization: The Water Institute
#
###################################################################################################

class Spyder:
    def __init__(self, url):
        """
        Initilaizes a spyder object which acts as a crawler
        through posted NOAA folders of grib/grib2 data
        """
        self.__url = url

    def url(self):
        return self.__url

    def filelist(self):
        """
        Generates the file list at the given url
        :return: list of files
        """
        import requests
        from bs4 import BeautifulSoup

        try:
            r = requests.get(self.__url, timeout=30)
            if r.ok:
                response_text = r.text
            else:
                print(
                    "[WARNING]: Error contacting server: "
                    + self.__url
                    + ", Status:"
                    + str(r.status_code),
                    flush=True,
                )
                return []
        except KeyboardInterrupt:
            raise
        except:
            print(
                "[WARNING]: Exception occured while contacting server: " + self.__url,
                flush=True,
            )
            raise

        soup = BeautifulSoup(response_text, "html.parser")

        links = []
        for node in soup.find_all("a"):
            linkaddr = node.get("href")
            if not ("?" in linkaddr or not (linkaddr not in self.__url)):
                links.append(self.__url + linkaddr)
        return links
