# Troubleshooting Guide - dBank Mobile App

**Last Updated**: January 25, 2025  
**App Version**: 1.2.0  
**Platforms**: iOS 14+, Android 8+

## Common Issues & Solutions

### Login Issues

#### Cannot Login - "Incorrect Password"
**Symptoms**: Password rejected, even though you're sure it's correct

**Solutions**:
1. **Check Caps Lock**: Ensure caps lock is off
2. **Wait 5 Minutes**: After 3 failed attempts, account locks for 5 minutes
3. **Reset Password**: 
   - Tap "Forgot Password"
   - Enter registered email
   - Follow link in email (valid 30 minutes)
   - Create new password (min 8 chars, 1 number, 1 special char)
4. **Clear App Cache** (Android):
   - Settings > Apps > dBank > Storage > Clear Cache
   - Retry login

**Still not working?** Contact support: 02-123-4567

---

#### App Keeps Logging Out
**Symptoms**: Logged out every time you open app

**Possible Causes**:
- Recent app update (v1.2)
- Session timeout (30 minutes inactive)
- Multiple devices logged in (max 2 devices allowed)

**Solutions**:
1. **Enable Biometric Login**:
   - Settings > Security > Enable Face ID/Fingerprint
   - Stays logged in for 7 days
2. **Check Device Limit**:
   - Settings > Devices > View Logged-In Devices
   - Remove old devices if needed
3. **Update App**: Ensure v1.2 or later

---

### Transaction Issues

#### Transaction Showing "Pending" for Long Time
**Symptoms**: Transfer stuck in pending for >30 minutes

**Normal Processing Times**:
- dBank to dBank: Instant
- To other Thai banks: 5 minutes - 2 hours
- International: 1-3 business days

**Solutions**:
1. **Wait**: Most resolve within 2 hours
2. **Check Beneficiary Details**: Incorrect account = delayed
3. **Check Balance**: Ensure sufficient funds + fees
4. **Business Hours**: Transfers after 3pm may process next business day
5. **Contact Support**: After 24 hours, call 02-123-4567 with transaction reference

---

#### Transaction Failed - "Insufficient Balance"
**Symptoms**: Transaction rejected even though balance seems sufficient

**Common Causes**:
- Minimum balance requirement (100 THB Digital Saving)
- Daily limit exceeded (50,000 THB)
- Pending transactions not yet deducted

**Solutions**:
1. **Check Available Balance** (not current balance):
   - Home > Accounts > Digital Saving > View Details
   - Available Balance = Current - Pending - Minimum Required
2. **Check Daily Limit**:
   - Settings > Limits > View Usage
   - Resets at midnight ICT
3. **Cancel Pending Transactions** (if accidental duplicates)

---

### Mobile Deposit Issues (New in v1.2)

#### Cannot Capture Check Image
**Symptoms**: Camera won't focus, image rejected

**Solutions**:
1. **Lighting**: Ensure bright, even lighting (no shadows)
2. **Background**: Place check on dark, plain surface
3. **Position**: Keep check within frame guides
4. **Angle**: Hold phone directly above check (90° angle)
5. **Stability**: Hold steady for 2-3 seconds for auto-capture

**Image Quality Requirements**:
- All 4 corners visible
- Text readable
- No glare or shadows
- File size <5MB

---

#### Deposit Rejected
**Common Rejection Reasons**:
- Check older than 6 months
- Already deposited
- Payee name doesn't match account name
- Check damaged or altered
- Insufficient funds in drawer's account (shown later)

**What to Do**:
1. **Check Email**: Rejection reason sent within 2 hours
2. **Retry with Better Image**: If image quality issue
3. **Branch Deposit**: For problematic checks
4. **Contact Drawer**: If insufficient funds

---

### Notification Issues

#### Not Receiving Notifications
**Symptoms**: No push notifications for transactions, login, etc.

**Solutions**:

**iOS**:
1. Settings > Notifications > dBank > Allow Notifications: ON
2. Settings > dBank > Background App Refresh: ON
3. Ensure Do Not Disturb is off
4. Delete and reinstall app (last resort)

**Android**:
1. Settings > Apps > dBank > Notifications: Enabled
2. Settings > Apps > dBank > Battery: Unrestricted
3. Disable battery optimization for dBank
4. Check if notification channel disabled:
   - Long-press notification > Settings > Enable all channels

**Still not working?**
- Ensure stable internet connection
- Known issue post-v1.2: Notifications delayed during peak hours (10am-2pm)
- Workaround: Check app directly for updates

---

### App Performance Issues

#### App Slow or Freezing
**Symptoms**: App takes long to load, freezes during use

**Solutions**:
1. **Close Background Apps**: Free up memory
2. **Restart Phone**: Clears temporary issues
3. **Update App**: v1.2 has 65% faster load times
4. **Check Storage**: Ensure >500MB free space
5. **Clear Cache** (Android):
   - Settings > Apps > dBank > Storage > Clear Cache
6. **Reinstall App** (if severe):
   - Export account statement first (if needed)
   - Uninstall and reinstall from app store

**Known Issue**: Dashboard slow during peak hours (12-1pm, 6-8pm)

---

#### App Crashes on Startup
**Symptoms**: App closes immediately after opening

**Solutions**:
1. **Update OS**: iOS 14+ or Android 8+ required
2. **Update App**: Ensure latest version (v1.2.0)
3. **Restart Device**: Simple but often works
4. **Free Up Storage**: Minimum 500MB required
5. **Reinstall App**: 
   - Delete app
   - Restart device
   - Reinstall from App Store/Play Store

**iOS 16.4 Specific**: Known display glitch on iPhone 14 Pro Max
- Workaround: Restart app
- Fix planned: v1.2.1 (Feb 2025)

---

### Interest Calculation Issues

#### Interest Not Credited on 1st of Month
**Symptoms**: Expected interest not showing in account

**Normal Behavior**:
- Interest credited on 1st of each month
- Compounded daily, paid monthly
- Subject to 15% withholding tax (auto-deducted)

**Solutions**:
1. **Wait 48 Hours**: ~2% of accounts experience 1-2 day delay (known issue)
2. **Check Statement**:
   - Accounts > Digital Saving > Statements
   - Interest will be backdated to 1st
3. **Contact Support**: After 2 days if still missing

**Why Delayed?**
- Accounts with balance >500,000 THB
- Batch processing timeout (fix in progress)

---

### Password & Security

#### Forgot Password
1. Login screen > "Forgot Password"
2. Enter registered email
3. Check email for reset link (valid 30 minutes)
4. Create new password:
   - Min 8 characters
   - At least 1 number
   - At least 1 special character (!@#$%^&*)
   - Cannot reuse last 3 passwords

#### Account Locked
**Causes**:
- 3 failed login attempts: Locked 5 minutes
- 5 failed attempts in 1 hour: Locked 30 minutes
- 10 failed attempts in 1 day: Locked 24 hours

**Solutions**:
- Wait for lock period to expire
- OR call support to unlock: 02-123-4567
- Verification required (ID, security questions)

---

## App Version-Specific Issues

### v1.2 Known Issues
1. **iOS 16.4 Display Glitch**: Status bar overlap (restart app)
2. **PDF Download Fails**: Use "Email Statement" instead
3. **Notification Delays**: During peak hours (check app directly)

---

## Contact Support

### Self-Service (24/7)
- **In-App Chat**: Help > Chat Support
- **FAQ**: Help > Frequently Asked Questions
- **Status Page**: status.dbank.co.th

### Live Support
- **Hotline**: 02-123-4567 (24/7)
  - Thai: Press 1
  - English: Press 2
- **Email**: support@dbank.co.th (response within 24h)
- **Branch**: Visit nearest dBank branch (8am-5pm, Mon-Fri)

### Emergency
- **Lost/Stolen Card**: 02-123-4567, press 3 (immediate block)
- **Fraudulent Transaction**: 02-123-4567, press 4
- **Security Issues**: security@dbank.co.th

---

## Diagnostic Information to Provide

When contacting support, have ready:
1. **Account Number**: (last 4 digits only if via unsecured channel)
2. **Device Info**: iOS/Android version, phone model
3. **App Version**: Settings > About > Version
4. **Issue Description**: When started, what you were doing
5. **Error Messages**: Screenshots helpful (mask sensitive info)
6. **Transaction Reference**: If transaction-related

---

## Preventive Tips

1. **Keep App Updated**: Enable auto-updates
2. **Regular Password Change**: Every 90 days (app will remind)
3. **Monitor Transactions**: Enable push notifications
4. **Secure Device**: Use screen lock + biometric
5. **Backup Email**: Keep registered email accessible
6. **Review Limits**: Adjust daily limits as needed

---

**Still need help?** Our support team is here 24/7!  
📞 02-123-4567 | 📧 support@dbank.co.th
