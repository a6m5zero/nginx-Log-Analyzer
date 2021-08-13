
import argparse
import logging
from logic import nginx
from datetime import datetime

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
    "LOG_FILENAME": f"./logs/{datetime.now().strftime('%Y_%m_%d')}.log",
}

def main():
    logging.basicConfig(filename=config['LOG_FILENAME'], format='%(asctime)s:%(levelname)s:%(message)s', 
                        datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
    logging.info('Running with config: ' + str(config))

    log_searcher = nginx.LogSearcher(config)
    log_parser = nginx.LogParser(log_searcher)
    log_calculator = nginx.Calculator(config, log_parser.parse_urls())
    report_creator = nginx.ReportCreator(config, log_calculator.calculate())
    report_creator.make_report()
    
    logging.info('Done')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--log_dir", help="Directory with Nginx logs files, default = './log'", default='./log')
    parser.add_argument("--report_size", help="Len of strings in report bu summary time, default = 1000", default=1000, type=int)
    parser.add_argument("--report_dir", help="Directory for generated reports, default = './reports'", default='./reports')
    args = parser.parse_args()
    
    if args.report_size:
        config['REPORT_SIZE'] = args.report_size
    elif args.report_dir:
        config['REPORT_DIR'] = args.report_dir
    elif args.log_dir:
        config['LOG_DIR'] = args.log_dir
    main()
