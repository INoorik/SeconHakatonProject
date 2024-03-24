#include <string>
#include <iostream>
#include <stdio.h>

bool check_flag(char *flag);

int main() {
	char user_input[100];
	fgets(user_input, 100, stdin);
	if(check_flag(user_input))
		std::cout<<<"Congratulations, you're logging in the Death Star II secret server. Again. [BIG RED SELF DESTROY BUTTON]"<std::endl;
	else
		std::cout<<"Im calling the Palpatine"<<std::endl;
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
