# backend/apps/standards/management/commands/generate_personnel_admin_sops.py

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.standards.models import StandardGroup, StandardSubGroup, Standard
from apps.users.models import User
from django.utils import timezone


class Command(BaseCommand):
    help = 'Generate Personnel & Administration SOPs (Group 2)'

    def handle(self, *args, **options):
        with transaction.atomic():
            # Get or create a system user for creation
            system_user, _ = User.objects.get_or_create(
                username='system',
                defaults={
                    'email': 'system@5eg.mil',
                    'is_active': True,
                    'is_admin': True
                }
            )

            # Create Personnel & Administration Group
            personnel_admin_group, created = StandardGroup.objects.get_or_create(
                name='Personnel & Administration',
                defaults={
                    'description': 'Standards governing personnel management, attendance, awards, and disciplinary procedures within the 5th Expeditionary Group.',
                    'order_index': 2,
                    'is_active': True,
                    'created_by': system_user
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS('Created Personnel & Administration group'))
            else:
                self.stdout.write(self.style.WARNING('Personnel & Administration group already exists'))

            # Create subgroups and their standards
            self._create_personnel_management_standards(personnel_admin_group, system_user)
            self._create_attendance_leave_standards(personnel_admin_group, system_user)
            self._create_awards_commendations_standards(personnel_admin_group, system_user)
            self._create_disciplinary_standards(personnel_admin_group, system_user)

            self.stdout.write(self.style.SUCCESS('Successfully generated all Personnel & Administration SOPs'))

    def _create_personnel_management_standards(self, group, user):
        """Create Personnel Management subgroup and its standards"""
        subgroup, _ = StandardSubGroup.objects.get_or_create(
            name='Personnel Management',
            standard_group=group,
            defaults={
                'description': 'Procedures for managing personnel throughout their service lifecycle from recruitment to separation.',
                'order_index': 1,
                'is_active': True,
                'created_by': user
            }
        )

        standards_data = [
            {
                'document_number': '2.1.1',
                'title': 'Recruitment & Application Procedure',
                'category': 'Procedure',
                'summary': 'Comprehensive procedures for recruiting new members and processing applications to the 5th Expeditionary Group.',
                'content': '''# Recruitment & Application Procedure

## Purpose
This procedure establishes the standardized process for recruiting potential members and processing applications to join the 5th Expeditionary Group, ensuring quality candidates are identified, vetted, and properly introduced to the organization.

## Scope
Applies to all recruitment activities, application processing, and initial screening of potential members across all branches and specialties within the 5EG.

## Recruitment Phase

### Step 1: Recruitment Planning
1.1. Assess personnel needs
   - Review manning levels by unit
   - Identify critical shortages
   - Project future requirements
   - Consider training pipeline time
   - Account for attrition rates

1.2. Develop recruitment targets
   - Officer requirements
   - NCO requirements
   - Enlisted requirements
   - Specialty positions
   - Geographic distribution

1.3. Create recruitment materials
   - Update website content
   - Prepare social media campaigns
   - Design promotional materials
   - Record recruitment videos
   - Draft forum posts

### Step 2: Recruitment Execution
2.1. Active recruitment channels:
   - Star Citizen forums
   - Reddit communities
   - Discord servers
   - Streaming platforms
   - Word of mouth referrals

2.2. Recruitment messaging:
   - Emphasize milsim aspects
   - Highlight training programs
   - Showcase operations
   - Feature member testimonials
   - Explain progression system

2.3. Recruiter responsibilities:
   - Respond within 24 hours
   - Provide accurate information
   - Screen for basic eligibility
   - Direct to application
   - Track contact metrics

### Step 3: Initial Screening
3.1. Basic eligibility criteria:
   - Age 16+ (18+ for leadership)
   - Own Star Citizen account
   - Discord voice capable
   - English communication
   - Time zone compatibility

3.2. Red flag indicators:
   - History of unit hopping
   - Disciplinary issues mentioned
   - Unrealistic expectations
   - Inability to commit time
   - Poor communication skills

3.3. Referral tracking:
   - Record source of contact
   - Note recruiting member
   - Track conversion rates
   - Identify successful channels
   - Reward successful referrals

## Application Processing

### Step 4: Application Submission
4.1. Application requirements:
   - Complete online form
   - Discord username
   - Star Citizen handle
   - Time zone/availability
   - Previous experience
   - Motivation statement

4.2. Technical setup:
   - Automated acknowledgment
   - Application database entry
   - Recruiter notification
   - Tracking number assignment
   - Status portal access

4.3. Application review timeline:
   - Initial review: 48 hours
   - Background check: 72 hours
   - Interview scheduling: 96 hours
   - Final decision: 7 days
   - Total process: 10 days maximum

### Step 5: Background Verification
5.1. Database checks:
   - Previous 5EG service
   - Blacklist verification
   - Allied unit inquiries
   - Public record search
   - Social media review

5.2. Reference verification:
   - Previous unit contact
   - Character references
   - Claimed experience
   - Leadership positions
   - Special qualifications

5.3. Documentation requirements:
   - Application form
   - Background check results
   - Reference responses
   - Recruiter notes
   - Red flag summary

### Step 6: Interview Process
6.1. Interview scheduling:
   - Offer multiple time slots
   - Accommodate time zones
   - Provide Discord link
   - Send reminder message
   - Have backup interviewer

6.2. Interview structure:
   - Welcome and introductions (5 min)
   - Experience discussion (10 min)
   - Expectations alignment (10 min)
   - Unit overview (15 min)
   - Questions and answers (10 min)
   - Next steps explanation (5 min)

6.3. Assessment areas:
   - Communication skills
   - Maturity level
   - Commitment ability
   - Team compatibility
   - Leadership potential
   - Technical knowledge

### Step 7: Decision Making
7.1. Approval criteria:
   - Meets basic requirements
   - Passes background check
   - Successful interview
   - Available positions
   - No red flags

7.2. Decision authorities:
   - Enlisted: Recruiting NCO
   - NCO: Recruiting Officer
   - Officer: Personnel Officer
   - Special: Department Head
   - Waiver: Executive Officer

7.3. Decision documentation:
   - Approval/denial reason
   - Conditions if any
   - Assigned unit/pathway
   - Start date coordination
   - Onboarding assignment

### Step 8: Notification
8.1. Acceptance notification:
   - Congratulations message
   - Discord invite link
   - Onboarding schedule
   - Point of contact
   - Required preparations

8.2. Deferral notification:
   - Specific reasons
   - Improvement suggestions
   - Reapplication timeline
   - Encouragement included
   - Alternative options

8.3. Denial notification:
   - Professional message
   - General reason category
   - Appeal process (if applicable)
   - Future eligibility
   - Best wishes

## Special Circumstances

### Prior Service Returns
- Expedited processing
- Service record review
- Previous issues check
- Rank restoration consideration
- Unit preference honored

### Allied Unit Transfers
- Reciprocity agreements
- Rank recognition
- Abbreviated process
- Documentation transfer
- Integration support

### Specialty Positions
- Technical assessment
- Portfolio review
- Skill demonstration
- Department interview
- Probationary period

## Quality Control

### Metrics Tracking
- Applications received
- Conversion rates
- Processing times
- Dropout points
- Success predictors

### Process Improvement
- Monthly review meeting
- Applicant feedback
- Recruiter suggestions
- Bottleneck identification
- System updates

### Recruiter Management
- Training requirements
- Performance standards
- Recognition program
- Resource provision
- Workload balance

## Documentation Requirements

### Application File Contents
- Original application
- Background check results
- Interview notes
- Decision documentation
- Correspondence record

### Data Protection
- Personal information security
- Access restrictions
- Retention periods
- Deletion procedures
- Privacy compliance

### Reporting Requirements
- Weekly pipeline report
- Monthly statistics
- Quarterly analysis
- Annual review
- Exception reports

## Common Issues

### Problem: Application Backlog
**Solutions:**
- Additional recruiters
- Streamlined process
- Automated screening
- Batch processing
- Clear priorities

### Problem: Poor Quality Applicants
**Solutions:**
- Refine messaging
- Target better channels
- Improve screening
- Enhance requirements
- Recruiter training

### Problem: High Early Dropout
**Solutions:**
- Better expectation setting
- Improved screening
- Buddy system
- Early engagement
- Exit interviews

## Best Practices

### Do's
- Respond promptly
- Be professional
- Set clear expectations
- Document everything
- Follow up regularly

### Don'ts
- Make promises
- Rush screening
- Ignore red flags
- Skip steps
- Discriminate

## Templates and Tools

### Standard Messages
- Initial contact response
- Application acknowledgment
- Interview invitation
- Acceptance letter
- Denial notification

### Tracking Spreadsheets
- Application pipeline
- Conversion metrics
- Time zone matrix
- Recruiter workload
- Success analysis

## References
- 2.1.2 Enlistment & Onboarding Procedure
- 2.1.3 Service Record Management Procedure
- 4.1.1 Basic Combat Training (BCT) Curriculum
- 9.2.1 Public Recruitment Guidelines''',
                'difficulty_level': 'Intermediate',
                'is_required': True,
                'tags': ['recruitment', 'personnel', 'application', 'screening', 'procedure']
            },
            {
                'document_number': '2.1.2',
                'title': 'Enlistment & Onboarding Procedure',
                'category': 'Procedure',
                'summary': 'Step-by-step procedures for enlisting accepted applicants and conducting initial onboarding.',
                'content': '''# Enlistment & Onboarding Procedure

## Purpose
This procedure ensures all accepted applicants are properly enlisted into the 5th Expeditionary Group and receive comprehensive onboarding that prepares them for successful integration into their assigned units.

## Scope
Applies to all new members from the point of acceptance through completion of initial onboarding, regardless of branch or intended specialty.

## Pre-Enlistment Phase

### Step 1: Acceptance Processing
1.1. Verify acceptance package:
   - Approved application
   - Background check clearance
   - Interview assessment
   - Unit assignment
   - Start date confirmed

1.2. Create personnel file:
   - Assign service number
   - Initialize service record
   - Create database entry
   - Set up permissions
   - Generate documentation

1.3. System access setup:
   - Discord roles assignment
   - Forum account creation
   - Website registration
   - Training platform access
   - Communication channels

### Step 2: Welcome Package Delivery
2.1. Digital welcome packet includes:
   - Welcome letter from CO
   - Unit organization chart
   - Initial reading materials
   - Onboarding schedule
   - Contact information

2.2. Administrative forms:
   - Personnel information form
   - Emergency contact data
   - Availability schedule
   - Specialty preferences
   - Commitment agreement

2.3. Resource provision:
   - Discord channel guide
   - Website navigation help
   - Uniform/insignia guidance
   - Communication protocols
   - FAQ document

## Enlistment Ceremony

### Step 3: Oath Administration
3.1. Scheduling requirements:
   - Within 72 hours of acceptance
   - Accommodate time zones
   - Officer available
   - Witnesses present
   - Recording capability

3.2. Ceremony procedure:
   - Gathering in designated channel
   - Introduction of new member
   - Oath reading by officer
   - Oath repetition by enlistee
   - Welcome from attendees

3.3. Oath of enlistment text:
```
"I, [state your name], do solemnly swear that I will support and defend 
the constitution and interests of the 5th Expeditionary Group against 
all enemies, foreign and domestic; that I will bear true faith and 
allegiance to the same; and that I will obey the orders of the Commander 
of the 5th Expeditionary Group and the orders of the officers appointed 
over me, according to regulations and the Uniform Code of Military Justice. 
So help me God."
```

3.4. Post-ceremony actions:
   - Update service record
   - Issue initial rank
   - Assign mentor/buddy
   - Schedule BCT
   - Provide unit welcome

### Step 4: Initial Documentation
4.1. Service record establishment:
   - Personal data entry
   - Initial rank recording
   - Unit assignment documentation
   - Specialization preferences
   - Training requirements

4.2. Access verification:
   - Discord permissions check
   - Forum access test
   - Website login confirmation
   - Document repository access
   - Communication systems check

4.3. Initial briefings scheduled:
   - Command structure overview
   - Unit history/traditions
   - Expectations brief
   - Training pathway
   - First assignment

## Onboarding Execution

### Step 5: Day 1 Orientation
5.1. Welcome session (1 hour):
   - Command welcome message
   - Mentor introduction
   - Fellow recruits meeting
   - Basic etiquette review
   - Question period

5.2. Administrative completion:
   - Form submission verification
   - System access confirmation
   - Initial issue items
   - Schedule confirmation
   - Point of contact review

5.3. Unit integration:
   - Squadron/section assignment
   - Chain of command introduction
   - Workspace familiarization
   - Initial duties assignment
   - Buddy system activation

### Step 6: Week 1 Activities
6.1. Daily check-ins:
   - Mentor meeting (15 min)
   - Progress assessment
   - Question resolution
   - Adjustment support
   - Encouragement provision

6.2. Essential training:
   - Discord usage
   - Communication protocols
   - Basic military customs
   - Unit procedures
   - Safety briefings

6.3. Social integration:
   - Unit social event
   - Informal meetings
   - Game sessions
   - Voice channel time
   - Relationship building

### Step 7: Progressive Integration
7.1. Week 2 objectives:
   - Advanced system training
   - Role-specific orientation
   - First operational exposure
   - Increased responsibilities
   - Performance feedback

7.2. Week 3-4 progression:
   - BCT preparation/start
   - Specialization exploration
   - Mentorship expansion
   - Unit contribution
   - Culture absorption

7.3. 30-day milestone:
   - Formal progress review
   - Feedback session
   - Adjustment recommendations
   - Future pathway discussion
   - Celebration recognition

## Onboarding Tracks

### Standard Enlisted Track
- Week 1: Orientation and basics
- Week 2: Systems and procedures
- Week 3-4: BCT preparation
- Week 5-8: BCT completion
- Week 9+: Unit integration

### Prior Service Track
- Day 1-3: Abbreviated orientation
- Week 1: Systems refresh
- Week 2: Unit integration
- Week 3+: Full duties
- Month 2: Leadership consideration

### Officer Candidate Track
- Week 1-2: Enhanced orientation
- Week 3-4: Leadership preparation
- Week 5-12: OCS program
- Week 13-16: Practicum
- Week 17+: Commission

### Specialist Track
- Week 1: Standard orientation
- Week 2-4: Technical assessment
- Week 5-8: Specialized training
- Week 9-12: Certification
- Week 13+: Full duties

## Support Systems

### Mentorship Program
**Mentor Selection:**
- Similar time zone
- Compatible personality
- Experienced member
- Good standing
- Volunteer basis

**Mentor Responsibilities:**
- Daily check-in first week
- Weekly thereafter
- Answer questions
- Provide guidance
- Report concerns

### Buddy System
**Buddy Assignment:**
- Recent graduate preferred
- Same unit/section
- Peer relationship
- Mutual support
- Shared experiences

**Buddy Activities:**
- Attend events together
- Practice procedures
- Share lessons learned
- Social connection
- Encouragement exchange

## Progress Monitoring

### Tracking Metrics
- Attendance record
- Training progression
- Integration indicators
- Engagement level
- Satisfaction feedback

### Early Warning Signs
- Missed appointments
- Poor communication
- Confusion persistent
- Isolation behaviors
- Expressed doubts

### Intervention Strategies
- Increased mentor contact
- Leadership engagement
- Schedule adjustment
- Additional support
- Alternate pathways

## Quality Assurance

### Feedback Collection
**From New Members:**
- Day 7 survey
- Day 30 interview
- Day 90 assessment
- Ongoing suggestions
- Exit interviews

**From Mentors:**
- Weekly reports
- Issue escalation
- Success stories
- Process improvements
- Resource needs

### Process Refinement
- Monthly review meeting
- Feedback analysis
- Bottleneck identification
- Success factor analysis
- Continuous improvement

## Common Challenges

### Challenge: Time Zone Difficulties
**Solutions:**
- Flexible scheduling
- Recorded sessions
- Multiple offerings
- Regional mentors
- Asynchronous options

### Challenge: Information Overload
**Solutions:**
- Paced delivery
- Reference materials
- Repeated exposure
- Check comprehension
- Prioritize critical

### Challenge: Social Integration
**Solutions:**
- Structured activities
- Buddy emphasis
- Small group events
- Common interests
- Patient approach

## Documentation Requirements

### Onboarding Checklist
- [ ] Oath administered
- [ ] Service record created
- [ ] Access granted
- [ ] Mentor assigned
- [ ] Orientation completed
- [ ] Week 1 activities done
- [ ] 30-day review conducted

### File Maintenance
- Digital copies retained
- Progress tracking updated
- Feedback documented
- Issues recorded
- Achievements noted

## Success Indicators

### Individual Level
- Attendance consistent
- Engagement active
- Questions decreasing
- Confidence growing
- Relationships forming

### Unit Level
- Retention rates high
- Integration smooth
- Mentors satisfied
- Culture strengthened
- Mission readiness

## References
- 2.1.1 Recruitment & Application Procedure
- 2.1.3 Service Record Management Procedure
- 4.1.1 Basic Combat Training (BCT) Curriculum
- 7.2.1 Discord Channel Usage Guidelines''',
                'difficulty_level': 'Intermediate',
                'is_required': True,
                'tags': ['enlistment', 'onboarding', 'orientation', 'integration', 'procedure']
            },
            {
                'document_number': '2.1.3',
                'title': 'Service Record Management Procedure',
                'category': 'Procedure',
                'summary': 'Procedures for creating, maintaining, and updating personnel service records throughout their career.',
                'content': '''# Service Record Management Procedure

## Purpose
This procedure establishes standards for creating, maintaining, and safeguarding service records that document each member's career progression, achievements, training, and administrative actions within the 5th Expeditionary Group.

## Scope
Applies to all personnel records from initial enlistment through separation or retirement, covering all branches and ranks within the organization.

## Record Creation

### Step 1: Initial Record Establishment
1.1. Create new service record upon enlistment:
   - Generate unique service number
   - Input personal information
   - Record enlistment date
   - Document initial rank
   - Note recruiting source

1.2. Required initial entries:
   - Full legal name
   - Discord username
   - Star Citizen handle
   - Email address
   - Time zone

1.3. Optional demographic data:
   - Country/region
   - Language capabilities
   - Previous military service
   - Relevant civilian experience
   - Special skills

### Step 2: Record Structure Setup
2.1. Digital file organization:
```
Service_Number/
├── Administrative/
│   ├── Enlistment_Documents/
│   ├── Promotion_Orders/
│   ├── Transfer_Records/
│   └── Correspondence/
├── Training/
│   ├── Basic_Training/
│   ├── Advanced_Courses/
│   ├── Certifications/
│   └── Qualifications/
├── Operations/
│   ├── Mission_Participation/
│   ├── After_Action_Reports/
│   └── Commendations/
├── Disciplinary/
│   ├── Counseling_Records/
│   ├── Article_15s/
│   └── Investigations/
└── Medical/
    ├── Physical_Status/
    └── Leave_Records/
```

2.2. Database fields configuration:
   - Personal information table
   - Service history table
   - Training records table
   - Awards/decorations table
   - Disciplinary actions table

2.3. Access permissions setup:
   - Member: Read own record
   - NCO: Read subordinates
   - Officer: Read/write unit
   - Personnel: Full access
   - Command: Override access

## Record Maintenance

### Step 3: Routine Updates
3.1. Mandatory update triggers:
   - Promotion/demotion
   - Unit transfer
   - Training completion
   - Award receipt
   - Disciplinary action

3.2. Update timeline requirements:
   - Promotions: Within 24 hours
   - Transfers: Within 48 hours
   - Training: Within 72 hours
   - Awards: Within 1 week
   - Other: Within 2 weeks

3.3. Update procedures:
   - Verify source documentation
   - Make database entry
   - Upload supporting docs
   - Update summary page
   - Notify member

### Step 4: Periodic Reviews
4.1. Quarterly record audit:
   - Verify data accuracy
   - Check completeness
   - Update contact info
   - Confirm active status
   - Note discrepancies

4.2. Annual comprehensive review:
   - Full record examination
   - Member verification
   - Historical correction
   - Archive old documents
   - Future planning notes

4.3. Pre-promotion review:
   - Eligibility verification
   - Completeness check
   - Achievement compilation
   - Issue resolution
   - Board preparation

### Step 5: Data Entry Standards
5.1. Documentation requirements:
   - Date/time stamp all entries
   - Include authorizing official
   - Reference source documents
   - Use standard formats
   - Maintain chronology

5.2. Standard entry format:
```
[DATE-TIME] - [ENTRY TYPE] - [DETAILS]
Entered by: [Name, Rank, Position]
Authority: [Document/Order Reference]
Notes: [Additional context if needed]
```

5.3. Correction procedures:
   - Strike through errors
   - Add correction below
   - Note reason for change
   - Maintain original
   - Document authorization

## Specific Record Types

### Promotion Records
**Required Documentation:**
- Promotion order
- Board recommendation
- Time in grade verification
- Training requirements met
- Command endorsement

**Entry Format:**
```
PROMOTION ENTRY
Date: [DATE]
From: [Previous Rank]
To: [New Rank]
Authority: [Order Number]
Effective: [Date]
Ceremony: [Date/Location]
```

### Training Records
**Required Documentation:**
- Course completion certificate
- Instructor verification
- Performance evaluation
- Practical scores
- Graduation date

**Categories:**
- Basic Military Training
- Advanced Individual Training
- Professional Development
- Leadership Courses
- Technical Certifications

### Operational Records
**Mission Participation:**
- Operation name/date
- Role/position
- Performance notes
- Lessons learned
- Recognition received

**Metrics Tracked:**
- Operations attended
- Leadership positions
- Critical roles
- Hours logged
- Success rate

### Awards and Decorations
**Documentation Required:**
- Citation text
- Approval authority
- Presentation date
- Witness signatures
- Photo (if available)

**Award Categories:**
- Valor decorations
- Achievement medals
- Service ribbons
- Unit citations
- Letters of commendation

### Disciplinary Records
**Documentation Standards:**
- Incident report
- Investigation summary
- Member statement
- Witness statements
- Disposition action

**Privacy Protections:**
- Limited access
- Sealed after time
- Expungement criteria
- Appeal documentation
- Rehabilitation notes

## Access and Security

### Step 6: Access Control
6.1. Access levels defined:
   - Level 1: Own record only
   - Level 2: Direct subordinates
   - Level 3: Unit records
   - Level 4: Branch records
   - Level 5: All records

6.2. Access logging:
   - User ID recorded
   - Access time/date
   - Records viewed
   - Changes made
   - Reason documented

6.3. Security measures:
   - Encrypted storage
   - Secure transmission
   - Regular backups
   - Audit trails
   - Intrusion detection

### Step 7: Privacy Protection
7.1. Personal information handling:
   - Minimize collection
   - Limit distribution
   - Secure storage
   - Controlled access
   - Deletion policy

7.2. Release authorization:
   - Member consent required
   - Official purposes only
   - Redaction procedures
   - Third-party restrictions
   - Legal compliance

7.3. Breach procedures:
   - Immediate containment
   - Affected notification
   - Investigation launch
   - Corrective measures
   - Prevention updates

## Quality Control

### Accuracy Verification
**Regular Checks:**
- Data entry audits
- Source verification
- Member confirmation
- Cross-reference checks
- Error correction

**Error Prevention:**
- Double-entry critical data
- Automated validation
- Required fields
- Format enforcement
- Regular training

### Completeness Assurance
**Missing Data Identification:**
- Automated gap analysis
- Periodic reports
- Member notifications
- Supervisor alerts
- Correction deadlines

**Documentation Standards:**
- Required vs optional
- Minimum requirements
- Quality thresholds
- Supporting evidence
- Verification needs

## Separation Procedures

### Step 8: Record Finalization
8.1. Separation checklist:
   - Final entries complete
   - Awards/decs updated
   - Discharge type recorded
   - Character of service
   - Reentry eligibility

8.2. Archive preparation:
   - Digital compilation
   - Verification complete
   - Member copy provided
   - Archive location noted
   - Retrieval process set

8.3. Post-separation access:
   - Member rights defined
   - Request procedures
   - Verification required
   - Privacy maintained
   - Support available

## Common Issues

### Issue: Incomplete Records
**Prevention:**
- Regular audits
- Automated reminders
- Clear responsibilities
- Training emphasis
- Accountability measures

### Issue: Conflicting Information
**Resolution:**
- Research sources
- Member input
- Witness statements
- Document precedence
- Official determination

### Issue: Lost Documentation
**Recovery:**
- Backup restoration
- Recreation procedures
- Affidavit acceptance
- Alternative sources
- Future prevention

## References
- 2.1.2 Enlistment & Onboarding Procedure
- 2.1.4 Performance Evaluation Guidelines
- 2.1.5 Promotion Board Procedure
- 2.3.2 Service Citation Documentation Guidelines''',
                'difficulty_level': 'Intermediate',
                'is_required': True,
                'tags': ['records', 'personnel', 'documentation', 'administration', 'procedure']
            },
            {
                'document_number': '2.1.4',
                'title': 'Performance Evaluation Guidelines',
                'category': 'Guidelines',
                'summary': 'Guidelines for conducting fair and comprehensive performance evaluations of all personnel.',
                'content': '''# Performance Evaluation Guidelines

## Purpose
These guidelines establish standards and procedures for evaluating personnel performance to ensure fair, consistent, and meaningful assessments that support career development and organizational effectiveness.

## Evaluation Philosophy

### Core Principles
- **Objectivity**: Based on observable behaviors and measurable outcomes
- **Consistency**: Applied uniformly across all personnel
- **Development**: Focused on growth and improvement
- **Recognition**: Acknowledging exceptional performance
- **Documentation**: Creating defensible records

### Evaluation Purposes
- Provide performance feedback
- Guide career development
- Support promotion decisions
- Identify training needs
- Recognize achievements
- Address deficiencies

## Evaluation Timeline

### Regular Evaluations
**Quarterly Reviews** (Informal)
- Progress check-ins
- Goal adjustment
- Immediate feedback
- Course correction
- Development planning

**Annual Evaluations** (Formal)
- Comprehensive assessment
- Written documentation
- Career counseling
- Goal establishment
- Official record

### Special Evaluations
**Triggered By:**
- Change of rater
- Significant achievement
- Performance issues
- Promotion consideration
- Transfer/separation

## Performance Categories

### Primary Rating Areas

**1. Leadership** (All ranks)
- Initiative demonstrated
- Decision-making quality
- Team influence
- Mentorship provided
- Example setting

**2. Technical Proficiency**
- MOS knowledge
- Skill application
- Problem solving
- Innovation shown
- Continuous learning

**3. Military Bearing**
- Attendance record
- Communication skills
- Customs compliance
- Appearance standards
- Discipline maintained

**4. Mission Accomplishment**
- Task completion
- Quality of work
- Timeliness
- Resource management
- Operational success

**5. Teamwork**
- Cooperation level
- Unit contribution
- Peer relationships
- Conflict resolution
- Morale influence

### Rating Scale
**5 - Outstanding**: Far exceeds standards; top 10%
**4 - Exceeds**: Above standards; top 25%
**3 - Meets**: Fully meets all standards
**2 - Below**: Some improvement needed
**1 - Unsatisfactory**: Significant improvement required

## Evaluation Process

### Preparation Phase
**Rater Responsibilities:**
1. Review period performance
2. Gather supporting documentation
3. Consult performance notes
4. Consider peer input
5. Prepare specific examples

**Ratee Responsibilities:**
1. Complete self-assessment
2. Document achievements
3. Identify challenges faced
4. Propose future goals
5. Gather supporting materials

### Assessment Guidelines

**Objectivity Measures:**
- Use specific examples
- Avoid personal bias
- Compare to standards
- Consider circumstances
- Document reasoning

**Common Rating Errors to Avoid:**
- **Halo Effect**: One trait influences all
- **Recency Bias**: Only recent events considered
- **Central Tendency**: Everyone rated average
- **Strictness/Leniency**: Consistently too harsh/easy
- **Similar-to-Me**: Favoring similar personalities

### Documentation Standards

**Performance Examples Format:**
```
CATEGORY: [Leadership/Technical/etc.]
SITUATION: [Context and challenge]
ACTION: [What member did]
RESULT: [Outcome achieved]
IMPACT: [Significance to unit/mission]
```

**Bullet Point Guidelines:**
- Start with action verb
- Include quantifiable results
- Specify impact level
- Keep concise
- Use active voice

## Specific Rank Considerations

### Junior Enlisted (E1-E3)
**Focus Areas:**
- Learning progression
- Attitude/motivation
- Basic skill development
- Following instructions
- Team integration

**Expectations:**
- Punctual attendance
- Eager participation
- Steady improvement
- Positive attitude
- Team player

### NCO (E4-E6)
**Focus Areas:**
- Leadership development
- Technical expertise
- Training others
- Initiative taking
- Problem solving

**Expectations:**
- Lead by example
- Mentor juniors
- Technical competence
- Unit contribution
- Professional growth

### Senior NCO (E7-E9)
**Focus Areas:**
- Strategic thinking
- Unit leadership
- Policy implementation
- Mentor development
- Institutional knowledge

**Expectations:**
- Shape unit culture
- Develop leaders
- Advise officers
- Drive standards
- Long-term vision

### Company Grade Officers (O1-O3)
**Focus Areas:**
- Decision-making
- Command presence
- Planning ability
- Communication skills
- Leadership growth

**Expectations:**
- Lead from front
- Sound judgment
- Clear communication
- Mission focus
- Learn continuously

### Field Grade Officers (O4-O6)
**Focus Areas:**
- Strategic planning
- Resource management
- Multi-unit coordination
- Policy development
- Executive skills

**Expectations:**
- Big picture thinking
- Complex problem solving
- Organizational influence
- Mentorship culture
- Innovation leadership

## Counseling Integration

### Performance Counseling
**Initial Counseling:**
- Set expectations
- Establish goals
- Define success
- Identify resources
- Schedule reviews

**Progress Counseling:**
- Review performance
- Adjust goals
- Address issues
- Recognize success
- Plan development

**Final Counseling:**
- Discuss evaluation
- Future planning
- Career guidance
- Development needs
- Recognition due

### Counseling Documentation
```
COUNSELING RECORD
Date: [DATE]
Counselor: [Name, Rank]
Member: [Name, Rank]
Type: [Initial/Progress/Final]

Topics Discussed:
1. [Performance area]
2. [Specific examples]
3. [Improvement needed]
4. [Resources provided]
5. [Next steps]

Member Response: [Summary]
Follow-up Date: [DATE]
Signatures: [Both parties]
```

## Special Situations

### New Members
- Adjust expectations
- Focus on learning
- Document progress
- Provide support
- Compare to peers

### Returning Members
- Consider time away
- Assess reintegration
- Note previous performance
- Set realistic goals
- Provide refreshers

### Cross-Training Personnel
- Evaluate both MOSs
- Consider learning curve
- Recognize flexibility
- Document versatility
- Plan development

### Acting Positions
- Rate at acting level
- Note regular duties
- Recognize stretch
- Document growth
- Consider potential

## Appeals Process

### Grounds for Appeal
- Procedural errors
- Factual inaccuracies
- Bias/discrimination
- Missing information
- Unfair standards

### Appeal Procedure
1. Informal resolution attempt
2. Written appeal submission
3. Next level review
4. Supporting documentation
5. Decision notification

### Timeline
- Informal: 7 days
- Formal submission: 14 days
- Review completion: 30 days
- Final decision: 45 days
- Implementation: Immediate

## Best Practices

### For Raters
**Do:**
- Keep performance notes
- Provide regular feedback
- Use specific examples
- Be fair and consistent
- Focus on development

**Don't:**
- Wait until evaluation
- Use vague language
- Show favoritism
- Ignore problems
- Rate personality

### For Ratees
**Do:**
- Track accomplishments
- Seek feedback
- Accept criticism
- Show improvement
- Document activities

**Don't:**
- Argue ratings
- Make excuses
- Compare others
- Expect perfection
- Ignore feedback

## Quality Assurance

### Review Chain
1. Immediate supervisor rates
2. Next level endorses
3. Personnel reviews
4. Command approves
5. Member acknowledges

### Consistency Checks
- Rating distribution analysis
- Cross-unit comparison
- Historical trending
- Outlier investigation
- Calibration sessions

### Training Requirements
**For Raters:**
- Evaluation system training
- Bias awareness
- Counseling skills
- Documentation standards
- Legal requirements

**For All:**
- System understanding
- Self-assessment skills
- Goal setting
- Career planning
- Feedback reception

## References
- 2.1.3 Service Record Management Procedure
- 2.1.5 Promotion Board Procedure
- 2.4.1 Progressive Disciplinary Action Guidelines
- 4.4.1 Monthly Training Requirements''',
                'difficulty_level': 'Advanced',
                'is_required': True,
                'tags': ['evaluation', 'performance', 'counseling', 'career', 'guidelines']
            },
            {
                'document_number': '2.1.5',
                'title': 'Promotion Board Procedure',
                'category': 'Procedure',
                'summary': 'Comprehensive procedures for conducting promotion boards and selecting personnel for advancement.',
                'content': '''# Promotion Board Procedure

## Purpose
This procedure establishes the standardized process for conducting promotion boards to ensure fair, transparent, and merit-based advancement of personnel through the ranks of the 5th Expeditionary Group.

## Scope
Applies to all promotion considerations from E-2 through O-5, with specific procedures varying by rank category. Flag officer promotions follow separate strategic procedures.

## Promotion Philosophy

### Merit-Based System
- Performance drives promotion
- Potential considered equally
- Time-in-grade minimum only
- Leadership qualities essential
- Unit needs balanced

### Promotion Criteria
**Primary Factors:**
- Sustained superior performance
- Leadership demonstration
- Professional development
- Unit contribution
- Future potential

**Secondary Factors:**
- Time in service
- Special qualifications
- Diversity of experience
- Education/training
- Awards/recognition

## Board Composition

### Enlisted Boards (E2-E6)
**Board Members:**
- Board President (E-7 or above)
- Two voting members (E-6 or above)
- Recorder (non-voting)
- Personnel representative (advisory)

**Rank Requirements:**
- All members senior to candidates
- At least one from different unit
- No direct supervisors
- Diverse experience preferred

### NCO Boards (E7-E9)
**Board Members:**
- Board President (E-9 or Officer)
- Three voting members (E-8 or above)
- Recorder (non-voting)
- Command representative
- Personnel advisor

**Selection Criteria:**
- Proven leadership record
- Board experience
- Cross-branch knowledge
- Objectivity demonstrated

### Officer Boards (O1-O5)
**Board Members:**
- Board President (O-5 or above)
- Four voting members (senior rank)
- Recorder (non-voting)
- Legal advisor (as needed)
- Personnel representative

**Diversity Requirements:**
- Multiple branches represented
- Operational/staff mix
- Combat/support balance
- Gender consideration

## Pre-Board Phase

### Step 1: Eligibility Determination
1.1. Time-in-grade requirements:
   - E-2: 6 months as E-1
   - E-3: 6 months as E-2
   - E-4: 12 months as E-3
   - E-5: 18 months as E-4
   - E-6: 24 months as E-5
   - E-7: 36 months as E-6
   - E-8: 36 months as E-7
   - E-9: 48 months as E-8

1.2. Additional requirements:
   - Professional military education
   - Required training complete
   - No pending adverse actions
   - Commander recommendation
   - Physical standards met

1.3. Eligibility list compilation:
   - Database query run
   - Manual verification
   - Commander confirmation
   - Candidate notification
   - Opt-out opportunity

### Step 2: Record Preparation
2.1. Personnel file review:
   - Completeness check
   - Recent updates verified
   - Evaluations current
   - Awards documented
   - Training recorded

2.2. Board file assembly:
   - Performance evaluations (all)
   - Training certificates
   - Awards/decorations
   - Disciplinary records (if any)
   - Commander endorsement

2.3. Candidate submission:
   - Letter to board (optional)
   - Recent accomplishments
   - Future goals statement
   - Additional documentation
   - Photo update

### Step 3: Board Scheduling
3.1. Timeline establishment:
   - 60 days advance notice
   - Record submission deadline
   - Board convene date
   - Results announcement
   - Promotion ceremony

3.2. Board member notification:
   - Selection letters sent
   - Availability confirmed
   - Materials provided
   - Training scheduled
   - Oath administered

3.3. Logistics coordination:
   - Secure meeting space
   - Technology setup
   - Materials preparation
   - Schedule finalized
   - Backup plans ready

## Board Execution

### Step 4: Board Convening
4.1. Opening procedures:
   - Member attendance
   - Oath administration
   - Charge reading
   - Ground rules established
   - Questions addressed

4.2. Charge to the board:
```
"You are charged to select the best qualified personnel for 
promotion to [RANK]. Your selections should be based solely 
on performance, potential, and the needs of the service. 
Personal knowledge of candidates will not unfairly advantage 
or disadvantage any individual. Your deliberations will remain 
confidential."
```

4.3. Voting procedures:
   - Secret ballot system
   - Majority rule
   - Discussion protocols
   - Scoring methodology
   - Tie-breaking process

### Step 5: Record Review
5.1. Systematic approach:
   - Alphabetical order
   - Equal time allocation
   - Standardized review
   - Note-taking allowed
   - Questions documented

5.2. Evaluation factors:
   - Performance trajectory
   - Leadership indicators
   - Breadth of experience
   - Education/training
   - Special achievements

5.3. Red flags identification:
   - Disciplinary issues
   - Performance decline
   - Attendance problems
   - Integrity concerns
   - Pattern recognition

### Step 6: Deliberation Process
6.1. Initial scoring:
   - Individual assessment
   - Numerical scores
   - Ranking creation
   - Statistical analysis
   - Outlier identification

6.2. Discussion phase:
   - Score comparison
   - Candidate strengths
   - Concerns raised
   - Consensus building
   - Final adjustments

6.3. Selection determination:
   - Promotion quota applied
   - Natural breakpoints
   - Quality threshold
   - Alternate list
   - Documentation complete

## Post-Board Phase

### Step 7: Results Processing
7.1. Administrative actions:
   - Results compilation
   - Quality check
   - Command notification
   - Personnel update
   - System entry

7.2. Notification procedures:
   - Command channels first
   - Selectee notification
   - Non-selection counseling
   - Public announcement
   - Ceremony planning

7.3. Effective date coordination:
   - Standard 1st of month
   - Ceremony alignment
   - Pay adjustment
   - Authority update
   - Record modification

### Step 8: Promotion Execution
8.1. Ceremony planning:
   - Date/time selection
   - Venue coordination
   - Guest invitations
   - Program creation
   - Reception planning

8.2. Ceremony elements:
   - Opening remarks
   - Orders reading
   - Oath administration
   - Insignia presentation
   - Closing comments

8.3. Post-ceremony actions:
   - Record updates
   - Access modifications
   - Duty adjustment
   - Mentorship assignment
   - Development planning

## Special Circumstances

### Battlefield/Merit Promotions
**Criteria:**
- Exceptional performance
- Combat leadership
- Life-saving actions
- Mission critical success
- Commander initiated

**Process:**
- Immediate recommendation
- Expedited review
- Command approval
- Retroactive board
- Permanent record

### Below-the-Zone
**Eligibility:**
- Top 10% performance
- Exceptional potential
- Command endorsement
- No time waivers
- Competition basis

**Selection Rate:**
- Maximum 10% of eligible
- Quality over quantity
- High performer focus
- Future leader identification
- Career acceleration

### Administrative Promotions
**Automatic Promotions:**
- E-1 to E-2: Time only
- Professional milestone
- Correction action
- Prior agreement
- Special program

## Appeals Process

### Grounds for Appeal
- Procedural error
- Missing information
- Bias evidence
- Calculation error
- New information

### Appeal Procedures
1. Written submission required
2. Supporting documentation
3. Command endorsement
4. Personnel review
5. Board president decision

### Timeline Limits
- Appeal submission: 30 days
- Review completion: 60 days
- Decision final: 90 days
- No secondary appeals
- Recompete next cycle

## Quality Assurance

### Board Training
**Required Topics:**
- Evaluation standards
- Bias prevention
- Legal requirements
- Scoring methodology
- Confidentiality rules

### Process Monitoring
- Random audits
- Statistical analysis
- Feedback collection
- Trend identification
- Continuous improvement

### Metrics Tracked
- Selection rates
- Demographic distribution
- Performance correlation
- Time-to-promotion
- Retention impact

## Documentation Requirements

### Board Records
**Maintained Documents:**
- Board charge
- Member roster
- Score sheets
- Deliberation notes
- Results memorandum

**Retention Period:**
- Active records: 2 years
- Historical data: 5 years
- Statistical summaries: Permanent
- Individual scores: Destroyed after approval
- Appeals: 3 years

## Best Practices

### For Board Members
- Review all records thoroughly
- Maintain objectivity
- Document reasoning
- Respect confidentiality
- Focus on potential

### For Candidates
- Maintain records
- Seek mentorship
- Pursue development
- Document achievements
- Accept outcomes professionally

### For Commands
- Ensure fair opportunities
- Provide honest evaluations
- Support development
- Recognize achievement
- Counsel non-selects

## References
- 2.1.3 Service Record Management Procedure
- 2.1.4 Performance Evaluation Guidelines
- 2.1.6 Transfer Request Procedure
- 2.3.1 Award Nomination & Approval Procedure''',
                'difficulty_level': 'Advanced',
                'is_required': True,
                'tags': ['promotion', 'board', 'advancement', 'career', 'procedure']
            },
            {
                'document_number': '2.1.6',
                'title': 'Transfer Request Procedure',
                'category': 'Procedure',
                'summary': 'Procedures for requesting and processing personnel transfers between units or positions.',
                'content': '''# Transfer Request Procedure

## Purpose
This procedure establishes the process for personnel to request transfers between units, positions, or specialties within the 5th Expeditionary Group, ensuring operational continuity while supporting career development and personal needs.

## Scope
Applies to all voluntary transfer requests within the organization. Does not cover directed transfers, emergency reassignments, or separation procedures.

## Transfer Categories

### Unit Transfers
**Definition**: Movement between squadrons, ships, or major units
**Common Reasons**:
- Career development
- Specialty alignment
- Leadership opportunities
- Personal preference
- Operational needs

### Position Transfers
**Definition**: Change of duty position within same unit
**Common Reasons**:
- Skill utilization
- Development needs
- Performance optimization
- Medical requirements
- Advancement preparation

### Branch Transfers
**Definition**: Movement between Navy, Marines, or support branches
**Requirements**:
- Branch-specific training
- Command approval
- Position availability
- Qualification meeting
- Extended process

### Specialty Changes
**Definition**: Change in Military Occupational Specialty (MOS)
**Considerations**:
- Retraining required
- Time commitment
- Unit impact
- Career implications
- Aptitude assessment

## Eligibility Requirements

### Time-in-Position
**Minimum Requirements**:
- Initial assignment: 6 months
- Subsequent assignments: 12 months
- Leadership positions: 18 months
- Specialty positions: 24 months
- Waiverable for cause

### Performance Standards
**Prerequisites**:
- Current evaluation "Meets" or above
- No pending adverse actions
- Training requirements current
- Attendance standards met
- Command endorsement possible

### Special Restrictions
**Transfer Limitations**:
- Not during operations
- Critical manning positions
- Recent promotion (90 days)
- Pending board appearance
- Active investigation

## Request Process

### Step 1: Initial Consideration
1.1. Self-assessment:
   - Current satisfaction evaluation
   - Career goal alignment
   - Skill match analysis
   - Personal factors review
   - Timing appropriateness

1.2. Research phase:
   - Available positions review
   - Unit culture investigation
   - Requirements verification
   - Timeline understanding
   - Impact assessment

1.3. Informal coordination:
   - Supervisor discussion
   - Mentor consultation
   - Receiving unit contact
   - Peer feedback
   - Family consideration

### Step 2: Formal Request Submission
2.1. Request package preparation:
   - Transfer request form
   - Personal statement
   - Current evaluations
   - Training records
   - Endorsement letters

2.2. Personal statement elements:
```
TRANSFER REQUEST STATEMENT

1. Current Position: [Unit, position, time in position]
2. Requested Transfer: [Specific unit/position desired]
3. Reasons for Request: [Professional and/or personal]
4. Qualifications: [Relevant skills and experience]
5. Benefit to Service: [How transfer helps organization]
6. Availability: [Earliest/latest transfer dates]
7. Alternatives: [Other acceptable options]
```

2.3. Routing procedures:
   - Immediate supervisor
   - Department head
   - Current commander
   - Personnel office
   - Receiving commander

### Step 3: Command Review
3.1. Losing unit assessment:
   - Mission impact analysis
   - Replacement availability
   - Transfer timing
   - Performance verification
   - Recommendation formulation

3.2. Evaluation criteria:
   - Unit manning levels
   - Critical skills retention
   - Development benefit
   - Member welfare
   - Service needs balance

3.3. Commander options:
   - Approve immediately
   - Approve with conditions
   - Defer to specific date
   - Recommend alternative
   - Disapprove with counseling

### Step 4: Personnel Coordination
4.1. Personnel office actions:
   - Eligibility verification
   - Position matching
   - Timeline coordination
   - System updates
   - Communication facilitation

4.2. Receiving unit coordination:
   - Position confirmation
   - Qualification review
   - Integration planning
   - Sponsor assignment
   - Welcome preparation

4.3. Administrative processing:
   - Orders preparation
   - Record updates
   - Access modifications
   - Travel coordination
   - Checklist creation

## Decision Process

### Step 5: Transfer Board (if required)
5.1. Board convening triggers:
   - Multiple applicants
   - Critical position
   - Cross-branch transfer
   - Disagreement exists
   - Special circumstances

5.2. Board composition:
   - Personnel officer (chair)
   - Losing unit representative
   - Gaining unit representative
   - Neutral senior member
   - Recorder (non-voting)

5.3. Selection criteria:
   - Best qualified
   - Unit needs priority
   - Development potential
   - Service benefit
   - Fairness maintained

### Step 6: Notification Procedures
6.1. Approval notification:
   - Written orders issued
   - Report date specified
   - Requirements listed
   - Sponsor identified
   - Checklist provided

6.2. Conditional approval:
   - Conditions specified
   - Timeline provided
   - Requirements clear
   - Appeal rights noted
   - Support offered

6.3. Disapproval notification:
   - Reasons provided
   - Counseling offered
   - Alternatives discussed
   - Reapplication timeline
   - Appeal process explained

## Execution Phase

### Step 7: Transfer Preparation
7.1. Out-processing checklist:
   - [ ] Knowledge transfer
   - [ ] Project completion
   - [ ] Equipment return
   - [ ] Access removal
   - [ ] Exit interview

7.2. Transition planning:
   - Overlap period scheduled
   - Replacement training
   - Documentation updated
   - Handover meeting
   - Contact exchange

7.3. Member preparation:
   - New unit research
   - Skill refreshment
   - Administrative completion
   - Personal readiness
   - Family preparation

### Step 8: Transfer Execution
8.1. Departure procedures:
   - Final counseling
   - Evaluation closeout
   - Recognition ceremony
   - Farewell events
   - Contact maintenance

8.2. Reporting procedures:
   - Check-in requirements
   - Sponsor meeting
   - Command introduction
   - Integration schedule
   - Expectation setting

8.3. Integration timeline:
   - Day 1: Administrative
   - Week 1: Orientation
   - Week 2-4: Training
   - Month 2: Full duties
   - Month 3: Evaluation

## Special Circumstances

### Hardship Transfers
**Qualifying Circumstances**:
- Family medical emergency
- Extreme financial hardship
- Compassionate reasons
- Safety concerns
- Exceptional situations

**Expedited Process**:
- Emergency request
- Documentation minimal
- Command priority
- Quick decision
- Immediate execution

### Performance-Based Transfers
**Indicators**:
- Poor unit fit
- Personality conflicts
- Skill mismatch
- Development needs
- Fresh start required

**Special Handling**:
- Counseling required
- Plan development
- Monitoring increased
- Support provided
- Success focus

### Voluntary Demotion Transfers
**Considerations**:
- Personal request
- Stress reduction
- Skill alignment
- Life balance
- Career refocus

**Requirements**:
- Written request
- Counseling mandatory
- Impact briefing
- Approval levels
- Permanent record

## Post-Transfer

### Step 9: Follow-Up Actions
9.1. 30-day check-in:
   - Integration assessment
   - Issue identification
   - Support verification
   - Expectation alignment
   - Adjustment needs

9.2. 90-day evaluation:
   - Performance review
   - Satisfaction assessment
   - Development planning
   - Feedback collection
   - Success measurement

9.3. Lessons learned:
   - Process effectiveness
   - Timeline adequacy
   - Communication quality
   - Support sufficiency
   - Improvement recommendations

## Common Issues

### Issue: Manning Imbalances
**Mitigation Strategies**:
- Cross-training programs
- Incentive offerings
- Rotation scheduling
- Pipeline management
- Directed assignments

### Issue: Skill Retention
**Solutions**:
- Retention bonuses
- Development opportunities
- Recognition programs
- Work-life balance
- Career counseling

### Issue: Transfer Abuse
**Prevention Measures**:
- Time requirements
- Pattern monitoring
- Counseling intervention
- Command discretion
- Policy enforcement

## Appeal Process

### Grounds for Appeal
- Policy violation
- Information missing
- Discrimination evidence
- Changed circumstances
- Process errors

### Appeal Submission
- Written format required
- New information included
- Command endorsement
- Personnel review
- Decision timeline

## Metrics and Monitoring

### Transfer Statistics
**Tracked Metrics**:
- Request volume
- Approval rates
- Processing time
- Satisfaction scores
- Retention impact

### Trend Analysis
- Hot spots identification
- Cycle patterns
- Reason analysis
- Success correlation
- Policy effectiveness

## References
- 2.1.3 Service Record Management Procedure
- 2.1.4 Performance Evaluation Guidelines
- 2.1.7 Separation/Discharge Procedure
- 4.2.7 Logistics Specialist Training Guidelines''',
                'difficulty_level': 'Intermediate',
                'is_required': True,
                'tags': ['transfer', 'personnel', 'career', 'assignment', 'procedure']
            },
            {
                'document_number': '2.1.7',
                'title': 'Separation/Discharge Procedure',
                'category': 'Procedure',
                'summary': 'Procedures for processing voluntary and involuntary separations from service.',
                'content': '''# Separation/Discharge Procedure

## Purpose
This procedure establishes the process for separating personnel from the 5th Expeditionary Group, ensuring proper documentation, benefits preservation, and organizational continuity while treating departing members with dignity and respect.

## Scope
Covers all types of separation including voluntary resignation, retirement, medical discharge, administrative separation, and involuntary discharge. Does not cover temporary absences or leaves.

## Separation Categories

### Voluntary Separation
**Honorable Discharge**
- Completed service obligation
- Personal decision
- Career change
- Family reasons
- Positive record

**General Discharge**
- Satisfactory service
- Some misconduct
- Performance issues
- Pattern violations
- Command discretion

### Involuntary Separation
**Other Than Honorable**
- Serious misconduct
- Pattern violations
- Security violations
- Integrity issues
- Board action

**Dishonorable Discharge**
- Court martial only
- Serious offenses
- Criminal conduct
- Treason/desertion
- Permanent record

### Medical Separation
**Medical Discharge**
- Unable to perform
- Permanent condition
- Board determination
- Benefits eligible
- Honorable status

### Administrative Separation
**Convenience of Service**
- Manning adjustments
- Skill redundancy
- Reorganization
- No fault implied
- Benefits retained

## Voluntary Separation Process

### Step 1: Intent Notification
1.1. Submission requirements:
   - Written notice
   - 30-day minimum
   - Reason statement
   - Requested date
   - Contact information

1.2. Notice format:
```
SEPARATION REQUEST

Date: [Current Date]
To: Commanding Officer via Chain of Command
From: [Rank, Name, Service Number]

1. I hereby request voluntary separation from the 5th 
   Expeditionary Group effective [date].

2. Reason for separation: [Brief explanation]

3. I understand my obligations regarding:
   - Knowledge transfer
   - Equipment return
   - Security requirements
   - Exit processing

4. Post-separation contact: [Email/Discord]

Signature: [Digital signature]
```

1.3. Routing process:
   - Immediate supervisor
   - Department head
   - Executive officer
   - Commanding officer
   - Personnel office

### Step 2: Command Review
2.1. Retention consideration:
   - Member value assessed
   - Retention offered
   - Issues addressed
   - Alternatives explored
   - Decision documented

2.2. Approval process:
   - Request evaluation
   - Impact assessment
   - Timeline verification
   - Replacement planning
   - Approval/modification

2.3. Special considerations:
   - Critical positions
   - Ongoing operations
   - Special knowledge
   - Security clearances
   - Project completion

### Step 3: Separation Planning
3.1. Timeline establishment:
   - Final duty day
   - Knowledge transfer period
   - Out-processing schedule
   - Terminal activities
   - Ceremony planning

3.2. Replacement coordination:
   - Position advertisement
   - Successor identification
   - Training overlap
   - Handover schedule
   - Continuity assured

3.3. Administrative preparation:
   - Record review
   - Benefits calculation
   - Access lists
   - Equipment inventory
   - Final evaluations

## Out-Processing Procedures

### Step 4: Knowledge Transfer
4.1. Documentation requirements:
   - Position handbook update
   - Project status reports
   - Contact lists
   - Password transfers
   - Lessons learned

4.2. Training responsibilities:
   - Successor mentoring
   - Team briefings
   - Process documentation
   - Historical context
   - Relationship transition

4.3. Project disposition:
   - Completion push
   - Handoff preparation
   - Status documentation
   - Risk identification
   - Mitigation planning

### Step 5: Administrative Clearance
5.1. Department checkouts:
   - Operations clearance
   - Training records
   - Medical clearance
   - Finance settlement
   - Security debriefing

5.2. Equipment return:
   - Issued gear inventory
   - Condition verification
   - Loss documentation
   - Turn-in receipts
   - Access cards/keys

5.3. Digital cleanup:
   - Account closures
   - Access revocation
   - File transfers
   - Email forwarding
   - Profile archival

### Step 6: Final Actions
6.1. Personnel actions:
   - Final evaluation
   - Service record closure
   - Discharge certificate
   - Character determination
   - Benefits briefing

6.2. Recognition activities:
   - Award processing
   - Farewell ceremony
   - Unit gathering
   - Plaque/certificate
   - Photo opportunities

6.3. Exit interview:
   - Experience feedback
   - Process improvement
   - Issue identification
   - Recommendation capture
   - Contact verification

## Involuntary Separation

### Step 7: Due Process (Involuntary)
7.1. Notification requirements:
   - Written charges
   - Evidence provided
   - Rights explained
   - Representation offered
   - Timeline specified

7.2. Board procedures:
   - Member selection
   - Evidence presentation
   - Defense opportunity
   - Witness testimony
   - Deliberation process

7.3. Appeal rights:
   - Process explanation
   - Timeline limits
   - Submission requirements
   - Review levels
   - Final authority

### Step 8: Expedited Processing
8.1. Security requirements:
   - Immediate access suspension
   - Classified debrief
   - Equipment recovery
   - Investigation support
   - Monitor assignment

8.2. Administrative priorities:
   - Record protection
   - Evidence preservation
   - Witness statements
   - Timeline documentation
   - Legal coordination

8.3. Communication management:
   - Unit notification
   - Rumor control
   - Privacy protection
   - Official statements
   - Morale monitoring

## Post-Separation

### Step 9: Alumni Status
9.1. Honorable discharge benefits:
   - Alumni discord access
   - Event invitations
   - Reference availability
   - Network maintenance
   - Recognition continued

9.2. Restricted access:
   - Public channels only
   - No operational data
   - Limited privileges
   - Case basis review
   - Reinstatement possible

9.3. Prohibited access:
   - Complete ban
   - No contact allowed
   - Security flagged
   - Allies notified
   - Permanent record

### Step 10: Record Management
10.1. File disposition:
   - Active to inactive
   - Archive location
   - Access restrictions
   - Retention period
   - Destruction schedule

10.2. Reference policy:
   - Verification only
   - Dates of service
   - Character confirmed
   - Details restricted
   - Written preferred

10.3. Reentry eligibility:
   - Honorable: Immediate
   - General: 6 months
   - OTH: Case basis
   - Dishonorable: Never
   - Medical: When cleared

## Special Situations

### Retirement Processing
**Additional Requirements**:
- Service computation
- Retirement ceremony
- Special recognition
- Legacy documentation
- Mentor transition

### Medical Discharge
**Medical Board Process**:
- Condition documentation
- Duty limitation review
- Board convening
- Member representation
- Benefit determination

### Death in Service
**Posthumous Actions**:
- Next of kin notification
- Memorial service
- Record finalization
- Benefits processing
- Honor preservation

## Quality Assurance

### Process Monitoring
**Metrics Tracked**:
- Separation types
- Processing time
- Exit feedback
- Return rates
- Issue patterns

### Continuous Improvement
**Review Elements**:
- Exit interview analysis
- Process bottlenecks
- Policy effectiveness
- Member satisfaction
- Best practices

### Lessons Learned
**Documentation**:
- Common issues
- Success stories
- Process improvements
- Policy recommendations
- Training needs

## Legal Considerations

### Privacy Protection
- Information limits
- Need-to-know basis
- Record security
- Reference restrictions
- Legal compliance

### Documentation Standards
- Factual only
- Objective language
- Proper authorization
- Complete records
- Audit ready

### Appeal Procedures
- Written submission
- Evidence based
- Timeline adherence
- Proper routing
- Final decision

## Support Resources

### Member Support
- Transition assistance
- Counseling available
- Career guidance
- Reference letters
- Network access

### Command Support
- Replacement pipeline
- Knowledge retention
- Morale monitoring
- Process guidance
- Legal assistance

## References
- 2.1.3 Service Record Management Procedure
- 2.1.4 Performance Evaluation Guidelines
- 2.1.6 Transfer Request Procedure
- 2.4.1 Progressive Disciplinary Action Guidelines''',
                'difficulty_level': 'Advanced',
                'is_required': True,
                'tags': ['separation', 'discharge', 'retirement', 'personnel', 'procedure']
            }
        ]

        for data in standards_data:
            standard, created = Standard.objects.get_or_create(
                document_number=data['document_number'],
                defaults={
                    'title': data['title'],
                    'standard_sub_group': subgroup,
                    'content': data['content'],
                    'summary': data['summary'],
                    'version': '1.0',
                    'status': 'Active',
                    'author': user,
                    'approved_by': user,
                    'approval_date': timezone.now(),
                    'effective_date': timezone.now(),
                    'difficulty_level': data['difficulty_level'],
                    'tags': data['tags'],
                    'is_required': data.get('is_required', False)
                }
            )
            if created:
                self.stdout.write(f'  Created: {data["document_number"]} - {data["title"]}')

    def _create_attendance_leave_standards(self, group, user):
        """Create Attendance & Leave subgroup and its standards"""
        subgroup, _ = StandardSubGroup.objects.get_or_create(
            name='Attendance & Leave',
            standard_group=group,
            defaults={
                'description': 'Standards for attendance requirements and leave management procedures.',
                'order_index': 2,
                'is_active': True,
                'created_by': user
            }
        )

        standards_data = [
            {
                'document_number': '2.2.1',
                'title': 'Minimum Attendance Requirements',
                'category': 'Information',
                'summary': 'Information on minimum attendance requirements by rank and position within the 5EG.',
                'content': '''# Minimum Attendance Requirements

## Purpose
This document provides clear information on minimum attendance requirements for all ranks and positions within the 5th Expeditionary Group, ensuring operational readiness while accommodating real-life obligations.

## Attendance Philosophy

### Core Principles
- **Readiness**: Maintaining operational capability through consistent participation
- **Flexibility**: Recognizing real-world commitments and obligations
- **Accountability**: Clear expectations and consistent enforcement
- **Progression**: Increased responsibility with higher rank

### Attendance Categories
**Official Events**:
- Operations (scheduled missions)
- Official training sessions
- Mandatory formations
- Command ceremonies
- Board appearances

**Credited Activities**:
- Unofficial training
- Recruitment activities
- Administrative duties
- Mentorship sessions
- Special projects

## Rank-Based Requirements

### Junior Enlisted (E1-E3)
**Minimum Monthly Requirement**: 1 Official Event

**Breakdown**:
- 1× Operation OR
- 1× Official Training OR
- 1× Mandatory Formation

**Additional Expectations**:
- Participate in unit activities
- Respond to communications
- Complete assigned training
- Support recruitment when able

**Grace Period**: 
- First month: No requirements (onboarding)
- Months 2-3: Encouraged participation
- Month 4+: Full requirements

### Non-Commissioned Officers (E4-E6)
**Minimum Monthly Requirement**: 1 Official Event + 1 Leadership Activity

**Official Event** (1 required):
- 1× Operation OR
- 1× Official Training OR
- 1× Staff duty

**Leadership Activity** (1 required):
- Staff MOS training OR
- Mentor junior members OR
- Lead unofficial training OR
- Recruitment support

**Additional Expectations**:
- Set example for junior enlisted
- Maintain technical proficiency
- Support unit administration
- Develop subordinates

### Senior NCOs (E7-E9)
**Minimum Monthly Requirement**: 2 Official Events + 2 Leadership Activities

**Official Events** (2 required):
- Operations (priority)
- Official training delivery
- Command meetings
- Board participation

**Leadership Activities** (2 required):
- Staff 2× MOS training sessions
- Conduct performance counseling
- Lead recruitment efforts
- Unit development projects

**Additional Expectations**:
- Shape unit culture
- Advise command
- Develop NCO corps
- Maintain standards

### Warrant Officers
**Minimum Monthly Requirement**: 1 Official Event + 1 Technical Activity

**Official Event** (1 required):
- Technical operations
- Specialized training
- Board appearances
- Command advisement

**Technical Activity** (1 required):
- Staff MOS training
- Technical development
- System improvements
- Knowledge documentation

**Focus Areas**:
- Technical expertise
- Training development
- Process improvement
- Mentorship

### Company Grade Officers (O1-O3)
**Minimum Monthly Requirement**: 1 Official Event + 1 Command Activity

**Official Event** (1 required):
- Lead operations
- Deliver training
- Attend meetings
- Ceremony participation

**Command Activity** (1 required):
- Staff MOS training
- Unit administration
- Personnel development
- Planning sessions

**Leadership Focus**:
- Direct leadership
- Unit readiness
- Personnel welfare
- Mission planning

### Field Grade Officers (O4-O6)
**Minimum Monthly Requirement**: 2 Official Events + 2 Strategic Activities

**Official Events** (2 required):
- Command operations
- Strategic meetings
- Board presidency
- Ceremonial duties

**Strategic Activities** (2 required):
- Staff MOS training
- Policy development
- Strategic planning
- Multi-unit coordination

**Executive Focus**:
- Strategic thinking
- Resource management
- Policy implementation
- Organizational development

## Position-Based Modifiers

### Command Positions
**Additional Requirements**:
- Squadron COs: +1 operation/month
- Department Heads: +1 staff meeting/month
- Ship Captains: +1 operation/month
- Staff Officers: +1 planning session/month

### Instructor Positions
**Modified Requirements**:
- Lead 2× training sessions = 1 operation credit
- Curriculum development = leadership activity
- Student mentorship = credited activity

### Support Positions
**Alternative Credits**:
- Recruitment: 2 successful recruits = 1 event
- Media: 1 production = 1 event
- Technical: Major project = 1 event
- Administrative: Special project = 1 event

## Tracking and Measurement

### Attendance Tracking
**What Counts**:
- Sign-in at event start
- Participation for 50%+ duration
- Proper excusal if leaving early
- Make-up opportunities

**What Doesn't Count**:
- Social-only events
- Partial participation (<50%)
- Unexcused absence
- Observer status only

### Monthly Reporting
**Individual Tracking**:
- Personal attendance log
- Automated system tracking
- Supervisor verification
- Monthly summary

**Unit Reporting**:
- Unit attendance percentage
- Trend analysis
- Issue identification
- Recognition opportunities

## Excusal Policies

### Valid Excusals
**Automatic Approval**:
- Military duty (real world)
- Medical emergency
- Family emergency
- Scheduled work conflict
- Pre-approved vacation

**Case-by-Case**:
- Technical difficulties
- Last-minute conflicts
- Transportation issues
- Weather events
- Time zone challenges

### Excusal Procedures
1. Notify chain of command ASAP
2. Provide brief explanation
3. Offer make-up availability
4. Document in system
5. Follow up when able

## Enforcement

### Progressive Actions
**First Violation**:
- Counseling session
- Expectation review
- Support offered
- Documentation only

**Second Violation**:
- Written warning
- Attendance plan
- Increased monitoring
- Limited privileges

**Third Violation**:
- Formal review board
- Possible demotion
- Restricted duties
- Final warning

**Continued Violations**:
- Separation proceedings
- Discharge consideration
- Character determination

### Positive Recognition
**Exceptional Attendance**:
- 100% monthly: Letter of commendation
- 100% quarterly: Award consideration
- 100% annually: Special recognition
- Above and beyond: Immediate recognition

## Special Circumstances

### Extended Absence
**Authorized Reasons**:
- Military deployment
- Medical treatment
- Family emergency
- Educational pursuits
- Work assignments

**Requirements**:
- Formal leave request
- Expected duration
- Contact maintenance
- Return planning

### Modified Standards
**Eligible Situations**:
- Different time zones (>8 hours)
- Documented medical conditions
- Verified hardships
- Probationary periods

**Approval Process**:
- Written request
- Supporting documentation
- Command review
- Period limitation

### Make-Up Opportunities
**Options Available**:
- Attend different unit's event
- Complete special project
- Extended duty period
- Additional training delivery
- Administrative support

## Time Zone Considerations

### Accommodation Measures
**Pacific Time Zone** (Primary):
- Standard event scheduling
- Full participation expected

**Other US Time Zones**:
- Alternative time slots
- Recorded training options
- Flexible operation times

**International Members**:
- Regional event coordination
- Asynchronous participation
- Modified requirements possible
- Make-up opportunities priority

## Attendance Benefits

### Career Impact
**Positive Attendance**:
- Promotion consideration
- Leadership selection
- Award eligibility
- Preferred assignments
- Recognition priority

**Poor Attendance**:
- Promotion delays
- Limited opportunities
- Reduced responsibilities
- Career stagnation
- Potential separation

## Key Reminders

### Member Responsibilities
- Know your requirements
- Track your attendance
- Communicate issues early
- Make up missed events
- Support unit readiness

### Leadership Responsibilities
- Track subordinate attendance
- Provide make-up opportunities
- Address issues early
- Recognize good attendance
- Support member challenges

## Quick Reference Table

| Rank | Operations/Training | Leadership/Support | Total Monthly |
|------|-------------------|-------------------|---------------|
| E1-E3 | 1 | 0 | 1 |
| E4-E6 | 1 | 1 | 2 |
| E7-E9 | 2 | 2 | 4 |
| WO | 1 | 1 | 2 |
| O1-O3 | 1 | 1 | 2 |
| O4-O6 | 2 | 2 | 4 |

## References
- 2.2.2 Leave of Absence Request Procedure
- 2.2.3 Extended Absence Management Guidelines
- 2.4.1 Progressive Disciplinary Action Guidelines
- 4.4.1 Monthly Training Requirements''',
                'difficulty_level': 'Basic',
                'is_required': True,
                'tags': ['attendance', 'requirements', 'participation', 'accountability', 'information']
            },
            {
                'document_number': '2.2.2',
                'title': 'Leave of Absence Request Procedure',
                'category': 'Procedure',
                'summary': 'Step-by-step procedure for requesting and processing leave of absence from unit activities.',
                'content': '''# Leave of Absence Request Procedure

## Purpose
This procedure outlines the process for requesting, approving, and managing leaves of absence to accommodate member's real-world obligations while maintaining unit readiness and accountability.

## Scope
Applies to all planned absences exceeding normal attendance requirements. Does not cover single event excusals or permanent separation from service.

## Leave Categories

### Standard Leave (1-30 days)
**Common Reasons**:
- Vacation/holiday
- Work obligations
- Family events
- Medical procedures
- Educational commitments

**Approval Authority**: Direct supervisor
**Notice Required**: 7 days
**Documentation**: Basic request form

### Extended Leave (31-90 days)
**Common Reasons**:
- Military deployment
- Extended work travel
- Medical treatment
- Family emergency
- Educational programs

**Approval Authority**: Department head
**Notice Required**: 14 days
**Documentation**: Detailed justification

### Long-term Leave (91-180 days)
**Common Reasons**:
- Combat deployment
- Serious medical condition
- Family hardship
- Career obligations
- Extended education

**Approval Authority**: Unit commander
**Notice Required**: 30 days
**Documentation**: Comprehensive package

### Inactive Reserve Status (181+ days)
**Common Reasons**:
- Indefinite deployment
- Chronic medical issues
- Major life changes
- Career conflicts
- Uncertain return

**Approval Authority**: Personnel board
**Notice Required**: 30 days
**Documentation**: Board review package

## Request Process

### Step 1: Initial Determination
1.1. Assess leave need:
   - Duration required
   - Flexibility available
   - Impact on duties
   - Alternative options
   - Return certainty

1.2. Category selection:
   - Review definitions
   - Calculate duration
   - Consider extensions
   - Plan conservatively
   - Allow buffers

1.3. Timing considerations:
   - Unit operations schedule
   - Training cycles
   - Critical events
   - Manning levels
   - Personal factors

### Step 2: Request Preparation
2.1. Form completion:
```
LEAVE OF ABSENCE REQUEST

Section 1: Member Information
Name: [Rank, Full Name]
Service Number: [Number]
Unit: [Current Assignment]
Position: [Current Duty]

Section 2: Leave Details
Type: [Standard/Extended/Long-term/IRS]
Start Date: [Specific Date]
End Date: [Specific Date]
Total Days: [Number]

Section 3: Reason for Leave
Primary Reason: [Category]
Detailed Explanation: [Narrative]
Supporting Documentation: [List]

Section 4: Coverage Plan
Duties Requiring Coverage: [List]
Suggested Coverage: [Names]
Handoff Plan: [Details]
Contact During Leave: [Yes/No/Limited]

Section 5: Certification
"I understand my obligations to maintain communication 
and return as scheduled. I will notify my chain of 
command immediately of any changes."

Signature: [Digital Signature]
Date: [Submission Date]
```

2.2. Supporting documentation:
   - Orders (military)
   - Medical documentation
   - Travel itinerary
   - Work requirements
   - Educational enrollment

2.3. Coverage planning:
   - Identify critical duties
   - Propose coverage
   - Document handoffs
   - Emergency contacts
   - Return preparation

### Step 3: Submission Process
3.1. Routing sequence:
   1. Immediate supervisor
   2. Department head (if required)
   3. Unit commander (if required)
   4. Personnel office
   5. Final approval authority

3.2. Timeline management:
   - Submit per notice requirements
   - Track routing progress
   - Follow up if delayed
   - Maintain communication
   - Confirm receipt

3.3. Communication protocol:
   - Use official channels
   - Maintain professionalism
   - Provide updates
   - Respond promptly
   - Document everything

### Step 4: Review and Approval
4.1. Supervisor review:
   - Impact assessment
   - Coverage adequacy
   - Timing evaluation
   - History consideration
   - Recommendation formulation

4.2. Approval considerations:
   - Mission impact
   - Member standing
   - Previous leaves
   - Unit manning
   - Precedent setting

4.3. Decision options:
   - Approve as requested
   - Approve with modifications
   - Defer to better timing
   - Conditional approval
   - Disapprove with reasoning

### Step 5: Notification
5.1. Approval notification:
```
LEAVE APPROVAL NOTIFICATION

Your leave request has been APPROVED:
- Type: [Category]
- Dates: [Start] to [End]
- Conditions: [Any special requirements]
- Check-in Requirements: [Frequency]
- Return Processing: [Instructions]

Point of Contact: [Name, Position]
Emergency Contact: [Name, Number]
```

5.2. Disapproval notification:
```
LEAVE DISAPPROVAL NOTIFICATION

Your leave request has been DISAPPROVED:
- Reason: [Specific explanation]
- Alternatives: [Suggested options]
- Resubmission: [If applicable]
- Appeal Rights: [Process]
- POC for Questions: [Name]
```

5.3. Distribution:
   - Member notification
   - Chain of command
   - Personnel records
   - Unit calendar
   - Coverage personnel

## During Leave

### Step 6: Leave Management
6.1. Member responsibilities:
   - Maintain contact (if required)
   - Monitor unit communications
   - Respond to emergencies
   - Update status changes
   - Prepare for return

6.2. Unit responsibilities:
   - Respect leave status
   - Emergency contact only
   - Maintain coverage
   - Track return date
   - Plan reintegration

6.3. Communication protocols:
   - Check-in schedule
   - Contact methods
   - Emergency thresholds
   - Update requirements
   - Privacy balance

### Step 7: Status Changes
7.1. Extension requests:
   - Submit before expiration
   - Provide justification
   - Update return date
   - Maintain approval level
   - Document reasons

7.2. Early return:
   - Notify immediately
   - Coordinate reintegration
   - Update systems
   - Resume duties
   - Brief leadership

7.3. Emergency recall:
   - Defined circumstances only
   - Command authority required
   - Travel support provided
   - Grace period allowed
   - Document thoroughly

## Return Procedures

### Step 8: Check-In Process
8.1. Pre-return actions:
   - Confirm return date
   - Review missed activities
   - Update availability
   - Prepare for duties
   - Contact supervisor

8.2. Return processing:
   - Report to supervisor
   - Update personnel
   - Receive briefings
   - Resume access
   - Restart duties

8.3. Reintegration timeline:
   - Day 1: Administrative
   - Week 1: Refresher training
   - Week 2: Partial duties
   - Week 3: Full duties
   - Month 1: Full integration

### Step 9: Post-Leave Actions
9.1. Documentation updates:
   - Close leave record
   - Update attendance
   - File documents
   - Record lessons
   - Archive communications

9.2. Performance considerations:
   - No negative impact
   - Catch-up period
   - Modified expectations
   - Support provided
   - Normal progression

9.3. Feedback collection:
   - Process effectiveness
   - Coverage success
   - Communication adequacy
   - Improvement suggestions
   - Policy recommendations

## Special Circumstances

### Emergency Leave
**Expedited Process**:
- Verbal notification acceptable
- Documentation follows
- Immediate approval
- Retroactive processing
- Full support provided

**Qualifying Events**:
- Death in family
- Serious illness/injury
- Natural disasters
- Legal obligations
- Command directed

### Medical Leave
**Additional Requirements**:
- Medical documentation
- Privacy protection
- Periodic updates
- Return clearance
- Accommodation planning

**Support Provided**:
- Extended timelines
- Flexible return
- Modified duties
- Continued belonging
- Full reintegration

### Deployment Leave
**Military Specific**:
- Orders verification
- Open-ended approval
- Hero status
- Priority return
- Recognition provided

**Maintenance During**:
- Honorary inclusion
- Achievement tracking
- Welcome planning
- Position protection
- Smooth transition

## Policy Guidelines

### Accumulation Limits
- Maximum 30 days standard leave/year
- Extended leave case-by-case
- No banking/carryover
- Use or lose annually
- Exceptions rare

### Abuse Prevention
- Pattern monitoring
- Verification rights
- False statement consequences
- Counseling intervention
- Progressive discipline

### Equal Treatment
- Consistent application
- No favoritism
- Rank irrelevant
- Fair consideration
- Appeals available

## Common Issues

### Issue: Late Requests
**Prevention**: Calendar planning, early communication
**Mitigation**: Expedited review, conditional approval

### Issue: Coverage Gaps
**Prevention**: Cross-training, depth building
**Mitigation**: Duty sharing, temporary assignments

### Issue: Communication Breakdown
**Prevention**: Clear requirements, multiple channels
**Mitigation**: Escalation procedures, assumption protocols

## References
- 2.2.1 Minimum Attendance Requirements
- 2.2.3 Extended Absence Management Guidelines
- 2.1.6 Transfer Request Procedure
- 2.1.7 Separation/Discharge Procedure''',
                'difficulty_level': 'Intermediate',
                'is_required': True,
                'tags': ['leave', 'absence', 'attendance', 'procedure', 'administration']
            },
            {
                'document_number': '2.2.3',
                'title': 'Extended Absence Management Guidelines',
                'category': 'Guidelines',
                'summary': 'Guidelines for managing extended absences while maintaining unit cohesion and member connection.',
                'content': '''# Extended Absence Management Guidelines

## Purpose
These guidelines provide frameworks for managing extended member absences (30+ days) in a way that maintains unit readiness, preserves member connections, and facilitates successful reintegration upon return.

## Management Principles

### Core Values
- **Member Retention**: Extended absence doesn't mean abandonment
- **Unit Readiness**: Maintain capability despite absences
- **Flexibility**: Accommodate real-world obligations
- **Connection**: Keep absent members engaged
- **Reintegration**: Plan for successful return

### Strategic Approach
- Proactive planning reduces disruption
- Communication maintains relationships
- Documentation ensures continuity
- Support demonstrates commitment
- Patience enables retention

## Absence Categories and Strategies

### Military Deployment (30-365+ days)
**Management Approach**:
- Hero status designation
- Honorary event inclusion
- Achievement tracking
- Care package coordination
- Welcome back planning

**Communication Strategy**:
- Monthly unit updates
- Deployment-safe channels
- Operational security minded
- Morale support focus
- Family inclusion

**Reintegration Planning**:
- Pre-return contact
- Refresher training scheduled
- Position guaranteed
- Recognition planned
- Buddy assigned

### Medical Absence (30-180+ days)
**Management Approach**:
- Privacy protection paramount
- Flexible timeline
- Modified duty options
- Support network activation
- Accommodation planning

**Communication Strategy**:
- Member-driven frequency
- Health status optional
- Positive encouragement
- Unit card/messages
- No pressure applied

**Reintegration Planning**:
- Medical clearance first
- Gradual return option
- Duty modifications ready
- Support continued
- Success focused

### Career/Education (30-180 days)
**Management Approach**:
- Professional development recognized
- Knowledge sharing expected
- Part-time participation allowed
- Leadership opportunities preserved
- Investment perspective

**Communication Strategy**:
- Bi-weekly check-ins
- Professional updates
- Learning application
- Milestone celebration
- Network maintenance

**Reintegration Planning**:
- Skills utilization immediate
- Teaching opportunities
- Advanced placement possible
- Knowledge capture
- Career progression

### Personal/Family (30-90 days)
**Management Approach**:
- Compassionate understanding
- Privacy respected
- Minimal requirements
- Support offered
- Judgment withheld

**Communication Strategy**:
- Low-key contact
- Optional participation
- Resource sharing
- Emotional support
- Patience exercised

**Reintegration Planning**:
- Gentle re-engagement
- No explanations required
- Normal progression
- Fresh start offered
- Full acceptance

## Operational Management

### Coverage Planning
**Immediate Actions** (Days 1-7):
- Duty redistribution
- Critical task identification
- Temporary assignments
- Access management
- Communication plan

**Short-term Solutions** (Weeks 2-4):
- Cross-training acceleration
- Mentorship reassignment
- Project reallocation
- Schedule adjustment
- Workload balancing

**Long-term Adaptations** (Month 2+):
- Organizational restructure
- Permanent coverage
- New member integration
- Process optimization
- Succession planning

### Documentation Requirements
**Maintain Current**:
- Leave status/duration
- Contact information
- Coverage assignments
- Project disposition
- Return planning

**Privacy Protection**:
- Medical information secured
- Personal details limited
- Need-to-know basis
- Professional handling
- Rumor prevention

### Communication Protocols
**Unit to Member**:
- Regular update schedule
- Major event notifications
- Achievement recognition
- Support offerings
- Return coordination

**Member to Unit**:
- Check-in requirements
- Status updates (optional)
- Availability changes
- Extension requests
- Return notifications

**Public Communication**:
- Absent member recognition
- Privacy protection
- Positive messaging
- Contribution acknowledgment
- Return anticipation

## Support Systems

### Buddy System
**Buddy Selection**:
- Similar experience
- Good communication
- Reliable character
- Time availability
- Positive attitude

**Buddy Responsibilities**:
- Regular contact
- Unit liaison
- Information relay
- Morale support
- Reintegration assistance

### Unit Support
**Leadership Actions**:
- Public recognition
- Resource provision
- Flexibility demonstration
- Team rallying
- Patience modeling

**Peer Support**:
- Message sending
- Event inclusion
- Achievement sharing
- Welcome planning
- Acceptance preparing

### Administrative Support
**Personnel Actions**:
- Status tracking
- Benefit preservation
- Record maintenance
- System updates
- Process facilitation

**Technical Support**:
- Access maintenance
- Account preservation
- Data protection
- System updates
- Credential renewal

## Reintegration Framework

### Pre-Return Phase (30 days out)
**Coordination Elements**:
- Contact increase
- Schedule discussion
- Training planning
- Expectation setting
- Welcome preparation

**Administrative Prep**:
- Access restoration
- System updates
- Record review
- Equipment ready
- Position confirmation

### Return Week
**Day 1-2: Administrative**
- Check-in processing
- System access
- Brief leadership
- Meet changes
- Set schedule

**Day 3-4: Orientation**
- Unit update brief
- Policy changes
- New personnel
- System changes
- Q&A session

**Day 5-7: Transition**
- Light duties
- Shadow current
- Refresh skills
- Social events
- Feedback session

### First Month Back
**Week 1: Basics**
- Administrative complete
- Refresher training
- Social reintegration
- Light workload
- Close monitoring

**Week 2: Building**
- Increase duties
- Skill validation
- Team integration
- Normal workload
- Regular check-ins

**Week 3-4: Normalizing**
- Full duties
- Leadership roles
- Project assignment
- Performance tracking
- Standard expectations

## Success Metrics

### Individual Level
**Positive Indicators**:
- Communication maintained
- Return executed
- Duties resumed
- Relationships strong
- Performance normal

**Warning Signs**:
- Communication ceased
- Return delayed
- Isolation observed
- Performance degraded
- Disengagement noted

### Unit Level
**Effectiveness Measures**:
- Coverage seamless
- Morale maintained
- Mission success
- Return rate high
- Relationships preserved

**Areas for Improvement**:
- Coverage gaps
- Morale impacts
- Mission degradation
- Low returns
- Relationship loss

## Common Challenges

### Challenge: Communication Breakdown
**Prevention Strategies**:
- Multiple contact methods
- Flexible requirements
- Proactive outreach
- Low pressure approach
- Alternative channels

**Recovery Actions**:
- Escalate carefully
- Check welfare
- Offer support
- Maintain patience
- Document attempts

### Challenge: Extended Extensions
**Management Approach**:
- Understand reasons
- Adjust expectations
- Maintain connection
- Plan alternatives
- Show flexibility

**Decision Points**:
- 30-day increments
- Status review
- Option discussion
- Alternative paths
- Mutual agreement

### Challenge: Difficult Reintegration
**Common Issues**:
- Skills atrophied
- Relationships changed
- Culture shifted
- Technology updated
- Confidence lowered

**Mitigation Strategies**:
- Patience exercised
- Training provided
- Mentorship assigned
- Gradual progression
- Success celebrated

## Best Practices

### For Leadership
**Do**:
- Plan proactively
- Communicate regularly
- Show flexibility
- Maintain connection
- Celebrate returns

**Don't**:
- Abandon members
- Pressure returns
- Ignore struggles
- Rush reintegration
- Show frustration

### For Absent Members
**Do**:
- Maintain contact
- Update status
- Plan return
- Accept support
- Communicate needs

**Don't**:
- Disappear completely
- Ignore requirements
- Delay notifications
- Refuse help
- Burn bridges

### For Units
**Do**:
- Rally together
- Share workload
- Stay positive
- Plan welcome
- Show patience

**Don't**:
- Resent absence
- Complain publicly
- Resist coverage
- Exclude member
- Forget contributions

## Policy Reminders

### Rights and Obligations
**Member Rights**:
- Privacy protection
- Position preservation
- Fair treatment
- Support access
- Appeal process

**Member Obligations**:
- Communication maintenance
- Policy compliance
- Timely notifications
- Professional conduct
- Return commitment

### Command Responsibilities
- Fair application
- Support provision
- Privacy protection
- Reintegration planning
- Success enabling

## References
- 2.2.1 Minimum Attendance Requirements
- 2.2.2 Leave of Absence Request Procedure
- 2.1.3 Service Record Management Procedure
- 4.3.1 NCO Leadership Course Information''',
                'difficulty_level': 'Intermediate',
                'is_required': True,
                'tags': ['absence', 'management', 'retention', 'reintegration', 'guidelines']
            }
        ]

        for data in standards_data:
            standard, created = Standard.objects.get_or_create(
                document_number=data['document_number'],
                defaults={
                    'title': data['title'],
                    'standard_sub_group': subgroup,
                    'content': data['content'],
                    'summary': data['summary'],
                    'version': '1.0',
                    'status': 'Active',
                    'author': user,
                    'approved_by': user,
                    'approval_date': timezone.now(),
                    'effective_date': timezone.now(),
                    'difficulty_level': data['difficulty_level'],
                    'tags': data['tags'],
                    'is_required': data.get('is_required', False)
                }
            )
            if created:
                self.stdout.write(f'  Created: {data["document_number"]} - {data["title"]}')

    def _create_awards_commendations_standards(self, group, user):
        """Create Awards & Commendations subgroup and its standards"""
        subgroup, _ = StandardSubGroup.objects.get_or_create(
            name='Awards & Commendations',
            standard_group=group,
            defaults={
                'description': 'Procedures for nominating, approving, and documenting awards and commendations.',
                'order_index': 3,
                'is_active': True,
                'created_by': user
            }
        )

        standards_data = [
            {
                'document_number': '2.3.1',
                'title': 'Award Nomination & Approval Procedure',
                'category': 'Procedure',
                'summary': 'Comprehensive procedure for nominating personnel for awards and processing approvals.',
                'content': '''# Award Nomination & Approval Procedure

## Purpose
This procedure establishes the process for nominating deserving personnel for awards and commendations, ensuring fair recognition of exceptional service, achievement, and valor within the 5th Expeditionary Group.

## Scope
Applies to all award nominations from unit-level commendations through the highest decorations, covering all branches and ranks within the organization.

## Award Categories

### Valor Awards
**Distinguished Service Cross**
- Extraordinary heroism in combat
- Risk of life beyond call of duty
- Direct combat action
- Command approval required
- Witness statements mandatory

**Silver Star**
- Gallantry in action against enemy
- Distinguished service in combat
- Lesser than DSC criteria
- Brigade level approval
- Combat documentation required

**Bronze Star**
- Heroic or meritorious achievement
- Combat or non-combat
- Significant contribution
- Battalion approval
- Detailed citation required

### Achievement Awards
**Meritorious Service Medal**
- Superior performance of duties
- Sustained exceptional service
- Significant accomplishment
- Command level approval
- Performance documentation

**Achievement Medal**
- Outstanding achievement
- Single act or sustained
- Above normal expectations
- Unit level approval
- Specific accomplishments

**Commendation Medal**
- Meritorious service
- Above average performance
- Unit contribution
- Company level approval
- Period of service

### Service Awards
**Good Conduct Medal**
- Continuous honorable service
- 12 months minimum
- No disciplinary actions
- Automatic consideration
- Administrative review

**Campaign Medals**
- Participation in operations
- Specific campaigns
- Time/location based
- Automatic award
- Verification required

**Service Ribbons**
- Time in service
- Special qualifications
- Training completion
- Administrative action
- Record verification

### Unit Awards
**Presidential Unit Citation**
- Extraordinary heroism
- Unit-wide action
- Strategic impact
- Highest approval
- Historical significance

**Meritorious Unit Citation**
- Outstanding achievement
- Unit excellence
- Mission success
- Command approval
- Collective effort

## Nomination Process

### Step 1: Identification of Achievement
1.1. Recognition triggers:
   - Witnessed heroic act
   - Exceptional performance noted
   - Mission critical success
   - Sustained superior service
   - Peer recommendation

1.2. Initial documentation:
   - Date/time of action
   - Location/circumstances
   - Witnesses present
   - Impact assessment
   - Supporting evidence

1.3. Eligibility verification:
   - Service requirements met
   - No pending adverse actions
   - Previous awards checked
   - Time limits observed
   - Chain of command clear

### Step 2: Nomination Package Preparation
2.1. Required documents:
   - DA Form 638 equivalent
   - Proposed citation
   - Achievement documentation
   - Witness statements
   - Chain of command endorsements

2.2. Citation writing:
```
CITATION FORMAT

[RANK NAME] distinguished [himself/herself] by [meritorious 
service/outstanding achievement/heroism] while serving as 
[POSITION] with [UNIT] from [DATE] to [DATE]. 

[Specific accomplishments in detail, using action words and 
quantifiable results where possible. Include impact on mission, 
unit, and larger organization.]

[RANK NAME]'s [outstanding dedication/exceptional performance/
courageous actions] reflect great credit upon [himself/herself], 
[UNIT], and the 5th Expeditionary Group.
```

2.3. Supporting documentation:
   - Operation reports
   - Performance evaluations
   - Training records
   - Witness statements
   - Photo/video evidence

### Step 3: Chain of Command Processing
3.1. Immediate supervisor:
   - Initial review
   - Fact verification
   - Recommendation added
   - Package completion
   - Forward timing

3.2. Each level review:
   - Merit assessment
   - Award level appropriate
   - Documentation complete
   - Comparison to standards
   - Endorsement decision

3.3. Processing timeline:
   - Initial: 5 duty days
   - Company: 5 duty days
   - Battalion: 7 duty days
   - Brigade: 10 duty days
   - Final: 10 duty days

### Step 4: Board Review (If Required)
4.1. Board composition:
   - Senior officer president
   - Two voting members
   - Awards expert advisor
   - Recorder (non-voting)
   - Legal review (if needed)

4.2. Review criteria:
   - Achievement significance
   - Documentation quality
   - Award appropriateness
   - Previous recognition
   - Precedent consideration

4.3. Board options:
   - Approve as submitted
   - Upgrade recommendation
   - Downgrade recommendation
   - Return for more information
   - Disapprove with rationale

### Step 5: Final Approval
5.1. Approval authorities:
   - Squad/Team awards: Company Commander
   - Company awards: Battalion Commander
   - Battalion awards: Brigade Commander
   - Brigade awards: Division Commander
   - Valor awards: Commanding General

5.2. Final review elements:
   - Legal sufficiency
   - Policy compliance
   - Precedent alignment
   - Political sensitivity
   - Public relations impact

5.3. Decision documentation:
   - Approval memorandum
   - Orders publication
   - Database entry
   - Certificate preparation
   - Ceremony planning

## Award Presentation

### Step 6: Ceremony Planning
6.1. Ceremony types:
   - Formal formation
   - Unit gathering
   - Command ceremony
   - Private presentation
   - Virtual ceremony

6.2. Ceremony elements:
   - Invocation/opening
   - Citation reading
   - Award presentation
   - Recipient remarks
   - Command comments

6.3. Guest considerations:
   - Family invitations
   - Unit attendance
   - Photography arranged
   - Reception planning
   - Streaming setup

### Step 7: Presentation Execution
7.1. Setup requirements:
   - Award/certificate ready
   - Citation printed
   - Podium/flags arranged
   - Audio/video tested
   - Rehearsal completed

7.2. Presentation protocol:
   - Formation called
   - Recipient centered
   - Citation read fully
   - Award presented properly
   - Handshake/salute exchanged

7.3. Documentation:
   - Photography/video
   - Attendance record
   - Social media ready
   - News release drafted
   - Historical archive

## Post-Award Actions

### Step 8: Administrative Processing
8.1. Record updates:
   - Service record entry
   - Award database update
   - Ribbon authorization
   - Promotion points added
   - Public record created

8.2. Notification distribution:
   - Personnel office
   - Home unit
   - Public affairs
   - Family notification
   - Alumni association

8.3. Follow-up actions:
   - Thank you notes
   - Lessons captured
   - Process feedback
   - Precedent documented
   - Files archived

## Special Circumstances

### Posthumous Awards
**Additional Requirements**:
- Next of kin coordination
- Memorial service integration
- Legacy preservation
- Media sensitivity
- Expedited processing

**Presentation Protocol**:
- Family receives award
- Citation modified appropriately
- Memorial incorporation
- Unit representation
- Honor guard possible

### Retroactive Awards
**Justification Required**:
- Why delayed
- New information discovered
- Administrative error
- Witness availability
- Command oversight

**Processing Differences**:
- Extended documentation
- Historical verification
- Previous denials reviewed
- Statute limitations
- Special approval needed

### Foreign Awards
**Coordination Requirements**:
- Allied force liaison
- Approval channels
- Wear authorization
- Translation needs
- Diplomatic protocol

### Classified Actions
**Special Handling**:
- Sanitized citations
- Classified annexes
- Limited ceremony
- Security clearances
- Delayed recognition

## Quality Control

### Award Standards
**Maintaining Integrity**:
- Consistent criteria
- Fair application
- Inflation prevention
- Merit-based only
- Documentation required

**Common Errors**:
- Inflated language
- Insufficient detail
- Missing documentation
- Incorrect level
- Timeline violations

### Review Mechanisms
**Random Audits**:
- Package quality
- Process compliance
- Timeline adherence
- Decision consistency
- Record accuracy

**Annual Analysis**:
- Award distribution
- Demographics review
- Trend identification
- Policy effectiveness
- Improvement recommendations

## Award Levels Guide

### Quick Reference
| Achievement Level | Appropriate Award | Approval Level |
|------------------|------------------|----------------|
| Unit impact | Achievement Medal | Company |
| Multi-unit impact | Commendation Medal | Battalion |
| Strategic impact | Meritorious Service | Brigade |
| Combat valor | Bronze Star+ | Division+ |
| Extraordinary heroism | Silver Star+ | Corps+ |

### Time Requirements
- Immediate valor: No minimum
- Achievement: Single act
- Meritorious service: 6 months
- Good conduct: 12 months
- Campaign: Participation

## Common Issues

### Issue: Lost Recommendations
**Prevention**: Digital tracking, multiple copies
**Recovery**: Resubmission process, expedited review

### Issue: Delayed Processing
**Prevention**: Timeline enforcement, regular follow-up
**Mitigation**: Expedite authority, command attention

### Issue: Inconsistent Standards
**Prevention**: Board training, written criteria
**Correction**: Review process, precedent documentation

## Best Practices

### For Nominators
- Document immediately
- Be specific and quantify
- Follow format exactly
- Submit promptly
- Track progress

### For Reviewers
- Review thoroughly
- Apply standards consistently
- Provide feedback
- Meet timelines
- Document decisions

### For Commands
- Recognize promptly
- Maintain standards
- Celebrate achievements
- Support process
- Learn from awards

## References
- 2.3.2 Service Citation Documentation Guidelines
- 2.1.3 Service Record Management Procedure
- 2.1.4 Performance Evaluation Guidelines
- 9.1.2 Promotion Ceremony Protocols''',
                'difficulty_level': 'Advanced',
                'is_required': True,
                'tags': ['awards', 'medals', 'recognition', 'procedure', 'nominations']
            },
            {
                'document_number': '2.3.2',
                'title': 'Service Citation Documentation Guidelines',
                'category': 'Guidelines',
                'summary': 'Guidelines for writing effective citations and maintaining award documentation.',
                'content': '''# Service Citation Documentation Guidelines

## Purpose
These guidelines establish standards for writing compelling, accurate citations and maintaining comprehensive award documentation that properly recognizes service members' achievements while preserving historical records.

## Citation Writing Principles

### Core Elements
Every citation must contain:
- **Who**: Full name, rank, position
- **What**: Specific achievement/action
- **When**: Dates of action/service
- **Where**: Location/unit/operation
- **Why**: Significance and impact
- **How**: Methods and leadership shown

### Writing Standards
**Language Requirements**:
- Active voice preferred
- Strong action verbs
- Specific, not general
- Quantifiable when possible
- Professional tone throughout

**Avoid**:
- Passive constructions
- Vague descriptions
- Excessive superlatives
- Classified information
- Personal opinions

## Citation Formats

### Valor Citation Structure
```
Opening: [RANK NAME] distinguished [himself/herself] by 
[heroism/gallantry] in action against [enemy forces] on 
[DATE] at [LOCATION].

Body: When [situation description], [RANK NAME] [specific 
actions taken]. Despite [dangers/obstacles faced], [he/she] 
[continued actions]. [His/Her] actions resulted in [specific 
outcomes and lives saved/mission success].

Closing: [RANK NAME]'s [courage/valor] under fire reflects 
great credit upon [himself/herself], [UNIT], and the 5th 
Expeditionary Group.
```

### Achievement Citation Structure
```
Opening: [RANK NAME] distinguished [himself/herself] by 
[outstanding achievement/meritorious service] while serving 
as [POSITION] with [UNIT] from [DATE] to [DATE].

Body: [RANK NAME] [specific accomplishments with metrics]. 
[He/She] demonstrated exceptional [leadership/skill] by 
[specific examples]. Additionally, [secondary achievements]. 
The impact of these actions [measurable results].

Closing: [RANK NAME]'s exemplary performance reflects great 
credit upon [himself/herself], [UNIT], and the 5th 
Expeditionary Group.
```

### Service Citation Structure
```
Opening: For [exceptionally meritorious service/outstanding 
dedication] while serving as [POSITION] with [UNIT] from 
[DATE] to [DATE].

Body: During this period, [RANK NAME] [primary achievements]. 
[His/Her] leadership in [specific area] resulted in [outcomes]. 
Furthermore, [additional contributions]. [He/She] consistently 
[sustained performance examples].

Closing: [RANK NAME]'s dedication to duty and professional 
excellence reflect great credit upon [himself/herself], [UNIT], 
and the 5th Expeditionary Group.
```

## Action Words and Phrases

### Strong Openers
**For Valor**:
- Courageously engaged
- Fearlessly led
- Heroically defended
- Valiantly fought
- Boldly assaulted

**For Achievement**:
- Expertly managed
- Innovatively developed
- Successfully implemented
- Strategically planned
- Effectively coordinated

**For Service**:
- Consistently demonstrated
- Tirelessly devoted
- Professionally executed
- Steadfastly maintained
- Continuously improved

### Impact Statements
**Quantifiable Results**:
- "Increased operational readiness by 35%"
- "Saved 12 crew members"
- "Reduced costs by €50,000"
- "Trained 45 personnel"
- "Completed 120 missions"

**Qualitative Results**:
- "Restored unit morale"
- "Established new standard"
- "Inspired peers"
- "Transformed culture"
- "Built lasting partnerships"

## Documentation Requirements

### Primary Documentation
**Essential Records**:
1. Original nomination form
2. Final citation text
3. Approval chain documentation
4. Orders/authorization
5. Presentation records

**Supporting Evidence**:
- Witness statements
- Operation reports
- Performance records
- Photographs/video
- News articles

### Witness Statement Format
```
WITNESS STATEMENT

I, [RANK NAME], personally witnessed [nominee's] actions on 
[DATE] at [LOCATION].

[Detailed account of what was observed, including specific 
actions, timeline, conditions, and results]

The above statement is true to the best of my knowledge.

[Signature]
[Printed Name, Rank]
[Date]
[Contact Information]
```

### Record Maintenance
**Digital Files Organization**:
```
/Awards_Documentation/
├── [Service_Number]/
│   ├── Nominations/
│   │   ├── [Award_Date]_Nomination.pdf
│   │   ├── [Award_Date]_Citation.doc
│   │   └── [Award_Date]_Supporting/
│   ├── Approvals/
│   │   ├── [Award_Date]_Approval.pdf
│   │   └── [Award_Date]_Orders.pdf
│   └── Presentations/
│       ├── [Award_Date]_Photos/
│       └── [Award_Date]_Ceremony.mp4
```

## Writing Best Practices

### Do's
1. **Be Specific**
   - Use exact dates, numbers, locations
   - Name specific operations/exercises
   - Include measurable outcomes
   - Cite particular instances

2. **Show Impact**
   - Unit-level effects
   - Mission accomplishment
   - Resource savings
   - Personnel influenced

3. **Use Variety**
   - Different sentence structures
   - Various action verbs
   - Multiple examples
   - Diverse accomplishments

4. **Maintain Flow**
   - Logical progression
   - Smooth transitions
   - Clear connections
   - Strong conclusion

### Don'ts
1. **Avoid Clichés**
   - "Above and beyond"
   - "110% effort"
   - "Second to none"
   - "Tireless efforts"

2. **Skip Generalities**
   - "Always outstanding"
   - "Best Marine"
   - "Never failed"
   - "Perfect officer"

3. **Exclude Opinions**
   - "I believe"
   - "In my opinion"
   - "Seemed to"
   - "Probably"

4. **Omit Irrelevancies**
   - Personal information
   - Unrelated achievements
   - Ancient history
   - Future promises

## Special Citation Situations

### Classified Operations
**Sanitization Requirements**:
- Remove operation names
- Generalize locations
- Obscure unit identities
- Protect methods
- Maintain meaning

**Example Transformation**:
- Classified: "Operation STEELPAW at Grid 247531"
- Sanitized: "combat operations in hostile territory"

### Joint Operations
**Multi-Service Considerations**:
- Service-appropriate language
- Rank equivalencies
- Cultural sensitivities
- Shared credit
- Combined standards

### Group Awards
**Individual Recognition Within**:
- Highlight leadership roles
- Specify contributions
- Maintain unit focus
- Balance individual/team
- Equal opportunity

## Citation Review Checklist

### Content Review
- [ ] All facts verified
- [ ] Dates accurate
- [ ] Spelling correct
- [ ] Grammar proper
- [ ] Format compliant

### Impact Review
- [ ] Achievement clear
- [ ] Significance shown
- [ ] Outcomes stated
- [ ] Level appropriate
- [ ] Standards met

### Security Review
- [ ] Classification checked
- [ ] OPSEC maintained
- [ ] Privacy protected
- [ ] Release authorized
- [ ] Public suitable

### Administrative Review
- [ ] Signatures complete
- [ ] Routing documented
- [ ] Timeline met
- [ ] Files organized
- [ ] Copies distributed

## Common Citation Errors

### Error: Vague Accomplishments
**Wrong**: "Performed duties in an outstanding manner"
**Right**: "Processed 347 personnel actions with 100% accuracy"

### Error: Unsubstantiated Claims
**Wrong**: "Best pilot in the squadron"
**Right**: "Ranked #1 of 12 pilots in combat efficiency"

### Error: Inappropriate Tone
**Wrong**: "This guy was absolutely incredible"
**Right**: "Demonstrated exceptional leadership qualities"

### Error: Missing Impact
**Wrong**: "Completed all assigned tasks"
**Right**: "Completed critical repairs 6 hours ahead of schedule, enabling mission launch"

## Historical Preservation

### Archive Requirements
**Permanent Records**:
- Original citations
- Award orders
- Photographs
- Ceremony programs
- News coverage

**Retention Periods**:
- Digital copies: Permanent
- Paper originals: 50 years
- Working files: 5 years
- Drafts: 1 year
- Emails: 3 years

### Historical Context
**Include When Relevant**:
- First of type awards
- Operation significance
- Precedent setting
- Unit history connection
- Legacy impact

## Quality Assurance

### Citation Review Board
**Composition**:
- Senior NCO (writing expert)
- Officer (awards experience)
- Admin specialist
- Previous recipient
- Historian

**Review Focus**:
- Factual accuracy
- Writing quality
- Format compliance
- Impact clarity
- Historical value

### Continuous Improvement
**Feedback Collection**:
- Board comments
- Recipient input
- Command guidance
- Process efficiency
- Best practices

**Training Requirements**:
- Annual writer training
- Citation examples study
- Common errors review
- System updates
- Mentorship program

## Quick Reference Guide

### Citation Length Guidelines
- Bronze Star: 8-12 sentences
- Achievement Medal: 6-10 sentences
- Commendation Medal: 5-8 sentences
- Unit awards: 10-15 sentences
- Certificates: 3-5 sentences

### Processing Timelines
- Draft: 2 days
- Review: 2 days
- Revision: 1 day
- Approval: 5-10 days
- Production: 3 days

## References
- 2.3.1 Award Nomination & Approval Procedure
- 2.1.3 Service Record Management Procedure
- 7.2.2 Operational Security (OPSEC) Advice
- 3.4.1 After Action Report (AAR) Procedure''',
                'difficulty_level': 'Intermediate',
                'is_required': True,
                'tags': ['citations', 'documentation', 'awards', 'writing', 'guidelines']
            }
        ]

        for data in standards_data:
            standard, created = Standard.objects.get_or_create(
                document_number=data['document_number'],
                defaults={
                    'title': data['title'],
                    'standard_sub_group': subgroup,
                    'content': data['content'],
                    'summary': data['summary'],
                    'version': '1.0',
                    'status': 'Active',
                    'author': user,
                    'approved_by': user,
                    'approval_date': timezone.now(),
                    'effective_date': timezone.now(),
                    'difficulty_level': data['difficulty_level'],
                    'tags': data['tags'],
                    'is_required': data.get('is_required', False)
                }
            )
            if created:
                self.stdout.write(f'  Created: {data["document_number"]} - {data["title"]}')

    def _create_disciplinary_standards(self, group, user):
        """Create Disciplinary Procedures subgroup and its standards"""
        subgroup, _ = StandardSubGroup.objects.get_or_create(
            name='Disciplinary Procedures',
            standard_group=group,
            defaults={
                'description': 'Guidelines and procedures for maintaining discipline and addressing misconduct.',
                'order_index': 4,
                'is_active': True,
                'created_by': user
            }
        )

        standards_data = [
            {
                'document_number': '2.4.1',
                'title': 'Progressive Disciplinary Action Guidelines',
                'category': 'Guidelines',
                'summary': 'Framework for applying progressive discipline fairly and consistently across the organization.',
                'content': '''# Progressive Disciplinary Action Guidelines

## Purpose
These guidelines establish a fair, consistent, and progressive approach to addressing misconduct and performance issues within the 5th Expeditionary Group, focusing on correction and improvement while maintaining good order and discipline.

## Disciplinary Philosophy

### Core Principles
- **Corrective, Not Punitive**: Focus on changing behavior
- **Progressive Nature**: Escalating responses to repeated issues
- **Fair and Consistent**: Equal treatment for similar offenses
- **Timely Response**: Address issues promptly
- **Documentation**: Maintain proper records

### Goals of Discipline
- Correct inappropriate behavior
- Maintain unit standards
- Protect unit cohesion
- Ensure mission readiness
- Develop better service members

## Levels of Disciplinary Action

### Level 1: Verbal Counseling
**When Applied**:
- First minor offense
- Unintentional violations
- Performance issues
- Attendance problems
- Minor policy infractions

**Process**:
- Private discussion
- Explain issue clearly
- Set expectations
- Offer support
- Document basics only

**Documentation**:
```
COUNSELING RECORD (Verbal)
Date: [DATE]
Member: [Rank Name]
Counselor: [Rank Name]
Issue: [Brief description]
Action: Verbal counseling conducted
Follow-up: [Date if needed]
```

### Level 2: Written Counseling
**When Applied**:
- Repeated minor offenses
- First moderate offense
- Failed improvement
- Pattern developing
- Formal warning needed

**Process**:
- Formal meeting scheduled
- Written statement prepared
- Member input allowed
- Expectations documented
- Signed acknowledgment

**Documentation Format**:
```
WRITTEN COUNSELING STATEMENT

Date: [DATE]
To: [Rank, Name]
From: [Counselor Rank, Name]
Subject: Written Counseling - [Issue]

1. This counseling is regarding: [Specific behavior/issue]
2. Previous discussions: [Dates of verbal counseling]
3. Expected standard: [Clear expectations]
4. Corrective actions required: [Specific steps]
5. Timeline for improvement: [Specific dates]
6. Consequences of non-improvement: [Next steps]

Member acknowledgment: ________________
Counselor signature: ________________
```

### Level 3: Letter of Reprimand
**When Applied**:
- Serious first offense
- Multiple written counselings
- Moderate misconduct
- Leadership failures
- Trust violations

**Authority Level**: Company Commander or above

**Content Requirements**:
- Specific misconduct detailed
- Standards violated cited
- Impact on unit described
- Previous counseling noted
- Future expectations stated

**Member Rights**:
- Written response allowed
- 72 hours to respond
- Response filed with letter
- Appeal process available
- Representation permitted

### Level 4: Administrative Demotion
**When Applied**:
- Serious misconduct
- Leadership failure
- Repeated offenses
- Loss of confidence
- Inability to perform

**Process Requirements**:
- Board recommendation
- Command approval
- Member notification
- Appeal opportunity
- Effective date set

**Documentation Package**:
- Demotion recommendation
- Supporting counselings
- Performance records
- Member's response
- Board proceedings

### Level 5: Separation Proceedings
**When Applied**:
- Pattern of misconduct
- Serious offense
- Rehabilitation failed
- Unit detriment
- Command decision

**Types**:
- General discharge
- Other than honorable
- Administrative board
- Command directed
- Medical evaluation

**Due Process**:
- Formal notification
- Legal consultation
- Board hearing
- Evidence presentation
- Appeal rights

## Offense Categories and Responses

### Minor Offenses
**Examples**:
- Late to formation (first)
- Uniform violation
- Missed deadline
- Communication failure
- Protocol breach

**Typical Response**:
- First offense: Verbal counseling
- Second offense: Written counseling
- Third offense: Letter of reprimand

### Moderate Offenses
**Examples**:
- Disrespect to NCO
- Safety violation
- Missed movement
- False statement
- Negligent damage

**Typical Response**:
- First offense: Written counseling/LOR
- Second offense: Demotion consideration
- Third offense: Separation proceedings

### Serious Offenses
**Examples**:
- Disrespect to officer
- Security violation
- Discrimination/harassment
- Integrity violation
- Criminal conduct

**Typical Response**:
- First offense: LOR minimum
- Often: Immediate demotion
- Possible: Separation proceedings

### Zero Tolerance Offenses
**Examples**:
- Sexual assault/harassment
- Hate crimes
- Espionage/sabotage
- Drug use
- Felony conviction

**Response**: Immediate separation proceedings

## Disciplinary Process

### Step 1: Issue Identification
1.1. Observation/report received
1.2. Initial fact gathering
1.3. Preliminary assessment
1.4. Notification to chain
1.5. Member notification

### Step 2: Investigation
2.1. Appointing authority designated
2.2. Investigating officer assigned
2.3. Evidence collection
2.4. Witness interviews
2.5. Member statement

### Step 3: Decision Making
3.1. Facts reviewed
3.2. Standards applied
3.3. Previous record considered
3.4. Mitigation factors weighed
3.5. Appropriate level determined

### Step 4: Implementation
4.1. Member notification
4.2. Counseling conducted
4.3. Documentation completed
4.4. Rights explained
4.5. Timeline established

### Step 5: Follow-Up
5.1. Improvement monitored
5.2. Support provided
5.3. Progress documented
5.4. Completion noted
5.5. Record updated

## Special Considerations

### New Members
**Grace Period Factors**:
- Learning curve expected
- Mistakes anticipated
- Extra guidance provided
- Patience exercised
- Focus on education

**Modified Approach**:
- Extended verbal counseling
- Mentorship emphasis
- Positive reinforcement
- Clear expectations
- Frequent check-ins

### Senior Personnel
**Additional Considerations**:
- Higher standards expected
- Example setting required
- Impact magnified
- Trust essential
- Swift action needed

**Process Modifications**:
- Shortened timeline
- Higher approval level
- Broader impact assessment
- Public trust factor
- Legacy considerations

### Medical/Personal Issues
**Evaluation Required**:
- Medical documentation
- Fitness for duty
- Temporary factors
- Support needed
- Accommodation possible

**Alternative Actions**:
- Medical leave
- Modified duties
- Counseling referral
- Support services
- Delayed proceedings

## Rights and Procedures

### Member Rights
**Fundamental Rights**:
- Know accusations
- Present defense
- Have representation
- Appeal decisions
- Fair treatment

**Procedural Rights**:
- Timely notification
- Evidence access
- Witness calling
- Statement opportunity
- Record review

### Command Responsibilities
**Required Actions**:
- Fair investigation
- Timely resolution
- Proper documentation
- Rights protection
- Consistent application

**Prohibited Actions**:
- Mass punishment
- Public humiliation
- Excessive delay
- Prejudgment
- Retaliation

## Documentation Standards

### Record Keeping
**Required Elements**:
- Date/time/location
- Persons present
- Issue description
- Action taken
- Member response

**File Management**:
- Secure storage
- Limited access
- Retention periods
- Disposal procedures
- Privacy protection

### Documentation Timeline
- Verbal counseling: Note within 24 hours
- Written counseling: File within 48 hours
- Letter of reprimand: Process within 7 days
- Demotion: Complete within 30 days
- Separation: Timeline varies

## Appeal Process

### Grounds for Appeal
- Procedural errors
- New evidence
- Disproportionate action
- Bias demonstrated
- Rights violated

### Appeal Levels
1. Immediate supervisor
2. Next level commander
3. Unit commander
4. Personnel board
5. Commanding General

### Appeal Timeline
- Submission: 7 days
- Review: 14 days
- Decision: 21 days
- Implementation: Immediate
- Final: 30 days total

## Best Practices

### For Leaders
**Do**:
- Address issues immediately
- Document consistently
- Apply standards fairly
- Focus on improvement
- Maintain confidentiality

**Don't**:
- Play favorites
- Delay action
- Embarrass publicly
- Hold grudges
- Ignore patterns

### For Members
**Do**:
- Accept responsibility
- Show improvement
- Seek clarification
- Use chain of command
- Learn from mistakes

**Don't**:
- Argue during counseling
- Refuse to sign
- Retaliate
- Spread rumors
- Repeat offenses

## Rehabilitation Focus

### Improvement Plans
**Elements Include**:
- Specific goals
- Timeline set
- Resources provided
- Mentorship assigned
- Progress checkpoints

### Success Indicators
- Behavior changed
- Performance improved
- Attitude positive
- Integration successful
- Leadership potential

### Failure Indicators
- Continued violations
- No improvement
- Negative influence
- Resistance shown
- Impact on unit

## Quality Assurance

### Review Requirements
**Regular Audits**:
- Consistency checks
- Timeline compliance
- Documentation quality
- Rights protection
- Outcome analysis

**Annual Training**:
- Policy updates
- Case studies
- Legal changes
- Best practices
- Scenario exercises

## References
- 2.4.2 Incident Reporting & Investigation Procedure
- 2.1.4 Performance Evaluation Guidelines
- 2.1.7 Separation/Discharge Procedure
- 1.3.8 Delegation of Authority Guidelines''',
                'difficulty_level': 'Advanced',
                'is_required': True,
                'tags': ['discipline', 'counseling', 'progressive', 'misconduct', 'guidelines']
            },
            {
                'document_number': '2.4.2',
                'title': 'Incident Reporting & Investigation Procedure',
                'category': 'Procedure',
                'summary': 'Procedures for reporting incidents and conducting fair, thorough investigations.',
                'content': '''# Incident Reporting & Investigation Procedure

## Purpose
This procedure establishes standardized methods for reporting incidents and conducting investigations within the 5th Expeditionary Group, ensuring prompt response, fair treatment, and accurate documentation of all significant events.

## Scope
Applies to all incidents requiring formal investigation including misconduct allegations, accidents, security breaches, and other events requiring official inquiry and documentation.

## Incident Categories

### Category 1: Minor Incidents
**Definition**: Events with limited impact requiring basic documentation
**Examples**:
- Minor equipment damage
- First-time policy violations
- Minor injuries
- Communication failures
- Training mishaps

**Response Time**: Within 24 hours
**Investigation Level**: Supervisor/Team Leader
**Documentation**: Basic incident report

### Category 2: Significant Incidents
**Definition**: Events requiring formal investigation and command attention
**Examples**:
- Moderate misconduct
- Significant equipment loss
- Security violations
- Discrimination complaints
- Safety violations resulting in injury

**Response Time**: Within 4 hours
**Investigation Level**: Department Head/Officer
**Documentation**: Full investigation package

### Category 3: Critical Incidents
**Definition**: Events with major impact requiring immediate response
**Examples**:
- Serious misconduct/crime
- Major security breach
- Severe injury/death
- Command climate issues
- Media attention likely

**Response Time**: Immediate
**Investigation Level**: Command-directed team
**Documentation**: Comprehensive investigation

## Reporting Procedures

### Step 1: Initial Discovery
1.1. Incident identification:
   - Direct observation
   - Third-party report
   - System alert
   - Routine inspection
   - Anonymous tip

1.2. Immediate actions:
   - Ensure safety
   - Preserve scene
   - Prevent escalation
   - Notify chain of command
   - Begin documentation

1.3. Initial assessment:
   - Determine category
   - Identify involved parties
   - Assess ongoing risk
   - Resource requirements
   - Notification needs

### Step 2: Formal Reporting
2.1. Report submission timeline:
   - Category 1: Within 24 hours
   - Category 2: Within 4 hours
   - Category 3: Within 1 hour

2.2. Initial incident report format:
```
INCIDENT REPORT - INITIAL

Report Number: [Auto-generated]
Date/Time of Incident: [DTG]
Date/Time of Report: [DTG]
Location: [Specific location/channel/platform]

Category: [1/2/3]
Type: [Misconduct/Accident/Security/Other]

Personnel Involved:
- Subject(s): [Name, Rank, Unit]
- Witness(es): [Names and contact]
- Victim(s): [If applicable]

Brief Description:
[Factual summary of what occurred, no opinions]

Immediate Actions Taken:
[List all actions]

Notifications Made:
[Who was notified and when]

Reporting Official: [Name, Rank, Position]
Contact Information: [Phone/Email/Discord]
```

2.3. Distribution requirements:
   - Immediate supervisor
   - Department head
   - Security (if applicable)
   - Personnel office
   - Command (Cat 2/3)

### Step 3: Preservation Requirements
3.1. Evidence preservation:
   - Discord logs/screenshots
   - Email chains
   - Voice recordings
   - Video evidence
   - Physical evidence

3.2. Digital evidence handling:
   - No alteration
   - Time stamps preserved
   - Chain of custody
   - Backup copies
   - Access restricted

3.3. Witness information:
   - Contact details secured
   - Initial statements taken
   - Availability confirmed
   - Bias noted
   - Protection needs assessed

## Investigation Process

### Step 4: Investigation Assignment
4.1. Appointing authority determines:
   - Lead investigator
   - Team composition
   - Timeline requirements
   - Resource allocation
   - Special requirements

4.2. Investigator qualifications:
   - Appropriate rank/experience
   - No conflict of interest
   - Training completed
   - Availability confirmed
   - Objectivity demonstrated

4.3. Investigation team composition:
   - Lead investigator
   - Assistant (if needed)
   - Technical expert
   - Witness interviewer
   - Recorder/administrator

### Step 5: Investigation Planning
5.1. Initial planning meeting:
   - Review incident report
   - Identify key questions
   - Determine witness list
   - Evidence requirements
   - Timeline establishment

5.2. Investigation plan elements:
```
INVESTIGATION PLAN

Incident: [Reference number and brief description]
Lead Investigator: [Name, Rank]
Timeline: [Start date - Completion date]

Key Questions to Answer:
1. What happened?
2. When did it occur?
3. Who was involved?
4. Where did it occur?
5. Why did it happen?
6. How can it be prevented?

Evidence to Collect:
- Documentary: [List]
- Digital: [List]
- Physical: [List]
- Testimonial: [List]

Witness Interview Schedule:
[Name - Date/Time - Location]

Special Considerations:
[Privacy, medical, legal, etc.]
```

5.3. Legal/policy review:
   - Applicable regulations
   - Rights advisement
   - Privacy considerations
   - Union requirements
   - Medical limitations

### Step 6: Evidence Collection
6.1. Documentary evidence:
   - Policies/procedures
   - Training records
   - Performance evaluations
   - Previous incidents
   - Correspondence

6.2. Digital evidence:
   - System logs
   - Communication records
   - Access records
   - Timestamps
   - Metadata

6.3. Physical evidence:
   - Photographs
   - Damaged equipment
   - Scene documentation
   - Medical records
   - Environmental factors

### Step 7: Witness Interviews
7.1. Interview preparation:
   - Question development
   - Rights advisement
   - Recording setup
   - Privacy ensured
   - Support present

7.2. Interview format:
```
WITNESS INTERVIEW RECORD

Date/Time: [DTG]
Location: [Interview location]
Interviewer: [Name, Rank]
Witness: [Name, Rank, Unit]
Others Present: [Names and roles]

Rights Advisement Given: [Yes/No]
Recording Made: [Yes/No]

Questions and Responses:
[Formatted Q&A]

Statement Review:
Witness allowed to review: [Yes/No]
Corrections made: [Yes/No]
Final statement accurate: [Yes/No]

Signatures:
Witness: ________________
Interviewer: ________________
```

7.3. Special interview considerations:
   - Victim sensitivity
   - Subject rights
   - Youth procedures
   - Medical limitations
   - Language barriers

### Step 8: Analysis and Findings
8.1. Evidence analysis:
   - Credibility assessment
   - Corroboration check
   - Timeline construction
   - Pattern identification
   - Gap analysis

8.2. Finding development:
   - Facts established
   - Standards identified
   - Violations determined
   - Causation analyzed
   - Recommendations formed

8.3. Report preparation:
```
INVESTIGATION REPORT OUTLINE

I. Executive Summary
   - Incident overview
   - Key findings
   - Recommendations

II. Investigation Authority
   - Appointing official
   - Investigation team
   - Timeline

III. Background
   - Incident description
   - Initial response
   - Scope of investigation

IV. Methodology
   - Evidence collected
   - Interviews conducted
   - Analysis performed

V. Findings of Fact
   - Chronological narrative
   - Evidence summary
   - Credibility assessments

VI. Analysis
   - Standards applicable
   - Violations identified
   - Contributing factors

VII. Recommendations
   - Disciplinary actions
   - Corrective measures
   - Policy changes
   - Training needs

VIII. Appendices
   - Evidence index
   - Witness statements
   - Supporting documents
```

## Post-Investigation

### Step 9: Report Submission
9.1. Quality review:
   - Completeness check
   - Legal sufficiency
   - Privacy compliance
   - Grammar/formatting
   - Classification review

9.2. Submission package:
   - Executive summary
   - Full report
   - Evidence binder
   - Recommendation memo
   - Distribution list

9.3. Briefing preparation:
   - Key points summary
   - Visual aids
   - Q&A anticipation
   - Decision options
   - Implementation plan

### Step 10: Command Decision
10.1. Decision factors:
   - Investigation findings
   - Credibility determinations
   - Previous precedent
   - Mitigation factors
   - Unit impact

10.2. Decision options:
   - No action warranted
   - Administrative action
   - Disciplinary action
   - System changes
   - Training required

10.3. Implementation:
   - Written decision
   - Notification plan
   - Appeal rights
   - Timeline established
   - Monitoring assigned

## Special Investigation Types

### EO/EEO Investigations
**Additional Requirements**:
- Specialized investigator
- Strict confidentiality
- Interim measures
- Climate assessment
- Prevention focus

### Safety Investigations
**Focus Areas**:
- Root cause analysis
- Prevention measures
- System failures
- Training adequacy
- Equipment factors

### Security Investigations
**Special Handling**:
- Clearance requirements
- Need-to-know limits
- Classified handling
- Counterintelligence
- Damage assessment

## Quality Control

### Investigation Standards
**Required Elements**:
- Thoroughness
- Objectivity
- Timeliness
- Documentation
- Legal sufficiency

**Common Deficiencies**:
- Incomplete interviews
- Missing evidence
- Bias appearance
- Delayed completion
- Poor documentation

### Review Process
**Levels of Review**:
1. Investigator self-check
2. Legal review
3. Command review
4. Higher HQ (if required)
5. External audit

### Lessons Learned
**Capture Methods**:
- After-action reviews
- Trend analysis
- Best practices
- Training updates
- Policy refinement

## Rights and Protections

### Subject Rights
- Notification of allegations
- Representation allowed
- Statement opportunity
- Evidence review (limited)
- Appeal process

### Witness Protections
- Retaliation prohibited
- Confidentiality (when possible)
- Support services
- Limited disclosure
- Immunity (if authorized)

### Victim Rights
- Respectful treatment
- Regular updates
- Support services
- Privacy protection
- Input considered

## Common Issues

### Issue: Delayed Reporting
**Prevention**: Clear requirements, multiple channels
**Mitigation**: Investigate delay, extend timeline

### Issue: Witness Reluctance
**Prevention**: Build trust, ensure protection
**Response**: Alternative evidence, command emphasis

### Issue: Evidence Spoliation
**Prevention**: Immediate preservation, clear policy
**Response**: Document loss, investigate cause

## References
- 2.4.1 Progressive Disciplinary Action Guidelines
- 1.3.10 Civilian Protection Decision Framework
- 7.2.2 Operational Security (OPSEC) Advice
- 2.1.3 Service Record Management Procedure''',
                'difficulty_level': 'Advanced',
                'is_required': True,
                'tags': ['investigation', 'reporting', 'incidents', 'discipline', 'procedure']
            }
        ]

        for data in standards_data:
            standard, created = Standard.objects.get_or_create(
                document_number=data['document_number'],
                defaults={
                    'title': data['title'],
                    'standard_sub_group': subgroup,
                    'content': data['content'],
                    'summary': data['summary'],
                    'version': '1.0',
                    'status': 'Active',
                    'author': user,
                    'approved_by': user,
                    'approval_date': timezone.now(),
                    'effective_date': timezone.now(),
                    'difficulty_level': data['difficulty_level'],
                    'tags': data['tags'],
                    'is_required': data.get('is_required', False)
                }
            )
            if created:
                self.stdout.write(f'  Created: {data["document_number"]} - {data["title"]}')