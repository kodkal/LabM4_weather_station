# API Documentation
## Weather Station RESTful API Reference

---

### Document Information
- **Student Name**: [Your Name]
- **Version**: 1.0
- **Last Updated**: [Date]
- **Base URL**: `https://localhost:8443/api`

---

## Table of Contents
1. [Overview](#1-overview)
2. [Authentication](#2-authentication)
3. [Endpoints](#3-endpoints)
4. [Data Models](#4-data-models)
5. [Error Handling](#5-error-handling)
6. [Rate Limiting](#6-rate-limiting)
7. [Security](#7-security)
8. [Examples](#8-examples)

---

## 1. Overview

### 1.1 API Description
The Weather Station API provides secure access to IoT sensor data including temperature, humidity, and pressure readings. All endpoints require authentication except for the health check.

### 1.2 Base Information
- **Protocol**: HTTPS (TLS 1.2+)
- **Port**: 8443
- **Content-Type**: `application/json`
- **Authentication**: JWT Bearer tokens

### 1.3 API Versioning
Current version: v1 (embedded in URL path)

---

## 2. Authentication

### 2.1 Authentication Flow
```
1. Client sends credentials to /api/auth/login
2. Server validates and returns JWT token
3. Client includes token in Authorization header
4. Token expires after 1 hour
5. Client can refresh using /api/auth/refresh
```

### 2.2 Token Format
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 2.3 Token Payload Structure
```json
{
  "user_id": "string",
  "device_id": "string",
  "exp": 1234567890,
  "iat": 1234567890,
  "jti": "unique-token-id"
}
```

---

## 3. Endpoints

### 3.1 Authentication Endpoints

#### POST /api/auth/login
**Description**: Authenticate and receive JWT token

**Request Body**:
```json
{
  "username": "string",
  "password": "string",
  "device_id": "string (optional)"
}
```

**Response (200 OK)**:
```json
{
  "token": "jwt-token-string",
  "expires_in": 3600,
  "token_type": "Bearer"
}
```

**Response (401 Unauthorized)**:
```json
{
  "error": "Invalid credentials"
}
```

#### POST /api/auth/refresh
**Description**: Refresh an existing valid token

**Headers**:
```
Authorization: Bearer [current-token]
```

**Response (200 OK)**:
```json
{
  "token": "new-jwt-token",
  "expires_in": 3600
}
```

#### POST /api/auth/logout
**Description**: Invalidate current token

**Headers**:
```
Authorization: Bearer [token]
```

**Response (200 OK)**:
```json
{
  "message": "Successfully logged out"
}
```

---

### 3.2 Weather Data Endpoints

#### GET /api/data
**Description**: Get current sensor readings

**Headers**:
```
Authorization: Bearer [token]
```

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| format | string | No | Response format (json/csv) |
| units | string | No | Temperature units (celsius/fahrenheit) |

**Response (200 OK)**:
```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "device_id": "weather-station-001",
  "data": {
    "temperature": 22.5,
    "humidity": 45.2,
    "pressure": 1013.25,
    "altitude": 1420.5
  },
  "location": "UVU Lab",
  "is_simulated": false
}
```

#### GET /api/data/history
**Description**: Get historical sensor data

**Headers**:
```
Authorization: Bearer [token]
```

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| start | datetime | No | Start timestamp (ISO 8601) |
| end | datetime | No | End timestamp (ISO 8601) |
| limit | integer | No | Max results (default: 100) |
| offset | integer | No | Pagination offset |

**Response (200 OK)**:
```json
{
  "data": [
    {
      "timestamp": "2024-01-01T12:00:00Z",
      "temperature": 22.5,
      "humidity": 45.2,
      "pressure": 1013.25
    }
  ],
  "count": 100,
  "next": "/api/data/history?offset=100",
  "previous": null
}
```

#### POST /api/data
**Description**: Submit new sensor reading (if authorized)

**Headers**:
```
Authorization: Bearer [token]
Content-Type: application/json
```

**Request Body**:
```json
{
  "temperature": 22.5,
  "humidity": 45.2,
  "pressure": 1013.25,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**Response (201 Created)**:
```json
{
  "id": "reading-uuid",
  "message": "Data recorded successfully"
}
```

---

### 3.3 System Endpoints

#### GET /api/status
**Description**: Get system status and health

**Headers**:
```
Authorization: Bearer [token] (optional)
```

**Response (200 OK)**:
```json
{
  "status": "operational",
  "uptime": "2d 14h 30m",
  "version": "1.0.0",
  "sensor_status": "connected",
  "last_reading": "2024-01-01T12:00:00Z",
  "buffer_size": 50,
  "authenticated": true
}
```

#### GET /api/config
**Description**: Get current configuration (admin only)

**Headers**:
```
Authorization: Bearer [admin-token]
```

**Response (200 OK)**:
```json
{
  "device_id": "weather-station-001",
  "location": "UVU Lab",
  "sensor_type": "BME280",
  "reading_interval": 60,
  "simulation_mode": false
}
```

#### PUT /api/config
**Description**: Update configuration (admin only)

**Headers**:
```
Authorization: Bearer [admin-token]
Content-Type: application/json
```

**Request Body**:
```json
{
  "reading_interval": 30,
  "location": "New Location"
}
```

**Response (200 OK)**:
```json
{
  "message": "Configuration updated",
  "updated_fields": ["reading_interval", "location"]
}
```

---

## 4. Data Models

### 4.1 SensorReading
```json
{
  "id": "string (UUID)",
  "timestamp": "string (ISO 8601)",
  "device_id": "string",
  "temperature": "number (Celsius)",
  "humidity": "number (percentage)",
  "pressure": "number (hPa)",
  "altitude": "number (meters)",
  "location": "string",
  "is_simulated": "boolean"
}
```

### 4.2 User
```json
{
  "id": "string",
  "username": "string",
  "device_id": "string",
  "role": "string (admin/user)",
  "created_at": "string (ISO 8601)",
  "last_login": "string (ISO 8601)"
}
```

### 4.3 Error
```json
{
  "error": "string",
  "message": "string",
  "code": "number",
  "timestamp": "string (ISO 8601)",
  "path": "string"
}
```

---

## 5. Error Handling

### 5.1 HTTP Status Codes

| Code | Status | Description |
|------|--------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created |
| 400 | Bad Request | Invalid request format |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Access denied |
| 404 | Not Found | Resource not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily down |

### 5.2 Error Response Format
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "Additional context"
    }
  }
}
```

### 5.3 Common Error Codes
| Code | Description |
|------|-------------|
| AUTH_REQUIRED | Authentication is required |
| TOKEN_EXPIRED | JWT token has expired |
| TOKEN_INVALID | JWT token is invalid |
| RATE_LIMIT | Rate limit exceeded |
| VALIDATION_ERROR | Input validation failed |
| NOT_FOUND | Resource not found |
| SERVER_ERROR | Internal server error |

---

## 6. Rate Limiting

### 6.1 Limits
| Endpoint | Limit | Window |
|----------|-------|--------|
| /api/auth/login | 5 requests | 15 minutes |
| /api/data | 60 requests | 1 minute |
| /api/data/history | 10 requests | 1 minute |
| Default | 100 requests | 1 minute |

### 6.2 Rate Limit Headers
```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1234567890
```

### 6.3 Rate Limit Response (429)
```json
{
  "error": "Rate limit exceeded",
  "retry_after": 30
}
```

---

## 7. Security

### 7.1 Security Features
- ✅ HTTPS/TLS only (no HTTP)
- ✅ JWT authentication with expiration
- ✅ Input validation on all endpoints
- ✅ SQL injection prevention
- ✅ Rate limiting
- ✅ CORS configuration
- ✅ Security headers

### 7.2 Required Headers
```http
Content-Type: application/json
Authorization: Bearer [token]
X-Request-ID: [optional-tracking-id]
```

### 7.3 Security Headers (Response)
```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000
```

---

## 8. Examples

### 8.1 Complete Authentication Flow
```bash
# 1. Login
curl -X POST https://localhost:8443/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'

# Response
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "expires_in": 3600
}

# 2. Use token to get data
curl -X GET https://localhost:8443/api/data \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."

# 3. Refresh token before expiry
curl -X POST https://localhost:8443/api/auth/refresh \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

### 8.2 Python Client Example
```python
import requests
import json

class WeatherStationClient:
    def __init__(self, base_url="https://localhost:8443/api"):
        self.base_url = base_url
        self.token = None
    
    def login(self, username, password):
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"username": username, "password": password},
            verify=False  # Only for self-signed certs
        )
        if response.status_code == 200:
            self.token = response.json()["token"]
            return True
        return False
    
    def get_data(self):
        if not self.token:
            raise Exception("Not authenticated")
        
        response = requests.get(
            f"{self.base_url}/data",
            headers={"Authorization": f"Bearer {self.token}"},
            verify=False
        )
        return response.json()

# Usage
client = WeatherStationClient()
if client.login("user", "password"):
    data = client.get_data()
    print(f"Temperature: {data['data']['temperature']}°C")
```

### 8.3 JavaScript/Fetch Example
```javascript
// Login and get data
async function getWeatherData() {
    // Login
    const loginResponse = await fetch('https://localhost:8443/api/auth/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            username: 'user',
            password: 'password'
        })
    });
    
    const {token} = await loginResponse.json();
    
    // Get data
    const dataResponse = await fetch('https://localhost:8443/api/data', {
        headers: {'Authorization': `Bearer ${token}`}
    });
    
    return await dataResponse.json();
}
```

### 8.4 Error Handling Example
```python
def safe_api_call(url, token):
    try:
        response = requests.get(
            url,
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            # Token expired, refresh
            new_token = refresh_token(token)
            return safe_api_call(url, new_token)
        elif response.status_code == 429:
            # Rate limited, wait and retry
            retry_after = int(response.headers.get('Retry-After', 30))
            time.sleep(retry_after)
            return safe_api_call(url, token)
        else:
            # Other error
            error = response.json().get('error', 'Unknown error')
            raise Exception(f"API Error: {error}")
            
    except requests.RequestException as e:
        # Network error
        raise Exception(f"Network error: {e}")
```

---

## 9. Testing the API

### 9.1 Health Check
```bash
# No auth required
curl https://localhost:8443/api/status
```

### 9.2 Test Authentication
```bash
# Test with wrong credentials
curl -X POST https://localhost:8443/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "wrong", "password": "wrong"}'
# Should return 401
```

### 9.3 Test Rate Limiting
```bash
# Send multiple requests quickly
for i in {1..10}; do
  curl -X GET https://localhost:8443/api/data \
    -H "Authorization: Bearer [token]"
done
# Should get 429 after limit
```

---

## 10. Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | [Date] | Initial API implementation |
| | | - Basic authentication |
| | | - Data endpoints |
| | | - Rate limiting |

---

## 11. Support

For API issues or questions:
- Check error messages and codes
- Review security test results
- Contact instructor if needed

---

*API Documentation v1.0 | Weather Station IoT Security Lab*