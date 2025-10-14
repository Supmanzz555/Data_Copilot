# Virtual Bank App Release v1.2 - Release Notes

**Release Date**: January 15, 2025  
**Version**: 1.2.0 (Build 12000)  
**Platforms**: iOS 14+, Android 8+

## Major Changes

### Performance Improvements
- **Login Speed**: Reduced average login time from 3.5s to 1.2s (65% improvement)
- **Dashboard Load**: Optimized data fetching, now loads 2x faster
- **App Size**: Reduced from 85MB to 62MB through code optimization

### Digital Saving Enhancements
- **Mobile Deposit**: New feature - deposit checks via camera (Thai bank checks only)
- **Auto-Image Enhancement**: Automatically enhances photo quality for deposits
- **Interest Calculator**: Added visual projection graphs for savings goals
- **Widget Support**: iOS home screen widget showing real-time balance

### Digital Lending Updates
- **Instant Loan Top-up**: Existing customers can top-up loans without re-application
- **Credit Score Display**: Now shows your dBank credit score in-app
- **EMI Reminders**: Smart notifications 3 days before due date

### UI/UX Improvements
- Redesigned dashboard with card-based interface
- Dark mode support (iOS & Android)
- Improved accessibility (screen reader support)
- New Thai language font for better readability

### Security Updates
- Enhanced biometric authentication (Face ID, Fingerprint)
- Added device binding for high-value transactions
- Implemented transaction PIN for transfers >50,000 THB

## Bug Fixes
- Fixed crash when viewing transaction history on older devices
- Resolved Digital Saving interest calculation delay issue (90% reduction)
- Fixed notification badge not clearing on iOS
- Corrected QR code scanning issue in low light
- Fixed rare crash during app update

## Known Issues

### Critical
- **iOS 16.4 specific**: Minor display glitch on iPhone 14 Pro Max (status bar overlap)
  - Workaround: Restart app
  - Fix planned: v1.2.1 (Feb 2025)

### Medium Priority
- **Android 13**: Back gesture occasionally requires double-tap
  - Investigating with OS vendor
  
- **Digital Lending**: PDF statement download fails ~5% of time on iOS
  - Workaround: Use "Email Statement" option
  - Fix in progress

### Low Priority
- **Dark Mode**: Some icons not fully optimized for dark theme
- **Thai Language**: Few strings still showing in English (Settings page)

## Rollout Schedule
- **Phase 1** (Jan 15-17): 10% of users (beta testers)
- **Phase 2** (Jan 18-20): 50% of users
- **Phase 3** (Jan 21-23): 90% of users
- **Phase 4** (Jan 24+): 100% rollout complete

## Post-Release Metrics (7 days)
- **Adoption Rate**: 78% users upgraded within 3 days
- **Crash Rate**: 0.42% (target: <0.5%) ✅
- **App Store Rating**: 4.6/5 (up from 4.3)
- **Play Store Rating**: 4.5/5 (up from 4.2)

## User Feedback Summary
**Positive**:
- Faster login experience praised by 85% of users
- Dark mode highly requested, now implemented
- Mobile check deposit saves branch visits

**Negative**:
- **Spike in support tickets post-release** (Jan 15-22)
  - Digital Saving: Deposit delays reported (fixed in hotfix 1.2.0.1)
  - Digital Lending: Notification delays during peak (investigating)
  - General: Some users confused by new UI layout

## Support Impact
- **Ticket Volume**: Increased 35% in week post-release
- **Most Common**: "How to use mobile deposit?" (28% of tickets)
- **Second**: "Notification not working" (22% of tickets)
- **Third**: "App slower after update" (15% of tickets - perception issue)

## Breaking Changes
- Minimum OS requirement updated (iOS 14+, Android 8+)
- Old API endpoints deprecated (backward compatible until v2.0)

## Migration Guide
Users on iOS <14 or Android <8 will see upgrade prompt but can continue using v1.1 with limited features.

## Security & Compliance
- Passed BoT security audit (Jan 10, 2025)
- PDPA compliance verified
- Penetration testing completed (Jan 5-8)
- No critical vulnerabilities found

## Next Release
**v1.2.1** (Planned: February 2025)
- Fix iOS 16.4 display issue
- Improve notification delivery during peak hours
- Optimize Digital Lending PDF generation
- Add more Thai language strings

## Developer Notes
- Built with React Native 0.73
- Backend API v2.1
- Min SDK: Android 26, iOS 14
- New analytics SDK integrated (Firebase)

## Contact
For issues related to this release:
- **Critical bugs**: engineering@dbank.co.th
- **User support**: support@dbank.co.th
- **Feature requests**: product@dbank.co.th
