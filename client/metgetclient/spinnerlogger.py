#!/usr/bin/env python3
################################################################################
# MetGet Client
#
# This file is part of the MetGet distribution (https://github.com/waterinstitute/metget).
# Copyright (c) 2023, The Water Institute
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Author: Zach Cobell, zcobell@thewaterinstitute.org
#
################################################################################

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
