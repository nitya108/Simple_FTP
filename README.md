# Simple_FTP
Implement the Go-back-N automatic repeat request (ARQ)  and Selective Repeat ARQ scheme and carry out a number of experiments to evaluate its performance. We will be sending a file called `nitya.txt` from the client to the server. 

How to run the program for **Go-Back-N ARQ**:

1. open a command prompt at src folder and run the server, make sure to note your hostname:

`python server.py 7735 window2.txt 0.05 `

2. Open another command prompt and run the client:

`python client.py <hostname> 7735 nitya.txt <N> <MSS>`

How to run the program for **Selective Repeat ARQ**:

1. open a command prompt at src folder and run the server, make sure to note your hostname:

`python srserver.py 7735 window2.txt 0.05 `

2. Open another command prompt and run the client:

`python srclient.py <hostname> 7735 nitya.txt <N> <MSS>`
