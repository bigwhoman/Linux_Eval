#define _GNU_SOURCE
#include <sched.h>
#include <time.h>
#include <unistd.h>
#include <stdio.h>
#include <time.h>
#include <string.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <sys/mman.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>
#include <stdbool.h>
#include <signal.h>
#include <sys/syscall.h>
#include <sys/types.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/poll.h>
#include <sys/epoll.h>
#include <sys/resource.h>
#include <sys/time.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <errno.h>

/*
    change page size (min = 1 page)
 */

#define FILE_SIZE 4096

void munmap_test() {

	int fd =open("test_file.txt", O_RDWR);
	if (fd < 0) printf("invalid fd%d\n", fd);
	void *addr = (void *)syscall(SYS_mmap, NULL, FILE_SIZE, PROT_WRITE, MAP_PRIVATE, fd, 0);
	for (int i = 0; i < FILE_SIZE; i++) {
		((char *)addr)[i] = 'b';
	}
	syscall(SYS_munmap, addr, FILE_SIZE);
	close(fd);
	return;
}

int main(){
    char *buf_out = (char *) malloc (sizeof(char) * FILE_SIZE);
	for (int i = 0; i < FILE_SIZE; i++) {
		buf_out[i] = 'a';
	}

	int fd = open("test_file.txt", O_CREAT | O_TRUNC | O_WRONLY);
	if (fd < 0) printf("invalid fd in write: %d\n", fd);

	syscall(SYS_write, fd, buf_out, FILE_SIZE);
	close(fd);
    munmap_test();
    return 0;
}