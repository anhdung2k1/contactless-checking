#pragma once
#include <iostream>
#include <algorithm>
#include <curl/curl.h>
#include <string.h>

class CurlUtils{
    public:
        static size_t getToken(void *ptr, size_t size, size_t nmemb, std::string* data);
        static std::string handleString(std::string ans);
        static void authUtil(std::string url, std::string formData, bool& flag, CURL *&curl, CURLcode& res, struct curl_slist *&slist); //Curl Utils used to log in or register
        static std::string getUtil(CURL *curl, CURLcode res, std::string url, bool &flag);
        static std::string postUtil(CURL *curl, CURLcode res, std::string url, std::string formData, bool &flag);
        static std::string putUtil(CURL *curl, CURLcode res, std::string url, std::string formData, bool &flag);
        static std::string patchUtil(CURL *curl, CURLcode res, std::string url, std::string formData, bool &flag);
        static bool deleteUtil(CURL *curl, CURLcode res, std::string url, std::string formData);
        static void handleDestruct(CURL *curl, struct curl_slist *slist);
};