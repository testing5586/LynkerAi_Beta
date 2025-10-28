# LynkerAI Local Development Setup (VSCode)

This guide will help you set up LynkerAI for local development in VSCode.

## Prerequisites

- Python 3.11+
- PostgreSQL database (or use a cloud provider like Neon/Supabase)
- Node.js 18+ (if working with frontend)
- Git

## Step 1: Clone the Repository

```bash
git clone https://github.com/testing5586/LynkerAi_Beta.git
cd LynkerAi_Beta
```

## Step 2: Set Up Environment Variables

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Fill in your actual values in `.env`:**

   Open `.env` in VSCode and replace all placeholder values with your actual credentials:

   ```env
   # Get your OpenAI API key from https://platform.openai.com/api-keys
   OPENAI_API_KEY=sk-proj-YOUR_ACTUAL_KEY_HERE
   LYNKER_MASTER_KEY=sk-proj-YOUR_ACTUAL_KEY_HERE
   
   # Get your Supabase credentials from https://supabase.com/dashboard
   SUPABASE_URL=https://YOUR_PROJECT.supabase.co
   SUPABASE_KEY=YOUR_SUPABASE_ANON_KEY
   
   # Set up your PostgreSQL database
   DATABASE_URL=postgresql://user:password@localhost:5432/lynkerai
   PGHOST=localhost
   PGPORT=5432
   PGDATABASE=lynkerai
   PGUSER=your_db_user
   PGPASSWORD=your_db_password
   
   # Generate a random 32-character key for encryption
   MASTER_VAULT_KEY=your_32_character_random_string
   TMS_SECRET_KEY=your_tms_secret_key
   ```

3. **Where to get your credentials from Replit:**
   - Go to your Replit project
   - Click **Tools** → **Secrets**
   - Copy each secret value and paste into your local `.env`

## Step 3: Install Python Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

If you don't have a `requirements.txt`, install manually:

```bash
pip install flask flask-socketio openai pandas python-socketio pyyaml requests supabase psycopg2-binary cryptography python-dotenv
```

## Step 4: Load Environment Variables

Add this to the top of your main files (e.g., `admin_dashboard/app.py`):

```python
from dotenv import load_dotenv
load_dotenv()  # This loads .env file
```

## Step 5: Run the Application

```bash
# Navigate to admin dashboard
cd admin_dashboard

# Run Flask app
python app.py
```

The app should now be running on `http://localhost:5000`

## Step 6: Database Setup (if needed)

If you're using a local PostgreSQL database:

1. **Create database:**
   ```sql
   CREATE DATABASE lynkerai;
   ```

2. **Run migrations** (if you have them):
   ```bash
   # Your migration commands here
   ```

## Troubleshooting

### Missing Environment Variables
**Error:** `KeyError` or `NoneType` errors
**Solution:** Make sure all required variables in `.env` are filled in

### Database Connection Errors
**Error:** `psycopg2.OperationalError`
**Solution:** 
- Check your DATABASE_URL is correct
- Make sure PostgreSQL is running
- Verify username/password

### Import Errors
**Error:** `ModuleNotFoundError`
**Solution:** 
```bash
pip install -r requirements.txt
# or
pip install python-dotenv
```

## Key Differences: Replit vs Local

| Feature | Replit | VSCode Local |
|---------|--------|--------------|
| Environment Variables | Replit Secrets (auto-loaded) | `.env` file (manual setup) |
| Database | Auto-provisioned PostgreSQL | Self-hosted or cloud |
| Port | Always 5000 | Configurable (default 5000) |
| Hot Reload | Built-in | Use Flask debug mode |

## Security Reminders

- ✅ **NEVER commit `.env` to Git**
- ✅ `.gitignore` already protects `.env`
- ✅ Use `.env.example` to share structure (not secrets)
- ✅ Rotate API keys regularly
- ✅ Use different keys for dev/production

## Need Help?

If you encounter issues:
1. Check that `.env` has all required variables
2. Verify your virtual environment is activated
3. Ensure PostgreSQL is running
4. Check the console logs for specific error messages

---

**Happy coding!** 🚀
