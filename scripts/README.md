# 💰 **AWS Elastic Beanstalk Cost Control Scripts**

Control your AWS costs by starting/stopping the EB environment when needed.

## **💸 Cost Savings:**
- **Running**: ~$30/month 
- **Terminated**: ~$0/month
- **URL**: Remains the same after recreation

---

## **📜 Available Scripts:**

### **1. Check Status**
```bash
./scripts/eb-cost-control.sh status
```
Shows current environment status and costs.

### **2. Terminate Environment (Save Money)**
```bash
./scripts/eb-terminate.sh
```
- ✅ Saves ~$30/month
- ❌ API becomes unavailable
- ⏱️ Takes 2-3 minutes

### **3. Recreate Environment (Start Spending)**
```bash
./scripts/eb-recreate.sh  
```
- ❌ Costs ~$30/month
- ✅ API becomes available
- ⏱️ Takes 3-5 minutes
- 🔗 Same URL restored

### **4. Set Environment Variables (Interactive)**
```bash
./scripts/eb-set-env-vars.sh
```
- 🔐 Securely prompts for API keys and secrets
- ⚡ Uses AWS CLI instead of web console
- 🔒 Input is hidden while typing

### **5. Set Environment Variables (From File)**
```bash
./scripts/eb-set-env-from-file.sh [env-file]
```
- 📁 Reads secrets from secure .env file
- 🤖 Good for automation and CI/CD
- 🛡️ Validates all required variables

---

## **🚀 Quick Start:**

### **First Time Setup:**
```bash
cd /Users/kiransah/Desktop/code/tavily_assignment/exp_2

# 1. Create environment
./scripts/eb-recreate.sh

# 2. Set API keys and secrets
./scripts/eb-set-env-vars.sh
```

### **Save Money (Stop):**
```bash
cd /Users/kiransah/Desktop/code/tavily_assignment/exp_2
./scripts/eb-terminate.sh
```

### **Start Spending (Start):**
```bash
cd /Users/kiransah/Desktop/code/tavily_assignment/exp_2  
./scripts/eb-recreate.sh
# Note: Environment variables persist and don't need to be set again
```

### **Check Status:**
```bash
cd /Users/kiransah/Desktop/code/tavily_assignment/exp_2
./scripts/eb-cost-control.sh status
```

---

## **🔗 Environment Details:**

- **Environment Name**: `cognitive-core-fresh`
- **URL**: `http://cognitive-core-fresh.eba-c4n432jt.us-east-1.elasticbeanstalk.com`
- **Platform**: Python 3.12 on Amazon Linux 2023
- **Instance Type**: t3.micro
- **Region**: us-east-1

---

## **⚠️ Important Notes:**

1. **URL Stability**: The URL stays the same after recreation
2. **Data Persistence**: Database data persists (MongoDB Atlas is separate)
3. **Downtime**: 3-5 minutes downtime during recreation
4. **Configuration**: All settings are preserved in the scripts

---

## **💡 Usage Scenarios:**

### **Daily Development:**
```bash
# Start working
./scripts/eb-recreate.sh

# Done for the day  
./scripts/eb-terminate.sh
```

### **Demo/Testing:**
```bash
# Before demo
./scripts/eb-recreate.sh

# After demo
./scripts/eb-terminate.sh
```

### **Production (Keep Running):**
```bash
# Check if running
./scripts/eb-cost-control.sh status

# If terminated, recreate
./scripts/eb-recreate.sh
```

### **Environment Variables Setup:**

**Interactive (Recommended for first-time setup):**
```bash
./scripts/eb-set-env-vars.sh
# Will prompt for:
# - TAVILY_API_KEY
# - OPENAI_API_KEY  
# - MONGODB_CONNECTION_STRING
```

**From File (For automation):**
```bash
# Create secure env file
./scripts/eb-set-env-from-file.sh
# This creates: ~/.aws/eb-secrets-cognitive-core-fresh.env
# Edit the file with your real credentials, then run:
./scripts/eb-set-env-from-file.sh

# Or use custom file:
./scripts/eb-set-env-from-file.sh /path/to/my-secrets.env
```

---

## **🛠️ Troubleshooting:**

### **Script Permissions:**
```bash
chmod +x ./scripts/*.sh
```

### **AWS CLI Setup:**
```bash
aws configure
```

### **EB CLI Setup:**
```bash
cd backend
eb init
```

---

**💰 Remember**: Every day terminated = ~$1 saved!