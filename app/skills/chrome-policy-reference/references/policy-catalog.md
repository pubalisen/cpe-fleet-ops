# Chrome Enterprise Policy Catalog — Top 50

## Enrollment & Device Management

| Policy | Type | Values | Scope | Platform |
|--------|------|--------|-------|----------|
| DeviceEnrollmentMode | enum | forced, optional, disabled | Device | ChromeOS |
| ForceReenrollment | bool | true, false | Device | ChromeOS |
| DeviceBlockDevmode | bool | true, false | Device | ChromeOS |
| ChromeDeviceAutoUpdatePolicy | enum | allow, block, pin_to_version | Device | ChromeOS |
| DeviceGuestModeEnabled | bool | true, false | Device | ChromeOS |

## Security & Authentication

| Policy | Type | Values | Scope | Platform |
|--------|------|--------|-------|----------|
| BrowserSignin | int | 0 (disabled), 1 (enabled), 2 (forced) | User | Both |
| SafeBrowsingProtectionLevel | int | 0 (off), 1 (standard), 2 (enhanced) | User | Both |
| PasswordManagerEnabled | bool | true, false | User | Both |
| IncognitoModeAvailability | int | 0 (available), 1 (disabled), 2 (forced) | User | Both |
| DeveloperToolsAvailability | int | 0 (always), 1 (extensions), 2 (disabled) | User | Both |
| EnableMediaRouter | bool | true, false | User | Both |
| AutofillCreditCardEnabled | bool | true, false | User | Both |
| PaymentMethodQueryEnabled | bool | true, false | User | Both |

## Extension Management

| Policy | Type | Values | Scope | Platform |
|--------|------|--------|-------|----------|
| ExtensionInstallBlocklist | list | extension IDs or '*' | User | Both |
| ExtensionInstallAllowlist | list | extension IDs | User | Both |
| ExtensionInstallForcelist | list | extension_id;update_url | User | Both |
| ExtensionSettings | dict/JSON | per-extension configs | User | Both |
| BlockExternalExtensions | bool | true, false | User | Both |
| ExtensionInstallSources | list | URLs | User | Both |

## Data Loss Prevention

| Policy | Type | Values | Scope | Platform |
|--------|------|--------|-------|----------|
| PrintingEnabled | bool | true, false | User | Both |
| ScreenCaptureAllowed | bool | true, false | User | Both |
| ExternalStorageDisabled | bool | true, false | Device | ChromeOS |
| DataLeakPreventionRulesList | list/JSON | DLP rule definitions | User | Both |
| DownloadRestrictions | int | 0 (none), 1 (dangerous), 2 (potentially), 3 (all), 4 (malicious) | User | Both |
| SavingBrowserHistoryDisabled | bool | true, false | User | Both |
| SyncDisabled | bool | true, false | User | Both |

## Network & Proxy

| Policy | Type | Values | Scope | Platform |
|--------|------|--------|-------|----------|
| ProxyMode | enum | direct, auto_detect, pac_script, fixed_servers, system | User | Both |
| DnsOverHttpsMode | enum | off, automatic, secure | User | Both |
| WebRtcIPHandling | enum | default, disable_non_proxied_udp | User | Both |
| CertificateTransparencyEnforcementDisabledForUrls | list | URL patterns | User | Both |

## User Experience

| Policy | Type | Values | Scope | Platform |
|--------|------|--------|-------|----------|
| HomepageLocation | string | URL | User | Both |
| RestoreOnStartup | int | 1 (restore), 4 (URLs), 5 (new tab) | User | Both |
| BookmarkBarEnabled | bool | true, false | User | Both |
| TranslateEnabled | bool | true, false | User | Both |
| DefaultSearchProviderEnabled | bool | true, false | User | Both |
| DefaultBrowserSettingEnabled | bool | true, false | User | Chrome Browser |

## Reporting & Monitoring

| Policy | Type | Values | Scope | Platform |
|--------|------|--------|-------|----------|
| CloudReportingEnabled | bool | true, false | User | Both |
| ChromeReportingExtensionForceInstall | bool | true, false | User | Both |
| ReportDeviceUsers | bool | true, false | Device | ChromeOS |
| ReportDeviceActivityTimes | bool | true, false | Device | ChromeOS |
| ReportDeviceHardwareStatus | bool | true, false | Device | ChromeOS |
