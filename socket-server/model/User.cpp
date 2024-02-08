// Copyright [2024] <Anh Dung>
#include<string>
#include"User.h"
using std::string;

User::User() {
}

User::User(string name, string password) : name(name), password(password) {
}

User::User(int id, string name) : id(id), name(name) {
}

User::User(int id, string name, string password)
: id(id), name(name), password(password) {
}

int User::getId() {
    return id;
}

string User::getName() {
    return name;
}

string User::getPassword() {
    return password;
}

string User::getGender() {
    return gender;
}

string User::getBirthday() {
    return birthday;
}

string User::getAddress() {
    return address;
}

void User::setId(int id) {
    this->id = id;
}

void User::setName(string name) {
    this->name = name;
}

void User::setPassword(string password) {
    this->password = password;
}

void User::setGender(string gender) {
    this->gender = gender;
}

void User::setBirthday(string birthday) {
    this->birthday = birthday;
}

void User::setAddress(string address) {
    this->address = address;
}