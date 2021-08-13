Interface logs added request time ($ request_time in nginx
[http://nginx.org/en/docs/http/ngx_http_log_module.html#log_format](http://nginx.org/en/docs/http/ngx_http_log_module.html#log_format). Now you can parse the logs and run
primary analysis by identifying suspicious URLs

![](https://pandao.github.io/editor.md/images/logos/editormd-logo-180x180.png)


## Usage

```bash
#default
python3 log_parser.py

#with args
python3 log_parser.py --log_dir =log --report_size=1000 --report_dir =reports
"--log_dir", help="Directory with Nginx logs files"
"--report_size", help="Len of strings in report bu summary time, default = 1000"
"--report_dir", help="Directory for generated reports"
```
- count - how many times the URL occurs, absolute value
- count_perc - how many times the URL is encountered, in - percentage relative to the total number of requests
- time_sum - total $ request_time for the given URL, absolute value
- time_perc - total $ request_time for the given URL, as a percentage of the total $ request_time of all
requests
- time_avg - average $ request_time for the given URL
- time_max - maximum $ request_time for this URL
- time_med - the median $ request_time for the given URL

## Logs can be gzip or plain
