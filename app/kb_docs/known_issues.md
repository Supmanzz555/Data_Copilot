# Known Issues - All Products

**Last Updated**: January 25, 2025  
**Status**: Active monitoring

## Critical Issues

### None Currently Open
Last critical issue resolved: Jan 20, 2025

## High Priority Issues

### 1. Digital Lending - Notification Delays (Since v1.2 Release)
**Affected**: Digital Lending customers  
**Symptoms**: Loan approval/disbursement notifications delayed 15-60 minutes during peak hours (10am-2pm ICT)  
**Impact**: ~500 customers/day  
**Root Cause**: Notification queue overwhelmed post-v1.2 release  
**Workaround**: Check app directly for loan status  
**ETA Fix**: Hotfix 1.2.1 (Feb 5, 2025)  
**Severity**: High

### 2. Digital Saving - Interest Calculation Delays
**Affected**: ~2% of Digital Saving accounts on month-end  
**Symptoms**: Interest not credited on 1st of month, appears 1-2 days late  
**Impact**: 800-1000 accounts monthly  
**Root Cause**: Batch job timeout for large balance accounts (>500K THB)  
**Workaround**: Interest will be credited within 48 hours, backdated  
**ETA Fix**: Architecture redesign in v1.3 (March 2025)  
**Severity**: High

## Medium Priority Issues

### 3. iOS 16.4 - Display Glitch on iPhone 14 Pro Max
**Affected**: iPhone 14 Pro Max users on iOS 16.4  
**Symptoms**: Status bar overlaps app header  
**Impact**: ~3000 users  
**Root Cause**: Dynamic Island compatibility issue  
**Workaround**: Restart app or use landscape mode  
**ETA Fix**: v1.2.1 (Feb 2025)  
**Severity**: Medium

### 4. Digital Lending - PDF Statement Download Fails
**Affected**: iOS app users  
**Symptoms**: Statement download shows error ~5% of time  
**Impact**: ~100 customers/day  
**Root Cause**: File encoding issue in PDF generator  
**Workaround**: Use "Email Statement" feature instead  
**ETA Fix**: v1.2.1 (Feb 2025)  
**Severity**: Medium

### 5. Dashboard - Slow Loading Under High Traffic
**Affected**: All users during peak hours  
**Symptoms**: Dashboard takes 5-10 seconds to load (normally <2s)  
**Peak Hours**: 12pm-1pm ICT (lunch hour), 6pm-8pm ICT (evening)  
**Impact**: All users during peak  
**Root Cause**: Database connection pool saturation  
**Workaround**: Use pull-to-refresh or wait for off-peak hours  
**ETA Fix**: Infrastructure upgrade (Feb 15, 2025)  
**Severity**: Medium

## Low Priority Issues

### 6. Dark Mode - Icon Optimization Incomplete
**Affected**: Users using dark mode  
**Symptoms**: Some icons don't fully adapt to dark theme  
**Impact**: Cosmetic only  
**ETA Fix**: v1.3 (March 2025)  
**Severity**: Low

### 7. Thai Language - Missing Translations in Settings
**Affected**: Thai language users  
**Symptoms**: Few English strings visible in Settings page  
**Impact**: ~15 untranslated strings  
**ETA Fix**: v1.2.1 (Feb 2025)  
**Severity**: Low

### 8. Android 13 - Back Gesture Sensitivity
**Affected**: Android 13 users  
**Symptoms**: Back gesture occasionally requires double-tap  
**Impact**: User annoyance, no functional impact  
**Root Cause**: Android 13 gesture API change  
**ETA Fix**: Under investigation with Google  
**Severity**: Low

## Recently Resolved

### ✅ Digital Saving - Deposit Confirmation Email Delays (Fixed Jan 20)
- Was: Emails delayed 30-60 minutes
- Fix: Migrated to new email service provider
- Status: Resolved

### ✅ App Crash on Transaction History (Fixed Jan 18)
- Was: App crashed on older devices when viewing >100 transactions
- Fix: Implemented pagination
- Status: Resolved

### ✅ QR Code Scanner - Low Light Performance (Fixed Jan 19)
- Was: Scanner failed in low light conditions
- Fix: Enhanced camera algorithm
- Status: Resolved

## Issue Reporting
If you encounter these or new issues:
1. **In-App**: Help > Report Issue
2. **Email**: support@dbank.co.th
3. **Hotline**: 02-123-4567 (24/7)
4. **Emergency**: For critical security issues, email: security@dbank.co.th

## Monitoring
- All issues tracked in JIRA
- Real-time status: status.dbank.co.th
- Incident reports: Published within 2 hours of detection

## Escalation Path
- **Low**: Response within 48 hours
- **Medium**: Response within 24 hours
- **High**: Response within 4 hours
- **Critical**: Immediate response, war room activation
