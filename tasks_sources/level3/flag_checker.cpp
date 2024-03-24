#include <string>
#include <iostream>

bool check_flag(std::string flag);

int main() {
	std::string user_input;
	std::cin>>user_input;
	if(check_flag(user_input))
		std::cout<<"Congratulations, you have successfully solve this problem!"<<std::endl;
	else
		std::cout<<"Sorry, you have failed to solve this problem"<<std::endl;
}

bool check_flag(std::string flag) {
	return flag == "flag_{0y82dwxyel}";
}
