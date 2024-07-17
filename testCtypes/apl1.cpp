#include <stdio.h>
using namespace std;

int main2() {
	printf("Hello World 2!");
	return 0;
}

int main() {
	printf("Hello World 3!");
	main2();
	return 0;
}

int test1(int a) {
	printf("%i", a);
	return 1;
}

