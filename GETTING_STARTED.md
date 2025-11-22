# Getting Started - Quick Start Guide

This guide will walk you through setting up your trading system from scratch.

## Prerequisites Checklist

Before you begin, ensure you have:

- [ ] PostgreSQL 15+ installed
- [ ] Python 3.11+ installed
- [ ] Git installed
- [ ] VS Code installed (optional but recommended)

## Step-by-Step Setup

### Step 1: PostgreSQL Setup

**Install PostgreSQL** (if not already installed):
1. Download from: https://www.postgresql.org/download/windows/
2. Run the installer, use default port 5432
3. **Important**: Remember the password you set for the `postgres` user

**Create Database and User:**

Open Command Prompt and run:

```cmd
# Connect to PostgreSQL as superuser
psql -U postgres

# You'll be prompted for the postgres password
```

In the psql prompt, run:

```sql
-- Create the database
CREATE DATABASE trading_ai;

-- Create dedicated user
CREATE USER trading_user WITH PASSWORD 'your_secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE trading_ai TO trading_user;

-- Connect to the database
\c trading_ai

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO trading_user;

-- Exit psql
\q
```

**Verify the database:**

```cmd
psql -U trading_user -d trading_ai
# Enter your password when prompted
# If successful, you'll see: trading_ai=>

\q
```

---

### Step 2: Python Environment Setup

**Navigate to project directory:**

```cmd
cd C:\Users\jonat\OneDrive\Desktop\ai\projects\trading-ai
```

**Create virtual environment:**

```cmd
python -m venv venv
```

**Activate virtual environment:**

```cmd
venv\Scripts\activate
```

You should see `(venv)` in your command prompt.

**Upgrade pip:**

```cmd
python -m pip install --upgrade pip
```

**Install dependencies:**

```cmd
pip install -r requirements.txt
```

This will take a few minutes. You should see all packages installing.

---

### Step 3: Environment Configuration

**Create .env file:**

Copy the example file:

```cmd
copy .env.example .env
```

**Edit .env file:**

Open `.env` in VS Code or any text editor and update:

```env
# Update these with your actual values
DB_PASSWORD=your_secure_password  # The password you set for trading_user
INITIAL_CAPITAL=800               # Your starting capital
```

**Save the file.**

---

### Step 4: Database Initialization

**Run database setup:**

```cmd
python scripts/setup_database.py
```

**Expected output:**

```
============================================================
Trading System Database Setup
============================================================
Database: trading_ai
Host: localhost:5432
User: trading_user

Testing database connection...
✓ Database connection successful

Creating database tables...

✓ Created 6 tables:
  - market_data
  - indicators
  - signals
  - backtest_trades
  - backtest_runs
  - live_trades

============================================================
Database setup completed successfully!
============================================================
```

**If you get an error:**
- Check PostgreSQL is running (Windows Services)
- Verify credentials in `.env`
- Ensure database and user were created correctly

---

### Step 5: Verify Setup

**Run verification script:**

```cmd
python scripts/verify_setup.py
```

**Expected output:**

All checks should pass:

```
✓ Python version: 3.11.x
✓ Virtual environment: Active
✓ Environment variables: All set
✓ Required packages: All installed
✓ Project structure: Complete
✓ Database connection: Success
✓ All tables exist

Setup verification complete!
```

---

### Step 6: Initialize Git Repository

**First commit:**

```cmd
git add .
git commit -m "Initial project setup with documentation and database schema"
```

---

## You're Ready!

Your development environment is now set up. Here's what you have:

✅ PostgreSQL database with all tables created
✅ Python environment with all dependencies
✅ Project structure in place
✅ Configuration files ready
✅ Git repository initialized

## Next Steps

### Option 1: Start Development (Week 1)

Follow the development roadmap in `DEVELOPMENT_ROADMAP.md`:

1. **This week**: Build data ingestion
   - Create data fetcher
   - Download 6 months of historical data
   - Load into database

**Start here:**
```cmd
# Create the data fetcher module (you'll build this)
# See DEVELOPMENT_ROADMAP.md Week 1 for detailed tasks
```

### Option 2: Quick Test (Recommended First)

Create a simple test to verify everything works:

**Create `test_connection.py`:**

```python
# test_connection.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from database.connection import engine
from config import Config
import yfinance as yf

# Test 1: Database connection
print("Testing database connection...")
with engine.connect() as conn:
    print("✓ Database connected successfully")

# Test 2: Configuration
print(f"\n✓ Config loaded:")
print(f"  Risk per trade: {Config.RISK_PER_TRADE_PCT}%")
print(f"  Initial capital: ${Config.INITIAL_CAPITAL}")

# Test 3: Data fetch
print("\nTesting data fetch...")
data = yf.download("EURUSD=X", period="5d", interval="1d")
print(f"✓ Downloaded {len(data)} days of EUR/USD data")
print(data.tail())

print("\n✓ All systems operational!")
```

**Run it:**

```cmd
python test_connection.py
```

---

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'config'"

**Solution:** Make sure you're in the project root directory and venv is activated.

```cmd
cd C:\Users\jonat\OneDrive\Desktop\ai\projects\trading-ai
venv\Scripts\activate
```

### Issue: "psycopg2 not found" or installation failed

**Solution:**

```cmd
pip uninstall psycopg2
pip install psycopg2-binary
```

### Issue: "Permission denied" on database

**Solution:** Make sure you granted schema privileges:

```sql
psql -U postgres -d trading_ai
GRANT ALL ON SCHEMA public TO trading_user;
\q
```

### Issue: Virtual environment activation fails in PowerShell

**Solution:**

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\activate
```

---

## Development Workflow

**Daily workflow:**

1. **Activate environment:**
   ```cmd
   cd C:\Users\jonat\OneDrive\Desktop\ai\projects\trading-ai
   venv\Scripts\activate
   ```

2. **Work on code** (using VS Code or your preferred editor)

3. **Test your changes:**
   ```cmd
   python scripts/your_script.py
   ```

4. **Commit changes:**
   ```cmd
   git add .
   git commit -m "Description of changes"
   ```

5. **Deactivate when done:**
   ```cmd
   deactivate
   ```

---

## Project Documentation

- **README.md**: Project overview
- **ARCHITECTURE.md**: Technical architecture and design
- **SETUP.md**: Detailed setup instructions
- **STRATEGY.md**: Trading strategy documentation
- **DEVELOPMENT_ROADMAP.md**: Week-by-week development plan
- **GETTING_STARTED.md**: This file (quick start)

---

## Getting Help

If you encounter issues:

1. Check the documentation (especially SETUP.md)
2. Verify all prerequisites are installed
3. Check logs in `logs/trading_ai.log`
4. Run `python scripts/verify_setup.py` to diagnose

---

## What's Next?

You're now ready to start building! Here's the recommended path:

**Week 1: Data Pipeline**
- Build `ingestion/data_fetcher.py`
- Download historical data
- Load into database

See **DEVELOPMENT_ROADMAP.md** for the complete week-by-week plan.

**Happy coding!** 🚀

---

**Last Updated**: January 2025
