#include <string>
#include <iostream>

bool check_flag(std::string flag);

int main() {
	std::string user_input;
	std::cin>>user_input;
	if(check_flag(user_input))
		std::cout<<"Congratulations, you're logging in the Death Star I secret server. [BIG RED SELF DESTROY BUTTON]"<<std::endl;
	else
		std::cout<<"Im calling the Palpatine"<<std::endl;
}

bool check_flag(std::string flag) {
	return flag == "flag_{0y82dwxyel}";
}
