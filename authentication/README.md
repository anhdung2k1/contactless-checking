# Documentation Authentication Java-Spring Boot API
---
<a href = "#Prerequisites">Prerequisites</a>
---
- Technical:
    - Docker MySQL database installed in Docker Container
    - Set up account for using database: messager/messager
    - Spring Boot
    - Spring Security
    - JWT
    - Java environment (Java ver 17)
- Build: Maven 3.9.1
- Hibernate Core ORM: Hibernate

<h2>HOW TO RUN</h2> 

1. Cat the host in mysql_container by
```
docker exec -it mysql_container bash
```
```
cat /etc/hosts
```
It will show the host address IPv4 mysql is running --> In this point, we are going to use 172.21.0.3 IP address <br/>
2. Configure in docker-compose.yml file and ChatServerService.cpp file located in socket-server and change the IP communication to 172.21.0.3 <br/>
3. Checking the pwd directory path in each context in docker-compose.yml file and make a change point to right directory <br/>
4. Start a docker-compose.yml Java API by
```
docker-compose up authentication
```
- It will start the <strong>localhost:8080</strong> API

If you change your java code, you must "build" it before "up" it by
```
docker-compose build authentication
```

# How to make an API Requests from terminal (CURL Command)
---
<a>Prerequisites</a>
---
- Environment:
    - Linux
    - Curl
- Command going to use to make a test API
```
curl [options] [URL...]
```
- HTTP GET
    - The GET method requests a specific resource from the localhost:8080 server
    - GET is the default method when making HTTP requests with <strong>curl</strong>
```
$ curl http://localhost:8080/api/accounts -H "Authorization: Bearer <ACCESS_TOKEN>"
```
To filter result use query params:
```
$ curl http://localhost:8080/api/accounts?acc_id=1 -H "Authorization: Bearer <ACCESS_TOKEN>"
```

- HTTP POST
    - The POST method is used to create a resource on the server (localhost:8080). If the resource exists, it is overridden
    - The following command make <strong>POST request</strong> using the data specified with the ```-d ``` option:
```
$ curl -X POST http://localhost:8080/api/accounts/signup -H "Content-Type: application/json" -d '{"userName": "anhdung", "password": "anhdung"}'
```
- This command will return the response from the server that you made request. In this circumstances, the response we are going to get is a token <ACCESS_TOKEN>
- Using this token detached in Header for each request --> Authenticate each Filter request when making API call to inner Application
- HTTP PUT:
    - The PUT method is used to update or replace a resource on a server. It replaces all data of the specified resource with the request data.
```
$ curl -X PUT http://localhost:8080/api/users/1 -H "Content-Type: application/json" -d '{"address":"address1", "gender": "MALE"}' -H "Authorization: Bearer <ACCESS_TOKEN>"
```
- HTTP DELETE:
    - The DELETE method is used ti removes the specified resource from the server
```
$ curl -X DELETE http://localhost:80808/api/user/1
```

<a href = "JAVA_SPRING">Documentation for JAVA SPRING BOOT RESTful API</a>
---
<a>Documentation Overview</a>
1. The "Spring Web MVC Framework"
2. Spring Security

<a>1/ The "Spring Web MVC Framework"</a>
---
- The <a>Spring Web MVC framework</a> (often referred to as "Spring MVC") is a rich "model view controller" web framework <br/> 
- Spring MVC lets you create special ```@RestController``` beans to handle incoming HTTP requests. Methods in your controller are mapped to HTTP by using ```@RequestMapping``` annotations.<br/>

- If you want to take complete control of ```Spring MVC```, you can add your own ```@Configuration``` annotated. You can set your own ```@Bean``` Configuration putting on ```IOC``` container.
- To use it by <strong>Dependency Injection (DI)</strong> just use annotation ```@Autowired``` --> This will load the <strong>Bean</strong> that you have already defined.
- In the ```Services``` layer --> Will incharge on handle logic API 
- In the ```Repository``` layer --> Handling and Interacting connect with Database
- Define new model and entity --> Start application --> Auto generate with specific properties. <br/>
---
<a>2/ Spring Security</a>
---
- When added the Spring Security Framework to application, it automatically registers a filter chain that intercept all incoming requests. This chain consists of various filters, and each of them handles a particular use case
- Check if the requested URL is publicly accessible, based on configuration
- In case of session-based authentication, check if the user is already authenticated in the current session
- Check if the user is authorized to perform the requested action, and so on <br/>

<a><h4>AuthenticationManager</h4></a>
- ```AuthenticationManager``` as a coordinator where you can register multiple providers, and based on request type, it will deliver an authentication request to the correct provider

<a><h4>AuthenticationProvider</h4></a>
- ```AuthenticationProvider``` process specific types of authentication.
    -  ```authenticate```performs authentication with the request
    - ```DaoAuthenticationProvider``` retrieves user details from ```UserDetailsService```

<a><h4>UserDetailsService</h4></a>
- ```UserDetailService``` is described as a core interface that loads user-specific data.
- Extracting user identity information based on credentials from a database and then perform validation
- ```loadUserByUsername``` accepts username as a parameter and returns the user identity object

<a><h4>Authentication Using JWT with Spring Security</h4></a>
- To customize Spring Security for JWT use, we need a configuration class annotated with ```@EnableWebSecurity``` annotation in our classpath.
1. Configure the authentication manager with the correct provider
2. Configure web security (public URLs, private URLs, authorization, etc)

```
@Configuration
@EnableWebSecurity
@RequiredArgsConstructor
public class SecurityConfiguration {
    private final JwtAuthenticationFilter jwtAuthenticationFilter;
    private final AuthenticationProvider authenticationProvider;

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception{
        //Code
    }
}
```
- Add JwtFilterToken filter before each HTTP Request
- Hashing password when user are registered a new account
- Token will valid in setting duration, if token is running out of time --> the application will need to reauthenticate to continue use

---
<a><strong>API Requests</strong></a>

|.No | Path | Status | Notes | Description | Method | Authorization | User Required | Param | RequestBody | Response |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| User |
| 1 | /api/users | Done | - | - | Get | Bearer | client | - | - | userName |
| 2 | /api/users | Done | - | When Account is register user is create too | POST | Bearer | client | - | userName [type] |  User |
| 3 | /api/users/:id | Done | - | | GET | Bearer | client | id | - | userName, address, gender |
| 4 | /api/users/search | Done | - | Search By Name | GET | Bearer | client | - | keyword | userId, userName |
| 5 | /api/users/block | To-Do | - | Type: 0 is unblock, 1 is block | POST | Bearer | room-admin | - | user_id [type] | - |
| 6 | /api/users/:id | Done | Update User Information | - | PUT | Bearer | client | - | user_id [type] | User |
| 7 | /api/users/:id | Done | Delete User | - | DELETE | Bearer | admin | id | user_id [type] | boolean |
| |
| Account |
| 1 | /api/accounts/signin | Done | - | - | POST | no-auth | client | - | userName, password | token |
| 2 | /api/accounts/signup | Done | - | - | POST | no-auth | client | - | userName, password | token |
| 3 | /api/accounts | Done | - | - | GET | Bearer | admin | - | - | Accounts |
| 4 | /api/account/:id | Done | - | - | GET | Bearer | admin | id | - | Account |
| 5 | /api/account/:userName | Done | - | Get Account ID | GET | Bearer | client | - | - | acc_id |
| 6 | /api/accounts/:id | Done | - | Update Account Password | PUT | Bearer | admin | id | attributes | Account |
| 7 | /api/accounts/:id | Done | Delete Account need delete User respective with that account | Delete Account | DELETE | Bearer | admin | id | - | boolean |
| |
| Customer |
| 1 | /api/customers | Done | - | Create new Customer | POST | Bearer | client | - | Customers | Boolean |
| 2 | /api/customers/query | Done | - | Get all customers with name | GET | Bearer | client | query, page, size | - | Page<Map<String, Object>> |
| 3 | /api/customers/{customerId} | Done | - | Get customer by customer ID | GET | Bearer | client | customerId | - | Map<String, Object> |
| 4 | /api/customers/count | Done | - | Count customers | GET | Bearer | client | - | - | Long |
| 5 | /api/customers/getCheckIn/{customerId} | Done | - | Get customer check-in time | GET | Bearer | client | customerId | - | Map<String, Object> |
| 6 | /api/customers/getCheckOut/{customerId} | Done | - | Get customer check-out time | GET | Bearer | client | customerId | - | Map<String, Object> |
| 7 | /api/customers/{customerId} | Done | - | Update customer information | PATCH | Bearer | client | customerId | Customers | Customers |
| 8 | /api/customers/{customerId} | Done | - | Delete customer | DELETE | Bearer | client | customerId | - | Map<String, Boolean> |
| 9 | /api/customers | Done | - | Get all customers with pagination | GET | Bearer | client | page, size | - | Page<Customers> |
| |
| Notification |
| 1 | /api/notifications | Done | - | Create new Notification | POST | Bearer | client | - | String (message) | Boolean |
| 2 | /api/notifications | Done | - | Get all Notifications | GET | Bearer | client | - | - | List<NotificationEntity> |
| 3 | /api/notifications | Done | - | Delete all Notifications | DELETE | Bearer | client | - | - | Boolean |
| |
| Record |
| 1 | /api/records | Done | - | Create new Record | POST | Bearer | client | - | Records | Boolean |
| 2 | /api/records/query | Done | - | Get all Records by date | GET | Bearer | client | date | - | List<RecordEntity> |
| 3 | /api/records/count | Done | - | Count Records | GET | Bearer | client | - | - | Long |
| 4 | /api/records/{recordId} | Done | - | Delete one Record | DELETE | Bearer | client | recordId | - | Boolean |
| 5 | /api/records/query | Done | - | Delete all Records by date | DELETE | Bearer | client | date | - | Boolean |
| |
| Task |
| 1 | /api/tasks | Done | - | Create new Task | POST | Bearer | client | - | Task | Boolean |
| 2 | /api/tasks | Done | - | Get all Tasks with pagination | GET | Bearer | client | page, size | - | Page<Task> |
| 3 | /api/tasks/query | Done | - | Get all Tasks by Task Name | GET | Bearer | client | query, page, size | - | Page<Map<String, Object>> |
| 4 | /api/tasks/getTask/customer/query | Done | - | Get all Tasks by Customer Name | GET | Bearer | client | query, page, size | - | Page<Map<String, Object>> |
| 5 | /api/tasks/getTask/customers/query | Done | - | Get all Tasks by multiple Customer Names | GET | Bearer | client | queries, page, size | - | Page<Map<String, Object>> |
| 6 | /api/tasks/{taskId} | Done | - | Get Task by Task ID | GET | Bearer | client | taskId | - | Map<String, Object> |
| 7 | /api/tasks/count | Done | - | Count all Tasks | GET | Bearer | client | - | - | Long |
| 8 | /api/tasks/{taskId} | Done | - | Update Task Description | PATCH | Bearer | client | taskId | Task | Task |
| 9 | /api/tasks/{taskId} | Done | - | Delete Task by Task ID | DELETE | Bearer | client | taskId | - | Map<String, Boolean> |
| 10 | /api/tasks/getTask/{customerName} | Done | - | Get all Tasks by Customer Name (Exact Match) | GET | Bearer | client | customerName | - | List<TaskEntity> |




