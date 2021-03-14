#!/usr/bin/env python3
# MIT License
#
# Copyright (c) 2020 ADCIRC Development Group
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

from metbuild.cloudwatch import CloudWatch
logger = CloudWatch()

# Main function to process the message and create the output files and post to S3
def process_message(json_message):
    import time
    from metbuild.instance import Instance

    instance = Instance()

    instance.enable_termination_protection()

    logger.info("Processing message with id: "+json_message["MessageId"])

    logger.info(json_message['Body'])
    time.sleep(10)

    logger.info("Finished processing message with id: "+json_message["MessageId"])

    instance.disable_termination_protection()

    return


# Main function
# Check for a message in the queue. If it exists, process it
# otherwise, we're outta here
def main():
    from metbuild.queue import Queue
    logger.debug("Beginning execution")

    queue = Queue(logger)
    
    has_message,message = queue.get_next_message()
    if has_message:
        logger.debug("Found message in queue. Beginning to process")
        process_message(message)
        logger.debug("Deleting message "+message["MessageId"]+" from the queue")
        queue.delete_message(message["ReceiptHandle"])
    else:
        logger.info("No message available in queue. Shutting down.")

    logger.debug("Exiting script with status 0")
    exit(0)


if __name__ == "__main__":
    main()
