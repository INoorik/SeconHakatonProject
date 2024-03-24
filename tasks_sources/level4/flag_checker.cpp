#include <string>
#include <iostream>
#include <stdio.h>

bool check_flag(char *flag);

int main() {
	char user_input[100];
	fgets(user_input, 100, stdin);
	if(check_flag(user_input))
		std::cout<<"Congratulations, you have successfully solve this problem!"<<std::endl;
	else
		std::cout<<"Sorry, you have failed to solve this problem"<<std::endl;
}

bool check_flag(char *flag) {
	char mask[] = "fmcd[~gm~me|okcmm";
	for(int i = 0; flag[i] and mask[i]; i++)
	{
		if(((flag[i])^i) != mask[i])
			return false;
	}
	return true;
}
