# SPECTER Legal Assistant - Deployment Guide

## Quick Deployment with MongoDB Atlas + Render.com

### Step 1: Set up MongoDB Atlas (Free)

1. Go to [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create a free account
3. Create a new cluster (choose the free M0 tier)
4. Create a database user:
   - Go to Database Access
   - Add New Database User
   - Choose Password authentication
   - Set username and password
   - Grant "Read and write to any database" role
5. Configure Network Access:
   - Go to Network Access
   - Add IP Address
   - Choose "Allow access from anywhere" (0.0.0.0/0) for simplicity
6. Get connection string:
   - Go to Clusters
   - Click "Connect"
   - Choose "Connect your application"
   - Copy the connection string (looks like: `mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority`)

### Step 2: Deploy Backend to Render.com

1. Go to [Render.com](https://render.com) and create account
2. Connect your GitHub repository
3. Create a new Web Service
4. Configure the service:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3
5. Add environment variables:
   - `MONGODB_URL`: Your MongoDB Atlas connection string
   - `DATABASE_NAME`: `specter_legal`
   - `JWT_SECRET_KEY`: Generate a secure random string
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `LAWYER_SMTP_USER`: Your Gmail address (optional)
   - `LAWYER_SMTP_PASS`: Your Gmail app password (optional)
   - `LAWYER_RECEIVER_EMAIL`: Lawyer email address (optional)
6. Deploy the service

### Step 3: Migrate Data to MongoDB

After deployment, run the migration script:

```bash
# Set your MongoDB connection string
export MONGODB_URL="your-mongodb-atlas-connection-string"
export DATABASE_NAME="specter_legal"

# Run migration
cd backend
python migrate_to_mongo.py
```

### Step 4: Update Frontend Configuration

1. Get your deployed backend URL from Render (e.g., `https://your-app.onrender.com`)
2. Update the Netlify environment variables:
   - Go to your Netlify dashboard
   - Go to Site settings > Environment variables
   - Add `REACT_APP_API_URL` with your backend URL
3. Redeploy the frontend:
   ```bash
   netlify deploy --prod --dir=frontend/react_app/build
   ```

### Step 5: Test the Application

1. Visit your Netlify frontend URL
2. Try to register a new account
3. Test login functionality
4. Test the chat features

## Alternative: Local Development with MongoDB

If you want to test locally with MongoDB:

1. Install MongoDB locally or use Docker:
   ```bash
   # Using Docker
   docker run -d -p 27017:27017 --name mongodb mongo:latest
   ```

2. Set environment variables:
   ```bash
   export MONGODB_URL="mongodb://localhost:27017"
   export DATABASE_NAME="specter_legal"
   ```

3. Run migration:
   ```bash
   cd backend
   python migrate_to_mongo.py
   ```

4. Start the backend:
   ```bash
   cd backend
   python main.py
   ```

## Troubleshooting

### Common Issues:

1. **MongoDB Connection Error**: Check your connection string and network access settings
2. **Authentication Error**: Ensure JWT_SECRET_KEY is set and consistent
3. **CORS Error**: Make sure your frontend URL is added to the CORS origins in main.py
4. **Migration Error**: Ensure SQLite databases exist before running migration

### Environment Variables Checklist:

**Required:**
- `MONGODB_URL`
- `DATABASE_NAME`
- `JWT_SECRET_KEY`

**Optional:**
- `OPENAI_API_KEY` (for AI features)
- `LAWYER_SMTP_USER` (for email features)
- `LAWYER_SMTP_PASS` (for email features)
- `LAWYER_RECEIVER_EMAIL` (for email features)

## Production Considerations

1. **Security**: Use strong JWT secrets and secure MongoDB credentials
2. **Monitoring**: Set up logging and monitoring for your deployed services
3. **Backup**: Regular database backups through MongoDB Atlas
4. **SSL**: Ensure all connections use HTTPS/TLS
5. **Rate Limiting**: Consider adding rate limiting for API endpoints
