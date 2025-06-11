# pvai
This Python script mimics pv Linux utility in terms of reading from stdin, and writing to stdout. But it uses stderr to print AI thoughts on data going through pipe instead of monitoring the progress.

For now it works only with Google's Gemini, namely Generative Language API (genai) as the AI backend. 

## Usage
```shell
>python3 pvai.py --help
usage: pvai.py [-h] [--follow] [--unlimited]

This Python script mimics pv Linux utility in terms of reading from stdin, and writing to stdout. But it uses stderr to print AI thoughts on data going through pipe instead of monitoring the progress.

options:
  -h, --help   show this help message and exit
  --follow     Continuously print AI thoughts as the data are coming in from stdin. Otherwise gather the data first and share the thoughts at the end.
  --unlimited  AI response is not limited to sentence or paragraph
```
## Examples

### Example 1 
```shell
>echo "0xA000000" | python3 pvai.py >/dev/null
Data transfer started...sharing AI thoughts in stderr at the end after the data are through!
The provided data `0xA000000` likely represents a memory address in hexadecimal format, potentially printed as part of a debugging process or memory dump. It's impossible to say what it refers to without more context.
```
### Example 2 
```shell
>cat pvai.py | python3 pvai.py >/dev/null
Data transfer started...sharing AI thoughts in stderr at the end after the data are through!
The Python script `pvai.py` aims to replicate the functionality of the Linux `pv` command (pipe viewer) but instead of showing data transfer progress, it streams data from standard input to standard output while using a Gemini AI model to analyze the data passing through the pipe and print AI's thoughts to standard error. It uses a `secrets.yml` file to store the Gemini API key. The script offers a `--follow` argument to trigger real-time AI analysis as data chunks arrive, and an `--unlimited` flag to specify the AI response length. There are some legacy code commented out, possibly for future reuse or historical reasons.
```
### Example 3 
```shell
>curl https://github.com/llansky3/pvai --silent | python3 pvai.py >/dev/null
Data transfer started...sharing AI thoughts in stderr at the end after the data are through!
The data stream is the HTML source code of a GitHub repository page for a Python script named `pvai`, which mimics the Linux `pv` utility but uses AI to analyze data passing through a pipe and prints AI thoughts to standard error.
```