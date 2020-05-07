import sys, os
import logging

class EzLogger(object):
    LOGGER_FILE_PATH = 'output/vizio_test_logger.log'

    @staticmethod
    def getLogger(name):
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

        fpath, fname = os.path.split(EzLogger.LOGGER_FILE_PATH)
        if not os.path.exists(fpath):
            os.makedirs(fpath)
        handler = logging.FileHandler(EzLogger.LOGGER_FILE_PATH)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)  # logging to file
        logger.addHandler(logging.StreamHandler(sys.stdout))  # logging to stdout
        return logger

if __name__ == '__main__':
    logger = EzLogger.getLogger()
    logger.info('Hello from Ezlooger')