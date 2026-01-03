# Docker & Docker Compose Comprehensive Lab

## Lab Overview
This lab covers Docker environment variables, volumes, networks, Dockerfiles, Docker registries, and Docker Compose in a practical, hands-on project. You'll build a multi-container application with a web app, database, and cache layer.

## Prerequisites
- Docker installed (version 20.10+)
- Docker Compose installed (version 2.0+)
- Basic command line knowledge

---

## Part 1: Docker Basics

### 1.1 Docker Volumes

**Example 1: PostgreSQL with Bind Mount**
```bash
# Create directory on host for PostgreSQL data
sudo mkdir -p /etc/postgresql
sudo chmod 777 /etc/postgresql

# Run PostgreSQL with bind mount
docker run -d --name postgres -p 5432:5432 --restart always \
  -e POSTGRES_PASSWORD=dev123 \
  -v /etc/postgresql:/var/lib/postgresql/data \
  postgres

# Verify PostgreSQL is running
docker logs postgres

# Connect to PostgreSQL
docker exec -it postgres psql -U postgres

# Check data persists on host
ls -la /etc/postgresql/

# Clean up
docker rm -f postgres
```

**Example 3: Nginx with Configuration Bind Mount**
```bash
# Create Nginx configuration file on host
sudo mkdir -p /srv
sudo nano /srv/default.conf
```

Add this content to `/srv/default.conf`:
```nginx
server {
    listen 80;
    server_name localhost;

    location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
    }

    location /api {
        proxy_pass http://backend:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Run Nginx with configuration mount:
```bash
# Run Nginx container with custom config
docker run -d --name nginx -p 80:80 --restart always \
  -v /srv/default.conf:/etc/nginx/conf.d/default.conf \
  nginx

# Verify Nginx is running
docker logs nginx

# Test Nginx
curl http://localhost

# Edit config without restarting container
sudo nano /srv/default.conf

# Reload Nginx configuration
docker exec nginx nginx -s reload

# Clean up
docker rm -f nginx
```

**Volume Types Comparison:**
```bash
# Named Volume (managed by Docker)
-v my-volume:/container/path

# Bind Mount (specific host path)
-v /host/path:/container/path

# Anonymous Volume (temporary)
-v /container/path
```

### 1.3 Docker Networks

**Example 1: Bridge Network with Multi-Container Application**

Create a custom bridge network for container communication:

```bash
# Create custom bridge network
docker network create taskmate

# List networks
docker network ls

# Inspect network details
docker network inspect taskmate

# Run PostgreSQL on the network
docker run -h postgres -d --name postgres --restart always \
  -e POSTGRES_USER=dev \
  -e POSTGRES_PASSWORD=dev123 \
  -e POSTGRES_DB=taskmate_db \
  --network taskmate \
  -v /etc/postgresql:/var/lib/postgresql/data \
  postgres

# Verify PostgreSQL is running
docker logs postgres

# Check network connectivity
docker network inspect taskmate
```

Create environment file for Django application:
```bash
# Create environment file
sudo nano /srv/.env
```

Add this content to `/srv/.env`:
```
DJANGO_SECRET_KEY=m+_p!pqmik7x+yb$562(fq%n4*(mt4_$fw(hl#8w2+imfhj9iv
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=0.0.0.0
HOST=postgres
DB_USER=dev
DB_PASSWORD=dev123
DB_DATABASE=taskmate_db
DB_PORT=5432
```

Run Django application container on the same network:
```bash
# Run Django app connected to the same network
docker run --env-file /srv/.env -d --name taskmate -p 8000:8000 \
  --network taskmate --restart always \
  sothy/taskmate:postgresql-db

# Verify application is running
docker logs taskmate

# Test network connectivity between containers
docker exec taskmate ping -c 3 postgres

# Access the application
curl http://localhost:8000
```

**Example 2: Host Network Mode**

Using host network mode, containers share the host's network stack directly:

```bash
# Run PostgreSQL with host network
# Container uses host's network directly (no port mapping needed)
docker run -d --name postgres --restart always \
  -e POSTGRES_USER=dev \
  -e POSTGRES_PASSWORD=dev123 \
  -e POSTGRES_DB=taskmate_db \
  --network host \
  -v /etc/postgresql:/var/lib/postgresql/data \
  postgres

# Verify PostgreSQL is running
docker logs postgres

# PostgreSQL is accessible on host's IP:5432 directly
netstat -tulpn | grep 5432
```

Create environment file for Django application:
```bash
# Create environment file
sudo nano /srv/.env
```

Add this content to `/srv/.env`:
```
DJANGO_SECRET_KEY=m+_p!pqmik7x+yb$562(fq%n4*(mt4_$fw(hl#8w2+imfhj9iv
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=0.0.0.0
HOST=165.22.97.180
DB_USER=dev
DB_PASSWORD=dev123
DB_DATABASE=taskmate_db
DB_PORT=5432
```

Run Django application with host network:
```bash
# Run Django app with host network
# No port mapping needed, app accessible on host's port 8000
docker run --env-file /srv/.env -d --name taskmate \
  --network host --restart always \
  sothy/taskmate:postgresql-db

# Verify application is running
docker logs taskmate

# Access the application on host's IP
curl http://165.22.97.180:8000
curl http://localhost:8000
```

---

## Part 2: Dockerfile Creation

### 2.1 Node.js with Express

Create `package.json`:
```json
{
  "name": "express-app",
  "version": "1.0.0",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "express": "^4.18.2"
  }
}
```

Create `server.js`:
```javascript
const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

app.get('/', (req, res) => {
  res.json({
    message: 'Hello from Express!',
    environment: process.env.NODE_ENV || 'development'
  });
});

app.get('/health', (req, res) => {
  res.json({ status: 'healthy' });
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on port ${PORT}`);
});
```

Create `Dockerfile`:
```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install --production

# Copy application code
COPY server.js .

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Run application
CMD ["npm", "start"]
```

Build and run:
```bash
# Build the image
docker build -t nodejs-app:1.0 .

# Run the container
docker run -d -p 3000:3000 --name nodejs-app nodejs-app:1.0

# Test the application
curl http://localhost:3000/api
curl http://localhost:3000/api/health
curl http://localhost:3000/api/info

# View logs
docker logs nodejs-app

# Follow logs
docker logs -f nodejs-app

# Clean up
docker rm -f nodejs-app
```

---

### 2.2 Python with Django

Create `requirements.txt`:
```
Django==4.2.7
psycopg2-binary==2.9.9
gunicorn==21.2.0
```

Create `.env`:
```
DJANGO_SECRET_KEY=your-secret-key-here-change-in-production
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=*
HOST=postgres
DB_USER=dev
DB_PASSWORD=dev123
DB_DATABASE=django_db
DB_PORT=5432
```

Create `manage.py`:
```python
#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
```

Create `myproject/__init__.py`:
```python
# Empty file
```

Create `myproject/settings.py`:
```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'dev-secret-key-change-in-production')
DEBUG = os.getenv('DJANGO_DEBUG', 'False') == 'True'

# Allow all hosts
allowed_hosts_env = os.getenv('DJANGO_ALLOWED_HOSTS', '*')
if allowed_hosts_env == '*':
    ALLOWED_HOSTS = ['*']
else:
    ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_env.split(',') if host.strip()]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'myproject.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_DATABASE', 'django_db'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
        'HOST': os.getenv('HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```

Create `myproject/urls.py`:
```python
from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from django.db import connection
import socket
import os

def home(request):
    # Test database connection
    db_status = 'connected'
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception as e:
        db_status = f'error: {str(e)}'
    
    return JsonResponse({
        'message': 'Hello from Django!',
        'hostname': socket.gethostname(),
        'environment': os.getenv('APP_ENV', 'development'),
        'database': db_status
    })

def health(request):
    return JsonResponse({'status': 'healthy'})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),
    path('health/', health),
]
```

Create `myproject/wsgi.py`:
```python
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
application = get_wsgi_application()
```

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000')" || exit 1

# Run with gunicorn
CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
```

Build and run:
```bash
# First, run PostgreSQL container
docker network create django-net

docker run -d --name postgres --network django-net \
  -e POSTGRES_USER=dev \
  -e POSTGRES_PASSWORD=dev123 \
  -e POSTGRES_DB=django_db \
  postgres:15-alpine

# Build Django image
docker build -t django-app:1.0 .

# Run Django migrations
docker run --rm --network django-net --env-file .env \
  django-app:1.0 python manage.py migrate

# Create superuser (optional)
docker run -it --rm --network django-net --env-file .env \
  django-app:1.0 python manage.py createsuperuser

# Run Django application
docker run -d -p 8000:8000 --name django-app \
  --network django-net --env-file .env \
  django-app:1.0

# Test the application
curl http://localhost:8000
curl http://localhost:8000/health

# View logs
docker logs django-app

# Clean up
docker rm -f django-app postgres
docker network rm django-net
```

---

### 2.3 C# .NET Core

Create `Program.cs`:
```csharp
var builder = WebApplication.CreateBuilder(args);

// Add services to the container
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

// Configure the HTTP request pipeline
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseAuthorization();
app.MapControllers();

app.Run();
```

Create `Controllers/HealthController.cs`:
```csharp
using Microsoft.AspNetCore.Mvc;

namespace DotnetApp.Controllers;

[ApiController]
[Route("[controller]")]
public class HealthController : ControllerBase
{
    [HttpGet]
    public IActionResult Get()
    {
        return Ok(new { status = "healthy", timestamp = DateTime.UtcNow });
    }
}
```

Create `Controllers/HomeController.cs`:
```csharp
using Microsoft.AspNetCore.Mvc;

namespace DotnetApp.Controllers;

[ApiController]
[Route("")]
public class HomeController : ControllerBase
{
    private readonly IConfiguration _configuration;

    public HomeController(IConfiguration configuration)
    {
        _configuration = configuration;
    }

    [HttpGet]
    public IActionResult Get()
    {
        return Ok(new
        {
            message = "Hello from .NET Core!",
            environment = Environment.GetEnvironmentVariable("ASPNETCORE_ENVIRONMENT") ?? "Production",
            hostname = Environment.MachineName,
            version = "1.0.0"
        });
    }

    [HttpGet("api/info")]
    public IActionResult GetInfo()
    {
        return Ok(new
        {
            app = "ASP.NET Core Web API",
            version = "1.0.0",
            dotnetVersion = Environment.Version.ToString()
        });
    }
}
```

Create `DotnetApp.csproj`:
```xml
<Project Sdk="Microsoft.NET.Sdk.Web">

  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <RootNamespace>DotnetApp</RootNamespace>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.AspNetCore.OpenApi" Version="8.0.0" />
    <PackageReference Include="Swashbuckle.AspNetCore" Version="6.5.0" />
  </ItemGroup>

</Project>
```

Create `appsettings.json`:
```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning"
    }
  },
  "AllowedHosts": "*"
}
```

Create `Dockerfile`:
```dockerfile
# Build stage
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# Copy csproj and restore
COPY *.csproj ./
RUN dotnet restore

# Copy everything else and build
COPY . ./
RUN dotnet publish -c Release -o /app/publish

# Runtime stage
FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app
COPY --from=build /app/publish .

EXPOSE 8080

ENV ASPNETCORE_URLS=http://+:8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

ENTRYPOINT ["dotnet", "DotnetApp.dll"]
```

Build and run:
```bash
docker build -t dotnet-app:1.0 .
docker run -d -p 8080:8080 --name dotnet-app dotnet-app:1.0
curl http://localhost:8080
```

---

### 2.4 Java Spring Boot

Create `pom.xml`:
```xml
<project>
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>spring-app</artifactId>
    <version>1.0.0</version>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.0</version>
    </parent>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-actuator</artifactId>
        </dependency>
    </dependencies>
    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
```

Create `src/main/java/com/example/Application.java`:
```java
package com.example;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.HashMap;
import java.util.Map;

@SpringBootApplication
@RestController
public class Application {

    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }

    @GetMapping("/")
    public Map<String, String> home() {
        Map<String, String> response = new HashMap<>();
        response.put("message", "Hello from Spring Boot!");
        response.put("environment", System.getenv().getOrDefault("SPRING_PROFILES_ACTIVE", "default"));
        return response;
    }

    @GetMapping("/api/info")
    public Map<String, String> info() {
        Map<String, String> response = new HashMap<>();
        response.put("app", "Spring Boot Application");
        response.put("version", "1.0.0");
        return response;
    }
}
```

Create `src/main/resources/application.properties`:
```properties
server.port=8080
management.endpoints.web.exposure.include=health,info
management.endpoint.health.show-details=always
```

Create `Dockerfile`:
```dockerfile
# Build stage
FROM maven:3.9-eclipse-temurin-17 AS build
WORKDIR /app

COPY pom.xml .
RUN mvn dependency:go-offline

COPY src ./src
RUN mvn clean package -DskipTests

# Runtime stage
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app

COPY --from=build /app/target/*.jar app.jar

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=30s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8080/actuator/health || exit 1

ENTRYPOINT ["java", "-jar", "app.jar"]
```

Build and run:
```bash
# Build the image
docker build -t java-app:1.0 .

# Run the container
docker run -d -p 8080:8080 --name java-app java-app:1.0

# Test the application
curl http://localhost:8080
curl http://localhost:8080/api/info
curl http://localhost:8080/actuator/health

# View logs
docker logs java-app

# Clean up
docker rm -f java-app
```

---

### 2.5 Angular with Nginx

Create project structure:
```bash
mkdir -p angular-app/src/app
cd angular-app
```

Create `angular.json`:
```json
{
  "$schema": "./node_modules/@angular/cli/lib/config/schema.json",
  "version": 1,
  "newProjectRoot": "projects",
  "projects": {
    "angular-app": {
      "projectType": "application",
      "root": "",
      "sourceRoot": "src",
      "prefix": "app",
      "architect": {
        "build": {
          "builder": "@angular-devkit/build-angular:browser",
          "options": {
            "outputPath": "dist/angular-app",
            "index": "src/index.html",
            "main": "src/main.ts",
            "polyfills": ["zone.js"],
            "tsConfig": "tsconfig.app.json",
            "assets": [],
            "styles": ["src/styles.css"],
            "scripts": []
          },
          "configurations": {
            "production": {
              "budgets": [
                {
                  "type": "initial",
                  "maximumWarning": "500kb",
                  "maximumError": "1mb"
                }
              ],
              "outputHashing": "all"
            }
          }
        }
      }
    }
  }
}
```

Create `tsconfig.json`:
```json
{
  "compileOnSave": false,
  "compilerOptions": {
    "baseUrl": "./",
    "outDir": "./dist/out-tsc",
    "forceConsistentCasingInFileNames": true,
    "strict": true,
    "noImplicitOverride": true,
    "noPropertyAccessFromIndexSignature": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "sourceMap": true,
    "declaration": false,
    "downlevelIteration": true,
    "experimentalDecorators": true,
    "moduleResolution": "node",
    "importHelpers": true,
    "target": "ES2022",
    "module": "ES2022",
    "useDefineForClassFields": false,
    "lib": ["ES2022", "dom"]
  },
  "angularCompilerOptions": {
    "enableI18nLegacyMessageIdFormat": false,
    "strictInjectionParameters": true,
    "strictInputAccessModifiers": true,
    "strictTemplates": true
  }
}
```

Create `tsconfig.app.json`:
```json
{
  "extends": "./tsconfig.json",
  "compilerOptions": {
    "outDir": "./out-tsc/app",
    "types": []
  },
  "files": ["src/main.ts"],
  "include": ["src/**/*.d.ts"]
}
```

Create `src/index.html`:
```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Angular Docker App</title>
  <base href="/">
  <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
  <app-root></app-root>
</body>
</html>
```

Create `src/main.ts`:
```typescript
import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
import { AppModule } from './app/app.module';

platformBrowserDynamic().bootstrapModule(AppModule)
  .catch(err => console.error(err));
```

Create `src/styles.css`:
```css
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
    Ubuntu, Cantarell, 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
```

Create `src/app/app.module.ts`:
```typescript
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { AppComponent } from './app.component';

@NgModule({
  declarations: [AppComponent],
  imports: [BrowserModule, HttpClientModule],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
```

Create `src/app/app.component.ts`:
```typescript
import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-root',
  template: `
    <div class="container">
      <h1>{{ title }}</h1>
      <p>{{ message }}</p>
      <button (click)="fetchData()">Fetch Data</button>
      <div *ngIf="data">
        <pre>{{ data | json }}</pre>
      </div>
    </div>
  `,
  styles: [`
    .container {
      padding: 20px;
      text-align: center;
    }
  `]
})
export class AppComponent {
  title = 'Angular Docker App';
  message = 'Welcome to Angular with Docker!';
  data: any;

  constructor(private http: HttpClient) {}

  fetchData() {
    this.http.get('/api/info').subscribe(
      response => this.data = response,
      error => console.error('Error:', error)
    );
  }
}
```

Create `package.json`:
```json
{
  "name": "angular-app",
  "version": "1.0.0",
  "scripts": {
    "ng": "ng",
    "start": "ng serve",
    "build": "ng build",
    "build:prod": "ng build --configuration production"
  },
  "dependencies": {
    "@angular/animations": "^17.0.0",
    "@angular/common": "^17.0.0",
    "@angular/compiler": "^17.0.0",
    "@angular/core": "^17.0.0",
    "@angular/platform-browser": "^17.0.0",
    "@angular/platform-browser-dynamic": "^17.0.0"
  },
  "devDependencies": {
    "@angular-devkit/build-angular": "^17.0.0",
    "@angular/cli": "^17.0.0",
    "@angular/compiler-cli": "^17.0.0",
    "typescript": "~5.2.0"
  }
}
```

Create `nginx.conf`:
```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Uncomment if you have a backend API server
    # location /api {
    #     proxy_pass http://backend:8080;
    #     proxy_set_header Host $host;
    #     proxy_set_header X-Real-IP $remote_addr;
    # }
}
```

Create `Dockerfile`:
```dockerfile
# Build stage
FROM node:18-alpine AS build
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy source and build
COPY . .
RUN npm run build -- --configuration production

# Runtime stage
FROM nginx:alpine

# Copy built app to nginx
COPY --from=build /app/dist/angular-app /usr/share/nginx/html

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:80 || exit 1

CMD ["nginx", "-g", "daemon off;"]
```

Build and run:
```bash
# Build the image
docker build -t angular-app:1.0 .

# Run the container
docker run -d -p 80:80 --name angular-app angular-app:1.0

# Test the application
curl http://localhost

# View logs
docker logs angular-app

# Clean up
docker rm -f angular-app
```

---

### 2.6 React with Nginx

Create `public/index.html`:
```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="React Docker App" />
    <title>React Docker App</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
```

Create `src/index.js`:
```javascript
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

Create `src/index.css`:
```css
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}
```

Create `src/App.css`:
```css
.App {
  text-align: center;
}

.App-header {
  background-color: #282c34;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-size: calc(10px + 2vmin);
  color: white;
}

.App-header h1 {
  margin: 0;
  margin-bottom: 20px;
}

.App-header p {
  margin: 10px 0 20px 0;
}

.App-header button {
  background-color: #61dafb;
  border: none;
  color: #282c34;
  padding: 15px 32px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  font-size: 16px;
  margin: 4px 2px;
  cursor: pointer;
  border-radius: 4px;
  font-weight: bold;
}

.App-header button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.App-header pre {
  background-color: #1e1e1e;
  padding: 20px;
  border-radius: 5px;
  text-align: left;
  overflow-x: auto;
  max-width: 500px;
}
```

Create `src/App.js`:
```javascript
import React, { useState } from 'react';
import './App.css';

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/info');
      const json = await response.json();
      setData(json);
    } catch (error) {
      console.error('Error:', error);
    }
    setLoading(false);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>React Docker App</h1>
        <p>Welcome to React with Docker!</p>
        <button onClick={fetchData} disabled={loading}>
          {loading ? 'Loading...' : 'Fetch Data'}
        </button>
        {data && (
          <pre>{JSON.stringify(data, null, 2)}</pre>
        )}
      </header>
    </div>
  );
}

export default App;
```

Create `package.json`:
```json
{
  "name": "react-app",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": ["react-app"]
  },
  "browserslist": {
    "production": [">0.2%", "not dead", "not op_mini all"],
    "development": ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"]
  }
}
```

Create `nginx.conf`:
```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Uncomment if you have a backend API server
    # location /api {
    #     proxy_pass http://api-server:3000;
    #     proxy_set_header Host $host;
    #     proxy_set_header X-Real-IP $remote_addr;
    # }
}
```

Create `Dockerfile`:
```dockerfile
# Build stage
FROM node:18-alpine AS build
WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# Runtime stage
FROM nginx:alpine

COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost || exit 1

CMD ["nginx", "-g", "daemon off;"]
```

Build and run:
```bash
# Build the image
docker build -t react-app:1.0 .

# Run the container
docker run -d -p 80:80 --name react-app react-app:1.0

# Test the application
curl http://localhost

# View logs
docker logs react-app

# Clean up
docker rm -f react-app
```
---

### 2.7 Nuxt.js (Vue Meta-Framework) with Nginx

**Note:** Nuxt.js is built on top of Vue.js and provides additional features like server-side rendering, static site generation, and file-based routing.

Create project structure:
```bash
mkdir -p nuxt-app/pages
mkdir -p nuxt-app/public
cd nuxt-app
```

Create `pages/index.vue`:
```vue
<template>
  <div class="container">
    <h1>{{ title }}</h1>
    <p>{{ message }}</p>
    <button @click="fetchData" :disabled="loading">
      {{ loading ? 'Loading...' : 'Fetch Data' }}
    </button>
    <pre v-if="data">{{ JSON.stringify(data, null, 2) }}</pre>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const title = 'Nuxt.js Docker App'
const message = 'Welcome to Nuxt.js with Docker!'
const data = ref(null)
const loading = ref(false)

const fetchData = async () => {
  loading.value = true
  try {
    const response = await fetch('/api/info')
    data.value = await response.json()
  } catch (error) {
    console.error('Error:', error)
  }
  loading.value = false
}
</script>

<style scoped>
.container {
  padding: 20px;
  text-align: center;
}

h1 {
  font-size: 3rem;
  margin-bottom: 20px;
  color: #00dc82;
}

p {
  font-size: 1.5rem;
  margin-bottom: 30px;
}

button {
  padding: 12px 24px;
  font-size: 16px;
  cursor: pointer;
  margin: 10px;
  background-color: #00dc82;
  color: white;
  border: none;
  border-radius: 5px;
  font-weight: bold;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

button:hover:not(:disabled) {
  background-color: #00b868;
}

pre {
  background-color: #1e1e1e;
  color: #00dc82;
  padding: 20px;
  border-radius: 5px;
  text-align: left;
  overflow-x: auto;
  max-width: 500px;
  margin: 20px auto;
}
</style>
```

Create `app.vue` (root component):
```vue
<template>
  <div>
    <NuxtPage />
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
    Ubuntu, Cantarell, 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #f5f5f5;
}
</style>
```

Create `nuxt.config.ts`:
```typescript
// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  // Disable server-side rendering for static export
  ssr: false,
  
  // Static site generation
  nitro: {
    preset: 'static'
  },
  
  // App configuration
  app: {
    head: {
      title: 'Nuxt.js Docker App',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'Nuxt.js application with Docker' }
      ]
    }
  },

  // Development server configuration
  devServer: {
    port: 3000
  }
})
```

Create `package.json`:
```json
{
  "name": "nuxt-app",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "nuxt dev",
    "build": "nuxt build",
    "generate": "nuxt generate",
    "preview": "nuxt preview",
    "postinstall": "nuxt prepare"
  },
  "dependencies": {
    "nuxt": "^3.8.0",
    "vue": "^3.3.0"
  },
  "devDependencies": {
    "@nuxt/devtools": "^1.0.0"
  }
}
```

Create `.gitignore`:
```
# Nuxt dev/build outputs
.output
.nuxt
.nitro
.cache
dist

# Node dependencies
node_modules

# Logs
*.log

# Misc
.DS_Store
.fleet
.idea

# Local env files
.env
.env.*
!.env.example
```

Create `nginx.conf`:
```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # Enable gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript 
               application/x-javascript application/xml+rss 
               application/javascript application/json;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Uncomment if you have a backend API server
    # location /api {
    #     proxy_pass http://backend:8080;
    #     proxy_set_header Host $host;
    #     proxy_set_header X-Real-IP $remote_addr;
    #     proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    # }
}
```

Create `Dockerfile`:
```dockerfile
# Build stage
FROM node:18-alpine AS build
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application files
COPY . .

# Generate static site
RUN npm run generate

# Runtime stage
FROM nginx:alpine

# Copy generated static files
COPY --from=build /app/.output/public /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost || exit 1

CMD ["nginx", "-g", "daemon off;"]
```

Build and run:
```bash
# Build the image
docker build -t nuxt-app:1.0 .

# Run the container
docker run -d -p 80:80 --name nuxt-app nuxt-app:1.0

# Test the application
curl http://localhost

# View logs
docker logs nuxt-app

# Clean up
docker rm -f nuxt-app
```

---

## Part 3: Working with Docker Registry
### 3.1: With Docker Hub
```bash
# Run local registry
docker build . -t your_docker_hub_id/repo_name:tag
# Login to registry
docker login -u your_id -p your_password
# Push images to registry
docker push your_docker_hub_id/repo_name:tag

```
### 3.2: With DigitalOcean Container Registry
```bash
# Run local registry
docker build . -t registry.digitalocean.com/your_repo/repo_name:tag
# Login to registry
docker login registry.digitalocean.com -u your_id -p your_password
# Push images to registry
docker push registry.digitalocean.com/your_repo/repo_name:tag

```
---

## Part 4: Docker Compose Application

### 4.1 Complete Multi-Container Application

Create `docker-compose.yml`:
```yaml
version: '3.9'

services:
  web:
    build:
      context: .
      dockerfile: Dockerfile
    image: myapp:latest
    container_name: web-app
    ports:
      - "5000:5000"
    environment:
      - APP_ENV=production
      - DB_HOST=postgres
      - DB_PORT=5432
      - REDIS_HOST=redis
    env_file:
      - .env
    volumes:
      - ./app.py:/app/app.py
      - app-logs:/app/logs
    networks:
      - frontend
      - backend
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    container_name: postgres-db
    environment:
      POSTGRES_DB: ${DB_NAME:-mydb}
      POSTGRES_USER: ${DB_USER:-admin}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-secret123}
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./init-db.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - backend
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-admin}"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: redis-cache
    command: redis-server --appendonly yes
    volumes:
      - redis-data:/data
    networks:
      - backend
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: nginx-proxy
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - nginx-logs:/var/log/nginx
    networks:
      - frontend
    depends_on:
      - web
    restart: unless-stopped

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true

volumes:
  postgres-data:
  redis-data:
  app-logs:
  nginx-logs:
```

### 4.2 Docker Compose Commands

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f

# List running services
docker compose ps

# Execute command in service
docker compose exec web sh

# Scale service
docker compose up -d --scale web=3

# Stop services
docker compose stop

# Restart service
docker compose restart web

# Remove containers
docker compose down

# Remove everything including volumes
docker compose down -v

# Build services
docker compose build

# View resource usage
docker compose stats
```

---

## Part 5: Troubleshooting Commands

```bash
# View container logs
docker logs <container-name>
docker compose logs <service-name>

# Inspect container
docker inspect <container-name>

# View container processes
docker top <container-name>

# View resource usage
docker stats

# Execute shell in container
docker exec -it <container-name> sh

# View networks
docker network ls
docker network inspect <network-name>

# View volumes
docker volume ls
docker volume inspect <volume-name>

# Remove unused resources
docker system prune
docker volume prune
docker network prune

# View disk usage
docker system df
```

---

## Lab Exercises

### Exercise 1: Environment Variables
1. Create a container with 5 custom environment variables
2. Use an env file to manage configuration
3. Override env file variables with command-line args

### Exercise 2: Volumes
1. Create a named volume and persist data across container restarts
2. Use bind mounts to share code between host and container
3. Create a volume backup using `docker run`

### Exercise 3: Networks
1. Create custom bridge networks for frontend and backend
2. Connect containers to multiple networks
3. Test network isolation between frontend and backend

### Exercise 4: Build and Registry
1. Build a custom image with your own application
2. Push to local registry
3. Pull and run from registry

### Exercise 5: Docker Compose
1. Launch the complete stack with `docker compose up`
2. Scale the web service to 3 instances
3. Verify all health checks pass
4. Test database connectivity
5. Monitor logs and resource usage

---

## Summary

You've learned:
- ✅ Docker environment variables and env files
- ✅ Docker volumes (named volumes and bind mounts)
- ✅ Docker networks (bridge, custom networks)
- ✅ Writing Dockerfiles with best practices
- ✅ Multi-stage builds for optimization
- ✅ Working with Docker registries
- ✅ Docker Compose for multi-container applications
- ✅ Service dependencies and health checks
- ✅ Scaling and orchestration basics
- ✅ Production-ready configurations
