# 🧹 Repository Cleanup Plan

**Branch**: `feature/repo-cleanup`  
**Date**: October 2, 2025

---

## 📊 Current Repository Structure Analysis

### ✅ Keep (Active/Production)
```
├── backend/              # V1 Backend (Database + Research)
├── backend_v2/           # V2 Backend (Political Analyst) ⭐ DEPLOYED
├── frontend/             # V1 Frontend (CRA)
├── Frontend_v2/          # V2 Frontend (Vite) ⭐ DEPLOYED
├── documentation/        # Project documentation
├── scripts/              # Utility scripts
├── config/               # Configuration files
├── .venv/                # Python virtual environment
└── Deployment docs       # All DEPLOYMENT_*.md files
```

### ❌ Remove (Redundant/Experimental)
```
├── POCs/                             # Old proof of concepts
├── Political_Analyst_Workbench/      # Duplicate/old structure
├── ui_exploration/                   # UI experiments (archived in history)
├── tests/ (root level)               # Scattered test files
├── tools/                            # Old utility tools
├── reports/                          # Old test reports
├── playwright-report/                # Generated reports
├── test-results/                     # Generated test results
├── node_modules/ (root)              # Should not be at root level
└── Root-level test files:
    - test_backend_8001.py
    - test_cache.py
    - test_cache_key.py
    - test_tcs_sequential.py
    - test_websocket_quick.py
    - test-*.sh files (root level)
    - setup-*.sh files (root level)
```

### 🗑️ Clean (Generated/Temporary)
```
├── **/__pycache__/              # Python cache
├── **/*.pyc                     # Compiled Python
├── **/*.log                     # Log files
├── .elasticbeanstalk/logs/      # EB deployment logs
├── backend_v2/artifacts/*.html  # Generated artifacts (keep directory)
├── backend_v2/artifacts/*.png   # Generated artifacts (keep directory)
├── Frontend_v2/deployment-info.txt  # Sensitive deployment info
├── backend/backend-deployment-info.txt
├── backend_v2/backend-deployment-info.txt
```

---

## 🎯 Cleanup Strategy

### Phase 1: Remove Experimental/Old Folders
These folders are experimental or superseded by V2:
- [ ] `POCs/` - Proof of concepts (can be archived)
- [ ] `Political_Analyst_Workbench/` - Old structure replaced by backend_v2
- [ ] `ui_exploration/` - UI experiments replaced by Frontend_v2
- [ ] `tools/` - Old utility tools
- [ ] `reports/` - Old test reports

### Phase 2: Remove Test Artifacts
Generated test results and reports:
- [ ] `playwright-report/`
- [ ] `test-results/`
- [ ] `config/test-results.json`
- [ ] `config/test-results.xml`

### Phase 3: Remove Root-Level Test Files
Scattered test files that should be in proper test directories:
- [ ] `test_backend_8001.py`
- [ ] `test_cache.py`
- [ ] `test_cache_key.py`
- [ ] `test_tcs_sequential.py`
- [ ] `test_websocket_quick.py`
- [ ] `test-backend-v2.sh`
- [ ] `test-frontend-v2.sh`
- [ ] `test-integration-v2.sh`
- [ ] `test-mock-backend.sh`

### Phase 4: Remove Root-Level Setup Scripts
Move to scripts/ or remove:
- [ ] `setup-backend-v2.sh`
- [ ] `setup-frontend-v2.sh`
- [ ] `run-playwright-tests.sh`
- [ ] `playwright-local.config.ts`

### Phase 5: Clean Root node_modules
- [ ] Remove `node_modules/` from root (should only be in frontend folders)
- [ ] Remove `package.json` and `package-lock.json` from root

### Phase 6: Clean Generated Files
- [ ] Remove all `__pycache__` directories
- [ ] Remove all `.pyc` files
- [ ] Remove `.elasticbeanstalk/logs/`
- [ ] Remove `backend_v2/artifacts/*.html` and `*.png` (keep directory)
- [ ] Remove deployment-info.txt files (contain sensitive data)

### Phase 7: Update .gitignore
Add missing patterns:
```gitignore
# Elastic Beanstalk
.elasticbeanstalk/logs/
*-deployment-info.txt
deployment-info.txt

# Artifacts
artifacts/*.html
artifacts/*.png

# Test results
test-results/
playwright-report/
```

---

## 🔒 Files to Keep But Not Commit

These exist locally but should never be committed:
- `.env` files (already in .gitignore)
- `deployment-info.txt` files
- `.elasticbeanstalk/` directory
- Generated artifacts

---

## 📁 Recommended Final Structure

```
exp_2/
├── backend/                    # V1 Backend
│   ├── models/
│   ├── routers/
│   ├── services/
│   ├── tests/                  # Unit tests here
│   ├── app.py
│   ├── requirements.txt
│   └── aws-deploy-backend.sh
│
├── backend_v2/                 # V2 Backend (ACTIVE)
│   ├── langgraph_master_agent/
│   ├── shared/
│   ├── services/
│   ├── artifacts/              # Keep directory, clean files
│   ├── app.py
│   ├── requirements.txt
│   └── aws-deploy-backend.sh
│
├── frontend/                   # V1 Frontend
│   ├── src/
│   ├── public/
│   └── package.json
│
├── Frontend_v2/                # V2 Frontend (ACTIVE)
│   ├── src/
│   ├── public/
│   ├── e2e/
│   ├── aws-deploy.sh
│   └── aws-deploy-secure.sh
│
├── documentation/              # All docs
│   ├── 1-MVP/
│   ├── 2-MVP/
│   └── guides/
│
├── scripts/                    # Utility scripts
│   └── (move setup scripts here)
│
├── config/                     # Configs
│   └── playwright.config.ts
│
├── .venv/                      # Python venv (local only)
├── .git/                       # Git repo
├── .gitignore
├── README.md
├── DEPLOYMENT_GUIDE_V2.md
├── DEPLOYMENT_SETUP_SUMMARY.md
├── DEPLOYMENT_SUCCESS_V2.md
└── QUICK_DEPLOY_V2.md
```

---

## 💾 Backup Before Deletion

Before removing folders, ensure:
1. ✅ V2 backends are deployed and working
2. ✅ V2 frontends are deployed and working
3. ✅ All important code is in backend_v2 and Frontend_v2
4. ✅ Git history preserves old code if needed

---

## 🚀 Execution Order

1. **Backup**: Tag current state `git tag pre-cleanup`
2. **Remove old folders**: POCs, Political_Analyst_Workbench, ui_exploration, etc.
3. **Clean test artifacts**: Reports, results, temp files
4. **Move/remove root scripts**: Organize into proper locations
5. **Clean generated files**: Cache, logs, artifacts
6. **Update .gitignore**: Add missing patterns
7. **Commit**: "chore: major repository cleanup - remove old/experimental code"
8. **Verify**: Test that V2 deployments still work

---

## ⚠️ Safety Checks

Before proceeding:
- [ ] Current deployment (V2) is working
- [ ] All deployment URLs documented
- [ ] Created git tag for rollback
- [ ] Reviewed what will be deleted
- [ ] .env files are backed up

---

## 📊 Expected Results

**Before Cleanup:**
- ~20 root-level directories
- ~15 root-level test files
- Multiple redundant/experimental folders
- ~150+ MB of cache/generated files

**After Cleanup:**
- ~10 core directories
- Clean root level
- Only active V1 and V2 code
- ~50 MB smaller repository

---

**Ready to proceed with cleanup?**

