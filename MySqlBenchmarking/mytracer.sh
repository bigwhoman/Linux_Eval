strace -f -p "$(pidof mysqld)" 2> "$(uname -r).strace"&
STRACE_PID=$!

sleep 5

kill -s SIGINT "$STRACE_PID"

