# Entity-Relationship Diagram (ERD)
## Orthodontic Wire Generator - Database Design

**Document Version:** 1.0  
**Date:** January 9, 2026  
**Applicability:** Phase 2-3 (Cloud & Collaboration Features)  
**Current Status:** Planning Document (No database in V1.0)

---

## Overview

This document defines the database schema for future cloud-based features including:
- User accounts and authentication
- Cloud project storage
- Collaboration and sharing
- Batch processing queues
- Activity logging and analytics

**Note:** Version 1.0 is desktop-only with file-based storage. This ERD guides future development when transitioning to cloud platform.

---

## Database Technology Recommendations

### Primary Database: **PostgreSQL 14+**

**Rationale:**
- Excellent JSON support (for flexible metadata storage)
- Strong ACID compliance (data integrity)
- Mature, well-documented, open-source
- Excellent spatial data support (PostGIS for 3D coordinates)
- Proven scalability (millions of rows)

**Alternatives:**
- **MySQL/MariaDB:** Good alternative, slightly less advanced JSON support
- **MongoDB:** NoSQL option, good for flexible schemas but less mature for complex queries

### Object Storage: **AWS S3 / Google Cloud Storage**

For large binary files (STL meshes, wire paths):
- Store file metadata in PostgreSQL
- Store actual file content in object storage
- Reference via URL/path in database

**Cost:** ~$0.023 per GB/month (S3 Standard)

---

## Entity-Relationship Diagram

### High-Level Overview

```
┌──────────┐         ┌──────────┐         ┌──────────┐
│  Users   │────────▶│ Projects │◀────────│  Teams   │
└──────────┘   owns  └──────────┘  member └──────────┘
                          │                      │
                          │                      │
                          ▼                      ▼
                    ┌──────────┐         ┌──────────┐
                    │WireDesign│         │TeamMember│
                    └──────────┘         └──────────┘
                          │
                          ├──────┬─────────┐
                          ▼      ▼         ▼
                    ┌──────┐ ┌──────┐ ┌────────┐
                    │Exports│ │Comments│ │Activity│
                    └──────┘ └──────┘ └────────┘
```

---

## Core Entities

### 1. Users

Represents application users (orthodontists, lab techs, students).

```sql
CREATE TABLE users (
    user_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email               VARCHAR(255) UNIQUE NOT NULL,
    password_hash       VARCHAR(255) NOT NULL,  -- bcrypt hash
    full_name           VARCHAR(255) NOT NULL,
    organization        VARCHAR(255),           -- Practice/Lab name
    role                VARCHAR(50) NOT NULL,   -- 'orthodontist', 'technician', 'student', 'admin'
    
    -- Subscription
    subscription_tier   VARCHAR(50) DEFAULT 'free',  -- 'free', 'pro', 'enterprise'
    subscription_status VARCHAR(50) DEFAULT 'active', -- 'active', 'cancelled', 'expired'
    trial_ends_at       TIMESTAMP,
    
    -- Settings
    preferences         JSONB DEFAULT '{}',     -- UI preferences, default parameters
    
    -- Metadata
    created_at          TIMESTAMP DEFAULT NOW(),
    updated_at          TIMESTAMP DEFAULT NOW(),
    last_login_at       TIMESTAMP,
    email_verified      BOOLEAN DEFAULT FALSE,
    is_active           BOOLEAN DEFAULT TRUE,
    
    -- Constraints
    CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CHECK (role IN ('orthodontist', 'technician', 'student', 'admin')),
    CHECK (subscription_tier IN ('free', 'pro', 'enterprise'))
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_organization ON users(organization);
CREATE INDEX idx_users_created_at ON users(created_at DESC);
```

**Example Row:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "dr.sarah@orthodontics.com",
  "full_name": "Dr. Sarah Chen",
  "organization": "Chen Orthodontics",
  "role": "orthodontist",
  "subscription_tier": "pro",
  "preferences": {
    "default_workflow": "hybrid",
    "ui_theme": "dark_gradient",
    "default_tooth_count": 14
  },
  "created_at": "2026-01-15T10:30:00Z"
}
```

---

### 2. Projects

Container for related wire designs (e.g., one patient's treatment).

```sql
CREATE TABLE projects (
    project_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_user_id       UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    team_id             UUID REFERENCES teams(team_id) ON DELETE SET NULL,
    
    -- Project Info
    title               VARCHAR(255) NOT NULL,
    description         TEXT,
    patient_identifier  VARCHAR(100),  -- Optional, NOT PHI (e.g., "Case #12345")
    
    -- Status
    status              VARCHAR(50) DEFAULT 'draft',  -- 'draft', 'in_progress', 'completed', 'archived'
    
    -- Metadata
    created_at          TIMESTAMP DEFAULT NOW(),
    updated_at          TIMESTAMP DEFAULT NOW(),
    last_accessed_at    TIMESTAMP DEFAULT NOW(),
    
    -- Sharing
    is_public           BOOLEAN DEFAULT FALSE,
    share_token         VARCHAR(64) UNIQUE,  -- For public sharing links
    
    -- Tags
    tags                TEXT[],  -- Array of tags for organization
    
    -- Constraints
    CHECK (status IN ('draft', 'in_progress', 'completed', 'archived')),
    CHECK (LENGTH(title) >= 3)
);

-- Indexes
CREATE INDEX idx_projects_owner ON projects(owner_user_id);
CREATE INDEX idx_projects_team ON projects(team_id);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_updated_at ON projects(updated_at DESC);
CREATE INDEX idx_projects_tags ON projects USING GIN(tags);
```

**Example Row:**
```json
{
  "project_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "owner_user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Patient Case #12345 - Class II Correction",
  "description": "Severe Class II malocclusion, treatment plan includes upper and lower archwires",
  "patient_identifier": "Case #12345",
  "status": "in_progress",
  "tags": ["class-ii", "extraction", "upper-lower"],
  "created_at": "2026-01-15T14:20:00Z"
}
```

---

### 3. WireDesigns

Individual wire designs within a project.

```sql
CREATE TABLE wire_designs (
    design_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          UUID NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
    created_by_user_id  UUID NOT NULL REFERENCES users(user_id),
    
    -- Design Info
    name                VARCHAR(255) NOT NULL,  -- e.g., "Upper Arch - Stage 1"
    arch_type           VARCHAR(10) NOT NULL,   -- 'upper' or 'lower'
    version             INTEGER DEFAULT 1,      -- Version number for tracking changes
    
    -- Workflow
    workflow_mode       VARCHAR(20) NOT NULL,   -- 'automatic', 'manual', 'hybrid'
    
    -- Input Files (stored in S3/GCS)
    stl_file_url        TEXT NOT NULL,          -- S3 URL: s3://bucket/user/project/original.stl
    stl_file_hash       VARCHAR(64),            -- SHA-256 hash for integrity
    stl_file_size_bytes BIGINT,
    
    -- Detection Results
    num_teeth_detected  INTEGER,
    tooth_positions     JSONB,  -- Array of [x,y,z] coordinates
    detection_confidence JSONB, -- Array of confidence scores per tooth
    
    -- Wire Parameters
    parameters          JSONB NOT NULL,  -- All generation parameters
    /* Example parameters:
    {
      "height_offset_mm": 2.5,
      "depth_offset_mm": 0.0,
      "smoothing_sigma": 12.0,
      "smoothing_passes": 5,
      "points_per_segment": 300,
      "bracket_prescription": "roth"
    }
    */
    
    -- Wire Path (stored in S3/GCS for large datasets)
    wire_path_url       TEXT,                   -- S3 URL: s3://bucket/user/project/wire.json
    wire_path_points    INTEGER,                -- Number of points in path
    wire_length_mm      NUMERIC(10, 3),         -- Total wire length
    smoothness_score    NUMERIC(5, 4),          -- Quality metric (0.0 to 1.0)
    
    -- Metadata
    created_at          TIMESTAMP DEFAULT NOW(),
    updated_at          TIMESTAMP DEFAULT NOW(),
    generation_time_ms  INTEGER,                -- Algorithm execution time
    
    -- Status
    status              VARCHAR(50) DEFAULT 'draft',  -- 'draft', 'finalized', 'exported', 'archived'
    
    -- Constraints
    CHECK (arch_type IN ('upper', 'lower')),
    CHECK (workflow_mode IN ('automatic', 'manual', 'hybrid')),
    CHECK (status IN ('draft', 'finalized', 'exported', 'archived')),
    CHECK (version >= 1)
);

-- Indexes
CREATE INDEX idx_wire_designs_project ON wire_designs(project_id);
CREATE INDEX idx_wire_designs_created_by ON wire_designs(created_by_user_id);
CREATE INDEX idx_wire_designs_arch_type ON wire_designs(arch_type);
CREATE INDEX idx_wire_designs_status ON wire_designs(status);
CREATE INDEX idx_wire_designs_created_at ON wire_designs(created_at DESC);
```

**Example Row:**
```json
{
  "design_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "project_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "created_by_user_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Upper Arch - Initial Wire",
  "arch_type": "upper",
  "version": 1,
  "workflow_mode": "hybrid",
  "stl_file_url": "s3://ortho-wires/users/550e8400/projects/7c9e6679/upper_arch.stl",
  "num_teeth_detected": 14,
  "parameters": {
    "height_offset_mm": 2.5,
    "smoothing_sigma": 12.0,
    "smoothing_passes": 5
  },
  "wire_length_mm": 145.32,
  "smoothness_score": 0.9523,
  "status": "finalized",
  "created_at": "2026-01-15T15:00:00Z"
}
```

---

### 4. Exports

Track exported wire designs (G-code, STL, Arduino, etc.).

```sql
CREATE TABLE exports (
    export_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    design_id           UUID NOT NULL REFERENCES wire_designs(design_id) ON DELETE CASCADE,
    exported_by_user_id UUID NOT NULL REFERENCES users(user_id),
    
    -- Export Details
    format              VARCHAR(50) NOT NULL,   -- 'gcode', 'stl', 'arduino', 'csv', 'json', 'pdf'
    format_options      JSONB,                  -- Format-specific options (feed rate, etc.)
    
    -- File Storage
    file_url            TEXT NOT NULL,          -- S3 URL
    file_size_bytes     BIGINT,
    file_hash           VARCHAR(64),            -- SHA-256 hash
    
    -- Metadata
    created_at          TIMESTAMP DEFAULT NOW(),
    download_count      INTEGER DEFAULT 0,
    last_downloaded_at  TIMESTAMP,
    
    -- Constraints
    CHECK (format IN ('gcode', 'stl', 'arduino', 'csv', 'json', 'pdf'))
);

-- Indexes
CREATE INDEX idx_exports_design ON exports(design_id);
CREATE INDEX idx_exports_user ON exports(exported_by_user_id);
CREATE INDEX idx_exports_format ON exports(format);
CREATE INDEX idx_exports_created_at ON exports(created_at DESC);
```

---

### 5. Comments

User comments on wire designs (collaboration feature).

```sql
CREATE TABLE comments (
    comment_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    design_id           UUID NOT NULL REFERENCES wire_designs(design_id) ON DELETE CASCADE,
    user_id             UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    parent_comment_id   UUID REFERENCES comments(comment_id) ON DELETE CASCADE,  -- For replies
    
    -- Comment Content
    content             TEXT NOT NULL,
    
    -- Optional: Attach to specific location in 3D space
    location_3d         JSONB,  -- {x: 12.3, y: 5.6, z: 2.1} for spatial comments
    
    -- Metadata
    created_at          TIMESTAMP DEFAULT NOW(),
    updated_at          TIMESTAMP DEFAULT NOW(),
    is_resolved         BOOLEAN DEFAULT FALSE,
    
    -- Constraints
    CHECK (LENGTH(content) >= 1 AND LENGTH(content) <= 5000)
);

-- Indexes
CREATE INDEX idx_comments_design ON comments(design_id);
CREATE INDEX idx_comments_user ON comments(user_id);
CREATE INDEX idx_comments_parent ON comments(parent_comment_id);
CREATE INDEX idx_comments_created_at ON comments(created_at DESC);
```

---

### 6. ActivityLog

Track user actions for analytics and audit trail.

```sql
CREATE TABLE activity_log (
    log_id              BIGSERIAL PRIMARY KEY,
    user_id             UUID REFERENCES users(user_id) ON DELETE SET NULL,
    
    -- Activity Details
    action_type         VARCHAR(100) NOT NULL,  -- 'project_created', 'wire_generated', 'export_created', etc.
    entity_type         VARCHAR(50),            -- 'project', 'wire_design', 'export'
    entity_id           UUID,                   -- ID of affected entity
    
    -- Additional Context
    metadata            JSONB,                  -- Action-specific details
    
    -- Request Info
    ip_address          INET,
    user_agent          TEXT,
    
    -- Timestamp
    created_at          TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CHECK (entity_type IN ('project', 'wire_design', 'export', 'user', 'team'))
);

-- Indexes (Partition by month for performance)
CREATE INDEX idx_activity_log_user ON activity_log(user_id, created_at DESC);
CREATE INDEX idx_activity_log_entity ON activity_log(entity_type, entity_id);
CREATE INDEX idx_activity_log_action ON activity_log(action_type);
CREATE INDEX idx_activity_log_created_at ON activity_log(created_at DESC);
```

---

## Supporting Entities (Phase 3+)

### 7. Teams

For organizations with multiple users (dental labs, large practices).

```sql
CREATE TABLE teams (
    team_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_user_id       UUID NOT NULL REFERENCES users(user_id),
    
    -- Team Info
    name                VARCHAR(255) NOT NULL,
    description         TEXT,
    
    -- Subscription
    subscription_tier   VARCHAR(50) DEFAULT 'free',
    max_members         INTEGER DEFAULT 5,
    
    -- Metadata
    created_at          TIMESTAMP DEFAULT NOW(),
    updated_at          TIMESTAMP DEFAULT NOW(),
    is_active           BOOLEAN DEFAULT TRUE
);

CREATE TABLE team_members (
    team_id             UUID REFERENCES teams(team_id) ON DELETE CASCADE,
    user_id             UUID REFERENCES users(user_id) ON DELETE CASCADE,
    role                VARCHAR(50) NOT NULL,  -- 'owner', 'admin', 'member', 'viewer'
    joined_at           TIMESTAMP DEFAULT NOW(),
    
    PRIMARY KEY (team_id, user_id),
    CHECK (role IN ('owner', 'admin', 'member', 'viewer'))
);

-- Indexes
CREATE INDEX idx_team_members_team ON team_members(team_id);
CREATE INDEX idx_team_members_user ON team_members(user_id);
```

---

### 8. ProjectShares

Granular sharing permissions for projects.

```sql
CREATE TABLE project_shares (
    share_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          UUID NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
    shared_with_user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    shared_with_team_id UUID REFERENCES teams(team_id) ON DELETE CASCADE,
    shared_by_user_id   UUID NOT NULL REFERENCES users(user_id),
    
    -- Permissions
    permission_level    VARCHAR(50) NOT NULL,  -- 'view', 'comment', 'edit'
    
    -- Metadata
    created_at          TIMESTAMP DEFAULT NOW(),
    expires_at          TIMESTAMP,             -- Optional expiration
    
    -- Constraints
    CHECK (
        (shared_with_user_id IS NOT NULL AND shared_with_team_id IS NULL) OR
        (shared_with_user_id IS NULL AND shared_with_team_id IS NOT NULL)
    ),
    CHECK (permission_level IN ('view', 'comment', 'edit'))
);

-- Indexes
CREATE INDEX idx_project_shares_project ON project_shares(project_id);
CREATE INDEX idx_project_shares_user ON project_shares(shared_with_user_id);
CREATE INDEX idx_project_shares_team ON project_shares(shared_with_team_id);
```

---

### 9. BatchJobs

For laboratory batch processing workflows.

```sql
CREATE TABLE batch_jobs (
    job_id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    team_id             UUID REFERENCES teams(team_id) ON DELETE SET NULL,
    
    -- Job Details
    name                VARCHAR(255) NOT NULL,
    description         TEXT,
    total_items         INTEGER NOT NULL,
    completed_items     INTEGER DEFAULT 0,
    failed_items        INTEGER DEFAULT 0,
    
    -- Processing
    workflow_mode       VARCHAR(20) NOT NULL,
    parameters          JSONB NOT NULL,  -- Shared parameters for all items
    
    -- Status
    status              VARCHAR(50) DEFAULT 'pending',  -- 'pending', 'processing', 'completed', 'failed', 'cancelled'
    
    -- Timing
    created_at          TIMESTAMP DEFAULT NOW(),
    started_at          TIMESTAMP,
    completed_at        TIMESTAMP,
    
    -- Constraints
    CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled'))
);

CREATE TABLE batch_job_items (
    item_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id              UUID NOT NULL REFERENCES batch_jobs(job_id) ON DELETE CASCADE,
    
    -- Item Details
    stl_file_url        TEXT NOT NULL,
    item_name           VARCHAR(255),
    sequence_number     INTEGER NOT NULL,  -- Order within batch
    
    -- Result
    design_id           UUID REFERENCES wire_designs(design_id),
    status              VARCHAR(50) DEFAULT 'pending',
    error_message       TEXT,
    
    -- Timing
    started_at          TIMESTAMP,
    completed_at        TIMESTAMP,
    
    -- Constraints
    CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'skipped'))
);

-- Indexes
CREATE INDEX idx_batch_jobs_user ON batch_jobs(user_id);
CREATE INDEX idx_batch_jobs_status ON batch_jobs(status);
CREATE INDEX idx_batch_job_items_job ON batch_job_items(job_id);
```

---

## Data Flow Examples

### Example 1: User Creates New Wire Design

```sql
-- 1. User logs in
SELECT * FROM users WHERE email = 'dr.sarah@orthodontics.com';

-- 2. Create new project
INSERT INTO projects (owner_user_id, title, description)
VALUES (
    '550e8400-e29b-41d4-a716-446655440000',
    'Patient Case #12345',
    'Class II correction'
)
RETURNING project_id;

-- 3. Upload STL → S3, create wire design
INSERT INTO wire_designs (
    project_id, 
    created_by_user_id, 
    name, 
    arch_type,
    workflow_mode,
    stl_file_url,
    parameters
)
VALUES (
    '7c9e6679-7425-40de-944b-e07fc1f90ae7',
    '550e8400-e29b-41d4-a716-446655440000',
    'Upper Arch - Stage 1',
    'upper',
    'automatic',
    's3://ortho-wires/users/550e8400/projects/7c9e6679/upper.stl',
    '{"height_offset_mm": 2.5, "smoothing_sigma": 12.0}'::jsonb
)
RETURNING design_id;

-- 4. Log activity
INSERT INTO activity_log (user_id, action_type, entity_type, entity_id)
VALUES (
    '550e8400-e29b-41d4-a716-446655440000',
    'wire_design_created',
    'wire_design',
    '3fa85f64-5717-4562-b3fc-2c963f66afa6'
);
```

---

### Example 2: Share Project with Colleague

```sql
-- Share project with another orthodontist
INSERT INTO project_shares (
    project_id,
    shared_with_user_id,
    shared_by_user_id,
    permission_level
)
VALUES (
    '7c9e6679-7425-40de-944b-e07fc1f90ae7',
    'colleague-user-id-here',
    '550e8400-e29b-41d4-a716-446655440000',
    'comment'  -- Can view and comment, but not edit
);
```

---

### Example 3: Batch Processing Query

```sql
-- Get all pending items in a batch job
SELECT 
    bji.item_id,
    bji.item_name,
    bji.stl_file_url,
    bj.parameters,
    bj.workflow_mode
FROM batch_job_items bji
JOIN batch_jobs bj ON bji.job_id = bj.job_id
WHERE bj.job_id = 'batch-job-id-here'
  AND bji.status = 'pending'
ORDER BY bji.sequence_number;
```

---

## JSON Schema Examples

### User Preferences (JSONB)

```json
{
  "ui_theme": "dark_gradient",
  "default_workflow": "hybrid",
  "default_parameters": {
    "height_offset_mm": 2.5,
    "depth_offset_mm": 0.0,
    "smoothing_sigma": 12.0,
    "smoothing_passes": 5,
    "tooth_count": 14
  },
  "keyboard_shortcuts": {
    "generate_wire": "Ctrl+G",
    "export": "Ctrl+E"
  },
  "recent_files": [
    "s3://ortho-wires/users/550e8400/recent1.stl",
    "s3://ortho-wires/users/550e8400/recent2.stl"
  ]
}
```

### Wire Design Parameters (JSONB)

```json
{
  "height_offset_mm": 2.5,
  "depth_offset_mm": 0.0,
  "smoothing_sigma": 12.0,
  "smoothing_passes": 5,
  "points_per_segment": 300,
  "bracket_prescription": "roth",
  "wire_material": "stainless_steel",
  "wire_diameter_inches": 0.016,
  "custom_adjustments": {
    "tooth_3": {"offset_x": 0.5, "offset_y": 0.2},
    "tooth_7": {"offset_z": -0.3}
  }
}
```

### Tooth Positions (JSONB)

```json
[
  {"tooth_number": 1, "position": [12.3, 5.6, 2.1], "confidence": 0.95},
  {"tooth_number": 2, "position": [10.1, 6.2, 2.3], "confidence": 0.92},
  {"tooth_number": 3, "position": [8.5, 7.1, 2.5], "confidence": 0.88},
  ...
]
```

---

## Migration Strategy (V1.0 → V2.0)

### Phase 1: Add Optional Cloud Sync (V1.5)

**Goal:** Allow users to optionally sync projects to cloud while maintaining local-first approach.

**Changes:**
1. Add "Sign In" button to desktop app (optional)
2. If signed in, auto-sync projects to cloud every 5 minutes
3. Local SQLite cache for offline work
4. Sync on app startup/shutdown

**Desktop Schema (SQLite):**
```sql
-- Local cache database (mirrors cloud structure)
CREATE TABLE local_projects (
    project_id TEXT PRIMARY KEY,
    cloud_synced_at TIMESTAMP,
    local_modified_at TIMESTAMP,
    sync_status TEXT,  -- 'synced', 'pending', 'conflict'
    data BLOB  -- Serialized project data
);
```

### Phase 2: Full Cloud Platform (V2.0)

**Goal:** Transition to cloud-first with offline support.

**Migration Steps:**
1. User clicks "Migrate to Cloud" in desktop app
2. App uploads all local projects to cloud
3. Cloud database populated with full schema (this ERD)
4. Desktop app becomes thin client (with offline cache)

---

## Database Sizing Estimates

### Year 1 Projections (500 active users)

| Table | Rows | Avg Row Size | Total Size |
|-------|------|--------------|------------|
| users | 500 | 2 KB | 1 MB |
| projects | 5,000 | 1 KB | 5 MB |
| wire_designs | 20,000 | 5 KB | 100 MB |
| exports | 40,000 | 1 KB | 40 MB |
| comments | 10,000 | 500 B | 5 MB |
| activity_log | 500,000 | 500 B | 250 MB |
| **Total Database** | | | **~400 MB** |

**File Storage (S3):**
- STL files: 20,000 × 10 MB avg = **200 GB**
- Wire paths: 20,000 × 500 KB avg = **10 GB**
- Exports: 40,000 × 200 KB avg = **8 GB**
- **Total S3:** **~220 GB** → **$5/month** at $0.023/GB

**Total Infrastructure Cost:** ~$50/month (database + storage + compute)

---

## Security & Compliance

### Data Protection

**Encryption:**
- At rest: AES-256 (PostgreSQL + S3)
- In transit: TLS 1.3 (HTTPS, database connections)
- Password storage: bcrypt with salt (cost factor 12)

**HIPAA Compliance (if storing PHI):**
⚠️ **IMPORTANT:** `patient_identifier` field should NOT contain PHI.
- Use case numbers, not patient names
- If full HIPAA compliance needed:
  - Business Associate Agreement (BAA) with cloud provider
  - Audit logging (all data access)
  - Encryption key management (KMS)
  - Access controls (role-based)

**GDPR Compliance (EU users):**
- Right to erasure: CASCADE delete on user account
- Data portability: Export all user data to JSON
- Consent tracking: Store in `user.preferences.consent_given`

### Access Control

**Row-Level Security (PostgreSQL RLS):**

```sql
-- Example: Users can only see their own projects
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;

CREATE POLICY project_owner_policy ON projects
    FOR ALL
    USING (owner_user_id = current_setting('app.user_id')::UUID);

CREATE POLICY project_shared_policy ON projects
    FOR SELECT
    USING (
        project_id IN (
            SELECT project_id FROM project_shares
            WHERE shared_with_user_id = current_setting('app.user_id')::UUID
        )
    );
```

---

## Backup & Disaster Recovery

### Backup Strategy

1. **Database:**
   - Automated daily backups (PostgreSQL WAL archiving)
   - Point-in-time recovery (PITR) up to 7 days
   - Weekly full backups retained for 30 days

2. **Object Storage (S3):**
   - Versioning enabled (retain 3 versions)
   - Cross-region replication (for disaster recovery)
   - Lifecycle policy: Archive to Glacier after 90 days

3. **Recovery Time Objective (RTO):** 4 hours
4. **Recovery Point Objective (RPO):** 1 hour

---

## API Design Hints

When building REST API on top of this schema:

**Endpoints:**
```
POST   /api/v1/projects                 # Create project
GET    /api/v1/projects/:id             # Get project details
PUT    /api/v1/projects/:id             # Update project
DELETE /api/v1/projects/:id             # Delete project

POST   /api/v1/projects/:id/designs     # Create wire design
GET    /api/v1/designs/:id              # Get wire design
PUT    /api/v1/designs/:id              # Update wire design

POST   /api/v1/designs/:id/exports      # Export wire
GET    /api/v1/exports/:id/download     # Download export file

POST   /api/v1/designs/:id/comments     # Add comment
GET    /api/v1/designs/:id/comments     # List comments
```

**Authentication:**
- JWT tokens (stored in `localStorage` for web app)
- API key for programmatic access
- OAuth2 for third-party integrations

---

## Conclusion

This ERD provides a comprehensive database design for future cloud and collaboration features. Key points:

1. **Not needed for V1.0** (desktop-only, file-based)
2. **Plan for Phase 2-3** (cloud storage, multi-user)
3. **Scalable design** (supports 10K+ users with minimal changes)
4. **Security-first** (encryption, RBAC, audit logging)
5. **Flexible** (JSONB fields for evolving requirements)

**Next Steps:**
- Keep this ERD as reference document
- Use JSON structure in current file-based storage (V1.0)
- Implement database when adding cloud features (V2.0)

---

**Document End - ERD v1.0**
