
## Race Odds Scraper – Setup Guide (Windows)

This scraper fetches race odss data from `https://www.odds.com.au/horse-racing/` and saves it into a CSV file and running at a specified time daily. You can install it easily using our PowerShell script or set it up manually.

---

## Option 1: Automatic Setup (Recommended)

### Requirements

* Windows 10/11
* Python

---

### Steps to Use the Auto Setup Script

1. **Download the Project Files**

   * Clone the repo or download it as ZIP and extract to a folder, e.g., `C:\RaceOddsScraper`

2. **Open PowerShell as Administrator**

   * Right-click the Start menu → **Windows PowerShell (Admin)**

3. **Run the Setup Script**

   ```powershell
   cd "C:\RaceOddsScraper"
    ```
   * Allow script execution if needed:
   ```powershell
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
   ```
    * Run the setup script:
   ```powershell
   .\setup_bot.ps1
   ```

4. **Follow the Prompts**

   * Enter the time to schedule the bot (e.g., `14:00`)
   * The script will:

     * Create a virtual environment
     * Install required dependencies
     * Schedule the task to run daily
     * Ensure only one instance runs at a time

---

## Option 2: Manual Setup


### Step 1: Install Python

* Download from [python.org/downloads](https://www.python.org/downloads/)
* During install, **check the box: "Add Python to PATH"**

---

### Step 2: Set Up the Project

1. **Open PowerShell**

2. Navigate to the project folder:

   ```powershell
   cd "C:\RaceOddsScraper"
   ```

3. **Create a Virtual Environment**

   ```powershell
   python -m venv venv
   ```

4. **Install Dependencies**

   ```powershell
   .\venv\Scripts\pip install -r requirements.txt
   ```
5. **Install Playwright browser dependencies**

   ```powershell
   .\venv\Scripts\playwright.exe install
   ```
---

### Step 3: Configure Environment Variables

Create a file named `.env` in the project folder with the following:

```env
OUTPUT_DIR="C:/Users/username/Documents/Output"
SCRAPE_INTERVAL=5
```

---

### Step 4: Test the Scraper

```powershell
.\venv\Scripts\python.exe main.py
```

---

### Step 5: Schedule the Task Manually

1. Open **Task Scheduler**

2. Click **"Create Task"**

3. Under **General Tab:**

   * Name: `RaceOddsScraper`
   * Run with highest privileges
   * Configure for Windows 10 or later

4. **Trigger Tab:**

   * Add a new Daily trigger at desired time

5. **Action Tab:**

   * Program/script:
     `C:\RaceOddsScraper\venv\Scripts\python.exe`
   * Add arguments:
     `"C:\RaceOddsScraper\main.py"`
   * Start in:
     `C:\RaceOddsScraper`

6. **Settings Tab:**

   * Check “**If the task is already running, stop the existing instance**”

---

## Logs

* Logs are saved in `logs` folder in  the project folder.
* To reschedule or remove the task, open **Task Scheduler** > **Task Library**.

---
