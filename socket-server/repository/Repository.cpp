// Copyright [2024] <Anh Dung>
#include"Repository.h"

using std::string;
using std::vector;
using std::stringstream;
using std::stoi;

struct Repository::connectionDetails {
    const char*server, *user, *password, *database;
};

MYSQL* Repository::mysqlConnectionSetup(
    struct connectionDetails mysql_details) {
    MYSQL *connection = mysql_init(NULL);
    if (!mysql_real_connect(connection,
    mysql_details.server, mysql_details.user,
    mysql_details.password, mysql_details.database, 0, NULL, 0)) {
        perror("Connection Error");
        exit(1);
    }
    return connection;
}

MYSQL_RES* Repository::mysqlExecuteQuery(
    MYSQL *connection, const char *sql_query) {
    if (mysql_query(connection, sql_query)) {
        perror("MySQL Query Error");
        exit(1);
    }
    return mysql_use_result(connection);
}

MYSQL* Repository::connectToDatabase(string address) {
    struct connectionDetails mySql;
    mySql.server = address.c_str();
    mySql.user = string(getenv("DB_USERNAME")).c_str();
    mySql.password = string(getenv("DB_PASSWORD")).c_str();
    mySql.database = string(getenv("DB_NAME")).c_str();
    return  mysqlConnectionSetup(mySql);
}

bool Repository::CheckUserName(string username, string address) {
    bool returnValue;
    string query = "select * from users where BINARY user_name = '" + username + "';";
    MYSQL *con = connectToDatabase(address);
    MYSQL_RES *res = mysqlExecuteQuery(con, query.c_str());
    if (mysql_fetch_row(res) != NULL) {
        returnValue = true;
    } else {
        returnValue = false;
    }
    mysql_free_result(res);
    mysql_close(con);
    return returnValue;
}
