# Production-Like Local Setup for Varivilambarangal

This setup allows you to test your Django + React application in a production-like environment locally, helping you debug integration issues before deploying to production.

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)
Run the setup script to configure everything automatically:

```powershell
.\setup_prod_local.ps1
```

This will:
- Create environment configuration files
- Set up Python virtual environment
- Install dependencies
- Run database migrations
- Build the frontend
- Create startup scripts

### Option 2: Manual Setup
If you prefer to set up manually:

1. **Configure Environment Variables**
   ```powershell
   # Backend
   Copy-Item backend\.env backend\.env.prod.local
   # Edit .env.prod.local with your settings

   # Frontend
   Copy-Item frontend\.env.local frontend\.env.prod.local
   # Edit .env.prod.local with API URL
   ```

2. **Setup Python Environment**
   ```powershell
   cd backend
   python -m venv .venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

3. **Setup Database**
   ```powershell
   # Make sure PostgreSQL is running
   createdb -U postgres classified_ads
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```

4. **Build Frontend**
   ```powershell
   cd ../frontend
   npm install
   npm run build
   ```

## 🏃 Running the Application

### Start Both Services
```powershell
.\start_prod_local.ps1
```

### Start Services Individually
```powershell
# Backend only
.\start_backend_prod_local.ps1

# Frontend only
.\start_frontend_prod_local.ps1
```

## 🌐 Access URLs

- **Frontend**: http://localhost:3000
- **Backend API**: https://varivilambarangal.com/api (or http://localhost:8000/api locally)
- **Django Admin**: http://localhost:8000/admin
- **Production Domain**: https://varivilambarangal.com (IP: 46.225.238.87)

## 🔧 Configuration Files

### Backend (.env.prod.local)
```env
DJANGO_ENV=prod
DEBUG=False
SECRET_KEY=dev-secret-key-change-in-prod-local-testing-only
ALLOWED_HOSTS=varivilambarangal.com,www.varivilambarangal.com,46.225.238.87
POSTGRES_DB=classified_ads
POSTGRES_USER=postgres
POSTGRES_PASSWORD=AAlkas@*&^
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
CORS_ALLOWED_ORIGINS=https://varivilambarangal.com,https://www.varivilambarangal.com,http://46.225.238.87
CSRF_TRUSTED_ORIGINS=https://varivilambarangal.com,https://www.varivilambarangal.com
```

### Frontend (.env.prod.local)
```env
NEXT_PUBLIC_API_URL=https://varivilambarangal.com/api
```

## 🐛 Debugging API Integration Issues

### 1. Check API Calls
- Open browser DevTools (F12)
- Go to Network tab
- Look for failed API requests (status codes 4xx/5xx)

### 2. Common Issues & Solutions

#### CORS Errors
- **Symptom**: `Access-Control-Allow-Origin` errors
- **Check**: Ensure `CORS_ALLOWED_ORIGINS` includes your frontend URL
- **Fix**: Update `backend/.env.prod.local`

#### API 404/500 Errors
- **Symptom**: API endpoints return 404 or 500
- **Check**: Backend logs for errors
- **Fix**: Check database connection, run migrations

#### Static Assets Not Loading
- **Symptom**: React app loads but CSS/JS missing
- **Check**: `npm run build` completed successfully
- **Fix**: Rebuild frontend: `cd frontend && npm run build`

#### Wrong API URL
- **Symptom**: API calls go to wrong URL
- **Check**: `NEXT_PUBLIC_API_URL` in frontend environment
- **Fix**: Update `frontend/.env.prod.local`

### 3. Testing API Endpoints

Test your API directly:
```bash
# Test LOV endpoint
curl http://localhost:8000/api/lov/

# Test with parameters
curl "http://localhost:8000/api/v1/lov/?type=CITY&language=en"
```

### 4. Check Logs

**Backend Logs**: Check terminal where backend is running
**Frontend Logs**: Check terminal where frontend is running
**Browser Console**: F12 → Console tab

## 📋 Production Deployment Checklist

Before deploying to production, ensure:

1. ✅ **Domain & IP**: varivilambarangal.com (IP: 46.225.238.87)
2. ✅ **Database**: PostgreSQL configured with proper credentials for 'classified_ads'
3. ✅ **Environment Variables**: All production secrets set
4. ✅ **ALLOWED_HOSTS**: Includes varivilambarangal.com, www.varivilambarangal.com, 46.225.238.87
5. ✅ **CORS Settings**: Allows https://varivilambarangal.com, https://www.varivilambarangal.com
6. ✅ **SSL/HTTPS**: Configure SSL certificates for the domain
7. ✅ **Static Files**: WhiteNoise or CDN configured
8. ✅ **Security**: Strong SECRET_KEY, DEBUG=False
9. ✅ **Reverse Proxy**: nginx or similar for serving both frontend and backend
10. ✅ **DNS**: Point varivilambarangal.com to IP 46.225.238.87

## 🆘 Troubleshooting

### PostgreSQL Issues
```bash
# Check if PostgreSQL is running
pg_isready -h localhost -p 5432

# Create database if missing
createdb -U postgres classified_ads

# Reset database
dropdb -U postgres classified_ads
createdb -U postgres classified_ads
cd backend && python manage.py migrate
```

### Port Conflicts
- Backend uses port 8000
- Frontend uses port 3000
- If ports are busy, kill processes or change ports

### Permission Issues
- Ensure PostgreSQL user has proper permissions
- Check file permissions for logs and static files

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all environment variables are set correctly
3. Ensure PostgreSQL is running and accessible
4. Check that both services started without errors