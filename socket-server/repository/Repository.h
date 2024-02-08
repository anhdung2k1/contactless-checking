// // Copyright [2023] <BRAINSTORMERS>
#pragma once
#include <mysql/mysql.h>
#include <iostream>
#include <vector>
#include <string>
#include <sstream>

#include"../model/User.h"

using std::string;
using std::vector;

class Repository {
 public:
    static string ConvertIntToString(int id);
    struct connectionDetails;
    static MYSQL* mysqlConnectionSetup(
        struct connectionDetails mysql_details);
    static MYSQL_RES* mysqlExecuteQuery(
        MYSQL *connection, const char *sql_query);
    static MYSQL* connectToDatabase(string address);
    static bool CheckUserName(string username, string address);
};