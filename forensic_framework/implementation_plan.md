# Role-Based Access Control Migration

Implemented a distinct dual-login system for Admin and Investigator roles within the Streamlit framework.

## Proposed Changes

### Database
- Update `users` table to support additional investigator profile fields.
- Seed the DB with dual roles: Auditor (Admin) and Field Investigator.

### UI / UX
- **Modified Login Page**: Choice between "Public/Investigator" and "Secure Admin" entry.
- **Investigator Portal**: High-end visual dashboard tailored for evidence collection.
- **Admin Dashboard**: Comprehensive auditing and system management view.

## Verification Plan
- Login as `admin` to verify Auditor dashboard.
- Login as `detective1` to verify Investigator dashboard.
