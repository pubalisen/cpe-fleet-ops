---
name: enrollment-playbook
description: >
  Step-by-step enrollment procedures for Chrome Browser and ChromeOS devices.
  Covers initial enrollment, forced re-enrollment, zero-touch enrollment,
  troubleshooting common enrollment failures, and deprovisioning.
---

# Chrome / ChromeOS Enrollment Playbook

## Enrollment Methods

### 1. Manual Enrollment (ChromeOS)
1. Power on the Chromebook → reach OOBE (Out of Box Experience)
2. Connect to Wi-Fi
3. At sign-in screen, enter the managed Google account (user@domain.com)
4. Device auto-enrolls into the org's management domain
5. Verify: Settings > About ChromeOS > "Managed by [domain]"

### 2. Forced Re-enrollment
When a device has been enterprise-enrolled before:
1. Admin Console → Devices → Chrome → Settings → Enrollment & Access
2. Set **Forced Re-enrollment** to "Force device to re-enroll"
3. Scope: Apply at the OU level where the device was last managed
4. After powerwash, device automatically re-enrolls (no user bypass)

**Common failure**: Device shows "This device is not managed" after powerwash
- Check: Was `ForceReenrollment` enabled BEFORE the powerwash?
- Check: Does the device serial exist in Admin Console → Devices?
- Fix: If serial is present, deprovision → re-add → re-enroll

### 3. Zero-Touch Enrollment
For new devices purchased through reseller:
1. Reseller registers device serials with Google Admin
2. Devices appear in Admin Console → Devices → Chrome → Provisioning
3. Assign target OU for auto-provisioned devices
4. On first boot, device enrolls without user interaction

### 4. Chrome Browser Cloud Management (CBCM)
For managed Chrome Browser on Windows/Mac/Linux:
1. Admin Console → Devices → Chrome → Managed Browsers
2. Generate enrollment token: Settings → Enrollment Token
3. Deploy token via:
   - Windows: Registry key `CloudManagementEnrollmentToken`
   - macOS: plist `com.google.Chrome.plist`
   - Linux: `/etc/opt/chrome/policies/managed/`
4. Chrome auto-enrolls on next launch

## Troubleshooting

### "Unable to find your account" at enrollment
- Verify: Admin Console → Account → Account settings → Device enrollment
- Check: "Allow users in your organization to enroll a Chrome device" is ON
- Check: User has the correct license (Chrome Enterprise Upgrade)

### Device stuck at enrollment screen
- Network: Can device reach `m.google.com`, `accounts.google.com`, `clients.google.com`?
- Proxy: Are these URLs allowlisted in the proxy/firewall?
- DNS: Resolve `accounts.google.com` successfully?

### Policy not applying after enrollment
- Wait 30 minutes for initial policy sync
- Force sync: chrome://policy → "Reload policies"
- Check: Correct OU assignment in Admin Console → Devices → Chrome
- Check: Policy scope (user vs device level)

## Deprovisioning
1. Admin Console → Devices → Chrome
2. Select device(s) → Actions → Deprovision
3. Options:
   - **Same org re-enrollment**: Device can re-enroll in same domain
   - **Different org**: Releases device for new organization
   - **Retire**: Permanently removes from management
4. After deprovisioning, powerwash the device
