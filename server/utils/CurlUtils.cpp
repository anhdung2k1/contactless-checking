#include "CurlUtils.h"

size_t CurlUtils::getToken(void* ptr, size_t size, size_t nmemb, std::string* data){
    data->append((char*)ptr, size* nmemb);
    return size * nmemb;
}
std::string CurlUtils::handleString(std::string ans){
    ans = ans.substr(9);
    ans.erase(remove(ans.begin(), ans.end(), '}'), ans.end());
    ans.erase(remove(ans.begin(), ans.end(), '"'), ans.end());
    return ans;
}
//Function auth utils
void CurlUtils::authUtil(std::string url, std::string formData, bool& flag, CURL *&curl, CURLcode& res, struct curl_slist *&slist){
    std::string token;
    slist = NULL;
    slist = curl_slist_append(slist, "Content-Type: application/json");

    curl = curl_easy_init(); // Triggered authen or register --> will init again
    if(!curl) std::cout << "CURL INITIALIZATION FAIL" << std::endl;
    else{
        //Set up Curl POST JSON
        curl_easy_setopt(curl, CURLOPT_URL, url.c_str()); // sign in requests
        curl_easy_setopt(curl, CURLOPT_NOPROGRESS, 1L);
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, formData.c_str());
        curl_easy_setopt(curl, CURLOPT_USERAGENT, "curl/7.38.0");
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, slist);
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, getToken);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &token);
        curl_easy_setopt(curl, CURLOPT_MAXREDIRS, 50L);
        curl_easy_setopt(curl, CURLOPT_CUSTOMREQUEST, "POST");
        curl_easy_setopt(curl, CURLOPT_TCP_KEEPALIVE, 1L);

        res = curl_easy_perform(curl);
        if(res != CURLE_OK){
            std::cout << "Failed" << std::endl;
            flag = false;
        } //Return the CURL CODE
        else{
            if(token.length() != 0) {
                token = CurlUtils::handleString(token);
                // std::cout << CurlUtils::handleString(token).c_str() << std::endl;
                curl_slist_append(slist, ("Authorization: Bearer "+ token).c_str());
                curl_easy_setopt(curl, CURLOPT_HTTPHEADER, slist); // Detached Bearer token into Header
                flag = true;
            }
            else {
                flag = false;
            }
        }
        curl_easy_strerror(res); //print error out
    }
}
//Function to CURL GET
std::string CurlUtils::getUtil(CURL *curl, CURLcode res, std::string url, bool &flag) {
    std::string response;
    curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, getToken);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);
    curl_easy_setopt(curl, CURLOPT_CUSTOMREQUEST, "GET"); //Define GET
    res = curl_easy_perform(curl);
    if(res != CURLE_OK) {
        std::cout << "Failed" << std::endl;
        flag = false;
    } //Return the CURL CODE
    return response;

}
//Function to CURL POST
std::string CurlUtils::postUtil(CURL *curl, CURLcode res, std::string url, std::string formData, bool &flag){
    std::string response;
    curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, formData.c_str());
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, getToken);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);
    curl_easy_setopt(curl, CURLOPT_CUSTOMREQUEST, "POST");

    res = curl_easy_perform(curl);
    if(res != CURLE_OK){
        std::cout << "Failed" << std::endl;
        flag = false;
    } //Return the CURL CODE
    return response;
}
//Function to CURL PUT
std::string CurlUtils::putUtil(CURL *curl, CURLcode res, std::string url, std::string formData, bool &flag){
    std::string response;
    curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, formData.c_str());
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, getToken);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);
    curl_easy_setopt(curl, CURLOPT_CUSTOMREQUEST, "PUT");

    res = curl_easy_perform(curl);
        if(res != CURLE_OK){
            std::cout << "Failed" << std::endl;
            flag = false;
        } //Return the CURL CODE
    return response;
}
//Function to CURL PATCH
std::string CurlUtils::patchUtil(CURL *curl, CURLcode res, std::string url, std::string formData, bool &flag){
    std::string response;
    curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, formData.c_str());
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, getToken);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);
    curl_easy_setopt(curl, CURLOPT_CUSTOMREQUEST, "PATCH");

    res = curl_easy_perform(curl);
        if(res != CURLE_OK){
            std::cout << "Failed" << std::endl;
            flag = false;
        } //Return the CURL CODE
    return response;
}
//Function to CURL Delete
bool CurlUtils::deleteUtil(CURL *curl, CURLcode res, std::string url, std::string formData){
    curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, formData.c_str());
    curl_easy_setopt(curl, CURLOPT_CUSTOMREQUEST, "DELETE");

    res = curl_easy_perform(curl);
    if(res != CURLE_OK){
        std::cout << "Failed" << std::endl;
        return false;
    } //Return the CURL CODE
    return true;
}
//Function to Destruct CURL unused 
void CurlUtils::handleDestruct(CURL *curl, struct curl_slist *slist){
        curl = NULL;
        curl_easy_cleanup(curl);
        slist = NULL;
        curl_slist_free_all(slist);
}