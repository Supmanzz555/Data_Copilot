# Support Ticket Handling Guidelines

**For**: dBank Customer Support Team  
**Effective Date**: January 1, 2025  
**Last Updated**: January 20, 2025 (post-v1.2 updates)

## Ticket Priority Classification

### Critical (P1) - Response: Immediate, Resolve: <2h
**Criteria**:
- Security breach or suspected fraud
- System-wide outage affecting >1000 users
- Data loss or corruption
- Regulatory compliance violation

**Examples**:
- "Unauthorized transaction on my account"
- "Cannot access any account, app shows error for everyone"
- "Personal data exposed to another customer"

**Actions**:
1. Escalate immediately to L2/Manager
2. War room activation if system-wide
3. Customer communication within 15 minutes
4. Incident report required

---

### High (P2) - Response: <30min, Resolve: <4h
**Criteria**:
- Individual customer cannot access account
- Transaction failed but money deducted
- Loan disbursement delayed >24h
- Large value transaction issue (>50,000 THB)

**Examples**:
- "Transferred 100K but not received by beneficiary"
- "Loan approved 2 days ago, funds not received"
- "Account locked, cannot login"

**Actions**:
1. Assign to experienced agent immediately
2. Escalate if not resolved in 2 hours
3. Update customer every hour
4. Follow up after resolution

---

### Medium (P3) - Response: <2h, Resolve: <24h
**Criteria**:
- Feature not working as expected
- Questions about fees or policies
- Statement requests
- Notification issues

**Examples**:
- "Interest not credited on time"
- "How do I use mobile deposit?"
- "Why was I charged this fee?"
- "Notifications not working since v1.2 update"

**Actions**:
1. Assign to available agent
2. Check KB for existing articles
3. Escalate if requires technical investigation
4. Close with customer confirmation

---

### Low (P4) - Response: <4h, Resolve: <48h
**Criteria**:
- General inquiries
- Feature requests
- Minor UI issues
- Account information updates

**Examples**:
- "Can I change my registered email?"
- "What's the interest rate for Digital Saving?"
- "Dark mode icons look weird"

**Actions**:
1. Assign to any available agent
2. Use templates for common questions
3. Batch process if similar issues
4. No escalation needed

---

## SLA (Service Level Agreements)

| Priority | First Response | Resolution | Update Frequency |
|----------|----------------|------------|------------------|
| Critical (P1) | Immediate | 2 hours | Every 30 min |
| High (P2) | 30 minutes | 4 hours | Every 1 hour |
| Medium (P3) | 2 hours | 24 hours | Every 4 hours |
| Low (P4) | 4 hours | 48 hours | Daily |

**Note**: Clock stops during customer wait (awaiting customer response)

---

## Ticket Assignment Rules

### Auto-Assignment
- Tickets distributed via round-robin to available agents
- P1/P2 go to senior agents first (>6 months experience)
- Language-based routing (Thai/English)

### Manual Assignment
- Manager can override for specialized cases
- Assign to same agent if follow-up ticket
- Balance workload across team

### Queue Limits
- Max 15 active tickets per agent
- P1: Max 2 simultaneous per agent
- Overflow assigned to backup team

---

## First Response Templates

### Acknowledge Receipt
```
สวัสดีค่ะ/ครับ [Customer Name],

ขอบคุณที่ติดต่อ dBank ค่ะ/ครับ 

เราได้รับเรื่องของคุณเรียบร้อยแล้ว (Ticket #[TICKET_ID])
Priority: [P1/P2/P3/P4]
Expected Resolution: [TIME]

ตอนนี้เราได้มอบหมายเรื่องนี้ให้ทีมที่เกี่ยวข้องตรวจสอบแล้วค่ะ/ครับ 
เราจะอัพเดทข้อมูลให้คุณทราบภายใน [TIME]

ขอแสดงความนับถือ,
[Agent Name]
dBank Customer Support
```

(English version available in system)

---

## Knowledge Base Integration

### Before Creating Ticket
**Always check KB first:**
- Help > Search FAQ
- kb.dbank.co.th (internal)
- ~40% of questions already documented

### Common KB Articles (Link to Customer)
1. **How to reset password**: kb.dbank.co.th/reset-password
2. **Mobile deposit guide**: kb.dbank.co.th/mobile-deposit
3. **Interest calculation explained**: kb.dbank.co.th/interest-calc
4. **Transaction limits**: kb.dbank.co.th/limits

### Update KB
- If same question asked >5 times in a week: Create/update KB article
- Submit to KB team: kb-team@dbank.co.th
- Credit given for contributions

---

## Repeat Questions (v1.2 Specific)

### Post-v1.2 Top FAQs

**1. "How do I use mobile deposit?"** (28% of tickets)
- **Action**: Send KB article + video tutorial
- **Link**: kb.dbank.co.th/mobile-deposit-tutorial
- **Follow-up**: "Did this help?" (measure effectiveness)

**2. "Notifications not working"** (22% of tickets)
- **Known Issue**: Post-v1.2 notification delays during peak hours
- **Workaround**: Check app directly
- **Action**: Add to KB, link in template response
- **ETA Fix**: v1.2.1 (Feb 5)

**3. "App slower after update"** (15% of tickets)
- **Reality**: v1.2 is 65% faster (perception issue)
- **Action**: Educate customer on performance improvements
- **Ask**: Specific scenario where slow? (gather data)

---

## PII (Personally Identifiable Information) Handling

### What is PII?
- Full name with account number
- Email address
- Phone number
- National ID number
- Full account number
- Transaction details with personal identifiers

### Rules
**NEVER share PII**:
- Via email (unless encrypted)
- In screenshots shared externally
- In Slack/Teams (use ticket system)
- In public KB articles (anonymize examples)

**Masking Requirements**:
- Account numbers: Show last 4 digits only (****1234)
- National ID: Show first 1, last 2 digits (3-****-***-**-12)
- Email: Mask middle (j***@example.com)
- Phone: Mask middle (08X-XXX-1234)

**Exceptions** (with customer consent):
- Internal escalations (use encrypted ticket system)
- Regulatory requests (log access)
- Fraud investigations (security team only)

---

## Escalation Path

### When to Escalate
- Cannot resolve within SLA timeframe
- Requires specialized knowledge (legal, compliance)
- Customer requests manager
- Potentially fraudulent activity
- Bug requires engineering team

### How to Escalate
1. **Update Ticket**:
   - Status: "Escalated"
   - Reason: [Clear explanation]
   - Attempts made: [List what you tried]
   - Customer impact: [High/Medium/Low]

2. **Notify Recipient**:
   - Slack: #support-escalations
   - Tag: @L2-support or @support-manager
   - Include: Ticket # and 1-sentence summary

3. **Inform Customer**:
   - "I'm escalating this to our specialist team"
   - "You'll receive an update within [TIME]"
   - Set expectation: Don't over-promise

---

## Quality Standards

### Required Information in Every Ticket
1. **Customer Details**:
   - Name (masked externally)
   - Account number (last 4 digits)
   - Contact method preference

2. **Issue Description**:
   - What happened?
   - When did it start?
   - What were they trying to do?
   - Error messages (if any)

3. **Device/App Info**:
   - Platform: iOS/Android
   - App version
   - OS version (if relevant)

4. **Actions Taken**:
   - Troubleshooting steps performed
   - Articles shared
   - Escalations made

5. **Resolution**:
   - What fixed it?
   - Root cause (if identified)
   - Follow-up required? (Yes/No)

---

## Post-Resolution

### Customer Confirmation
- **Always confirm**: "Has this resolved your issue?"
- **Get explicit consent** before closing
- **If No**: Reopen investigation

### CSAT Survey
- Auto-sent after ticket closure
- Target: >4.0/5 average
- Review feedback weekly in team meeting

### Follow-Up
- P1/P2: Follow up in 24 hours to ensure still resolved
- P3: Optional follow-up if complex issue
- P4: No follow-up needed

---

## Metrics & Performance

### Individual Agent Targets
- **First Response Time**: 90% within SLA
- **Resolution Time**: 85% within SLA
- **CSAT Score**: >4.2/5
- **Reopened Tickets**: <5%
- **Tickets per Day**: 28-35 (sustainable)

### Team Targets (Q1 2025)
- **Average Resolution Time**: <3h (current: 2.8h) ✅
- **First Contact Resolution**: >70% (current: 68%)
- **Customer Satisfaction**: >4.3 (current: 4.1)
- **KB Deflection Rate**: >25%

---

## Version-Specific Handling

### v1.2 Release Considerations
- **Ticket Spike Expected**: 35% increase post-major release (Jan 15-30)
- **New Features**: Mobile deposit, dark mode, enhanced login
- **Known Issues**: See known_issues.md
- **Temporary Team**: 3 additional agents during spike period

### Communication Templates
- Updated templates for v1.2 issues in system
- Tag tickets with: #v1.2-related
- Daily standup: Share patterns observed

---

## Self-Care & Team Support

### Prevent Burnout
- Max 8 hours/day (strict)
- 15-minute break every 2 hours
- Rotate difficult customer tickets
- Escalate if emotionally draining

### Team Support
- **Daily Standups**: 9am (15 minutes)
- **Weekly Retro**: Friday 4pm
- **Buddy System**: Pair new agents with mentors
- **Slack**: #support-team for quick questions

### Recognition
- **Ticket of the Week**: Outstanding resolution
- **Customer Praise**: Shared in all-hands
- **Performance Bonus**: Based on CSAT + metrics

---

## Tools & Resources

### Internal Tools
- **Ticketing System**: Zendesk (support.dbank.co.th)
- **KB**: kb.dbank.co.th
- **Customer DB**: Salesforce (read-only)
- **Logs**: Datadog (for tech issues)

### Quick Links
- Known Issues: [Link]
- Product Policies: [Link]
- Troubleshooting Guide: [Link]
- Escalation Form: [Link]

---

**Questions on these guidelines?**  
Contact: support-manager@dbank.co.th  
Slack: #support-team
