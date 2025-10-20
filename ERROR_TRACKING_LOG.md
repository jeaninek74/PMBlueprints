# PMBlueprints Platform - Error Tracking Log

**Purpose:** Track all identified issues, their fixes, and validation status  
**Created:** October 20, 2025  
**Last Updated:** October 20, 2025

---

## Active Issues (Identified - Not Fixed)

### Issue #1: Apple Pay Displayed in Payment Information
**Status:** ✅ FIXED  
**Priority:** HIGH  
**Reported:** October 20, 2025  
**Fixed:** October 20, 2025  
**Location:** Payment information page  

**Description:**  
Apple Pay was displayed as a payment option but should be removed.

**Steps to Reproduce:**
1. Navigate to payment information page
2. Observe Apple Pay option displayed

**Expected Behavior:**  
Apple Pay should not be displayed

**Fix Applied:**  
- Removed Apple Pay badge from templates/payment/checkout.html
- Removed 'apple_pay' from Stripe paymentMethodOrder array

**Commit:** 33edabb  
**Deployed:** October 20, 2025  
**Verified:** Pending user testing

---

### Issue #2: 500 Server Error on Payment Back Button
**Status:** ✅ FIXED  
**Priority:** CRITICAL  
**Reported:** October 20, 2025  
**Fixed:** October 20, 2025  
**Location:** Payment screen back button  

**Description:**  
Clicking the back button on the payment screen caused a 500 server error.

**Steps to Reproduce:**
1. Navigate to payment screen
2. Click back button
3. Observe 500 server error

**Expected Behavior:**  
Back button should navigate to previous page without error

**Root Cause:**  
Missing templates/payment/cancel.html template

**Fix Applied:**  
- Created templates/payment/cancel.html with proper layout
- Added "Back to Pricing" and "Go to Dashboard" buttons
- Added help text and support contact

**Commit:** 33edabb  
**Deployed:** October 20, 2025  
**Verified:** Pending user testing

---

### Issue #3: Main Page Buttons Not Functional
**Status:** ✅ VERIFIED  
**Priority:** HIGH  
**Reported:** October 20, 2025  
**Verified:** October 20, 2025  
**Location:** Main page (homepage)  

**Description:**  
Buttons on the main page were reported as not functional.

**Investigation Result:**  
All buttons verified working correctly:
- Get Started → /auth/register
- Browse Templates → /templates/browse (with filters)
- Subscribe Now → /payment/checkout/{tier}
- Preview → /templates/preview/{id}
- Try AI Generator → /ai-generator
- Try AI Suggestor → /ai_suggestions

**Status:**  
No fix required - all buttons functional

**Commit:** N/A  
**Verified:** October 20, 2025

---

### Issue #4: AI Suggestions Count Shows "19" Instead of "Unlimited"
**Status:** ✅ FIXED  
**Priority:** MEDIUM  
**Reported:** October 20, 2025  
**Fixed:** October 20, 2025  
**Location:** Welcome back page (dashboard)  

**Description:**  
Dashboard showed "19 AI suggestions" when it should display "Unlimited".

**Steps to Reproduce:**
1. Log in to dashboard
2. View welcome back page
3. Observe "19 AI suggestions" displayed

**Expected Behavior:**  
Should display "Unlimited AI suggestions"

**Fix Applied:**  
- Changed templates/dashboard_new.html line 44
- Replaced `{{ ai_suggestions|length }}` with "Unlimited"
- AI Suggestor has unlimited suggestions, not a fixed count

**Commit:** 33edabb  
**Deployed:** October 20, 2025  
**Verified:** Pending user testing

---

### Issue #5: "Back to Templates" Navigation Doesn't Preserve State
**Status:** ✅ FIXED  
**Priority:** MEDIUM  
**Reported:** October 20, 2025  
**Fixed:** October 20, 2025  
**Location:** Template detail/preview page  

**Description:**  
When browsing templates and clicking "back to templates", it didn't return to the previous filtered state.

**Steps to Reproduce:**
1. Browse templates with specific industry/category filter
2. Click on a template to view details
3. Click "back to templates"
4. Observe filter state is lost

**Expected Behavior:**  
Should return to the same filtered view with industry/category preserved

**Fix Applied:**  
- Updated routes/templates.py preview route to capture filter parameters
- Updated templates/templates/preview.html to build back URL with filters
- Updated templates/templates/browse.html to pass filters to preview links
- Filter state now preserved via URL parameters (industry, category, search)

**Commit:** 33edabb  
**Deployed:** October 20, 2025  
**Verified:** Pending user testing

---

### Issue #6: Template Filtering Returns "No Browse Templates Found"
**Status:** ✅ FIXED  
**Priority:** CRITICAL  
**Reported:** October 20, 2025  
**Fixed:** October 20, 2025  
**Location:** Browse templates page  

**Description:**  
When selecting industry and category and clicking filter, the page returns "No browse templates found". User expects to always see templates on the browse page.

**Root Cause:**  
- Filtering used AND logic (industry AND category)
- Many industry/category combinations don't exist (e.g., AI ML + Action Item Log)
- AND logic returned 0 results, showing error message
- User expectation: Always see templates, never see error

**Fix Applied:**  
- Implemented smart OR fallback logic in routes/templates.py
- Try AND first (both filters match)
- If AND returns 0 results, automatically fall back to OR (either filter matches)
- Simplified no-results message (only shown for search with no results)
- Removed error message for incompatible filter combinations

**Example:**  
- User selects: AI ML industry + Action Item Log category
- AND logic: 0 results
- OR fallback: 48 templates (31 AI ML + 17 Action Item Log)
- User always sees browse page with templates

**Commit:** dd92bea  
**Deployed:** October 20, 2025  
**Verified:** Tested with incompatible combinations - always returns templates

---

### Issue #7: Main Page Dropdown Auto-Navigation Issue
**Status:** ✅ FIXED  
**Priority:** HIGH  
**Reported:** October 20, 2025  
**Fixed:** October 20, 2025  
**Location:** Main page (homepage) industry dropdown  

**Description:**  
When selecting an industry from the dropdown on the main page, it automatically navigated to "Browse Templates".

**Steps to Reproduce:**
1. Navigate to main page
2. Select an industry from dropdown
3. Observe automatic navigation to Browse Templates page

**Expected Behavior:**  
Should wait for both industry AND template type selection, then require explicit button click

**Fix Applied:**  
- Removed auto-navigation event listeners from templates/index.html
- Users must now explicitly click "Browse Templates" button
- Prevents accidental navigation when making dropdown selections
- Added validation to ensure both dropdowns are selected before navigation

**Commit:** 33edabb  
**Deployed:** October 20, 2025  
**Verified:** Pending user testing

---

## Fixed Issues

(No fixed issues yet - this section will be updated as issues are resolved)

---

## Issue Summary

**Total Issues:** 7  
**Open:** 0  
**In Progress:** 0  
**Fixed:** 6  
**Verified:** 1  
**Pending User Testing:** 6

**By Priority:**
- Critical: 2 (1 fixed, 1 investigated)
- High: 3 (2 fixed, 1 verified)
- Medium: 2 (2 fixed)
- Low: 0

**By Status:**
- ✅ Fixed & Deployed: 6
- ✅ Verified Working: 1
- ⚠️ Investigated & Monitoring: 1

---

## Issue Categories

**Payment System:** 2 issues (#1, #2)  
**Navigation:** 2 issues (#5, #7)  
**Filtering:** 1 issue (#6)  
**UI/Display:** 2 issues (#3, #4)

---

## Next Actions

1. Fix payment page issues (remove Apple Pay, fix 500 error)
2. Fix main page dropdown navigation
3. Fix template filtering query
4. Fix "back to templates" navigation
5. Fix AI suggestions count display
6. Make main page buttons functional
7. Test all fixes
8. Update this log with fix status

---

**Log Maintained By:** Development Team  
**Review Frequency:** After each fix deployment  
**Validation Required:** User testing confirmation




---

## Homepage Update: "Why Project Managers Choose PMBlueprints" Section Styling

**Date:** October 20, 2025  
**Type:** Enhancement  
**Status:** ✅ COMPLETE

### Change Requested
Update the "Why Project Managers Choose PMBlueprints" section on the homepage with:
- Larger font size
- Orange color (#ff6b35) for all text
- Updated content to match user's design specifications

### Changes Made
**File Modified:** `templates/index.html`

**Updates:**
1. **Heading:** Changed from small white text to larger orange text
   - Font size: 1.75rem (from default)
   - Color: #ff6b35 (from white)
   
2. **List Items:** Changed from white text to larger orange text
   - Font size: 1.1rem (from default)
   - Color: #ff6b35 (from white)

3. **Content Updated:**
   - "Enterprise Quality Project Management Documents: Professional AI Generated templates designed by certified PMPs"
   - "AI-Powered PM CHAT: Create your own custom PM documents for any methodology (Agile, Waterfall, Scrum, PRINCE2, Hybrid, and 20+ more) with the AI GENERATOR."
   - Reordered items to prioritize Enterprise Quality and AI-Powered PM CHAT

### Deployment
- **Commit:** 1db899f - "Update Why Project Managers Choose PMBlueprints section - larger orange font"
- **Pushed to:** GitHub main branch
- **Auto-deployed:** Railway (successful)
- **Verification:** Live at https://www.pmblueprints.net

### Test Results
✅ **PASSED** - Section now displays in orange font (#ff6b35) with larger text size  
✅ **PASSED** - Content matches user's requested design  
✅ **PASSED** - All 7 bullet points display correctly  
✅ **PASSED** - Heading "Why Project Managers Choose PMBlueprints" is prominent and orange  

### Status
**COMPLETE** - Changes successfully deployed to production and verified on live site.




---

## Homepage Updates Complete - October 20, 2025

### Update 1: Left Side Content Replacement
**Status:** ✅ COMPLETE

**Changes Made:**
- Replaced left side content with new verbiage
- Increased font size to 1.35rem for better readability
- Maintained white text color
- Changed alignment from center to start (top-aligned with right side box)

**New Content:**
> "This platform offers AI-Generated Project Management document templates either prebuilt or created instantly for you. Examples include project plans, KPI dashboards, and budget plans tailored to your specific industry. You can also use the AI document generator, which works like a chat assistant but is purpose-built for project management. It supports all PM methodologies and follows PMI-compliant standards.
>
> Templates can be integrated directly into tools such as Monday.com, Smartsheet, Google Sheets, and Microsoft 365. By using this system, you can reduce the time spent creating project documentation by up to 70%, freeing project managers to focus on what matters most: successful project execution and delivery."

**Commits:**
- 303576c - "Update homepage: new left side content + white font + top alignment"
- 74a64c7 - "Increase font size for left side content to 1.35rem"

---

### Update 2: Workday Removal from Platform Integrations
**Status:** ✅ COMPLETE

**Files Modified:**
1. `templates/index.html` (3 instances removed)
   - Line 124: Software Integration bullet point
   - Line 176: Platform Integrations card description
   - Line 288-290: Business Value section (changed "5 Platforms" to "4 Platforms")

2. `templates/about.html` (1 instance removed)
   - Line 67: Platform Compatible description

3. `templates/integrations.html` (2 instances removed)
   - Lines 151-185: Entire Workday integration card removed
   - Line 196: Account requirements note

4. `templates/templates/detail.html` (1 instance removed)
   - Lines 205-210: Workday button removed

5. `templates/components/demo_banner.html` (1 instance removed)
   - Lines 169-171: Workday platform option removed

**Total Workday References Removed:** 8 instances across 5 template files

**Platform Count Updated:**
- Changed from "5 Platforms" to "4 Platforms" in Business Value section
- Updated all integration lists to show only: Monday.com, Smartsheet, Google Sheets, Microsoft 365

**Commit:**
- 9a7dbc2 - "Remove Workday from all platform integrations"

---

### Verification Results
✅ **Left Side Content** - Successfully updated with new verbiage, larger white font (1.35rem), top-aligned  
✅ **Workday Removal** - All references removed from homepage and throughout site  
✅ **Platform Count** - Updated from 5 to 4 platforms  
✅ **Orange Section** - "Why Project Managers Choose PMBlueprints" displays correctly in orange  

**Live Site:** https://www.pmblueprints.net  
**Deployment:** All changes successfully deployed via Railway

