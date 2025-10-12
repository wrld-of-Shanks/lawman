# Deploy SPECTER to Cloud (Free)

## Step 1: Set up MongoDB Atlas (Free Database)

1. Go to [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create a free account
3. Create a new cluster:
   - Choose "M0 Sandbox" (FREE)
   - Choose any cloud provider/region
   - Name your cluster (e.g., "specter-cluster")
4. Create a database user:
   - Go to "Database Access"
   - Click "Add New Database User"
   - Choose "Password" authentication
   - Username: `specter_user`
   - Password: Generate a secure password (save it!)
   - Database User Privileges: "Read and write to any database"
5. Configure Network Access:
   - Go to "Network Access"
   - Click "Add IP Address"
   - Choose "Allow access from anywhere" (0.0.0.0/0)
6. Get connection string:
   - Go to "Clusters"
   - Click "Connect" on your cluster
   - Choose "Connect your application"
   - Copy the connection string (looks like: `mongodb+srv://specter_user:PASSWORD@cluster.mongodb.net/?retryWrites=true&w=majority`)
   - Replace `<password>` with your actual password

## Step 2: Deploy Backend to Render.com

1. Go to [Render.com](https://render.com)
2. Create a free account
3. Connect your GitHub account
4. Create a new "Web Service"
5. Connect your repository: `wrld-of-Shanks/lawman`
6. Configure the service:
   - **Name**: `specter-backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
7. Add Environment Variables:
   - `MONGODB_URL`: Your MongoDB Atlas connection string
   - `DATABASE_NAME`: `specter_legal`
   - `JWT_SECRET_KEY`: Generate a random 32-character string
   - `OPENAI_API_KEY`: Your OpenAI API key (optional)
8. Click "Create Web Service"
9. Wait for deployment (5-10 minutes)
10. Copy your backend URL (e.g., `https://specter-backend.onrender.com`)

## Step 3: Migrate Data to MongoDB Atlas

After backend is deployed, run migration locally:

```bash
# Set your MongoDB Atlas connection string
export MONGODB_URL="your-mongodb-atlas-connection-string"
export DATABASE_NAME="specter_legal"

# Run migration
cd backend
python migrate_to_mongo.py
```

## Step 4: Update Frontend to Use Hosted Backend

1. Go to [Netlify Dashboard](https://app.netlify.com)
2. Find your "specter-legal-assistant" site
3. Go to "Site settings" → "Environment variables"
4. Add/Update:
   - `REACT_APP_API_URL`: Your Render backend URL (e.g., `https://specter-backend.onrender.com`)
5. Go to "Deploys" → "Trigger deploy" → "Deploy site"

## Step 5: Test Your Deployed App

1. Visit your Netlify URL: https://specter-legal-assistant.netlify.app
2. Try registering a new account
3. Test login functionality
4. Test on your phone!

## Quick Commands Summary

```bash
# 1. Set up MongoDB connection
export MONGODB_URL="mongodb+srv://specter_user:PASSWORD@cluster.mongodb.net/?retryWrites=true&w=majority"

# 2. Migrate data
cd backend && python migrate_to_mongo.py

# 3. Test locally first
MONGODB_URL="$MONGODB_URL" DATABASE_NAME="specter_legal" python main.py

# 4. Deploy to Render.com (through their web interface)

# 5. Update Netlify environment variable
# REACT_APP_API_URL=https://your-backend.onrender.com
```

## Troubleshooting

- **MongoDB Connection Error**: Check your connection string and network access
- **Render Deployment Failed**: Check build logs in Render dashboard
- **CORS Error**: Make sure your Netlify URL is in the CORS origins in main.py
- **Login Still Not Working**: Clear browser cache and try again

## Free Tier Limitations

- **MongoDB Atlas**: 512MB storage (plenty for this app)
- **Render.com**: Apps sleep after 15 minutes of inactivity (first request may be slow)
- **Netlify**: 100GB bandwidth per month

Your app will be fully functional on these free tiers!
