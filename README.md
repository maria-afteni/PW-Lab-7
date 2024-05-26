## CRUD API

---

### Overview

This CRUD API is built using Flask and provides basic functionalities to perform CRUD operations (Create, Read, Update, Delete) on projects. The API supports token-based authentication using JSON Web Tokens (JWT) and allows different levels of access based on user roles.

### Functionalities

1. **Token Generation**
   - Endpoint: `/token` (POST)
   - Description: Generates a JWT token for authentication.

2. **Get Projects**
   - Endpoint: `/projects` (GET)
   - Description: Retrieves a list of projects.

3. **Get Project by ID**
   - Endpoint: `/projects/<int:project_id>` (GET)
   - Description: Retrieves a project by its ID.

4. **Add Project**
   - Endpoint: `/projects` (POST)
   - Description: Adds a new project.

5. **Update Project**
   - Endpoint: `/projects/<int:project_id>` (PUT)
   - Description: Updates an existing project.

6. **Delete Project**
   - Endpoint: `/projects/<int:project_id>` (DELETE)
   - Description: Deletes an existing project.


### Authentication and Authorization

- Authentication is performed using JWT tokens.
- Different endpoints require different levels of permissions (roles) for access.
- Unauthorized access will result in appropriate error responses.

### Error Handling

- The API handles various error scenarios such as invalid requests, missing data, unauthorized access, and resource not found.
- Error responses provide descriptive messages to aid in troubleshooting.

### Swagger UI Documentation

- Swagger UI is integrated to provide interactive API documentation.
- The documentation includes details about endpoints, request parameters, responses, and security definitions.
