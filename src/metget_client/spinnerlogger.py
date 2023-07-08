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

class SpinnerLogger:
    """
    Class to handle the spinner animation and logging
    """

    def __init__(self):
        """
        Constructor
        """
        from sys import stdout

        try:
            from halo import Halo

            self.__is_tty = stdout.isatty()
        except ImportError:
            if stdout.isatty():
                print(
                    "[WARNING]: Halo package not found. Disabling animation.",
                    flush=True,
                )
            self.__is_tty = False

        self.__current_text = SpinnerLogger.standard_log(0, "initializing")

        if self.__is_tty:
            self.__spinner = Halo(
                text=self.__current_text,
                spinner="dots",
                placement="left",
            )
            self.__spinner.color = self.__spinner.text_color

    @staticmethod
    def __time_str() -> str:
        """
        Returns the current time in UTC

        Returns:
            str: Current time in UTC
        """
        from datetime import datetime

        return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    def start(self, text: str = None) -> None:
        """
        Starts the spinner animation

        Args:
            text (str, optional): Text to display. Defaults to None.

        Returns:
            None
        """
        if text is not None:
            self.__current_text = text
        if self.__is_tty:
            self.__spinner.start(self.__current_text)
        else:
            SpinnerLogger.__standard_print(self.__current_text)

    def set_text(self, text: str) -> None:
        """
        Sets the text to display in the spinner

        Args:
            text (str): Text to display

        Returns:
            None
        """
        self.__current_text = text
        if self.__is_tty:
            self.__spinner.text = self.__current_text
        else:
            SpinnerLogger.__standard_print(self.__current_text)

    def succeed(self, text: str = None) -> None:
        """
        Stops the spinner animation and displays a success message

        Args:
            text (str, optional): Text to display. Defaults to None.

        Returns:
            None
        """
        if text is not None:
            self.__current_text = text

        if self.__is_tty:
            self.__spinner.succeed(self.__current_text)
        else:
            SpinnerLogger.__standard_print(self.__current_text)

    def info(self, text: str = None) -> None:
        """
        Displays an info message in the spinner

        Args:
            text (str, optional): Text to display. Defaults to None.

        Returns:
            None
        """
        if text is not None:
            self.__current_text = text

        if self.__is_tty:
            self.__spinner.info(self.__current_text)
        else:
            SpinnerLogger.__standard_print(self.__current_text)

    def fail(self, text: str = None) -> None:
        """
        Stops the spinner animation and displays a failure message

        Args:
            text (str, optional): Text to display. Defaults to None.

        Returns:
            None
        """
        if text is not None:
            self.__current_text = text

        if self.__is_tty:
            self.__spinner.fail(self.__current_text)
        else:
            SpinnerLogger.__standard_print(self.__current_text)

    @staticmethod
    def __standard_print(text: str) -> None:
        """
        Prints the given text to stdout

        Args:
            text (str): Text to print

        Returns:
            None
        """
        print(text, flush=True)

    @staticmethod
    def standard_log(count: int, status: str) -> str:
        """
        Returns a standard log message

        Args:
            count (int): Number of requests
            status (str): Status of the request

        Returns:
            str: Standard log message
        """
        return "[{:s}]: Checking request status...(n={:d}): {:s}".format(
            SpinnerLogger.__time_str(), count, status
        )
