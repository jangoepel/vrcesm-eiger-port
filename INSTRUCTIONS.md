# Instructions for Using This Repository

**Complete guide to upload, customize, and maintain the VR-CESM Eiger.Alps repository on GitHub**

---

## Quick Start

### 1. Download & Extract (2 minutes)

```bash
# Download the tarball from Claude
# Extract it:
tar -xzf vr-cesm-eiger-port.tar.gz
cd vr-cesm-eiger-port
```

### 2. Review Files (10 minutes)

**Check accuracy of:**
- `README.md` - Project overview correct?
- `docs/benchmarks.md` - Performance numbers look right?
- `docs/technical-notes.md` - Challenges accurately described?
- `PROJECT_STATUS.md` - Timeline and milestones accurate?

**Update as needed:**
```bash
# Edit any file
nano README.md
# or use your favorite editor (vim, emacs, VS Code)
```

### 3. Create GitHub Account (5 minutes)

If you don't have one already:
1. Go to https://github.com
2. Sign up (free account is fine)
3. Verify your email

### 4. Create New Repository (5 minutes)

On GitHub:
1. Click "+" → "New repository"
2. **Name:** `vr-cesm-eiger-port` (or your choice)
3. **Description:** "Variable-Resolution CESM3 porting and optimization on CSCS Eiger"
4. **Visibility:** 
   - **Public** (recommended for job applications - shows your work)
   - **Private** (if you prefer, can make public later)
5. **DO NOT** check "Initialize with README" (you already have one)
6. Click "Create repository"

### 5. Upload to GitHub (5 minutes)

**GitHub will show you instructions. Follow the "push an existing repository" section:**

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Make first commit
git commit -m "Initial commit: VR-CESM Eiger.Alps porting project"

# Add remote (replace with YOUR repository URL)
git remote add origin https://github.com/YOUR_USERNAME/vr-cesm-eiger-port.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**If prompted for credentials:**
- Username: your GitHub username
- Password: use a Personal Access Token (not your password)
  - Generate token at: https://github.com/settings/tokens
  - Select scope: `repo` (full control)

### 6. Verify on GitHub (2 minutes)

Visit your repository URL:
```
https://github.com/YOUR_USERNAME/vr-cesm-eiger-port
```

You should see:
- ✅ README displayed on main page
- ✅ All folders (docs, scripts, benchmarks, configs)
- ✅ Professional project structure

---

## Customization Checklist

### Essential Updates

- [ ] **Replace placeholder names:**
  - Search for "YOUR_USERNAME" and replace with your GitHub username
  - Search for "YOUR_ACCOUNT" in setup.md and replace
  - Search for "jan.goepel" and replace with your email/name

- [ ] **Update contact information:**
  - README.md: Update contact section
  - All .md files: Replace email addresses

- [ ] **Adjust timeline dates:**
  - PROJECT_STATUS.md: Update dates to match your actual timeline
  - README.md: Update "Last Updated" dates

- [ ] **Verify technical details:**
  - docs/benchmarks.md: Confirm all performance numbers
  - docs/technical-notes.md: Add/remove challenges as needed
  - configs/build-notes.md: Update module versions if different

### Optional Enhancements

- [ ] **Add images:**
  - Create `docs/images/` folder
  - Add screenshots of outputs or plots
  - Reference in README: `![Description](docs/images/plot.png)`

- [ ] **Add badges to README:**
  ```markdown
  ![Status](https://img.shields.io/badge/status-active-success)
  ![CESM](https://img.shields.io/badge/CESM-3.0beta06-blue)
  ```

- [ ] **Create a LICENSE file:**
  ```bash
  # MIT License (permissive)
  # See: https://choosealicense.com/licenses/mit/
  ```

- [ ] **Add CONTRIBUTORS.md:**
  - List collaborators
  - Acknowledge support

---

## Updating the Repository

### Making Changes

```bash
# Edit files locally
nano README.md

# See what changed
git status
git diff

# Stage changes
git add README.md  # Specific file
# or
git add .          # All changes

# Commit with descriptive message
git commit -m "Updated project timeline and added Q4 results"

# Push to GitHub
git push
```

### Good Commit Messages

**Do:**
- ✅ "Added VR grid scaling results"
- ✅ "Fixed typos in benchmarks.md"
- ✅ "Updated timeline to reflect Q4 completion"

**Don't:**
- ❌ "changes"
- ❌ "update"
- ❌ "fixed stuff"

### Branching (Optional)

For experimental changes:
```bash
# Create branch
git checkout -b experimental-analysis

# Make changes, commit
git add .
git commit -m "Testing new analysis approach"
git push origin experimental-analysis

# Merge back when ready
git checkout main
git merge experimental-analysis
git push
```

---

## Common Git Tasks

### Check Status
```bash
git status           # What changed?
git log --oneline    # Recent commits
git remote -v        # Where does this push to?
```

### Undo Changes
```bash
# Undo local changes (not committed)
git checkout -- README.md

# Undo last commit (keep changes)
git reset HEAD~1

# Undo last commit (discard changes) - CAREFUL!
git reset --hard HEAD~1
```

### Pull Updates
```bash
# If you edit on GitHub and want to sync locally
git pull origin main
```

### Fix Common Mistakes

**Wrong remote URL:**
```bash
git remote set-url origin https://github.com/CORRECT_USERNAME/vr-cesm-eiger-port.git
```

**Forgot to add files:**
```bash
git add forgotten_file.txt
git commit --amend --no-edit
git push --force-with-lease
```

**Merge conflict:**
```bash
# Edit conflicted files, resolve markers: <<<<< ===== >>>>>
git add resolved_file.txt
git commit -m "Resolved merge conflict"
```

---

## Using This Repository for Job Applications

### 1. Add to CV

**Under Technical Skills or Projects:**
```
GitHub: github.com/YOUR_USERNAME/vr-cesm-eiger-port
```

**Or as a project entry:**
```
VR-CESM Porting Project
- Ported Variable-Resolution CESM3 to CSCS Eiger.Alps
- Achieved 82% parallel efficiency at 12 nodes (11.16 years/day)
- Comprehensive documentation: github.com/YOUR_USERNAME/vr-cesm-eiger-port
```

### 2. Mention in Cover Letter

**Example:**
```
"You can see examples of my HPC work in my GitHub repository documenting 
the CESM3 porting effort, which includes performance optimization, 
distributed systems debugging, and automated diagnostic tools:
https://github.com/YOUR_USERNAME/vr-cesm-eiger-port"
```

### 3. In Interviews

**Talking Points:**
- Walk through technical challenges (docs/technical-notes.md)
- Explain scaling results (docs/benchmarks.md)
- Discuss diagnostic tools (scripts/spinup_diagnostics.py)
- Show systematic approach (PROJECT_STATUS.md)

---

## Troubleshooting

### "Repository not found"
- Check remote URL: `git remote -v`
- Verify repository exists on GitHub
- Check you're logged into correct account

### "Permission denied"
- Use HTTPS URL (not SSH) if you haven't set up SSH keys
- Generate Personal Access Token for password
- Or set up SSH keys: https://docs.github.com/en/authentication

### "Cannot push to main"
- Main branch might be protected
- Push to a feature branch first: `git push origin feature-branch`
- Or unprotect main in repository settings

### "Large files rejected"
- GitHub has 100 MB file limit
- Check: `git ls-files -s | awk '$1 > 100000000'`
- Remove large files, use .gitignore
- For data: use Git LFS or external storage

### "Detached HEAD state"
```bash
git checkout main
git pull
```

---

## Best Practices

### What to Commit
- ✅ Documentation (*.md)
- ✅ Scripts (*.py, *.sh)
- ✅ Small data files (<10 MB)
- ✅ Configuration files

### What NOT to Commit
- ❌ Large data files (*.nc, *.h5)
- ❌ Build artifacts (*.o, *.exe)
- ❌ Personal credentials
- ❌ Temporary files

### .gitignore
Already configured in this repository to exclude:
- NetCDF files (*.nc)
- Build artifacts
- Temporary files
- IDE files

### Commit Frequency
- Commit often: Every logical change
- Don't wait until "everything is perfect"
- Small, atomic commits are better than huge ones

---

## Maintenance Schedule

**Monthly (during active work):**
- Update PROJECT_STATUS.md with progress
- Add new results to benchmarks.md
- Document new challenges in technical-notes.md

**After major milestones:**
- Update README.md overview
- Add plots to docs/images/
- Tag releases: `git tag v1.0 -m "Completed spin-up phase"`

**Annual:**
- Review and archive
- Update contact information
- Check for broken links

---

## GitHub Features to Explore

### Issues
Track tasks and bugs:
- Go to "Issues" tab
- Click "New issue"
- Useful for TODO list

### Wiki
Additional documentation space:
- Enable in repository settings
- Good for tutorials, FAQs

### GitHub Pages
Host documentation as website:
- Settings → Pages → Enable
- Auto-builds from README.md
- URL: https://YOUR_USERNAME.github.io/vr-cesm-eiger-port

### Projects
Kanban-style project management:
- "Projects" tab → "New project"
- Organize tasks visually

---

## Next Steps After Upload

1. **Test the URL** - Make sure it's accessible
2. **Add to CV** - Update your CV with the GitHub link
3. **Share** - Send link to collaborators or potential employers
4. **Maintain** - Keep updating as project progresses
5. **Promote** - Share in relevant communities (CESM forum, etc.)

---

## Resources

### Git Learning
- Git Basics: https://git-scm.com/book/en/v2
- Interactive Tutorial: https://learngitbranching.js.org
- Cheat Sheet: https://training.github.com/downloads/github-git-cheat-sheet/

### Markdown Formatting
- Guide: https://www.markdownguide.org
- GitHub Flavored: https://guides.github.com/features/mastering-markdown/

### GitHub Help
- Docs: https://docs.github.com
- Community: https://github.community

---

## Questions?

- **Git issues:** https://stackoverflow.com (tag: git)
- **GitHub issues:** https://support.github.com
- **This project:** Open an issue in the repository

---

**Good luck with your GitHub repository! This documentation showcases your excellent HPC and systems work.** 🚀

*Last Updated: November 2025*
