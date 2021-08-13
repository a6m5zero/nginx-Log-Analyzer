from pathlib import Path
from distutils import file_util
import datetime as dt
import re
import gzip
import logging


def sort_list_of_dict(list_, key):
    """QUICK SORT OF LIST WITH DICTS BY KEY"""

    if len(list_) <= 1:
        return list_
    left_list = list(filter(lambda x: x[key]>list_[0][key], list_))
    middle = [i for i in list_ if i[key] == list_[0][key]]
    right_list = list(filter(lambda x: x[key]<list_[0][key], list_))
    return sort_list_of_dict(left_list, key) + middle + sort_list_of_dict(right_list, key)


class FileReaderGenerator():
    
    def __init__(self, filename):
        self.filename = filename

    def read_lines(self):
        if 'gz' in str(self.filename):
            logging.info(f'FileReaderGenerator: read gzip file: {self.filename}')
            file = gzip.open(self.filename, 'r')
        else:
            logging.info(f'FileReaderGenerator: read plain/text file: {self.filename}')
            file = open(self.filename, 'r')
        
        for line in file:
            yield line.decode() if isinstance(line, bytes) else line
        file.close()

class LogSearcher(object):

    def __init__(self, config):
        super().__init__()
        self.log_dir = config['LOG_DIR']
        logging.info(f'LogSearcher: start search in dir: {self.log_dir}')
    
    def find_log_file(self):
        """Find the last log file in folder from config"""
        
        p = Path(self.log_dir)
        log_list = list(p.glob('*nginx*.log*')) + list(p.glob('*nginx*.gz'))
        datepattern = re.compile("\d{8}")
        now_date = dt.datetime.now()
        deltatime = dt.timedelta.max
        if log_list:
            for log in log_list:
                match = re.search(datepattern, str(log))
                log_date = dt.datetime.strptime(match[0],"%Y%m%d")
                timedel = now_date-log_date
                if timedel < deltatime:
                    deltatime = timedel
                    self.log_file = log
        else:
            print("No files in LOG_DIR! Stopped")
            logging.exception(f'LogSearcher: Exception! No files in LOG_DIR: {self.log_dir}', exc_info = False)
            quit(0)
        
        logging.info(f'LogSearcher: Done! log file is : {self.log_file}')
        return self.log_file
        
        
class LogParser(object):

    def __init__(self, log_searcher):
        self.log_filename = log_searcher.find_log_file()

    def parse_urls(self):
        url_dict = {}
        for line in FileReaderGenerator(self.log_filename).read_lines():
            try:
                url = re.search(r'".+ HTTP/', line)
                if url:
                    url = url.group().split(' ')[1]
                else:
                    logging.warning(f'{self.__class__.__name__}: no URL in string {line.splitlines()[0]}')
                    raise ValueError
                request_time = re.search(r'" \d+[.]\d\d\d', line)
                if request_time:
                    request_time = float(request_time.group()[2:])
                else:
                    logging.warning(f'{self.__class__.__name__}: no REQUEST_TIME in string {line.splitlines()[0]}, continue!')
                    raise ValueError
            except ValueError: 
                continue

            if url_dict.get(url):
                url_dict[url].append(request_time)
            else:
                url_dict[url] = [request_time]
        logging.info(f'{self.__class__.__name__}: parsing {len(url_dict)} URLs done')
        return url_dict

class Calculator(object):

    # JSON example for append into calculated_results:
    # {"count": 2767,
    # "time_avg": 62.994999999999997, 
    # "time_max": 9843.5689999999995, 
    # "time_sum": 174306.35200000001, 
    # "url": "/api/v2/internal/html5/phantomjs/queue/?wait=1m", 
    # "time_med": 60.073, 
    # "time_perc": 9.0429999999999993, 
    # "count_perc": 0.106}

    calculated_results = []

    def __init__(self, config, urls_dict):
        self.urls_dict = urls_dict    
        self.timesum = {}
        self.config = config
        self.sum_request_time = sum([sum(list_) for list_ in self.urls_dict.values()])
            
    def calculate(self):
        for url in self.urls_dict:
            url_dict = {
                        "url": url,
                        "count": self.count(url),
                        "count_perc": self.count_perc(url)[:15],
                        "time_avg": self.time_avg(url)[:15],
                        "time_max": self.time_max(url)[:15],
                        "time_sum": self.time_sum(url)[:15],
                        "time_med": self.time_med(url)[:15],
                        "time_perc": self.time_perc(url)[:15],
                        }
            self.calculated_results.append(url_dict)

        return sort_list_of_dict(self.calculated_results, 'time_sum')[:self.config['REPORT_SIZE']]

    def count(self, url):
        return str(len(self.urls_dict[url]))

    def count_perc(self, url):
        count_all = len(self.urls_dict.items())
        return str((int(self.count(url))/count_all))

    def time_avg(self, url):
        return str(sum(self.urls_dict[url])/len(self.urls_dict[url]))

    def time_max(self, url):
        return str(max(self.urls_dict[url]))

    def time_sum(self, url):
        return str(sum(self.urls_dict[url]))

    def time_med(self, url):
        return str(sorted(self.urls_dict[url])[len(self.urls_dict[url])//2])

    def time_perc(self,url):
        return '%.10f' % (sum(self.urls_dict[url])/self.sum_request_time)

    def append_urls(self, url_tuples_list):
        pass

class ReportCreator():

    def __init__(self, config, report = '1') -> str:
        self.reports_dir = config['REPORT_DIR']
        self.report = report

    def make_report(self):
        report_name = self.reports_dir+'/report-'+dt.date.today().strftime('%Y.%m.%d')+'.html'
        file_util.copy_file('./report/report.html', report_name)
        infile = ''

        logging.info(f'{self.__class__.__name__}: Report template is: ./report/report.html')
        with open(report_name, mode='r+') as report_file:
            infile = report_file.read()
        infile = infile.replace('$table_json', str(self.report))
        
        with open(report_name, mode='w+') as report_file:
            report_file.write(infile)
        logging.info(f'{self.__class__.__name__}: Report created is: {report_name}')

