# backend/apps/standards/management/commands/generate_command_control_sops.py

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.standards.models import StandardGroup, StandardSubGroup, Standard
from apps.users.models import User
from django.utils import timezone


class Command(BaseCommand):
    help = 'Generate Command & Control SOPs (Group 1)'

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

            # Create Command & Control Group
            command_control_group, created = StandardGroup.objects.get_or_create(
                name='Command & Control',
                defaults={
                    'description': 'Standards governing command structure, operational command procedures, and decision-making frameworks within the 5th Expeditionary Group.',
                    'order_index': 1,
                    'is_active': True,
                    'created_by': system_user
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS('Created Command & Control group'))
            else:
                self.stdout.write(self.style.WARNING('Command & Control group already exists'))

            # Create subgroups and their standards
            self._create_command_structure_standards(command_control_group, system_user)
            self._create_operational_command_standards(command_control_group, system_user)
            self._create_decision_making_standards(command_control_group, system_user)

            self.stdout.write(self.style.SUCCESS('Successfully generated all Command & Control SOPs'))

    def _create_command_structure_standards(self, group, user):
        """Create Command Structure subgroup and its standards"""
        subgroup, _ = StandardSubGroup.objects.get_or_create(
            name='Command Structure',
            standard_group=group,
            defaults={
                'description': 'Standards defining organizational hierarchy, authority, and command relationships.',
                'order_index': 1,
                'is_active': True,
                'created_by': user
            }
        )

        standards_data = [
            {
                'document_number': '1.1.1',
                'title': 'Chain of Command Reference',
                'category': 'Information',
                'summary': 'Comprehensive reference guide for the 5EG command hierarchy and reporting structure.',
                'content': '''# Chain of Command Reference

## Purpose
This document provides a comprehensive reference for all personnel regarding the 5th Expeditionary Group's chain of command structure, reporting relationships, and command authorities.

## Command Hierarchy

### Expeditionary Force Level
- **Commander, 5th Expeditionary Group (C5EG)**: Overall command authority
- **Deputy Commander (DC5EG)**: Second in command, assumes command in C5EG absence
- **Chief of Staff (CoS)**: Principal staff officer, coordinates staff activities

### Fleet Level
- **Fleet Admiral**: Commands multiple battle groups within a fleet
- **Vice Admiral**: Deputy fleet commander
- **Fleet Operations Officer**: Manages fleet-wide operations

### Battle Group Level
- **Battle Group Commander (Admiral/Commodore)**: Commands capital ship and escorts
- **Battle Group XO**: Executive officer for battle group operations
- **Battle Group Operations Officer**: Coordinates battle group activities

### Squadron Level
- **Squadron Commander (Captain/Commander)**: Commands 4-12 vessels of similar type
- **Squadron Executive Officer**: Deputy squadron commander
- **Flight Leaders**: Command individual flights within squadron

### Individual Unit Level
- **Ship/Unit Commanding Officer**: Commands individual vessel or ground unit
- **Executive Officer (XO)**: Second in command of unit
- **Department Heads**: Lead specific departments (Operations, Engineering, etc.)

## Reporting Relationships

### Direct Report Structure
1. Individual personnel report to immediate supervisor
2. Department heads report to XO
3. XO reports to Commanding Officer
4. Unit COs report to Squadron/Group Commander
5. Squadron Commanders report to Battle Group Commander
6. Battle Group Commanders report to Fleet Admiral
7. Fleet Admirals report to C5EG

### Staff Relationships
- Staff officers provide advice and coordination but do not exercise command
- Staff sections report to Chief of Staff
- Special staff (Legal, Medical, Chaplain) have direct access to commander

## Command Authority Types

### Command Authority Levels
- **Full Command**: Complete authority over assigned forces
- **Operational Command**: Authority for specific operations
- **Tactical Command**: Authority during combat operations
- **Administrative Command**: Authority over personnel and logistics

### Special Authorities
- **Emergency Command Authority**: Assumption of command during emergencies
- **Acting Command Authority**: Temporary command assignment
- **Direct Liaison Authorized (DIRLAUTH)**: Permission to coordinate directly

## Reference Tables

### Rank Structure Quick Reference
| Branch | Junior Enlisted | NCO | Senior NCO | Junior Officer | Senior Officer | Flag Officer |
|--------|----------------|-----|------------|----------------|----------------|--------------|
| Navy | E1-E3 | E4-E6 | E7-E9 | O1-O3 | O4-O6 | O7-O10 |
| Marines | E1-E3 | E4-E6 | E7-E9 | O1-O3 | O4-O6 | O7-O10 |

### Command Precedence
1. Designated commander
2. Deputy/Executive Officer
3. Senior department head by date of rank
4. Senior officer present by rank/date of rank

## Communication Channels
- **Command Channel**: For orders and directives
- **Staff Channel**: For coordination and information
- **Technical Channel**: For technical matters
- **Emergency Channel**: For urgent matters requiring immediate action

## Additional References
- See 1.1.2 for Succession of Command procedures
- See 1.1.3 for Officer/NCO authority guidelines
- See 1.1.4 for proper forms of address''',
                'difficulty_level': 'Basic',
                'is_required': True,
                'tags': ['command', 'hierarchy', 'reference', 'organization']
            },
            {
                'document_number': '1.1.2',
                'title': 'Succession of Command Procedure',
                'category': 'Procedure',
                'summary': 'Step-by-step procedures for assuming command when primary commander is unavailable.',
                'content': '''# Succession of Command Procedure

## Purpose
This procedure establishes the process for orderly succession of command when the designated commander is unable to exercise command due to absence, incapacitation, or other circumstances.

## Scope
Applies to all command positions within the 5th Expeditionary Group from unit level through expeditionary force level.

## Procedure

### Step 1: Identify Need for Succession
1.1. Determine commander is unable to exercise command due to:
   - Combat casualty
   - Medical incapacitation  
   - Communications loss exceeding 30 minutes
   - Capture or missing in action
   - Administrative absence (leave, TDY)
   - Relief for cause

1.2. Time of succession is logged in unit journal

1.3. Notification sent to higher headquarters

### Step 2: Determine Successor
2.1. Check for designated successor in:
   - Published succession of command memorandum
   - Unit standing orders
   - Higher headquarters directive

2.2. If no designated successor, follow precedence:
   - Deputy/Executive Officer
   - Senior department head (by date of rank)
   - Senior officer present (by rank, then date of rank)
   - Senior NCO (if no officers present)

2.3. Verify successor is qualified:
   - Appropriate security clearance
   - Required training/certification
   - Medical fitness for duty
   - Not under investigation/disciplinary action

### Step 3: Assumption of Command
3.1. Succeeding commander announces assumption via:
   - All-hands announcement
   - Written assumption memorandum
   - Entry in unit journal
   - Notification to higher HQ

3.2. Format for assumption: "I, [RANK NAME], hereby assume command of [UNIT] as of [DATE/TIME]"

3.3. Obtain command authentication codes/materials:
   - Command authorization codes
   - Classified material access
   - Financial signature authority
   - Personnel action authority

### Step 4: Notifications
4.1. Immediate notifications (within 1 hour):
   - Higher headquarters
   - Adjacent units
   - Direct reporting units
   - Key staff members

4.2. Administrative notifications (within 24 hours):
   - Personnel office
   - Finance office
   - Security office
   - Support elements

### Step 5: Command Actions
5.1. Initial actions upon assumption:
   - Review current operations/mission status
   - Confirm DEFCON/alert status
   - Review personnel status
   - Check logistics/maintenance status

5.2. Issue initial guidance:
   - Confirm or modify current orders
   - Establish command priorities
   - Schedule staff briefings
   - Set battle rhythm

### Step 6: Documentation
6.1. Required documentation:
   - Assumption of command memorandum
   - Unit journal entry
   - Personnel action form
   - After-action report (if combat related)

6.2. Distribution:
   - Higher headquarters
   - Personnel records
   - Unit files
   - Historical records

## Special Circumstances

### Combat Succession
- Announcement may be abbreviated: "[RANK NAME] has command"
- Focus on mission continuity
- Full documentation completed when tactical situation permits

### Disputed Succession
- Senior officer present arbitrates
- Contact higher HQ for resolution
- Maintain current operations pending resolution

### Temporary Succession
- Used for absences less than 30 days
- "Acting" designation used
- Limited personnel/financial authorities

## References
- 1.1.1 Chain of Command Reference
- 1.1.3 Officer/NCO Authority Guidelines
- 1.1.5 Temporary Command Assignment Procedure''',
                'difficulty_level': 'Intermediate',
                'is_required': True,
                'tags': ['command', 'succession', 'procedure', 'emergency']
            },
            {
                'document_number': '1.1.3',
                'title': 'Officer/NCO Authority Guidelines',
                'category': 'Guidelines',
                'summary': 'Guidelines defining the authority, responsibilities, and limitations of officers and NCOs.',
                'content': '''# Officer/NCO Authority Guidelines

## Purpose
These guidelines establish the authority, responsibilities, and limitations for commissioned officers and non-commissioned officers within the 5th Expeditionary Group.

## Officer Authority

### Commissioned Officer Authority
Commissioned officers derive authority from their commission and assignment. This authority includes:

**Command Authority**
- Exercise command over assigned personnel
- Issue lawful orders to subordinates
- Enforce standards and discipline
- Make operational decisions within scope

**Administrative Authority**
- Approve leave and passes (within limits)
- Initiate personnel actions
- Authorize expenditures (within limits)
- Sign official correspondence

**Operational Authority**
- Plan and direct operations
- Allocate resources
- Modify tactical procedures
- Authorize weapons release (when designated)

### Officer Limitations
- Cannot override lawful orders from superiors
- Must operate within rules of engagement
- Cannot exceed financial authority limits
- Must respect NCO authority over enlisted matters

## NCO Authority

### Non-Commissioned Officer Authority
NCOs serve as the primary link between officers and enlisted personnel.

**Leadership Authority**
- Direct supervision of enlisted personnel
- Enforce standards and regulations
- Conduct training and mentorship
- Maintain discipline and order

**Technical Authority**
- Serve as subject matter experts
- Oversee technical task execution
- Certify personnel qualifications
- Maintain equipment readiness

**Advisory Authority**
- Advise officers on enlisted matters
- Recommend personnel actions
- Provide ground truth assessment
- Influence command decisions

### NCO Limitations
- Cannot assume command unless no officers present
- Cannot countermand officer orders
- Must channel concerns through chain of command
- Cannot authorize policy changes

## Shared Responsibilities

### Both Officers and NCOs Must:
- Maintain good order and discipline
- Ensure welfare of subordinates
- Uphold standards and traditions
- Foster professional development
- Maintain operational readiness

### Professional Relationships
**Officer-NCO Relationship Guidelines:**
- Mutual respect required
- Open communication encouraged
- Disagreements handled privately
- Unity of command presented publicly
- Professional boundaries maintained

**Division of Responsibilities:**
- Officers: "What" and "Why"
- NCOs: "How" and "When"
- Shared: Standards enforcement

## Authority in Special Situations

### Emergency Authority
When normal command is disrupted:
- Senior person present assumes control
- Life safety takes precedence
- Document actions taken
- Restore normal command ASAP

### Acting Authority
When assigned acting positions:
- Authority limited to essential functions
- Major decisions deferred when possible
- Cannot make permanent personnel actions
- Document all significant decisions

### Cross-Branch Authority
When working with other service branches:
- Rank equivalency applies
- Home unit policies prevail
- Coordinate through liaison officers
- Respect service traditions

## Guidelines for Exercise of Authority

### Best Practices
1. **Lead by Example**
   - Maintain highest standards
   - Display professional conduct
   - Show technical competence
   - Demonstrate moral courage

2. **Communicate Clearly**
   - Issue clear, concise orders
   - Explain intent when possible
   - Confirm understanding
   - Provide feedback

3. **Develop Subordinates**
   - Delegate appropriately
   - Allow learning from mistakes
   - Provide mentorship
   - Recognize achievements

4. **Maintain Perspective**
   - Consider second/third order effects
   - Seek input from others
   - Balance mission and personnel
   - Admit and correct errors

### Common Pitfalls to Avoid
- Micromanagement
- Favoritism
- Abuse of authority
- Failure to delegate
- Ignoring NCO input
- Bypassing chain of command

## Accountability

### Officers Accountable For:
- Command decisions
- Mission accomplishment
- Personnel welfare
- Resource management
- Policy compliance

### NCOs Accountable For:
- Enlisted performance
- Training standards
- Equipment maintenance
- Discipline enforcement
- Technical proficiency

## References
- 1.1.1 Chain of Command Reference
- 1.1.4 Rank Recognition & Address Information
- 2.4.1 Progressive Disciplinary Action Guidelines''',
                'difficulty_level': 'Intermediate',
                'is_required': True,
                'tags': ['authority', 'leadership', 'officers', 'NCOs', 'guidelines']
            },
            {
                'document_number': '1.1.4',
                'title': 'Rank Recognition & Address Information',
                'category': 'Information',
                'summary': 'Information guide for identifying ranks and proper forms of address across all branches.',
                'content': '''# Rank Recognition & Address Information

## Purpose
This document provides comprehensive information for recognizing ranks and using proper forms of address within the 5th Expeditionary Group across all service branches.

## Navy Ranks and Address

### Enlisted Ranks
| Rank | Abbreviation | Insignia Description | Proper Address |
|------|--------------|---------------------|----------------|
| Starman Recruit | SR | No insignia | "Recruit" or "Starman" |
| Starman Apprentice | SA | Two diagonal stripes | "Starman" |
| Starman | SN | Three diagonal stripes | "Starman" |
| Petty Officer 3rd Class | PO3 | Eagle with one chevron | "Petty Officer [Name]" |
| Petty Officer 2nd Class | PO2 | Eagle with two chevrons | "Petty Officer [Name]" |
| Petty Officer 1st Class | PO1 | Eagle with three chevrons | "Petty Officer [Name]" |
| Chief Petty Officer | CPO | Eagle with three chevrons, one rocker | "Chief [Name]" |
| Senior Chief Petty Officer | SCPO | Eagle with three chevrons, two rockers | "Senior Chief [Name]" |
| Master Chief Petty Officer | MCPO | Eagle with three chevrons, three rockers | "Master Chief [Name]" |

### Officer Ranks
| Rank | Abbreviation | Insignia Description | Proper Address |
|------|--------------|---------------------|----------------|
| Ensign | ENS | One gold bar | "Ensign [Name]" or "Sir/Ma'am" |
| Lieutenant Junior Grade | LTJG | One silver bar | "Lieutenant [Name]" or "Sir/Ma'am" |
| Lieutenant | LT | Two silver bars | "Lieutenant [Name]" or "Sir/Ma'am" |
| Lieutenant Commander | LCDR | Gold oak leaf | "Commander [Name]" or "Sir/Ma'am" |
| Commander | CDR | Silver oak leaf | "Commander [Name]" or "Sir/Ma'am" |
| Captain | CAPT | Eagle | "Captain [Name]" or "Sir/Ma'am" |
| Rear Admiral (lower) | RDML | One star | "Admiral [Name]" or "Sir/Ma'am" |
| Rear Admiral (upper) | RADM | Two stars | "Admiral [Name]" or "Sir/Ma'am" |
| Vice Admiral | VADM | Three stars | "Admiral [Name]" or "Sir/Ma'am" |
| Admiral | ADM | Four stars | "Admiral [Name]" or "Sir/Ma'am" |

## Marine Ranks and Address

### Enlisted Ranks
| Rank | Abbreviation | Insignia Description | Proper Address |
|------|--------------|---------------------|----------------|
| Private | Pvt | No insignia | "Private [Name]" |
| Private First Class | PFC | One chevron | "Private [Name]" |
| Lance Corporal | LCpl | One chevron, crossed rifles | "Lance Corporal [Name]" |
| Corporal | Cpl | Two chevrons | "Corporal [Name]" |
| Sergeant | Sgt | Three chevrons | "Sergeant [Name]" |
| Staff Sergeant | SSgt | Three chevrons, one rocker | "Staff Sergeant [Name]" |
| Gunnery Sergeant | GySgt | Three chevrons, two rockers | "Gunny" or "Gunnery Sergeant [Name]" |
| Master Sergeant | MSgt | Three chevrons, three rockers | "Master Sergeant [Name]" |
| First Sergeant | 1stSgt | Three chevrons, three rockers, diamond | "First Sergeant [Name]" |
| Master Gunnery Sergeant | MGySgt | Three chevrons, four rockers | "Master Guns" or "Master Gunnery Sergeant [Name]" |
| Sergeant Major | SgtMaj | Three chevrons, four rockers, star | "Sergeant Major [Name]" |

### Officer Ranks
| Rank | Abbreviation | Insignia Description | Proper Address |
|------|--------------|---------------------|----------------|
| Second Lieutenant | 2ndLt | One gold bar | "Lieutenant [Name]" or "Sir/Ma'am" |
| First Lieutenant | 1stLt | One silver bar | "Lieutenant [Name]" or "Sir/Ma'am" |
| Captain | Capt | Two silver bars | "Captain [Name]" or "Sir/Ma'am" |
| Major | Maj | Gold oak leaf | "Major [Name]" or "Sir/Ma'am" |
| Lieutenant Colonel | LtCol | Silver oak leaf | "Colonel [Name]" or "Sir/Ma'am" |
| Colonel | Col | Eagle | "Colonel [Name]" or "Sir/Ma'am" |
| Brigadier General | BGen | One star | "General [Name]" or "Sir/Ma'am" |
| Major General | MajGen | Two stars | "General [Name]" or "Sir/Ma'am" |
| Lieutenant General | LtGen | Three stars | "General [Name]" or "Sir/Ma'am" |
| General | Gen | Four stars | "General [Name]" or "Sir/Ma'am" |

## Forms of Address Guidelines

### General Rules
1. **First Contact**: Use full rank and last name
2. **Subsequent Contact**: May use shortened form
3. **Formal Settings**: Always use full rank
4. **Combat Operations**: May use position titles

### Special Situations

**Senior NCOs**
- Navy Chiefs addressed as "Chief" regardless of level
- Marine Gunnery Sergeants may be called "Gunny"
- First Sergeants and Sergeants Major by full title

**Medical Personnel**
- Doctors addressed as "Doctor" or by rank
- Corpsmen/Medics may be called "Doc" informally

**Warrant Officers**
- Addressed as "Chief" or "Mister/Miss [Name]"
- CW4 and CW5 addressed as "Chief"

**Retired Personnel**
- May use rank if retired honorably
- Indicated as "[Rank], Retired" in writing

### Written Communication

**Formal Letters**
- Opening: "Dear [Rank] [Last Name]:"
- Closing: "Respectfully," or "Very respectfully,"

**Email**
- Subject line rank abbreviations acceptable
- Body text use full rank first time

**Reports**
- First reference: Full rank and name
- Subsequent: Last name or position

### Cultural Considerations

**Cross-Branch Interactions**
- Use home service traditions
- When in doubt, err on formal side
- Respect service-specific customs

**International Forces**
- Research allied rank structures
- Use NATO rank equivalents when applicable
- Default to "Sir/Ma'am" if uncertain

## Common Mistakes to Avoid

1. **Never**:
   - Address officers by last name alone
   - Use first names on duty
   - Skip "Sir/Ma'am" responses
   - Assume familiarity

2. **Always**:
   - Err on side of formality
   - Use proper titles
   - Stand when addressing seniors
   - Maintain military bearing

## Quick Reference Cards

### Navy Quick Salute Guide
- Officers: All commissioned officers
- Warrant Officers: Yes
- Enlisted: E7 and above in command positions

### Marine Quick Salute Guide  
- Officers: All commissioned officers
- Warrant Officers: Yes
- Enlisted: Never (unless in command)

## References
- 1.1.1 Chain of Command Reference
- 1.1.3 Officer/NCO Authority Guidelines
- 9.1.1 Military Customs Information''',
                'difficulty_level': 'Basic',
                'is_required': True,
                'tags': ['ranks', 'protocol', 'address', 'recognition', 'etiquette']
            },
            {
                'document_number': '1.1.5',
                'title': 'Temporary Command Assignment Procedure',
                'category': 'Procedure',
                'summary': 'Procedures for temporarily assigning command authority for short-term absences.',
                'content': '''# Temporary Command Assignment Procedure

## Purpose
This procedure establishes the process for temporarily assigning command authority during short-term absences of the primary commander, ensuring continuity of operations without permanent change of command.

## Scope
Applies to temporary absences of 30 days or less. Absences exceeding 30 days require succession of command procedures (see 1.1.2).

## Procedure

### Step 1: Determine Need for Temporary Assignment
1.1. Identify qualifying absence:
   - Scheduled leave (personal, medical, emergency)
   - Temporary duty (TDY) assignment
   - Training or schools
   - Medical procedures (outpatient)
   - Administrative requirements

1.2. Calculate absence duration:
   - Start date and time
   - Expected return date and time
   - Include travel time if applicable

1.3. Assess operational requirements:
   - Scheduled operations during absence
   - Critical decisions pending
   - Key events or inspections
   - Personnel actions required

### Step 2: Select Acting Commander
2.1. Primary selection criteria:
   - Current deputy/executive officer
   - Senior department head
   - Officer with relevant experience
   - Previously successful acting commander

2.2. Verify availability:
   - No conflicting absences
   - Medically fit for duty
   - No pending disciplinary actions
   - Appropriate security clearance

2.3. Assess qualifications:
   - Familiar with current operations
   - Completed required training
   - Previous command experience (preferred)
   - Good standing with higher HQ

### Step 3: Define Acting Authority Limits
3.1. Authorized actions:
   - Maintain current operations
   - Emergency response decisions
   - Routine personnel actions
   - Time-sensitive operational decisions

3.2. Restricted actions (require consultation):
   - Major policy changes
   - Permanent personnel assignments
   - Significant resource reallocation
   - Non-routine disciplinary actions

3.3. Prohibited actions:
   - Permanent change of station orders
   - Relief for cause actions
   - Major equipment disposition
   - Policy changes affecting other units

### Step 4: Prepare Assignment Documentation
4.1. Temporary Command Memorandum includes:
   - Acting commander designation
   - Effective dates and times
   - Authority limitations
   - Special instructions
   - Contact information for commander

4.2. Required attachments:
   - Current operation orders
   - Pending actions list
   - Key points of contact
   - Decision criteria guidance

4.3. Distribution list:
   - Acting commander
   - Higher headquarters
   - All department heads
   - Key staff sections
   - Administrative offices

### Step 5: Conduct Turnover Brief
5.1. Operations brief covering:
   - Current mission status
   - Personnel readiness
   - Equipment status
   - Scheduled events
   - Open issues/concerns

5.2. Administrative brief covering:
   - Pending personnel actions
   - Financial obligations
   - Correspondence requiring action
   - Scheduled meetings/calls
   - Access codes/passwords

5.3. Emergency procedures review:
   - Alert notification procedures
   - Emergency contact numbers
   - Classified material access
   - Decision thresholds
   - Higher HQ expectations

### Step 6: Execute Transfer of Authority
6.1. Formal announcement:
   - All-hands email/message
   - Posted memorandum
   - Staff notification
   - Log entry

6.2. Sample announcement:
   "Effective [DATE/TIME], [RANK NAME] is designated Acting Commanding Officer of [UNIT] until [DATE/TIME]. All personnel will accord [him/her] the respect and obedience due to that position."

6.3. Authority transfer items:
   - Command seal/stamp
   - Signature authority cards
   - Classified access badges
   - Command phone/radio
   - Emergency action codes

### Step 7: Maintain Communications
7.1. Commander check-in requirements:
   - Initial safe arrival confirmation
   - Daily SITREP review (if required)
   - On-call availability for major decisions
   - Emergency contact protocol

7.2. Acting commander reporting:
   - Daily activity summary
   - Significant events notification
   - Decision log maintenance
   - Issues requiring guidance

### Step 8: Resume Command
8.1. Return notification:
   - 24-hour advance notice (when possible)
   - Confirm return date/time
   - Schedule resumption brief

8.2. Resumption brief covers:
   - Actions taken during absence
   - Decisions made
   - Issues requiring attention
   - Personnel changes
   - Lessons learned

8.3. Formal resumption:
   - Announcement to unit
   - Return of authority items
   - Administrative notifications
   - Thank acting commander

## Special Considerations

### Extended Absence Procedures
If absence extends beyond planned:
- Notify higher HQ immediately
- Reassess acting commander availability
- Consider succession of command
- Document extension reasons

### Multiple Simultaneous Absences
When commander and deputy both absent:
- Higher HQ approval required
- Enhanced reporting requirements
- Consider delaying one absence
- Detailed continuity plan required

### Emergency Recall Procedures
Commander may be recalled for:
- Combat operations
- Major casualties
- Significant disciplinary issues
- Higher HQ directive

## Forms and Templates

### Temporary Command Memorandum Template
```
MEMORANDUM FOR RECORD

SUBJECT: Temporary Command Assignment - [UNIT]

1. Effective [DATE/TIME], [RANK NAME] is designated Acting Commanding Officer of [UNIT].

2. This assignment will remain in effect until [DATE/TIME] or until properly relieved.

3. Authority limitations: [SPECIFY]

4. Points of contact: [LIST]

[SIGNATURE BLOCK]
```

## References
- 1.1.2 Succession of Command Procedure
- 1.1.3 Officer/NCO Authority Guidelines
- 1.2.1 Fleet Command Procedure''',
                'difficulty_level': 'Intermediate',
                'is_required': False,
                'tags': ['command', 'temporary', 'acting', 'procedure', 'assignment']
            },
            {
                'document_number': '1.1.6',
                'title': 'Multi-Unit Command Coordination Guidelines',
                'category': 'Guidelines',
                'summary': 'Guidelines for coordinating command between multiple units during joint operations.',
                'content': '''# Multi-Unit Command Coordination Guidelines

## Purpose
These guidelines establish procedures for coordinating command and control when multiple units operate together, ensuring unity of effort while maintaining unit integrity and chain of command.

## Principles of Multi-Unit Operations

### Unity of Command
- Single commander designated for operation
- Clear command relationships established
- All units understand reporting structure
- Conflicting orders resolved at lowest level

### Unity of Effort
- Common operational objectives
- Synchronized planning process
- Shared intelligence and resources
- Coordinated communications plan

### Mutual Support
- Units positioned to support each other
- Shared logistics when appropriate
- Cross-unit medical support
- Combined defensive measures

## Command Relationship Types

### Operational Control (OPCON)
**Definition**: Authority to direct forces for specific missions

**Includes**:
- Task organization authority
- Mission assignment
- Tactical control
- Local security directives

**Excludes**:
- Administrative control
- Logistic responsibilities
- Permanent reassignment
- Disciplinary authority

### Tactical Control (TACON)
**Definition**: Limited control for tactical movement and maneuver

**Includes**:
- Local direction of movements
- Tactical positioning
- Immediate mission tasking

**Excludes**:
- Task organization changes
- Administrative functions
- Long-term planning authority

### Support Relationships
**Direct Support**: Unit provides support to specific unit
**General Support**: Unit supports overall operation
**Reinforcing**: Unit supports another supporting unit
**Mutual Support**: Units support each other as needed

## Establishing Multi-Unit Command

### Pre-Operation Planning
1. **Command Structure Determination**
   - Identify senior commander
   - Define command relationships
   - Establish support priorities
   - Create liaison requirements

2. **Communications Architecture**
   - Primary command frequency
   - Unit internal frequencies
   - Emergency frequencies
   - Data link assignments

3. **Operating Area Assignment**
   - Geographic boundaries
   - Overlapping fire zones
   - Movement corridors
   - No-fire areas

### Liaison Officer Requirements
**Selection Criteria**:
- Appropriate rank for level
- Operations experience
- Communication skills
- Cultural awareness

**Equipment Requirements**:
- Compatible communications
- Appropriate credentials
- Transportation means
- Survival equipment

**Responsibilities**:
- Represent commander's intent
- Facilitate coordination
- Resolve conflicts locally
- Provide unit updates

## Operational Coordination

### Battle Rhythm Synchronization
- Align planning cycles
- Coordinate briefing times
- Synchronize reporting
- Share intelligence products

### Resource Sharing Protocols
**Ammunition**:
- Emergency resupply only
- Track cross-leveling
- Maintain accountability
- Report to higher HQ

**Fuel**:
- Establish transfer procedures
- Document all transfers
- Emergency authorization levels
- Environmental precautions

**Medical**:
- Triage priorities
- Evacuation coordination
- Medical supply sharing
- Record keeping requirements

### Fire Support Coordination
**Coordination Measures**:
- Fire support coordination line (FSCL)
- Restricted fire areas (RFA)
- No-fire areas (NFA)
- Coordinated fire lines (CFL)

**Clearance Procedures**:
- Check fire protocols
- Friendly force tracking
- Civilian considerations
- Environmental restrictions

## Communication Protocols

### Standard Report Formats
**SITREP (Situation Report)**:
- Unit identification
- Current location/status
- Enemy contact
- Logistics status
- Planned movements

**SPOTREP (Spot Report)**:
- Size of enemy
- Activity observed
- Location (grid)
- Unit identification
- Time observed
- Equipment noted

### Inter-Unit Coordination Nets
**Command Net**: Senior commander to unit commanders
**Operations Net**: Operations centers coordination
**Intelligence Net**: Intelligence sharing
**Logistics Net**: Supply and maintenance
**Fire Support Net**: Artillery and air support

### Emergency Communications
- Lost communications procedures
- Authentication protocols
- Relay responsibilities
- Backup frequency plan

## Conflict Resolution

### Tactical Conflicts
**Resolution Process**:
1. Attempt resolution at lowest level
2. Involve liaison officers
3. Elevate to operations centers
4. Commander-to-commander discussion
5. Higher headquarters arbitration

**Common Conflicts**:
- Boundary disputes
- Resource allocation
- Priority of fires
- Movement conflicts

### Administrative Conflicts
- Different service regulations
- Discipline procedures
- Award recommendations
- Leave policies

## Special Situations

### Multinational Operations
**Additional Considerations**:
- Language barriers
- Equipment compatibility
- Cultural sensitivities
- National restrictions
- Rules of engagement differences

### Joint Service Operations
**Service-Specific Issues**:
- Rank equivalency
- Communication procedures
- Tactical differences
- Equipment compatibility
- Doctrine variations

### Emergency Command Transition
**When Senior Commander Casualty**:
- Pre-designated successor assumes command
- All units notified immediately
- Mission continues without pause
- Higher HQ notified ASAP

## Best Practices

### Planning Phase
- Include all units early
- Share intelligence freely
- Develop contingencies together
- Practice communication procedures

### Execution Phase
- Maintain liaison presence
- Regular coordination meetings
- Proactive information sharing
- Rapid issue resolution

### Post-Operation
- Combined after-action review
- Share lessons learned
- Update procedures
- Maintain relationships

## Common Pitfalls

### To Avoid
- Assuming understanding
- Withholding information
- Bypassing liaison officers
- Changing plans without coordination
- Ignoring unit capabilities/limitations

### Warning Signs
- Decreased communication
- Unilateral decisions
- Resource hoarding
- Boundary violations
- Mission creep

## References
- 1.2.1 Fleet Command Procedure
- 1.2.3 Task Force Assembly Procedure
- 3.1.1 Operation Development & Approval Procedure
- 7.1.1 Radio Discipline & Brevity Codes''',
                'difficulty_level': 'Advanced',
                'is_required': False,
                'tags': ['joint operations', 'coordination', 'multi-unit', 'command', 'guidelines']
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

    def _create_operational_command_standards(self, group, user):
        """Create Operational Command subgroup and its standards"""
        subgroup, _ = StandardSubGroup.objects.get_or_create(
            name='Operational Command',
            standard_group=group,
            defaults={
                'description': 'Procedures for fleet, battle group, and task force command operations.',
                'order_index': 2,
                'is_active': True,
                'created_by': user
            }
        )

        standards_data = [
            {
                'document_number': '1.2.1',
                'title': 'Fleet Command Procedure',
                'category': 'Procedure',
                'summary': 'Comprehensive procedures for commanding fleet-level operations.',
                'content': '''# Fleet Command Procedure

## Purpose
This procedure establishes standardized methods for commanding fleet-level operations within the 5th Expeditionary Group, encompassing multiple battle groups operating across star systems.

## Scope
Applies to all fleet-level operations involving two or more battle groups operating under unified command.

## Pre-Command Procedures

### Step 1: Fleet Activation
1.1. Receive fleet activation order from Expeditionary Force Command
1.2. Verify authentication codes and mission parameters
1.3. Review assigned forces and readiness status
1.4. Establish Fleet Command Center (FCC)

### Step 2: Fleet Organization
2.1. Designate fleet flagship
   - Assess C4I capabilities
   - Verify communication suites
   - Confirm battle management systems
   - Ensure command space availability

2.2. Assign battle group roles:
   - Strike Group Alpha (primary offensive)
   - Support Group Bravo (logistics/support)
   - Reserve Group Charlie (strategic reserve)
   - Screen Group Delta (defensive screen)

2.3. Establish command structure:
   - Fleet Admiral (commanding)
   - Vice Admiral (deputy)
   - Fleet Operations Officer
   - Fleet Intelligence Officer
   - Fleet Logistics Officer

### Step 3: Mission Analysis
3.1. Analyze strategic objectives
3.2. Assess threat environment
3.3. Determine force requirements
3.4. Identify critical vulnerabilities
3.5. Establish success criteria

## Fleet Command Execution

### Step 4: Operational Planning
4.1. Develop fleet operation order:
   - Situation assessment
   - Mission statement
   - Execution concept
   - Task organization
   - Coordinating instructions

4.2. Create synchronization matrix:
   - Movement timelines
   - Engagement sequences
   - Support requirements
   - Communication windows
   - Logistics flows

4.3. Establish decision points:
   - Go/no-go criteria
   - Branch plan triggers
   - Abort conditions
   - Success indicators

### Step 5: Force Deployment
5.1. Issue deployment orders:
   - Quantum jump coordinates
   - Formation requirements
   - Arrival synchronization
   - Contingency locations

5.2. Monitor deployment status:
   - Track quantum signatures
   - Confirm arrivals
   - Assess formation integrity
   - Verify communications

5.3. Establish operational geometry:
   - Battle group positioning
   - Mutual support distances
   - Escape vectors
   - Logistics corridors

### Step 6: Battle Management
6.1. Maintain tactical picture:
   - Sensor data fusion
   - Track correlation
   - Threat assessment
   - Blue force tracking

6.2. Direct engagements:
   - Weapons release authority
   - Target prioritization
   - Force allocation
   - Damage assessment

6.3. Coordinate support:
   - Fighter coverage
   - Electronic warfare
   - Logistics flow
   - Medical evacuation

### Step 7: Communication Management
7.1. Primary command net:
   - Fleet Admiral to Battle Group Commanders
   - Encrypted quantum-burst capable
   - Authentication protocols
   - Jamming resistant

7.2. Secondary nets:
   - Operations coordination
   - Intelligence sharing
   - Logistics management
   - Emergency communications

7.3. Emission control (EMCON):
   - EMCON levels by phase
   - Silent running protocols
   - Emergency break criteria
   - Deception measures

## Fleet Maneuver Procedures

### Standard Fleet Formations

**Line Ahead Formation**
- Maximum forward firepower
- Vulnerable flanks
- Good for pursuit/retreat
- Simple communication

**Line Abreast Formation**
- Broad sensor coverage
- Mutual support capability
- Complex coordination
- Good for search operations

**Defensive Sphere**
- 360-degree coverage
- Mutual support maximized
- Reduced mobility
- Best for static defense

**Diamond Formation**
- Balanced offense/defense
- Good maneuverability
- Moderate complexity
- Standard cruising formation

### Fleet Maneuver Commands
- "Execute Wheel Right/Left [degrees]" - Coordinated turn
- "Execute Inverse" - 180-degree reversal
- "Execute Scatter" - Evasive dispersal
- "Execute Rally [location]" - Reform at point

## Contingency Procedures

### Loss of Communications
1. Continue last orders for 15 minutes
2. Switch to backup frequency plan
3. Deploy courier shuttles
4. Execute pre-planned contingency
5. Attempt rally at designated point

### Fleet Commander Casualty
1. Deputy assumes command immediately
2. Transfer flag to alternate ship if needed
3. Notify all battle groups
4. Continue current operation
5. Report to higher headquarters

### Catastrophic Losses
- 25% losses: Consider tactical withdrawal
- 40% losses: Execute fighting retreat
- 50% losses: Scatter and escape
- 60% losses: Individual unit survival

## Post-Operation Procedures

### Mission Termination
1. Cease offensive operations
2. Consolidate forces
3. Assess damage/casualties
4. Secure operational area
5. Begin recovery operations

### Fleet Deactivation
1. Transfer forces to home commands
2. Submit after-action report
3. Archive operational records
4. Conduct lessons learned
5. Release fleet designation

## Command Tools and Systems

### Fleet Command Systems
- Strategic Operations Display (SOD)
- Tactical Action Console (TAC)
- Fleet Intelligence Terminal (FIT)
- Logistics Management System (LMS)

### Decision Support Tools
- Threat evaluation matrix
- Force allocation model
- Damage prediction algorithm
- Course of action analysis

## References
- 1.1.1 Chain of Command Reference
- 1.2.2 Battle Group Organization Guidelines
- 3.3.4 Assault Operation Planning & Execution
- 5.2.1 Fleet Formation Guidelines''',
                'difficulty_level': 'Advanced',
                'is_required': True,
                'tags': ['fleet', 'command', 'procedure', 'operations', 'advanced']
            },
            {
                'document_number': '1.2.2',
                'title': 'Battle Group Organization Guidelines',
                'category': 'Guidelines',
                'summary': 'Guidelines for organizing and structuring battle groups for various mission types.',
                'content': '''# Battle Group Organization Guidelines

## Purpose
These guidelines provide flexible frameworks for organizing battle groups within the 5th Expeditionary Group, optimizing force composition for mission success while maintaining operational flexibility.

## Battle Group Fundamentals

### Core Composition
Every battle group requires:
- Command element (flagship)
- Strike element (offensive capability)
- Screen element (defensive capability)
- Support element (logistics/maintenance)

### Command Structure
- Battle Group Commander (Admiral/Commodore)
- Deputy Commander/Chief of Staff
- Operations Officer (N3)
- Intelligence Officer (N2)
- Logistics Officer (N4)
- Communications Officer (N6)

## Standard Battle Group Types

### Strike Battle Group
**Primary Mission**: Offensive operations against enemy forces

**Typical Composition**:
- 1 Javelin-class destroyer (flagship)
- 2-3 Idris-class frigates
- 4-6 Hammerhead escorts
- 2 Polaris torpedo corvettes
- 1 Carrack support vessel
- 12-24 fighters/bombers

**Characteristics**:
- High offensive firepower
- Limited sustainability
- Rapid deployment capable
- Vulnerable to attrition

### Carrier Battle Group
**Primary Mission**: Fighter operations and area control

**Typical Composition**:
- 1 Bengal-class carrier (flagship)
- 2 Javelin destroyers
- 4 Idris frigates
- 6-8 Hammerhead escorts
- 2 Starfarer tankers
- 48-72 fighters

**Characteristics**:
- Fighter superiority focus
- Extended operational reach
- High logistics requirements
- Strategic asset protection needed

### Patrol Battle Group
**Primary Mission**: Area security and reconnaissance

**Typical Composition**:
- 1 Idris frigate (flagship)
- 3-4 Hammerhead gunships
- 6-8 Redeemer gunships
- 2 Terrapin scouts
- 1 Starfarer support
- 12-18 fighters

**Characteristics**:
- Wide area coverage
- Rapid response capability
- Lower logistics footprint
- Limited heavy engagement ability

### Assault Battle Group
**Primary Mission**: Planetary/station assault operations

**Typical Composition**:
- 1 Javelin destroyer (flagship)
- 2 Idris frigates
- 4 Retaliator bombers
- 6 Vanguard Hoplites
- 2 Valkyrie dropships
- Marine contingent (200+)

**Characteristics**:
- Marine transport capability
- Orbital bombardment assets
- Close air support elements
- Boarding specialists included

## Task Organization Guidelines

### Mission-Based Organization
**Reconnaissance in Force**:
- Emphasize scouts and EW assets
- Minimize logistics tail
- Include extraction capability
- Fast response elements

**Commerce Protection**:
- Distributed patrol elements
- Quick reaction force
- Cargo scanning capability
- Escort coordination

**Fleet Engagement**:
- Maximum firepower forward
- Layered defensive screens
- Reserve striking force
- Damage control emphasis

### Threat-Based Organization
**Vanduul Opposition**:
- Fighter-heavy composition
- Point defense emphasis
- High ammunition reserves
- Ramming countermeasures

**Pirate Suppression**:
- Fast patrol craft
- Boarding specialists
- Non-lethal options
- Intelligence gathering focus

**Peer Adversary**:
- Combined arms approach
- Electronic warfare assets
- Redundant command elements
- Sustained combat capability

## Force Integration Considerations

### Multi-Species Operations
When integrating allied forces:
- Account for communication differences
- Respect tactical preferences
- Establish clear boundaries
- Plan for logistics incompatibilities

### Auxiliary Forces
**Militia Integration**:
- Assign defensive sectors
- Provide liaison officers
- Simplified communication
- Clear ROE definition

**Contractor Support**:
- Define support limits
- Establish security procedures
- Verify capabilities
- Monitor performance

## Command and Control Architecture

### Flagship Selection Criteria
1. **C4I Capabilities**
   - Advanced sensor suites
   - Redundant communication
   - Battle management systems
   - Staff accommodation

2. **Survivability**
   - Heavy armor/shields
   - Damage control systems
   - Escape pod capacity
   - Secondary command center

3. **Operational Reach**
   - Quantum fuel capacity
   - Hangar facilities
   - Maintenance capability
   - Medical facilities

### Span of Control
**Optimal Ratios**:
- 1 commander to 3-5 major units
- 1 coordinator per warfare area
- 1 liaison per attached unit
- 1 watch team per 8-hour period

## Formation Guidelines

### Standard Formations

**Defensive Screen**
- Escorts 10-15km from capital ships
- Overlapping weapons coverage
- Multiple defensive layers
- Clear fire lanes

**Strike Formation**
- Concentrated firepower axis
- Mutual support distance
- Reserve positioning
- Rapid deployment capability

**Cruise Formation**
- Fuel efficiency spacing
- Sensor coverage optimization
- Quick transition capability
- Communication reliability

### Special Circumstances

**Quantum Travel Formation**
- Synchronized jump timing
- Arrival dispersion pattern
- Rally point designation
- Abort procedures

**Nebula Operations**
- Tightened formations
- Visual contact maintenance
- Enhanced electronic linking
- Buddy system implementation

## Logistics Considerations

### Sustainability Planning
**30-Day Operations**:
- 40% combat loadout
- 30% fuel reserves
- 20% maintenance supplies
- 10% emergency reserves

**Extended Operations**:
- Underway replenishment
- Forward supply caches
- Salvage operations
- Local procurement

### Support Ship Allocation
- 1 tanker per 6 combat ships
- 1 repair ship per battle group
- 1 medical ship per 1000 personnel
- 1 ammunition ship per strike group

## Battle Group Effectiveness Metrics

### Combat Readiness
- 90% operational availability
- 48-hour deployment capability
- 72-hour sustained operations
- 7-day independent operations

### Training Standards
- Monthly group exercises
- Quarterly fleet operations
- Semi-annual inspections
- Annual certification

## Adaptation Guidelines

### Scaling Procedures
**Reinforcement**:
- Integrate by capability
- Maintain command unity
- Adjust support accordingly
- Update communication plan

**Reduction**:
- Prioritize core capabilities
- Consolidate similar units
- Maintain balance
- Preserve command structure

### Emergency Reorganization
When suffering casualties:
1. Consolidate similar ships
2. Redistribute fighters
3. Prioritize flagship protection
4. Maintain screen integrity
5. Adjust mission parameters

## References
- 1.2.1 Fleet Command Procedure
- 1.2.3 Task Force Assembly Procedure
- 3.1.3 Slot Assignment & Reservation System
- 5.2.2 Defensive Screen Positioning Procedure''',
                'difficulty_level': 'Advanced',
                'is_required': True,
                'tags': ['battle group', 'organization', 'guidelines', 'fleet', 'composition']
            },
            {
                'document_number': '1.2.3',
                'title': 'Task Force Assembly Procedure',
                'category': 'Procedure',
                'summary': 'Step-by-step procedure for assembling task forces for specific mission requirements.',
                'content': '''# Task Force Assembly Procedure

## Purpose
This procedure outlines the systematic process for assembling task forces from available units to accomplish specific missions requiring tailored force composition.

## Scope
Applies to all task force formations smaller than battle groups but larger than individual squadrons, typically 4-8 vessels with specific mission focus.

## Procedure

### Step 1: Mission Analysis
1.1. Receive tasking order
   - Verify authentication
   - Confirm mission parameters
   - Identify constraints/restraints
   - Note timeline requirements

1.2. Define mission requirements:
   - Primary objectives
   - Secondary objectives
   - Success criteria
   - Acceptable risk level
   - Duration estimate

1.3. Analyze operational environment:
   - Threat assessment
   - Environmental factors
   - Civilian considerations
   - Support availability
   - Intelligence gaps

### Step 2: Force Requirements Determination
2.1. Identify capability requirements:
   - Firepower needs
   - Sensor coverage
   - Communication requirements
   - Sustainability needs
   - Special equipment

2.2. Calculate force size:
   - Minimum essential forces
   - Optimal force level
   - Reserve requirements
   - Support elements
   - Command overhead

2.3. Determine composition:
   - Ship types needed
   - Fighter requirements
   - Personnel specialties
   - Equipment specific
   - Logistics support

### Step 3: Unit Availability Assessment
3.1. Query unit status:
   - Current location
   - Readiness state
   - Manning levels
   - Equipment status
   - Commitment schedule

3.2. Evaluate suitability:
   - Mission capability match
   - Training currency
   - Crew experience
   - Recent operations tempo
   - Maintenance status

3.3. Check compatibility:
   - Communication systems
   - Tactical procedures
   - Logistics commonality
   - Command relationships
   - Previous joint operations

### Step 4: Task Force Designation
4.1. Request unit assignment:
   - Submit requirements to higher HQ
   - Specify needed capabilities
   - Indicate priority
   - Provide timeline
   - Note special requirements

4.2. Receive unit allocations:
   - Verify assigned units
   - Confirm availability dates
   - Check capability match
   - Identify shortfalls
   - Request adjustments if needed

4.3. Designate task force:
   - Assign numerical designation
   - Appoint commander
   - Define command relationships
   - Establish reporting chain
   - Set activation date

### Step 5: Command Element Establishment
5.1. Select task force commander:
   - Appropriate rank/experience
   - Mission-specific expertise
   - Availability for duration
   - Previous performance
   - Communication skills

5.2. Form command staff:
   - Operations officer
   - Intelligence officer
   - Logistics coordinator
   - Communications officer
   - Liaison officers

5.3. Establish command post:
   - Select flagship
   - Verify C4I systems
   - Allocate staff space
   - Test communications
   - Install mission systems

### Step 6: Unit Integration
6.1. Issue warning order:
   - Alert assigned units
   - Provide mission overview
   - Specify reporting instructions
   - Set preparation timeline
   - Indicate assembly location

6.2. Coordinate assembly:
   - Stagger arrival times
   - Assign holding areas
   - Plan integration sequence
   - Schedule inspections
   - Arrange logistics support

6.3. Conduct reception:
   - Verify unit arrival
   - Complete check-in process
   - Issue initial orders
   - Provide comm instructions
   - Assign berthing/positions

### Step 7: Task Force Preparation
7.1. Commander's conference:
   - Unit commander introductions
   - Mission brief
   - Concept of operations
   - Command relationships
   - Questions/concerns

7.2. Staff integration:
   - Liaison officer exchange
   - Watch bill coordination
   - Communication setup
   - Intelligence sharing
   - Logistics coordination

7.3. Standardization briefings:
   - Tactical procedures
   - Communication protocols
   - Emergency procedures
   - ROE review
   - Recognition signals

### Step 8: Readiness Verification
8.1. Individual unit checks:
   - Combat systems test
   - Communication verification
   - Personnel accountability
   - Supply status
   - Medical readiness

8.2. Integrated systems check:
   - Inter-ship communications
   - Data link functionality
   - IFF systems
   - Navigation synchronization
   - Sensor correlation

8.3. Mission rehearsal:
   - Key event practice
   - Communication drill
   - Emergency procedures
   - Contingency review
   - Timeline validation

### Step 9: Final Preparation
9.1. Intelligence update:
   - Latest threat data
   - Environmental updates
   - Friendly force status
   - Collection requirements
   - Information gaps

9.2. Logistics confirmation:
   - Fuel status
   - Ammunition loads
   - Spare parts
   - Medical supplies
   - Food/water

9.3. Final orders:
   - Detailed operation order
   - Graphic control measures
   - Communication plan
   - Movement instructions
   - Contingency plans

### Step 10: Task Force Activation
10.1. Formal activation:
   - Record activation time
   - Notify higher headquarters
   - Assume operational control
   - Begin mission timeline
   - Initiate reporting

10.2. Departure procedures:
   - Final personnel check
   - Navigation verification
   - Formation establishment
   - Communication check
   - Sensor activation

## Task Force Types and Composition

### Strike Task Force
**Mission**: Offensive operations against specific targets
**Typical Composition**:
- 1 Destroyer/Frigate (command)
- 2-3 Attack vessels
- 1-2 Escort ships
- Fighter detachment

### Reconnaissance Task Force
**Mission**: Intelligence gathering and surveillance
**Typical Composition**:
- 1 Command ship
- 2-3 Scout vessels
- 1 EW platform
- 2 Escorts

### Escort Task Force
**Mission**: Protection of high-value assets
**Typical Composition**:
- 1 Frigate (command)
- 3-4 Gunships
- 2 Interceptor flights
- 1 Support vessel

### Interdiction Task Force
**Mission**: Commerce raiding and blockade
**Typical Composition**:
- 1 Fast frigate (command)
- 2-3 Corvettes
- 2 Boarding craft
- 1 Intelligence vessel

## Special Considerations

### Multinational Task Forces
- Language requirements
- Procedural differences
- Equipment compatibility
- Cultural sensitivities
- National restrictions

### Time-Critical Assembly
- Abbreviated procedures
- Essential steps only
- Concurrent activities
- Reduced rehearsal
- Risk acceptance

### Distributed Assembly
- Rendezvous planning
- Sequential integration
- Communication relay
- Staggered timeline
- Contingency locations

## Common Issues and Solutions

### Integration Challenges
**Problem**: Incompatible systems
**Solution**: Assign liaison teams

**Problem**: Procedural differences
**Solution**: Conduct standardization training

**Problem**: Communication gaps
**Solution**: Establish relay capability

### Resource Shortfalls
**Problem**: Insufficient units
**Solution**: Request augmentation or modify mission

**Problem**: Capability gaps
**Solution**: Develop workarounds or request specialists

**Problem**: Logistics limitations
**Solution**: Arrange additional support or cache supplies

## References
- 1.2.1 Fleet Command Procedure
- 1.2.2 Battle Group Organization Guidelines
- 3.1.1 Operation Development & Approval Procedure
- 6.1.3 Field Resupply Procedure''',
                'difficulty_level': 'Advanced',
                'is_required': True,
                'tags': ['task force', 'assembly', 'procedure', 'organization', 'mission planning']
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

    def _create_decision_making_standards(self, group, user):
        """Create Decision Making subgroup and its standards"""
        subgroup, _ = StandardSubGroup.objects.get_or_create(
            name='Decision Making',
            standard_group=group,
            defaults={
                'description': 'Guidelines and frameworks for command decision-making in various operational contexts.',
                'order_index': 3,
                'is_active': True,
                'created_by': user
            }
        )

        standards_data = [
            {
                'document_number': '1.3.1',
                'title': 'Rules of Engagement Guidelines',
                'category': 'Guidelines',
                'summary': 'Framework for determining appropriate use of force in various operational scenarios.',
                'content': '''# Rules of Engagement Guidelines

## Purpose
These guidelines establish the framework for determining when and how forces may engage hostile forces, ensuring lawful, proportional, and mission-appropriate use of force while protecting friendly forces and minimizing civilian casualties.

## Fundamental Principles

### Right of Self-Defense
- Inherent right never restricted
- Individual and unit self-defense
- Defense of other friendly forces
- No duty to retreat in space
- Proportional response required

### Positive Identification (PID)
- Visual confirmation preferred
- Electronic signature correlation
- Behavioral indicators
- IFF response verification
- Intelligence correlation

### Proportionality
- Force matched to threat level
- Minimum force necessary
- Escalation procedures
- De-escalation when possible
- Collateral damage consideration

## Engagement Authorization Levels

### Self-Defense Engagement
**Authority**: Individual/Unit Commander
**Criteria**:
- Imminent threat to friendly forces
- Hostile act or demonstrated intent
- No other means available
- Proportional response

**Examples**:
- Incoming weapons fire
- Targeting sensors locked on
- Ramming approach vector
- Boarding attempt

### Offensive Engagement
**Authority**: Task Force Commander or Higher
**Criteria**:
- Positive identification of enemy
- Within designated engagement zone
- Mission accomplishment requirement
- ROE matrix compliance

**Examples**:
- Pre-planned strikes
- Opportunity targets
- Force protection strikes
- Interdiction operations

### Strategic Engagement
**Authority**: Fleet Commander or Higher
**Criteria**:
- High-value targets
- Potential escalation risk
- Political implications
- Collateral damage risk

**Examples**:
- Capital ship engagement
- Station/infrastructure strikes
- Population center proximity
- Neutral party proximity

## Threat Classification

### Declared Hostile Forces
- Positively identified enemy units
- Forces in designated hostile zones
- Previously engaged hostile units
- Intelligence-confirmed threats

### Unknown Forces
- Unidentified vessels/contacts
- Non-responsive to hails
- Suspicious behavior patterns
- Ambiguous signatures

### Neutral Forces
- Identified civilian vessels
- Medical/humanitarian ships
- Declared neutral parties
- Protected sites/vessels

## Escalation of Force Procedures

### Warning Procedures
1. **Long-Range Warning** (>50km)
   - Broadcast warning on guard frequency
   - Activate warning lights/signals
   - Alter course to demonstrate intent
   - Record all actions

2. **Medium-Range Warning** (10-50km)
   - Directed communications attempt
   - Warning shots (safe direction)
   - Active sensor targeting
   - Launch alert fighters

3. **Close-Range Warning** (<10km)
   - Final verbal warning
   - Disabling shots authorized
   - Boarding preparation
   - Weapons lock authorized

### Use of Force Continuum
1. Presence and communication
2. Non-lethal demonstration
3. Non-lethal force
4. Lethal force (last resort)

## Specific Engagement Scenarios

### Space Combat ROE
**Beyond Visual Range (BVR)**:
- PID required via multiple sources
- Authorization before launch
- Abort capability maintained
- Battle damage assessment

**Within Visual Range (WVR)**:
- Visual PID preferred
- Self-defense paramount
- Minimize collateral damage
- Preserve evidence when possible

### Boarding Operations ROE
**Compliant Boarding**:
- Minimal force display
- Weapons secured
- Courtesy maintained
- Documentation thorough

**Non-Compliant Boarding**:
- Graduated force authorized
- Disable before boarding
- Armed boarding team
- Medical team ready

**Opposed Boarding**:
- Lethal force authorized
- Suppress resistance
- Secure critical areas
- Detain all personnel

### Ground Operations ROE
**Civilian Environment**:
- Positive identification critical
- Collateral damage minimized
- Non-lethal options preferred
- Cultural sensitivity required

**Combat Environment**:
- Force protection priority
- Combined arms authorized
- Indirect fire restricted
- Air support available

## Special Considerations

### Protected Entities
Never engage except in self-defense:
- Medical vessels/facilities
- Escape pods/lifeboats
- Surrender indicators displayed
- Humanitarian operations
- Religious/cultural sites

### Restricted Weapons
Require special authorization:
- Nuclear weapons (prohibited)
- Orbital bombardment
- Area-effect weapons
- Chemical/biological agents
- EMP in populated areas

### Environmental Restrictions
Consider environmental impact:
- Planetary atmosphere operations
- Populated area proximity
- Critical infrastructure
- Hazardous material facilities
- Protected zones

## ROE Matrix

| Threat Level | Response Authorized | Approval Authority | Weapons Restrictions |
|--------------|-------------------|-------------------|---------------------|
| Imminent | Self-defense | Individual | Proportional |
| High | Preemptive | Unit Commander | Conventional |
| Medium | Deterrent | Task Force Cdr | Limited collateral |
| Low | Monitoring | No engagement | N/A |

## Documentation Requirements

### Engagement Reports
Required within 2 hours:
- Time and location
- Forces involved
- Actions taken
- Casualties/damage
- Current status

### Detailed Reports
Required within 24 hours:
- Complete chronology
- Decision rationale
- ROE compliance
- Lessons learned
- Recommendations

## Common Misunderstandings

### Clarifications
- Self-defense always authorized
- Warning shots not required for self-defense
- Hostile intent includes preparation to attack
- Withdrawal not required in space
- Civilians may be combatants

### Prohibited Actions
- Revenge/retribution attacks
- Attacking surrendering forces
- Using prohibited weapons
- Excessive force
- False surrender

## ROE Modifications

### Temporary Modifications
- Mission-specific ROE
- Geographic restrictions
- Time limitations
- Threat-based changes
- Higher HQ directives

### Emergency Modifications
- Commander's emergency authority
- Immediate threat response
- Documentation required
- Higher HQ notification
- Review board follows

## Training Requirements

### Initial Training
- ROE fundamentals
- Scenario-based exercises
- Decision drills
- Documentation practice
- Legal briefing

### Sustainment Training
- Monthly scenarios
- Quarterly evaluation
- Annual certification
- Lessons learned review
- Update briefings

## Quick Reference Card

### Always Authorized
✓ Self-defense
✓ Defense of others
✓ Protect mission essential assets
✓ Response to hostile acts

### Never Authorized
✗ Revenge attacks
✗ Attacking medical/religious sites
✗ Excessive force
✗ Prohibited weapons

### Requires Authorization
? Preemptive strikes
? Area weapons
? Infrastructure targets
? Cross-border operations

## References
- 1.3.2 Emergency Command Authority Procedure
- 1.3.3 Risk Assessment Guidelines
- 1.3.6 Mission Abort Decision Matrix
- 3.2.3 Emergency Abort Criteria''',
                'difficulty_level': 'Advanced',
                'is_required': True,
                'tags': ['ROE', 'engagement', 'force', 'combat', 'guidelines']
            },
            {
                'document_number': '1.3.2',
                'title': 'Emergency Command Authority Procedure',
                'category': 'Procedure',
                'summary': 'Procedures for exercising emergency command authority during crisis situations.',
                'content': '''# Emergency Command Authority Procedure

## Purpose
This procedure defines when and how commanders may exercise emergency authority beyond normal limits during crisis situations where immediate action is required to save lives, preserve forces, or accomplish critical missions.

## Scope
Applies to all commanding officers and designated representatives when normal command channels are unavailable or when delay would result in mission failure or unacceptable losses.

## Emergency Authority Activation

### Step 1: Recognize Emergency Conditions
1.1. Identify qualifying circumstances:
   - Communication loss with higher HQ exceeding 30 minutes
   - Immediate threat to force survival
   - Time-critical mission requirement
   - Catastrophic system failure
   - Mass casualty event

1.2. Assess situation severity:
   - Threat immediacy
   - Potential casualties
   - Mission impact
   - Available alternatives
   - Time constraints

1.3. Document initial conditions:
   - Time of emergency declaration
   - Circumstances requiring action
   - Communication attempts made
   - Personnel consulted
   - Options considered

### Step 2: Declare Emergency Authority
2.1. Make formal declaration:
   - Announce to command staff
   - Log in official record
   - State specific authorities assumed
   - Define expected duration
   - Broadcast to affected units

2.2. Sample declaration:
   "I hereby declare emergency command authority at [TIME] due to [CIRCUMSTANCES]. This authority will remain in effect until normal communications are restored or relieved by competent authority."

2.3. Notify available channels:
   - Adjacent units
   - Supporting elements
   - Any reachable higher HQ
   - Subordinate commands
   - Allied forces if applicable

### Step 3: Exercise Emergency Powers
3.1. Authorized actions include:
   - Deviate from standing orders
   - Reallocate resources
   - Change mission parameters
   - Authorize normally restricted weapons
   - Cross operational boundaries

3.2. Restrictions still apply to:
   - Laws of armed conflict
   - Prohibited weapons use
   - Deliberate targeting of civilians
   - False surrender/perfidy
   - Torture/mistreatment

3.3. Decision-making process:
   - Consult available advisors
   - Consider alternatives
   - Document reasoning
   - Implement safeguards
   - Monitor results

### Step 4: Emergency Operations Management
4.1. Establish crisis action team:
   - Operations representative
   - Intelligence officer
   - Logistics coordinator
   - Medical officer
   - Legal advisor (if available)

4.2. Implement battle rhythm:
   - Hourly situation updates
   - Decision brief cycle
   - Communication attempts
   - Resource status
   - Personnel accountability

4.3. Maintain documentation:
   - Decision log
   - Actions taken
   - Resources expended
   - Personnel changes
   - Results achieved

### Step 5: Restoration Procedures
5.1. Monitor for restoration conditions:
   - Communications reestablished
   - Higher authority arrived
   - Emergency conditions ended
   - Mission completed
   - Relief force arrived

5.2. Transfer authority process:
   - Brief incoming authority
   - Provide all documentation
   - Transfer command codes
   - Update unit status
   - Stand down crisis team

5.3. Submit after-action report:
   - Complete chronology
   - Decisions made
   - Results achieved
   - Lessons learned
   - Recommendations

## Types of Emergency Authority

### Operational Emergency Authority
**When Applied**: Immediate operational decisions required
**Scope**: Tactical and operational level decisions
**Examples**:
- Weapon release beyond ROE
- Cross boundary coordination
- Emergency logistics allocation
- Medical evacuation authorization
- Emergency destruction orders

### Administrative Emergency Authority
**When Applied**: Critical personnel/resource decisions
**Scope**: Unit administration and logistics
**Examples**:
- Emergency promotions
- Critical position assignments
- Resource reallocation
- Discipline beyond normal limits
- Emergency procurement

### Technical Emergency Authority
**When Applied**: System/equipment emergency decisions
**Scope**: Technical operations and safety
**Examples**:
- Safety procedure deviation
- Emergency maintenance authorization
- System limit overrides
- Emergency protocols activation
- Experimental procedure approval

## Decision Framework

### Emergency Decision Matrix
| Situation Type | Authority Level | Documentation | Review Required |
|---------------|----------------|---------------|-----------------|
| Force Protection | Immediate | Within 2 hours | Yes |
| Mission Critical | Rapid | Within 6 hours | Yes |
| Resource Allocation | Deliberate | Within 24 hours | Yes |
| Personnel Safety | Immediate | When able | No |
| System Override | Rapid | Concurrent | Yes |

### Risk Assessment Process
1. **Immediate Threats**
   - Act first, document later
   - Life safety paramount
   - Minimal consultation
   - Verbal orders acceptable

2. **Near-Term Threats**
   - Quick consultation
   - Abbreviated planning
   - Written orders preferred
   - Risk mitigation included

3. **Deliberate Decisions**
   - Full consultation
   - Formal planning process
   - Written orders required
   - Complete documentation

## Legal Considerations

### Legal Protections
Commanders exercising emergency authority in good faith are protected when:
- Legitimate emergency existed
- Actions were reasonable
- Military necessity present
- Proper documentation maintained
- No criminal intent

### Legal Limitations
Emergency authority does NOT permit:
- War crimes
- Violations of human rights
- Illegal orders
- Personal benefit actions
- Negligent endangerment

### Documentation Requirements
**Immediate** (during emergency):
- Basic decision log
- Key personnel consulted
- Major actions taken

**Short-term** (within 24 hours):
- Detailed chronology
- Decision rationale
- Resources utilized

**Long-term** (within 72 hours):
- Complete after-action report
- Supporting documentation
- Witness statements

## Common Emergency Scenarios

### Scenario 1: Fleet Engagement Without Orders
**Situation**: Enemy fleet detected, no communication with HQ
**Authority**: Engage if threat to force
**Documentation**: Engagement report priority

### Scenario 2: Medical Emergency Mass Casualty
**Situation**: Multiple ships with casualties, medical supplies limited
**Authority**: Reallocate medical resources, commandeer civilian medical
**Documentation**: Track all resource movements

### Scenario 3: System Cascade Failure
**Situation**: Multiple system failures, abandonment decision required
**Authority**: Order abandon ship, destroy classified
**Documentation**: Record evacuation priority and classified destruction

## Review and Accountability

### Automatic Review Triggers
- Any use of emergency authority
- Casualties during emergency
- Mission failure/success
- Resource expenditure >10% normal
- Duration >24 hours

### Review Board Composition
- Senior operational commander
- Legal representative
- Peer commander
- Technical expert
- Administrative representative

### Potential Outcomes
- Actions validated
- Lessons learned documented
- Procedural changes recommended
- Additional training required
- Disciplinary action (if negligence found)

## Training and Preparation

### Required Training
- Annual emergency authority seminar
- Quarterly decision exercises
- Monthly case study review
- Emergency drills
- Documentation practice

### Preparation Measures
- Pre-designated succession
- Emergency contact lists
- Decision templates ready
- Legal quick reference
- Documentation forms accessible

## References
- 1.1.2 Succession of Command Procedure
- 1.3.1 Rules of Engagement Guidelines
- 1.3.3 Risk Assessment Guidelines
- 8.1.3 Mass Casualty Response Procedure''',
                'difficulty_level': 'Advanced',
                'is_required': True,
                'tags': ['emergency', 'command', 'authority', 'crisis', 'procedure']
            },
            {
                'document_number': '1.3.3',
                'title': 'Risk Assessment Guidelines',
                'category': 'Guidelines',
                'summary': 'Framework for assessing operational risks and making informed command decisions.',
                'content': '''# Risk Assessment Guidelines

## Purpose
These guidelines provide commanders and staff with a systematic framework for identifying, analyzing, and mitigating operational risks to enable informed decision-making while accomplishing assigned missions.

## Risk Management Principles

### Fundamental Concepts
- Accept no unnecessary risk
- Make risk decisions at appropriate level
- Accept risk when benefits outweigh costs
- Integrate risk management into planning
- Apply risk management cyclically

### Risk Categories
**Mission Risk**: Probability and severity of loss due to operational factors
**Force Risk**: Threats to personnel and equipment
**Strategic Risk**: Broader implications beyond immediate operation
**Collateral Risk**: Potential civilian/environmental impact

## Risk Assessment Process

### Step 1: Mission Analysis
**Identify Mission Requirements**
- Primary objectives
- Secondary objectives  
- Commander's intent
- Success criteria
- Time constraints

**Determine Critical Factors**
- Key terrain/space
- Decisive points
- Centers of gravity
- Critical vulnerabilities
- Essential tasks

### Step 2: Threat Identification
**Enemy Threats**
- Force composition
- Capabilities assessment
- Probable courses of action
- Weapon systems
- Electronic warfare capability

**Environmental Threats**
- Space weather
- Debris fields
- Radiation zones
- Navigation hazards
- Communication interference

**Technical Threats**
- System failures
- Cyber attacks
- Supply chain disruption
- Maintenance issues
- Integration problems

### Step 3: Vulnerability Analysis
**Force Vulnerabilities**
- Personnel limitations
- Equipment shortfalls
- Training gaps
- Logistics constraints
- Communication weaknesses

**Operational Vulnerabilities**
- Predictable patterns
- Single points of failure
- Limited redundancy
- Time pressures
- Information gaps

### Step 4: Risk Determination
**Probability Assessment**
- **Frequent**: Likely to occur often
- **Likely**: Will occur several times
- **Occasional**: Will occur sometimes
- **Seldom**: Unlikely but possible
- **Unlikely**: Improbable

**Severity Assessment**
- **Catastrophic**: Mission failure, loss of major assets
- **Critical**: Major degradation, loss of key assets
- **Moderate**: Degraded operations, minor losses
- **Negligible**: Minimal impact

### Step 5: Risk Mitigation

**Risk Control Options**
1. **Eliminate**: Remove the hazard entirely
2. **Reduce**: Minimize probability or severity
3. **Control**: Implement safeguards
4. **Accept**: Acknowledge and monitor
5. **Transfer**: Shift risk to other elements

**Mitigation Strategies**
- Tactical adjustments
- Resource reallocation
- Timeline modification
- Force protection measures
- Contingency planning

## Risk Assessment Matrix

| Probability | Catastrophic | Critical | Moderate | Negligible |
|------------|--------------|----------|----------|------------|
| Frequent | Extreme | Extreme | High | Medium |
| Likely | Extreme | High | High | Medium |
| Occasional | High | High | Medium | Low |
| Seldom | High | Medium | Medium | Low |
| Unlikely | Medium | Medium | Low | Low |

### Risk Levels
- **Extreme Risk**: Mission stop, immediate action required
- **High Risk**: Commander approval required
- **Medium Risk**: Staff level approval
- **Low Risk**: Routine acceptance

## Operational Risk Factors

### Combat Operations
**Offensive Operations**
- Enemy strength uncertainty
- Logistics sustainment
- Weather dependencies
- Coordination complexity
- Collateral damage potential

**Defensive Operations**
- Position vulnerabilities
- Reaction time constraints
- Resource limitations
- Retrograde challenges
- Civilian considerations

### Support Operations
**Logistics Operations**
- Route security
- Supply availability
- Distribution timing
- Storage vulnerabilities
- Transportation assets

**Medical Operations**
- Casualty estimates
- Evacuation capacity
- Treatment capabilities
- Supply adequacy
- Disease prevention

## Decision-Making Framework

### Risk vs. Gain Analysis
**High Risk Acceptance Criteria**
- Mission critical objective
- No viable alternatives
- Acceptable loss parameters
- Mitigation measures in place
- Recovery plan exists

**Risk Communication**
- Clear risk statement
- Probability/severity assessment
- Mitigation measures proposed
- Residual risk level
- Decision recommendation

### Commander's Risk Guidance
**Standing Guidance Elements**
- Risk tolerance levels
- Delegation authorities
- Reporting requirements
- Review triggers
- Update frequency

## Continuous Assessment

### Risk Monitoring
**Indicators to Track**
- Threat changes
- Asset availability
- Environmental conditions
- Timeline pressure
- Intelligence updates

**Review Triggers**
- Significant event
- Intelligence change
- Asset loss
- Timeline shift
- Mission modification

### Risk Documentation
**Initial Assessment**
- Comprehensive analysis
- Mitigation planning
- Decision rationale
- Approval chain
- Distribution list

**Ongoing Documentation**
- Change log
- Decision updates
- Incident reports
- Lesson captures
- Trend analysis

## Specific Risk Scenarios

### Quantum Jump Operations
**Risks**:
- Navigation error
- Ambush potential
- Fuel miscalculation
- System failure
- Communication loss

**Mitigations**:
- Multiple navigation checks
- Scout reconnaissance
- Fuel reserves
- Backup systems
- Rally procedures

### Boarding Operations
**Risks**:
- Hostile resistance
- Booby traps
- Structural damage
- Hostage situations
- Legal complications

**Mitigations**:
- Intelligence preparation
- Specialized training
- Redundant teams
- Medical support
- Legal review

### Multi-Unit Operations
**Risks**:
- Coordination failure
- Friendly fire
- Communication breakdown
- Logistics strain
- Command confusion

**Mitigations**:
- Detailed planning
- Liaison exchange
- Redundant communications
- Supply buffers
- Clear command structure

## Risk Assessment Tools

### Planning Tools
- Risk assessment worksheet
- Probability/severity matrix
- Decision support template
- Go/no-go criteria
- Risk register

### Execution Tools
- Risk tracking board
- Update triggers
- Communication formats
- Review checklists
- Incident forms

## Common Risk Assessment Errors

### Planning Errors
- Optimism bias
- Incomplete analysis
- Risk dismissal
- Over-mitigation
- Poor communication

### Execution Errors
- Failure to reassess
- Ignoring indicators
- Delayed decisions
- Poor documentation
- Lesson loss

## Risk Culture Development

### Leadership Actions
- Model risk management
- Encourage reporting
- Reward prudent risks
- Learn from failures
- Maintain standards

### Training Requirements
- Risk management course
- Scenario exercises
- Case study analysis
- Tool familiarization
- Regular refreshers

## References
- 1.3.4 Resource Allocation Decision Framework
- 1.3.6 Mission Abort Decision Matrix
- 3.1.5 Contingency Planning Guidelines
- 8.1.3 Mass Casualty Response Procedure''',
                'difficulty_level': 'Intermediate',
                'is_required': True,
                'tags': ['risk', 'assessment', 'planning', 'decision', 'guidelines']
            },
            {
                'document_number': '1.3.4',
                'title': 'Resource Allocation Decision Framework',
                'category': 'Guidelines',
                'summary': 'Framework for making resource allocation decisions under constraints and competing priorities.',
                'content': '''# Resource Allocation Decision Framework

## Purpose
This framework guides commanders and staff in making effective resource allocation decisions when faced with limited resources and competing operational priorities.

## Resource Categories

### Critical Resources
**Personnel**
- Combat crews
- Specialized operators
- Technical experts
- Medical personnel
- Support staff

**Equipment**
- Combat vessels
- Fighter craft
- Weapons systems
- Sensors/electronics
- Life support

**Consumables**
- Quantum fuel
- Ammunition
- Medical supplies
- Food/water
- Spare parts

**Time**
- Mission windows
- Maintenance periods
- Training time
- Rest cycles
- Planning duration

## Allocation Principles

### Priority Framework
1. **Life Safety**: Immediate threats to personnel
2. **Mission Essential**: Critical to primary objectives
3. **Mission Enabling**: Supports main effort
4. **Mission Enhancing**: Improves effectiveness
5. **Routine**: Standard operations

### Allocation Factors
- Mission priority
- Operational phase
- Threat level
- Resource availability
- Alternative options

## Decision Process

### Step 1: Requirements Analysis
**Identify Demands**
- Compile all requests
- Verify legitimacy
- Assess criticality
- Determine timing
- Calculate totals

**Categorize by Priority**
- Emergency/immediate
- Mission critical
- High priority
- Routine
- Nice to have

### Step 2: Resource Inventory
**Current Status**
- On-hand quantities
- Condition/readiness
- Location/accessibility
- Committed resources
- Pipeline status

**Projected Availability**
- Incoming supplies
- Production capacity
- Recovery/repair
- External support
- Timeline certainty

### Step 3: Gap Analysis
**Calculate Shortfalls**
- Total requirements
- Available resources
- Critical gaps
- Timeline impacts
- Risk assessment

**Identify Alternatives**
- Substitution options
- Workarounds
- External sources
- Reduced consumption
- Mission adjustment

### Step 4: Allocation Strategy
**Distribution Methods**
- Proportional share
- Priority fill
- Time-phased
- Geographic
- Capability-based

**Decision Criteria**
- Operational impact
- Risk acceptance
- Efficiency gains
- Fairness perception
- Future flexibility

### Step 5: Implementation
**Execution Orders**
- Clear priorities
- Specific quantities
- Delivery timeline
- Points of contact
- Reporting requirements

**Monitoring Plan**
- Consumption tracking
- Effectiveness measures
- Adjustment triggers
- Feedback mechanism
- Update schedule

## Specific Resource Frameworks

### Personnel Allocation
**Combat Crew Distribution**
- Minimum manning levels
- Experience distribution
- Specialty coverage
- Fatigue management
- Cross-training consideration

**Decision Matrix**
| Mission Type | Min Crew | Optimal | Enhancement |
|-------------|----------|---------|-------------|
| Combat Patrol | 70% | 85% | 100% |
| Training | 50% | 70% | 85% |
| Maintenance | 30% | 50% | 70% |
| Stand-down | 20% | 30% | 50% |

### Ammunition Allocation
**Distribution Priority**
1. Units in contact
2. QRF/Reserve
3. Planned operations
4. Training requirements
5. War reserve

**Allocation Formula**
- Basic load: 100% for combat units
- Sustaining rate: Daily expenditure x days
- Reserve: 20% contingency
- Training: Minimum essential

### Fuel Management
**Quantum Fuel Priorities**
1. Emergency response
2. Combat operations
3. Logistics movement
4. Routine patrol
5. Training flights

**Conservation Measures**
- Route optimization
- Speed restrictions
- Formation efficiency
- Jump coordination
- Alternative missions

### Maintenance Resources
**Parts Priority**
- Mission critical systems
- Safety of flight
- Combat effectiveness
- Quality of life
- Training systems

**Technician Allocation**
- Emergency repairs
- Scheduled maintenance
- Preventive work
- Modifications
- Training

## Constraint Management

### Scarcity Protocols
**Severe Shortage** (<50% requirement)
- Mission prioritization
- Consolidation options
- External support request
- Conservation mandatory
- Command notification

**Moderate Shortage** (50-80% requirement)
- Efficiency measures
- Sharing agreements
- Reduced consumption
- Local purchase
- Timeline adjustment

**Minimal Shortage** (80-95% requirement)
- Normal prioritization
- Minor adjustments
- Monitor closely
- Plan ahead
- Document impacts

### Trade-off Analysis
**Decision Factors**
- Mission impact
- Risk increase
- Morale effects
- Long-term costs
- Precedent setting

**Trade-off Matrix**
| Resource A Loss | Resource B Gain | Net Effect | Decision |
|----------------|-----------------|------------|----------|
| -10% Fuel | +20% Ammo | Positive | Approve |
| -5% Crew | +10% Maintenance | Neutral | Consider |
| -15% Time | +5% Coverage | Negative | Deny |

## Dynamic Allocation

### Continuous Assessment
**Monitoring Elements**
- Consumption rates
- Effectiveness metrics
- Changing priorities
- New requirements
- Resource recovery

**Adjustment Triggers**
- Mission change
- Threat evolution
- Resource loss
- Timeline shift
- External support

### Reallocation Process
1. Identify change requirement
2. Assess current distribution
3. Calculate impacts
4. Obtain approvals
5. Execute redistribution
6. Monitor results

## Communication Framework

### Allocation Announcements
**Required Elements**
- Decision rationale
- Distribution plan
- Timeline/phases
- Points of contact
- Appeal process

**Format Example**
```
RESOURCE ALLOCATION DECISION #001
Effective: [DATE/TIME]
Resource: Quantum Fuel
Distribution: 
- Combat Ops: 45%
- Patrol Ops: 30%
- Training: 15%
- Reserve: 10%
Rationale: Increased threat level
Duration: 72 hours
POC: J4 Operations
```

### Feedback Mechanisms
- Unit impact reports
- Efficiency suggestions
- Alternative proposals
- Success metrics
- Lesson capture

## Decision Support Tools

### Automated Systems
- Resource tracking database
- Allocation algorithm
- Optimization software
- Predictive analytics
- Dashboard displays

### Manual Tools
- Decision matrix
- Priority worksheet
- Impact calculator
- Trade-off analyzer
- Timeline planner

## Ethical Considerations

### Fairness Principles
- Transparent process
- Objective criteria
- Equal opportunity
- Mission focus
- Documentation

### Special Circumstances
- Medical emergencies override
- Life safety paramount
- No discrimination
- Legal compliance
- Command guidance

## Common Allocation Challenges

### Political Pressure
- Document all decisions
- Maintain objectivity
- Refer to criteria
- Involve legal/ethics
- Elevate if needed

### Information Gaps
- Use best available
- Document assumptions
- Plan for updates
- Build flexibility
- Communicate uncertainty

### Time Pressure
- Pre-planned protocols
- Delegation ready
- Quick decision tools
- Default priorities
- Rapid communication

## References
- 1.3.3 Risk Assessment Guidelines
- 1.3.8 Delegation of Authority Guidelines
- 6.1.1 Quantum Fuel Management Guidelines
- 6.1.2 Ammunition Allocation Priorities''',
                'difficulty_level': 'Advanced',
                'is_required': False,
                'tags': ['resources', 'allocation', 'logistics', 'decision', 'framework']
            },
            {
                'document_number': '1.3.5',
                'title': 'Engagement/Disengagement Criteria',
                'category': 'Information',
                'summary': 'Criteria for deciding when to engage enemy forces and when to break contact.',
                'content': '''# Engagement/Disengagement Criteria

## Purpose
This document provides commanders with clear criteria for making engagement and disengagement decisions during combat operations, balancing mission accomplishment with force preservation.

## Engagement Decision Factors

### Mission Factors
**Primary Considerations**
- Direct mission relevance
- Timeline impact
- Resource expenditure
- Success probability
- Alternative options

**Mission Type Matrix**
| Mission Type | Engagement Threshold | Acceptable Risk |
|-------------|---------------------|-----------------|
| Strike | Low - Target focused | High |
| Reconnaissance | High - Avoid if possible | Low |
| Patrol | Medium - Selective | Medium |
| Escort | Low - Protect asset | High |
| Defense | Low - Hold position | Very High |

### Force Ratio Analysis
**Favorable Ratios** (Generally engage)
- 3:1 or better advantage
- Technological superiority
- Tactical surprise achieved
- Environmental advantage
- Support availability

**Even Ratios** (Selective engagement)
- 1:1 to 3:1 advantage
- Mission critical only
- Limited duration
- Escape route available
- Acceptable losses

**Unfavorable Ratios** (Generally avoid)
- Less than 1:1
- Technical disadvantage
- Poor position
- No support available
- High casualty risk

### Tactical Advantage Assessment
**Engage When Having**
- Surprise/initiative
- Superior position
- Better sensors/weapons
- Environmental advantage
- Reinforcement proximity

**Avoid Engagement When**
- Enemy has initiative
- Poor tactical position
- Equipment disadvantage
- Environmental hazards
- Isolation from support

## Engagement Authorization

### Immediate Engagement
**Authorized Without Higher Approval**
- Self-defense situations
- Protection of critical assets
- Time-sensitive targets
- Planned mission targets
- Fleeting opportunities (within ROE)

### Deliberate Engagement
**Requires Authorization**
- Non-mission targets
- High collateral risk
- Resource intensive
- Strategic implications
- Allied proximity

### Restricted Engagement
**Special Authorization Only**
- Civilian areas
- Neutral space
- Diplomatic vessels
- Medical facilities
- Cultural sites

## Disengagement Triggers

### Mandatory Disengagement
**Immediate Withdrawal Required**
- Mission accomplished
- Ammunition depletion <20%
- Casualties exceed 30%
- Critical system failures
- Superior force arrival

### Conditional Disengagement
**Commander's Discretion**
- Limited progress
- Mounting casualties
- Resource depletion
- Timeline pressure
- Better opportunity

### Fighting Withdrawal
**When Direct Disengagement Impossible**
- Maintain fire superiority
- Sequential unit withdrawal
- Covering positions
- Rally point designation
- Pursuit deterrence

## Disengagement Procedures

### Planning Phase
**Pre-Engagement Planning**
- Identify withdrawal routes
- Designate rally points
- Assign covering forces
- Set trigger points
- Brief all elements

### Execution Phase
**Disengagement Sequence**
1. Decision announcement
2. Covering fire initiation
3. Sequential withdrawal
4. Route security
5. Rally and account

### Post-Disengagement
**Immediate Actions**
- Personnel accountability
- Ammunition count
- Damage assessment
- Medical priorities
- Position report

## Specific Scenario Criteria

### Space Combat
**Engagement Factors**
- Quantum fuel reserves >40%
- Weapons loadout >50%
- Shield integrity >60%
- No critical damage
- Escape vector clear

**Disengagement Factors**
- Fuel reserves <30%
- Weapons depleted
- Shield failure imminent
- Jump drive damaged
- Overwhelming force

### Ground Operations
**Engagement Factors**
- Ammunition basic load
- Medical support available
- Air support on station
- Good defensive terrain
- Communication maintained

**Disengagement Factors**
- Ammunition critical
- Mass casualties
- Air support lost
- Position compromised
- Communication failure

### Boarding Actions
**Engagement Factors**
- Surprise maintained
- Breaching successful
- Resistance light
- Time available
- Extraction assured

**Disengagement Factors**
- Surprise lost
- Heavy resistance
- Time critical
- Casualties mounting
- Extraction threatened

## Decision Support Matrix

### Quick Reference Guide
| Factor | Weight | Engage | Disengage |
|--------|--------|--------|-----------|
| Mission Impact | 30% | Critical | Complete/Failed |
| Force Ratio | 25% | >2:1 | <1:1 |
| Resources | 20% | >60% | <40% |
| Position | 15% | Advantage | Disadvantage |
| Support | 10% | Available | None |

### Calculation Method
- Score each factor (1-10)
- Apply weightings
- Total >6.0 = Engage
- Total <4.0 = Disengage
- 4.0-6.0 = Commander judgment

## Environmental Considerations

### Space Environment
**Favorable Conditions**
- Clear sensor picture
- Good communication
- Multiple escape routes
- No navigation hazards
- Support proximity

**Unfavorable Conditions**
- Sensor interference
- Communication jamming
- Limited maneuver room
- Debris/hazard fields
- Isolation

### Planetary Environment
**Favorable Conditions**
- Good visibility
- Terrain advantage
- Weather favorable
- Population support
- Supply lines secure

**Unfavorable Conditions**
- Limited visibility
- Terrain disadvantage
- Severe weather
- Hostile population
- Extended supply lines

## Special Considerations

### Multi-Unit Operations
- Coordination complexity
- Mutual support requirements
- Unified decision making
- Communication critical
- Phased operations

### Time-Critical Decisions
- Default to safety
- Pre-planned responses
- Delegation prepared
- Quick assessment tools
- Clear abort criteria

### Political Constraints
- ROE limitations
- Escalation concerns
- Media presence
- Civilian proximity
- Alliance considerations

## Common Decision Errors

### Engagement Errors
- Sunk cost fallacy
- Overconfidence bias
- Mission creep
- Poor intelligence
- Emotion-driven

### Disengagement Errors
- Too late decision
- Poor coordination
- Route compromise
- Pursuit invitation
- Panic withdrawal

## Training Implications

### Decision Drills
- Scenario-based training
- Time pressure exercises
- Resource constraint drills
- Communication degraded
- Multi-factor analysis

### After Action Focus
- Decision timeline
- Factor weighting
- Information available
- Outcome analysis
- Improvement areas

## References
- 1.3.1 Rules of Engagement Guidelines
- 1.3.3 Risk Assessment Guidelines
- 1.3.6 Mission Abort Decision Matrix
- 5.1.5 Defensive Maneuvering Advice''',
                'difficulty_level': 'Advanced',
                'is_required': True,
                'tags': ['engagement', 'combat', 'tactics', 'decision', 'criteria']
            },
            {
                'document_number': '1.3.6',
                'title': 'Mission Abort Decision Matrix',
                'category': 'Guidelines',
                'summary': 'Matrix and guidelines for determining when to abort ongoing missions.',
                'content': '''# Mission Abort Decision Matrix

## Purpose
This matrix provides commanders with objective criteria and decision frameworks for determining when mission continuation poses unacceptable risks, enabling timely abort decisions that preserve forces while maintaining operational integrity.

## Abort Authority Levels

### Immediate Abort Authority
**Individual/Unit Level**
- Catastrophic system failure
- Imminent destruction threat
- Loss of life support
- Uncontrolled emergency
- Safety of flight critical

### Tactical Abort Authority
**Squadron/Task Force Commander**
- Mission parameters exceeded
- Unacceptable casualties
- Critical asset loss
- Timeline failure
- Environmental hazards

### Operational Abort Authority
**Battle Group/Fleet Commander**
- Strategic implications
- Multi-unit impacts
- Political ramifications
- Resource depletion
- Campaign effects

## Abort Decision Matrix

### Critical Factors Assessment
| Factor | Green (Continue) | Yellow (Assess) | Red (Abort) |
|--------|-----------------|-----------------|-------------|
| Mission Success Probability | >70% | 40-70% | <40% |
| Force Casualties | <10% | 10-25% | >25% |
| Resource Remaining | >60% | 30-60% | <30% |
| Time to Objective | On schedule | <20% delay | >20% delay |
| Enemy Strength | As briefed | +50% expected | +100% expected |
| System Functionality | >90% | 70-90% | <70% |

### Weighted Decision Scoring
**Scoring Method**
1. Rate each factor: Green=0, Yellow=1, Red=2
2. Apply factor weights (below)
3. Sum weighted scores
4. Compare to thresholds

**Factor Weights**
- Mission Success: 25%
- Force Casualties: 30%
- Resources: 15%
- Timeline: 10%
- Enemy Strength: 10%
- Systems: 10%

**Decision Thresholds**
- Score 0-0.5: Continue mission
- Score 0.6-1.2: Commander assessment
- Score >1.2: Abort recommended

## Phase-Specific Criteria

### Pre-Engagement Phase
**Continue Indicators**
- All systems nominal
- Timeline on track
- Intelligence confirmed
- Resources adequate
- Communications good

**Abort Indicators**
- Critical system failure
- Intelligence gaps
- Resource shortfalls
- Lost communications
- Weather/environment

### Engagement Phase
**Continue Indicators**
- Tactical advantage
- Acceptable losses
- Progress toward objective
- Support available
- Extraction viable

**Abort Indicators**
- Tactical surprise lost
- Casualties mounting
- No progress
- Support unavailable
- Extraction compromised

### Exploitation Phase
**Continue Indicators**
- Objectives achievable
- Resources sufficient
- Time remaining
- Security maintained
- Consolidation possible

**Abort Indicators**
- Objectives unreachable
- Resources depleted
- Time critical
- Security lost
- Overextension risk

## Mission-Specific Matrices

### Strike Missions
| Criterion | Weight | Abort Threshold |
|-----------|--------|----------------|
| Target viability | 30% | Cannot locate/identify |
| Weapons status | 25% | <50% operational |
| Threats | 20% | 2x expected |
| Fuel | 15% | <40% + reserve |
| Time | 10% | Window missed |

### Reconnaissance Missions
| Criterion | Weight | Abort Threshold |
|-----------|--------|----------------|
| Detection risk | 35% | Compromised |
| Intel value | 25% | Minimal/obtained |
| Escape routes | 20% | Blocked |
| Equipment | 10% | Sensors failed |
| Time | 10% | Exposure excessive |

### Escort Missions
| Criterion | Weight | Abort Threshold |
|-----------|--------|----------------|
| Asset survival | 40% | Under severe threat |
| Escort capability | 30% | <50% effective |
| Route security | 15% | Compromised |
| Time | 10% | Excessive delay |
| Alternatives | 5% | Better option exists |

## Environmental Abort Triggers

### Space Operations
**Mandatory Abort Conditions**
- Solar storm CAT-4+
- Debris field density critical
- Navigation failure
- Life support <2 hours
- Structural integrity compromised

### Atmospheric Operations
**Mandatory Abort Conditions**
- Weather below minimums
- Visibility zero
- Icing conditions severe
- Wind shear detected
- Landing site unusable

### Ground Operations
**Mandatory Abort Conditions**
- NBC contamination
- Seismic activity
- Flood/fire threat
- Civilian mass casualties
- Infrastructure collapse

## Abort Execution Procedures

### Immediate Actions
1. **Abort Declaration**
   - Clear announcement
   - All units acknowledge
   - Switch to abort plan
   - Weapons safe
   - Initiate withdrawal

2. **Coordination**
   - Higher HQ notification
   - Adjacent unit alert
   - Support request
   - Medical priority
   - Recovery initiation

3. **Movement**
   - Primary route execution
   - Security establishment
   - Casualty collection
   - Equipment recovery
   - Rear guard action

### Deliberate Abort
1. **Planning** (if time permits)
   - Route selection
   - Support coordination
   - Deception plan
   - Recovery assets
   - Timeline development

2. **Preparation**
   - Unit notification
   - Load planning
   - Medical setup
   - Security positions
   - Communications check

3. **Execution**
   - Phased withdrawal
   - Accountability checks
   - Asset recovery
   - Route security
   - Rally procedures

## Post-Abort Actions

### Immediate Requirements
- Personnel accountability
- Casualty treatment
- Equipment inventory
- Threat assessment
- Position report

### Short-term Actions
- Mission debrief
- Intelligence update
- Maintenance priority
- Resupply request
- Personnel needs

### Long-term Actions
- After-action report
- Lessons learned
- Training needs
- Equipment issues
- Procedure updates

## Psychological Considerations

### Abort Stigma Management
- Emphasize force preservation
- Document decision rationale
- Leader endorsement
- No blame culture
- Focus on lessons

### Crew Morale
- Immediate debrief
- Acknowledge difficulty
- Plan forward
- Address concerns
- Maintain readiness

## Common Abort Scenarios

### Scenario 1: Ambush Detection
**Indicators**: Multiple sensor anomalies, intelligence warnings
**Decision**: Abort if surprise lost
**Execution**: Immediate reversal, maximum speed

### Scenario 2: System Cascade Failure
**Indicators**: Multiple system warnings, degraded capability
**Decision**: Abort if combat effectiveness <50%
**Execution**: Fighting withdrawal to safe zone

### Scenario 3: Time Window Closure
**Indicators**: Delays accumulating, objective time critical
**Decision**: Abort if success impossible
**Execution**: Deliberate withdrawal, preserve assets

## Training Considerations

### Abort Decision Training
- Scenario-based exercises
- Time pressure drills
- Partial information decisions
- Multi-factor analysis
- Communication practice

### Common Training Errors
- Delayed decisions
- Poor communication
- Inadequate planning
- Panic responses
- Incomplete accounting

## Decision Documentation

### Required Elements
- Time of decision
- Factors considered
- Personnel consulted
- Rationale summary
- Execution method

### Format Template
```
MISSION ABORT DECISION
Time: [DTG]
Mission: [Designation]
Factors: [List with scores]
Decision Authority: [Name/Position]
Rationale: [Brief summary]
Execution: [Method chosen]
```

## References
- 1.3.1 Rules of Engagement Guidelines
- 1.3.3 Risk Assessment Guidelines
- 1.3.5 Engagement/Disengagement Criteria
- 3.2.3 Emergency Abort Criteria''',
                'difficulty_level': 'Advanced',
                'is_required': True,
                'tags': ['abort', 'mission', 'decision', 'matrix', 'safety']
            },
            {
                'document_number': '1.3.7',
                'title': 'Time-Critical Decision Making Advice',
                'category': 'Advice',
                'summary': 'Best practices for making effective decisions under severe time constraints.',
                'content': '''# Time-Critical Decision Making Advice

## Purpose
This advice document provides commanders and decision-makers with practical techniques and mental frameworks for making sound decisions when time is severely limited and the stakes are high.

## Understanding Time-Critical Decisions

### Characteristics
- Seconds to minutes available
- High consequence outcomes
- Incomplete information
- Stress/pressure elevated
- Multiple variables changing

### Common Scenarios
- Combat engagement
- Emergency response
- System failures
- Medical crises
- Collision avoidance

## Decision-Making Frameworks

### OODA Loop (Accelerated)
**Observe** (1-2 seconds)
- Scan critical indicators
- Identify immediate threats
- Note major changes
- Register anomalies

**Orient** (2-3 seconds)
- Apply experience patterns
- Recognize situation type
- Assess capabilities
- Consider constraints

**Decide** (1-2 seconds)
- Select from prepared options
- Apply decision rules
- Choose least-bad if needed
- Commit fully

**Act** (Immediate)
- Execute decisively
- Monitor initial results
- Prepare to adjust
- Communicate clearly

### Recognition-Primed Decision Model
1. **Situation Recognition**
   - Does this match a known pattern?
   - What worked before?
   - What's different now?

2. **Mental Simulation**
   - Will typical response work?
   - Quick mental rehearsal
   - Identify major flaws

3. **Implementation**
   - Execute if acceptable
   - Modify if needed
   - Monitor closely

## Pre-Decision Preparation

### Mental Conditioning
**Scenario Visualization**
- Imagine critical situations
- Rehearse responses
- Build pattern library
- Create muscle memory

**Decision Rules Development**
- "If X, then Y" protocols
- Red lines/triggers
- Default responses
- Abort criteria

**Stress Inoculation**
- Practice under pressure
- Time-limited drills
- Fatigue training
- Overload exercises

### Environmental Setup
**Information Management**
- Critical data prominent
- Clutter eliminated
- Key indicators highlighted
- Quick reference available

**Team Preparation**
- Roles pre-assigned
- Communication brevity
- Hand signals ready
- Backup designated

## During the Decision

### Cognitive Techniques
**Focus Narrowing**
- Ignore non-critical
- Find the vital few
- Block distractions
- Trust instruments

**Pattern Matching**
- What's this like?
- Standard response?
- Trained scenario?
- Gut check

**Satisficing**
- Good enough vs perfect
- 80% solution now
- Avoid analysis paralysis
- Act on sufficient data

### Physical Techniques
**Breathing Control**
- Combat breathing (4-4-4-4)
- Oxygenate brain
- Calm physiology
- Clear thinking

**Verbal Processing**
- Think out loud
- State the obvious
- Confirm understanding
- Build team awareness

### Communication Shortcuts
**Standard Phrases**
- "Breaking engagement"
- "Emergency descent"
- "Weapons free"
- "Abort, abort, abort"

**Priority Words**
- Use sparingly
- Clear meaning
- Immediate action
- No ambiguity

## Common Time Traps

### Analysis Paralysis
**Symptoms**
- Seeking more data
- Revisiting decided
- Second-guessing
- Delay tactics

**Solutions**
- Set decision deadline
- Use timer
- Default action
- Trust training

### Committee Thinking
**Symptoms**
- Too many voices
- Consensus seeking
- Responsibility diffusion
- Slow coordination

**Solutions**
- Clear authority
- Limited input
- Designated decider
- Post-decision debrief

### Perfect Solution Seeking
**Symptoms**
- Multiple option review
- Optimization attempts
- Risk elimination
- Certainty desire

**Solutions**
- "Good enough" mindset
- First workable option
- Accept some risk
- Learn from results

## Decision Quality Indicators

### Good Time-Critical Decisions
- Timely execution
- Clear direction
- Acceptable outcomes
- Team understanding
- Lessons captured

### Poor Time-Critical Decisions
- Delayed too long
- Confused execution
- Preventable losses
- Team confusion
- Repeated mistakes

## Post-Decision Actions

### Immediate
- Monitor execution
- Adjust if needed
- Communicate status
- Document basics
- Continue mission

### When Time Permits
- Detailed debrief
- Decision reconstruction
- Lessons identification
- Process improvement
- Training updates

## Specific Technique Guidance

### Combat Decisions
**Engagement Decision** (5 seconds max)
1. Threat level? (High/Med/Low)
2. Can I win? (Yes/No/Maybe)
3. Must I fight? (Yes/No)
4. Execute: Fight/Flee/Evade

**Weapon Release** (3 seconds max)
1. Target confirmed? (Yes/No)
2. Friendlies clear? (Yes/No)
3. Within ROE? (Yes/No)
4. Execute: Fire/Hold

### Emergency Response
**System Failure** (10 seconds max)
1. Immediate danger? (Life/Mission/None)
2. Backup available? (Yes/No)
3. Time to fix? (Now/Later/Never)
4. Execute: Emergency/Workaround/Continue

**Medical Crisis** (15 seconds max)
1. ABC status? (Airway/Breathing/Circulation)
2. Resources? (Here/Coming/None)
3. Transport? (Ready/Possible/No)
4. Execute: Treat/Stabilize/Evacuate

## Building Decision-Making Speed

### Training Progression
1. **Baseline** - Unlimited time
2. **Pressure** - Moderate time limit
3. **Stress** - Severe time limit
4. **Chaos** - Time limit + distractions
5. **Reality** - Full simulation

### Practice Scenarios
- Flash cards with situations
- Computer simulations
- Live exercises
- Mental rehearsals
- Video analysis

## Team Dynamics

### Effective Teams
- Trust commander
- Know their roles
- Communicate briefly
- Execute immediately
- Support decision

### Ineffective Teams
- Question during crisis
- Unclear roles
- Over-communicate
- Hesitate/delay
- Undermine decision

## Technology Aids

### Decision Support Systems
- Pre-programmed responses
- Automated warnings
- Quick calculations
- Pattern recognition
- Historical data

### Limitations
- System dependency
- Override capability
- Failure modes
- Human judgment
- Final authority

## Psychological Factors

### Confidence Building
- Small success accumulation
- Positive visualization
- Team reinforcement
- Leader presence
- Preparation emphasis

### Stress Management
- Accept imperfection
- Focus on controllable
- Trust the process
- Learn from outcomes
- Maintain perspective

## Key Takeaways

### Remember
1. **Speed over perfection** in true crises
2. **Preparation** enables rapid decisions
3. **Pattern recognition** is fastest
4. **Team trust** is essential
5. **Learning** improves future speed

### Avoid
1. **Overthinking** when time-critical
2. **Committee decisions** in emergencies
3. **Perfection seeking** under pressure
4. **Blame culture** for rapid decisions
5. **Ignoring lessons** from outcomes

## Final Advice
"In time-critical situations, a good decision executed immediately is better than a perfect decision too late. Train your mind, trust your instincts, and act decisively. The enemy of good time-critical decisions is not bad judgment—it's hesitation."

## References
- 1.3.2 Emergency Command Authority Procedure
- 1.3.5 Engagement/Disengagement Criteria
- 8.1.1 Ejection & Survival Procedure
- 8.2.3 Game Bug Workaround Advice''',
                'difficulty_level': 'Advanced',
                'is_required': False,
                'tags': ['decision', 'time-critical', 'emergency', 'advice', 'leadership']
            },
            {
                'document_number': '1.3.8',
                'title': 'Delegation of Authority Guidelines',
                'category': 'Guidelines',
                'summary': 'Guidelines for effectively delegating command authority while maintaining accountability.',
                'content': '''# Delegation of Authority Guidelines

## Purpose
These guidelines establish principles and procedures for delegating command authority effectively, ensuring mission accomplishment while maintaining proper oversight and accountability throughout the chain of command.

## Delegation Principles

### Fundamental Concepts
- Authority can be delegated, responsibility cannot
- Delegation must be clear and documented
- Delegated authority should match capability
- Oversight remains with delegating officer
- Two-way communication essential

### Benefits of Proper Delegation
- Increased operational tempo
- Leadership development
- Distributed decision-making
- Commander focus on priorities
- Organizational resilience

## Types of Delegation

### Full Delegation
**Characteristics**
- Complete authority transfer
- Independent decision-making
- Direct reporting modified
- Long-term assignment
- Formal documentation

**Appropriate For**
- Detached operations
- Geographic separation
- Specialized functions
- Routine operations
- Training commands

### Limited Delegation
**Characteristics**
- Specific authorities only
- Defined boundaries
- Regular reporting required
- Temporary duration
- Written limitations

**Appropriate For**
- Special projects
- Absence coverage
- Specific operations
- Trial periods
- Development opportunities

### Emergency Delegation
**Characteristics**
- Immediate need
- Verbal acceptable
- Documentation follows
- Mission critical
- Time limited

**Appropriate For**
- Combat operations
- System failures
- Casualty situations
- Communications loss
- Crisis response

## Delegation Authority Matrix

### By Rank/Position
| Position | Can Delegate | Cannot Delegate |
|----------|--------------|-----------------|
| Fleet Commander | Tactical operations | Strategic decisions |
| Battle Group Cdr | Unit employment | Force composition |
| Squadron Leader | Flight operations | Squadron mission |
| Ship Captain | Department duties | Command responsibility |
| Department Head | Section tasks | Department authority |

### By Function
| Function | Delegable | Retained |
|----------|-----------|----------|
| Operations | Execution details | Mission approval |
| Personnel | Routine actions | Disciplinary authority |
| Logistics | Procurement execution | Budget authority |
| Maintenance | Work authorization | Safety certification |
| Intelligence | Collection tasks | Assessment conclusions |

## Delegation Process

### Step 1: Assess Requirements
**Determine Need**
- Workload analysis
- Span of control
- Time availability
- Expertise required
- Development opportunity

**Identify Scope**
- Specific authorities
- Clear boundaries
- Resource limits
- Time constraints
- Reporting requirements

### Step 2: Select Delegate
**Selection Criteria**
- Competence demonstrated
- Experience appropriate
- Availability confirmed
- Willingness expressed
- Trust established

**Assessment Areas**
- Technical knowledge
- Leadership ability
- Decision quality
- Communication skills
- Stress management

### Step 3: Define Authority
**Documentation Elements**
- Specific powers granted
- Limitations stated
- Resources allocated
- Timeline defined
- Reporting specified

**Clarity Checklist**
- [ ] What decisions can be made?
- [ ] What requires approval?
- [ ] What resources available?
- [ ] When does it end?
- [ ] How to report progress?

### Step 4: Communicate Delegation
**To the Delegate**
- Face-to-face preferred
- Written follow-up
- Questions encouraged
- Support assured
- Expectations clear

**To the Organization**
- Announcement made
- Authority confirmed
- Contact established
- Support directed
- Changes documented

### Step 5: Monitor Execution
**Oversight Methods**
- Regular reports
- Milestone reviews
- Spot checks
- Open communication
- Performance metrics

**Balance Required**
- Avoid micromanagement
- Maintain visibility
- Provide support
- Allow mistakes
- Intervene if needed

## Effective Delegation Techniques

### Clear Communication
**Initial Brief Should Include**
- Mission/task definition
- Authority boundaries
- Available resources
- Success criteria
- Reporting schedule

**Example Format**
```
DELEGATION OF AUTHORITY

TO: [Name, Position]
AUTHORITY: [Specific powers]
PURPOSE: [Why delegating]
LIMITATIONS: [What cannot do]
RESOURCES: [What available]
DURATION: [Start-End]
REPORTING: [When/How]
```

### Graduated Delegation
**Progressive Approach**
1. Observe and assist
2. Assist with oversight
3. Act with approval
4. Act then report
5. Full authority

**Development Timeline**
- Week 1-2: Observation
- Week 3-4: Assisted execution
- Week 5-6: Supervised independence
- Week 7-8: Full delegation

### Reverse Delegation Prevention
**Common Attempts**
- "What should I do?"
- "This is too hard"
- "You decide"
- "I'm not sure"
- "What would you do?"

**Appropriate Responses**
- "What do you recommend?"
- "What are your options?"
- "What's your analysis?"
- "Make a decision and brief me"
- "Use your best judgment"

## Common Delegation Challenges

### Over-Delegation
**Symptoms**
- Loss of control
- Quality degradation
- Mission creep
- Authority confusion
- Accountability gaps

**Solutions**
- Reduce scope
- Increase oversight
- Clarify boundaries
- Provide training
- Reassess capability

### Under-Delegation
**Symptoms**
- Commander overload
- Bottlenecks
- Low morale
- Underdeveloped subordinates
- Slow decisions

**Solutions**
- Identify barriers
- Build trust
- Start small
- Accept imperfection
- Reward initiative

### Unclear Delegation
**Symptoms**
- Confusion
- Duplicate efforts
- Gaps in coverage
- Conflicting decisions
- Finger pointing

**Solutions**
- Written documentation
- Public announcement
- Regular reviews
- Clear boundaries
- Open communication

## Delegation in Special Circumstances

### Combat Operations
- Verbal delegation acceptable
- Documentation can follow
- Mission focus primary
- Safety paramount
- Flexibility required

### Multi-Unit Operations
- Coordination critical
- Boundaries essential
- Communication plan
- Unity of command
- Regular synchronization

### Training Environments
- Learning objective primary
- Mistakes acceptable
- Close supervision
- Frequent feedback
- Progressive complexity

## Accountability Framework

### Delegator Responsibilities
- Proper selection
- Clear communication
- Adequate resources
- Appropriate oversight
- Ultimate accountability

### Delegate Responsibilities
- Understand authority
- Stay within bounds
- Report as required
- Seek clarification
- Accept accountability

### Mutual Obligations
- Open communication
- Trust building
- Problem solving
- Lesson sharing
- Success recognition

## Revocation Procedures

### Revocation Triggers
- Mission failure risk
- Authority exceeded
- Negligence shown
- Trust broken
- Circumstances changed

### Revocation Process
1. Document reasons
2. Notify delegate
3. Inform organization
4. Reassume authority
5. Conduct review

## Best Practices

### Do's
- Match authority to ability
- Document delegations
- Communicate clearly
- Monitor appropriately
- Recognize success

### Don'ts
- Delegate responsibility
- Abandon oversight
- Micromanage execution
- Delegate up
- Change without notice

## Measurement and Feedback

### Success Indicators
- Missions accomplished
- Decisions timely
- Quality maintained
- Development shown
- Morale improved

### Review Process
- Regular one-on-ones
- Performance metrics
- 360-degree feedback
- Lessons learned
- Adjustment made

## References
- 1.1.3 Officer/NCO Authority Guidelines
- 1.1.5 Temporary Command Assignment Procedure
- 1.3.2 Emergency Command Authority Procedure
- 4.3.3 Command Qualification Guidelines''',
                'difficulty_level': 'Intermediate',
                'is_required': False,
                'tags': ['delegation', 'authority', 'leadership', 'command', 'guidelines']
            },
            {
                'document_number': '1.3.9',
                'title': 'Initiative vs Orders Balance',
                'category': 'Advice',
                'summary': 'Advice on balancing individual initiative with following orders in military operations.',
                'content': '''# Initiative vs Orders Balance

## Purpose
This document provides advice on balancing individual initiative with obedience to orders, helping leaders at all levels understand when to follow orders precisely and when to exercise judgment and initiative to achieve mission success.

## Understanding the Balance

### The Fundamental Tension
Military effectiveness requires both:
- **Discipline**: Following orders ensures coordination and unity of effort
- **Initiative**: Adapting to circumstances achieves mission success

The art of military leadership lies in knowing when each is appropriate.

### Mission Command Philosophy
"Tell subordinates what to achieve, not how to achieve it"
- Commanders provide intent and end state
- Subordinates determine best methods
- Initiative encouraged within intent
- Results matter more than process

## When to Follow Orders Precisely

### Situations Requiring Strict Compliance
**Coordinated Operations**
- Synchronized timing critical
- Multiple units involved
- Friendly fire risk
- Precise coordination required

**Legal/Ethical Boundaries**
- Rules of engagement
- Law of armed conflict
- Treatment of prisoners
- Use of force restrictions

**Safety Protocols**
- Emergency procedures
- Weapons handling
- Navigation requirements
- Communication security

**Administrative Requirements**
- Financial regulations
- Personnel policies
- Classification rules
- Report formats

### Recognizing "Must Follow" Orders
Look for key phrases:
- "You will..." (directive)
- "Do not deviate..." (restrictive)
- "Exactly as briefed..." (precise)
- "No exceptions..." (absolute)
- "By order of..." (authority)

## When to Exercise Initiative

### Situations Favoring Initiative
**Changed Circumstances**
- Enemy situation different
- Resources unavailable
- Timeline disrupted
- Assumptions invalid
- Opportunities emerged

**Communication Loss**
- Cannot reach higher HQ
- Time-critical decision
- Awaiting orders dangerous
- Local knowledge superior

**Mission Accomplishment**
- Orders becoming obstacle
- Better method apparent
- Risk acceptable
- Intent still achievable

### Initiative Indicators
Commander's language suggesting flexibility:
- "If possible..." (conditional)
- "Intent is to..." (outcome focused)
- "Generally..." (guideline)
- "When feasible..." (judgment)
- "Achieve..." (method flexible)

## Decision Framework

### The Initiative Decision Tree
1. **Is the order lawful?**
   - No → Must not follow
   - Yes → Continue

2. **Will following achieve intent?**
   - Yes → Generally follow
   - No → Consider initiative

3. **Do I understand commander's intent?**
   - No → Seek clarification
   - Yes → Continue

4. **Is deviation necessary?**
   - No → Follow orders
   - Yes → Document and proceed

5. **Can I communicate?**
   - Yes → Request modification
   - No → Use judgment

## Practical Application

### Tactical Level Examples
**Scenario**: Ordered to attack at 0600
- **Follow Orders**: If part of coordinated assault
- **Use Initiative**: If enemy withdrawing at 0530

**Scenario**: Hold position at all costs
- **Follow Orders**: If strategic chokepoint
- **Use Initiative**: If position compromised, withdrawal saves force

**Scenario**: Use specific route
- **Follow Orders**: If deconflicting with other units
- **Use Initiative**: If route blocked, alternative available

### Communication Strategies
**When Exercising Initiative**
- Report changes immediately when possible
- Explain reasoning briefly
- Confirm intent still met
- Accept responsibility

**Sample Report**:
"Deviation from orders. Enemy strength double expected. Attacking from north instead of south to maintain surprise. Will achieve objective by 0630. How copy?"

## Cultural Considerations

### Building Initiative-Friendly Culture
**Leaders Should**:
- Communicate intent clearly
- Reward smart initiative
- Accept honest mistakes
- Discourage zero-defect mentality
- Share lessons learned

**Subordinates Should**:
- Understand commander's intent
- Develop judgment through study
- Accept responsibility
- Communicate decisions
- Learn from outcomes

### Warning Signs of Imbalance
**Too Much Compliance**:
- Missed opportunities
- Predictable patterns
- Slow adaptation
- Low morale
- "That's not my job"

**Too Much Initiative**:
- Coordination failures
- Friendly conflicts
- Resource waste
- Authority confusion
- "Cowboys" running wild

## Risk Management

### Calculating Initiative Risk
**Low Risk Initiative**:
- Affects only your unit
- Resources available
- Time permits
- Reversible decision
- Limited downside

**High Risk Initiative**:
- Affects multiple units
- Resources limited
- Time critical
- Irreversible decision
- Major consequences

### Mitigation Strategies
- Document decision rationale
- Inform adjacent units
- Prepare contingencies
- Monitor closely
- Report results

## Historical Examples

### Successful Initiative
**Example 1**: Squadron 42 at Centauri
- Ordered: Hold formation
- Situation: Gap in enemy line spotted
- Initiative: Exploited gap
- Result: Decisive victory

**Example 2**: Defense of Mining Station 7
- Ordered: Withdraw if outnumbered
- Situation: Civilians trapped
- Initiative: Held position
- Result: Civilians saved, medals awarded

### Failed Initiative
**Example 1**: Patrol Boat Incident
- Ordered: Specific patrol route
- Situation: "Shortcut" identified
- Initiative: Route deviation
- Result: Ambushed, ship lost

**Example 2**: Supply Convoy Disaster
- Ordered: Wait for escort
- Situation: Behind schedule
- Initiative: Proceeded alone
- Result: Convoy captured

## Developing Judgment

### For Leaders
**Train Subordinates**:
- Provide intent practice
- Discuss historical examples
- Conduct decision exercises
- Allow controlled mistakes
- Recognize good initiative

**Clear Communication**:
- State restrictions explicitly
- Explain the "why"
- Define success criteria
- Identify decision points
- Provide backup plans

### For Subordinates
**Build Competence**:
- Study commander's patterns
- Learn from others' experiences
- Practice decision-making
- Understand higher mission
- Know your capabilities

**Questions to Ask**:
- What's the real objective?
- Why this specific method?
- What if circumstances change?
- Who else is affected?
- What's acceptable risk?

## Common Pitfalls

### Initiative Mistakes
- Acting on incomplete information
- Ignoring commander's intent
- Failing to communicate changes
- Exceeding capabilities
- Creating cascading problems

### Compliance Mistakes
- Following obviously bad orders
- Ignoring critical changes
- Missing opportunities
- Allowing preventable losses
- "Just following orders" excuse

## The Bottom Line

### Key Principles
1. **Orders exist for reasons** - Understand why before deviating
2. **Intent matters most** - Achieve the goal, adjust the method
3. **Communicate when possible** - Keep leadership informed
4. **Accept responsibility** - Own your decisions
5. **Learn continuously** - Every situation teaches

### Final Advice
"The best military leaders cultivate subordinates who know when to follow orders exactly and when to adapt intelligently. Train your mind to recognize the difference, develop the moral courage to act appropriately, and always keep the mission and your people foremost in your decisions."

## Quick Reference Guide

### Green Light for Initiative
✓ Commander's intent clear
✓ Situation significantly changed
✓ Better method available
✓ Risk acceptable
✓ Time critical

### Red Light for Initiative
✗ Coordinated operation
✗ Legal/ethical boundary
✗ Beyond your expertise
✗ Affects other units
✗ Communication possible

## References
- 1.1.3 Officer/NCO Authority Guidelines
- 1.3.1 Rules of Engagement Guidelines
- 1.3.7 Time-Critical Decision Making Advice
- 1.3.11 Asset Preservation vs Mission Success''',
                'difficulty_level': 'Advanced',
                'is_required': False,
                'tags': ['initiative', 'orders', 'leadership', 'judgment', 'advice']
            },
            {
                'document_number': '1.3.10',
                'title': 'Civilian Protection Decision Framework',
                'category': 'Guidelines',
                'summary': 'Framework for making decisions that balance mission accomplishment with civilian protection.',
                'content': '''# Civilian Protection Decision Framework

## Purpose
This framework guides commanders in making decisions that appropriately balance mission accomplishment with the protection of civilian lives and property, ensuring operations comply with legal obligations and ethical standards.

## Fundamental Principles

### Legal Obligations
- Distinction between combatants and civilians
- Proportionality in use of force
- Precautions in attack
- Prohibition of indiscriminate attacks
- Protection of civilian objects

### Ethical Imperatives
- Minimize harm to innocents
- Preserve civilian infrastructure
- Maintain force legitimacy
- Build population support
- Uphold military honor

## Civilian Categories

### Protected Persons
**Always Protected**
- Non-combatants
- Medical personnel
- Religious personnel
- Journalists
- Children

**Conditionally Protected**
- Government officials (unless combatant)
- Police (unless combatant)
- Infrastructure workers
- Transportation operators
- Communications personnel

### Loss of Protection
Civilians lose protection when:
- Directly participating in hostilities
- Operating military equipment
- Conducting military operations
- Gathering tactical intelligence
- Performing combat functions

## Decision Framework

### Step 1: Civilian Presence Assessment
**Information Gathering**
- Intelligence reports
- Sensor data
- Visual observation
- Local knowledge
- Pattern analysis

**Density Evaluation**
- No civilians present
- Sparse presence (<10)
- Moderate presence (10-50)
- Dense presence (50-200)
- Mass gatherings (>200)

### Step 2: Risk Evaluation
**Risk Matrix**
| Civilian Density | Military Value | Risk Level | Authority Required |
|-----------------|----------------|------------|-------------------|
| None | Any | Low | Unit Commander |
| Sparse | High | Medium | Battalion/Squadron |
| Moderate | High | High | Brigade/Group |
| Dense | Critical | Extreme | Division/Fleet |
| Mass | Any | Prohibited | Strategic Command |

### Step 3: Mitigation Measures
**Tactical Options**
- Timing adjustment (night ops)
- Precision weapons only
- Observation and wait
- Ground forces preferred
- Non-lethal alternatives

**Warning Procedures**
- Broadcast warnings
- Leaflet drops
- Social media alerts
- Local leader notification
- Demonstration effects

### Step 4: Proportionality Analysis
**Calculation Elements**
- Expected civilian casualties
- Military advantage anticipated
- Alternative methods available
- Time sensitivity
- Strategic implications

**Decision Threshold**
If civilian casualties likely exceed military advantage:
- Reconsider operation
- Seek alternatives
- Elevate decision
- Document reasoning

### Step 5: Execution Monitoring
**Real-Time Indicators**
- Civilian movement unexpected
- Density increased
- Human shields suspected
- Collateral damage occurring
- Mission assumptions invalid

**Abort Authorities**
- Any soldier: Obvious massacre prevention
- Team leader: Excessive casualties likely
- Unit commander: Proportionality exceeded
- Higher HQ: Strategic implications

## Specific Scenarios

### Urban Operations
**Challenges**
- High civilian density
- Limited visibility
- Mixed combatant/civilian
- Critical infrastructure
- Evacuation difficulties

**Mitigation Strategies**
- Isolation and bypass
- Precision engagement
- Incremental clearing
- Civilian safe routes
- Medical support ready

### Space Station Operations
**Unique Considerations**
- Life support systems
- Evacuation limitations
- Explosive decompression
- Civilian workforce
- Refugee populations

**Required Precautions**
- Avoid hull breaches
- Protect life support
- Secure escape routes
- Non-lethal priority
- Rescue assets ready

### Mining Colony Defense
**Typical Issues**
- Mixed civilian/military
- Corporate interests
- Family presence
- Critical resources
- Limited shelters

**Protection Measures**
- Evacuation planning
- Shelter designation
- Supply protection
- Medical facilities
- Communication maintenance

## Weapons Selection Guide

### Preferred in Civilian Areas
- Precision guided munitions
- Small arms (discriminate)
- Non-lethal weapons
- EMP (limited areas)
- Cyber weapons

### Restricted Near Civilians
- Area effect weapons
- Indirect fire
- Orbital bombardment
- Mines/booby traps
- Chemical agents

### Prohibited
- Nuclear weapons
- Biological weapons
- Poison weapons
- Expanding bullets
- Blinding lasers

## Communication Protocols

### Warning Messages
**Standard Format**:
"Attention civilians in [LOCATION]. Military operations will commence at [TIME]. For your safety, evacuate via [ROUTE] immediately. Remain will risk injury."

**Delivery Methods**
- All frequency broadcast
- Visual signals
- Audio warnings
- Digital alerts
- Physical messengers

### Post-Incident
**Immediate Actions**
- Cease fire
- Casualty assistance
- Medical priority
- Secure area
- Document scene

**Reporting Requirements**
- Incident time/location
- Civilian casualties
- Circumstances
- Decisions made
- Assistance provided

## Cultural Considerations

### Religious Sites
- Presume protected
- Verify military use
- Minimize damage
- Respect practices
- Consult advisors

### Medical Facilities
- Never target
- Verify neutrality
- Protect function
- Allow access
- Support if needed

### Educational Institutions
- Avoid if possible
- Verify combatant absence
- Minimize disruption
- Protect records
- Quick restoration

## Decision Documentation

### Required Elements
- Civilian presence assessment
- Military necessity stated
- Alternatives considered
- Mitigation measures taken
- Proportionality analysis

### Format Template
```
CIVILIAN IMPACT DECISION
DTG: [Date-Time-Group]
Location: [Grid/Coordinates]
Civilian Estimate: [Number/Density]
Military Objective: [Specific]
Alternatives Considered: [List]
Mitigation Measures: [List]
Decision: [Proceed/Abort/Modify]
Authority: [Name/Position]
```

## Common Dilemmas

### Human Shields
**Recognition**
- Forced positioning
- Unusual gatherings
- Military assets hidden
- Civilian distress
- Pattern changes

**Response Options**
- Refuse engagement
- Precision targeting
- Isolation tactics
- Psychological operations
- Time delay

### Mixed Areas
**Industrial/Military**
- Dual-use facilities
- Night shift workers
- Military production
- Civilian employees
- Economic impact

**Decision Factors**
- Military contribution
- Reversibility
- Alternative targets
- Economic warfare
- Long-term effects

## Training Requirements

### Individual Training
- Law of war basics
- Civilian identification
- Escalation procedures
- Reporting requirements
- Cultural awareness

### Unit Training
- Scenario exercises
- ROE application
- Decision drills
- Communication practice
- After-action reviews

## Accountability Measures

### Command Responsibility
- Clear guidance issued
- Training provided
- Resources allocated
- Decisions documented
- Investigations supported

### Individual Responsibility
- Orders questioned if illegal
- Civilians protected
- Force minimized
- Incidents reported
- Evidence preserved

## Best Practices

### Do's
- Always consider civilians
- Document decisions
- Use minimum force
- Provide warnings
- Render aid

### Don'ts
- Assume combatant status
- Use excessive force
- Ignore civilian casualties
- Destroy unnecessarily
- Cover up incidents

## Quick Reference Card

### Green Light Indicators
✓ No civilians present
✓ Clear military target
✓ Proportionate response
✓ Warnings provided
✓ Precision weapons available

### Red Light Indicators
✗ Mass civilians present
✗ Protected site
✗ Disproportionate harm
✗ No military necessity
✗ Alternative available

### Decision Checklist
□ Civilians identified?
□ Military value clear?
□ Alternatives considered?
□ Warnings possible?
□ Proportionality calculated?
□ Authority obtained?
□ Monitoring planned?

## References
- 1.3.1 Rules of Engagement Guidelines
- 1.3.3 Risk Assessment Guidelines
- 1.3.5 Engagement/Disengagement Criteria
- 3.2.3 Emergency Abort Criteria''',
                'difficulty_level': 'Advanced',
                'is_required': True,
                'tags': ['civilian', 'protection', 'ROE', 'ethics', 'framework']
            },
            {
                'document_number': '1.3.11',
                'title': 'Asset Preservation vs Mission Success',
                'category': 'Advice',
                'summary': 'Advice on balancing the preservation of valuable assets against mission accomplishment needs.',
                'content': '''# Asset Preservation vs Mission Success

## Purpose
This document provides advice for commanders facing the challenging decision of risking or sacrificing valuable assets to achieve mission success, helping balance force preservation with operational necessity.

## Understanding the Dilemma

### The Fundamental Conflict
Every military operation involves risk to:
- Personnel lives
- Equipment and vessels
- Strategic capabilities
- Future operations
- Political capital

The art of command lies in determining when these risks are justified by mission importance.

### Asset Categories

**Irreplaceable Assets**
- Capital ships (Bengal, Javelin)
- Experienced crews
- Specialized equipment
- Strategic installations
- Unique capabilities

**Replaceable but Valuable**
- Standard warships
- Fighter aircraft
- Trained personnel
- Common equipment
- Supply stockpiles

**Expendable Resources**
- Ammunition
- Fuel
- Consumables
- Drones
- Decoys

## Decision Philosophy

### Mission-First Mindset
"Ships and equipment exist to accomplish missions, not to be preserved"
- Assets are tools, not treasures
- Hoarding guarantees defeat
- Calculated risks necessary
- Victory requires sacrifice

### Preservation Wisdom
"A force preserved today can fight tomorrow"
- Pyrrhic victories worthless
- Sustainability matters
- Experience irreplaceable
- Morale considerations

## Risk Assessment Framework

### Mission Value Analysis
**Critical Missions** (High risk acceptable)
- Homeland defense
- Civilian evacuation
- Strategic objective
- Time-critical opportunity
- War-winning potential

**Important Missions** (Moderate risk acceptable)
- Tactical objectives
- Force projection
- Enemy attrition
- Territory control
- Supply security

**Routine Missions** (Minimal risk acceptable)
- Presence patrols
- Training operations
- Show of force
- Administrative moves
- Non-combat tasks

### Asset Value Calculation
**Factors to Consider**
- Replacement time
- Replacement cost
- Crew experience
- Capability uniqueness
- Strategic importance

**Value Matrix**
| Asset Type | Replace Time | Strategic Value | Acceptable Loss Rate |
|------------|--------------|-----------------|---------------------|
| Capital Ship | Years | Critical | <5% per campaign |
| Destroyer | Months | High | <10% per operation |
| Fighter | Weeks | Moderate | <20% per mission |
| Drone | Days | Low | Expendable |

## Decision Guidelines

### When to Accept High Risk

**Situational Indicators**
- Existential threat
- Fleeting opportunity
- Cascading benefits
- No alternatives
- Time critical

**Historical Example**: Battle of Vega II
- Situation: Enemy fleet threatening homeworld
- Decision: Commit entire reserve fleet
- Result: 40% losses, but invasion stopped
- Verdict: Justified by stakes

### When to Preserve Assets

**Preservation Indicators**
- Marginal gains only
- Alternatives available
- Attrition warfare
- Political operations
- Future needs critical

**Historical Example**: Kellog Withdrawal
- Situation: Minor system, heavy defenses
- Decision: Withdraw without engagement
- Result: Fleet preserved for crucial battle
- Verdict: Wisdom in restraint

## Tactical Considerations

### Force Multiplication
**Preserving Combat Power**
- Concentrate forces
- Achieve local superiority
- Quick decisive action
- Minimize exposure time
- Withdraw after success

**Example Application**
Instead of: Prolonged siege with steady losses
Better: Concentrated strike accepting higher immediate risk

### Asset Substitution
**Creative Alternatives**
- Use expendables first
- Deception operations
- Electronic warfare
- Allied contributions
- Unconventional methods

**Substitution Hierarchy**
1. Automated systems
2. Older equipment
3. Allied forces
4. Reserve units
5. Front-line assets

## Command Perspectives

### Squadron Leader Level
"Can I accomplish this mission without losing my entire unit?"
- Focus on tactical success
- Preserve unit cohesion
- Consider crew morale
- Think next mission
- Balance aggression/caution

### Battle Group Commander
"Is this objective worth a capital ship?"
- Operational perspective
- Campaign sustainability
- Strategic asset management
- Political implications
- Long-term effects

### Fleet Admiral
"Will this sacrifice enable strategic victory?"
- Grand strategy view
- Acceptable loss rates
- Industrial capacity
- Political will
- Historical judgment

## Psychological Factors

### Crew Considerations
**Morale Impact**
- Purposeful sacrifice accepted
- Wasteful loss devastating
- Success justifies risk
- Leadership trust critical
- Survivor guilt management

**Communication Strategy**
- Explain the stakes
- Honor the sacrifice
- Share the victory
- Support survivors
- Learn from losses

### Command Burden
**Decision Weight**
- Lives in your hands
- History will judge
- No perfect answers
- Isolation of command
- Living with consequences

**Coping Mechanisms**
- Clear conscience through preparation
- Document reasoning
- Seek counsel wisely
- Accept responsibility
- Focus on mission

## Practical Decision Tools

### Quick Assessment Method
1. **Mission Criticality** (1-10 scale)
2. **Asset Replaceability** (1-10 scale)
3. **Success Probability** (percentage)
4. **Alternative Options** (yes/no)

**Decision Formula**:
If (Mission Criticality × Success Probability) > (Asset Value × 5)
Then: Accept risk
Else: Seek alternatives

### Risk Mitigation Strategies
**Before Committing**
- Maximize preparation
- Stack advantages
- Plan extraction
- Ready reserves
- Prepare medical

**During Operations**
- Monitor closely
- Adapt quickly
- Reinforce success
- Cut losses early
- Document decisions

## Case Studies

### Case 1: The Idris Gambit
**Situation**: Enemy supply convoy protected by superior force
**Asset Risk**: Idris frigate and escorts
**Decision**: Attack using asteroid field for cover
**Result**: Convoy destroyed, frigate damaged but recovered
**Lesson**: Environmental advantages reduce risk

### Case 2: Station Siege Mistake
**Situation**: Pirate base heavily fortified
**Asset Risk**: Two Hammerheads
**Decision**: Frontal assault for quick victory
**Result**: Both ships lost, base eventually taken
**Lesson**: Patience preserves assets

### Case 3: The Bengal's Stand
**Situation**: Colony evacuation under attack
**Asset Risk**: Bengal carrier
**Decision**: Carrier holds alone while civilians escape
**Result**: Carrier lost, 50,000 civilians saved
**Lesson**: Some sacrifices transcend calculation

## Common Pitfalls

### Over-Preservation
**Symptoms**
- Missed opportunities
- Initiative surrendered
- Enemy emboldened
- Morale degraded
- War prolonged

**Correction**
- Remember mission purpose
- Accept calculated risks
- Trust subordinates
- Study successful risks
- Reward bold success

### Reckless Expenditure
**Symptoms**
- Unsustainable losses
- Diminished capability
- Morale collapse
- Strategic weakness
- Political problems

**Correction**
- Reassess risk tolerance
- Improve planning
- Consider alternatives
- Value experience
- Think long-term

## Wisdom for Commanders

### Key Principles
1. **No asset is too valuable to lose for the right mission**
2. **No mission is worth poorly calculated losses**
3. **Preservation without purpose leads to defeat**
4. **Sacrifice without achievement wastes lives**
5. **History remembers results, not ships saved**

### Questions to Ask
- What happens if I lose this asset?
- What happens if I fail this mission?
- Can I achieve this another way?
- Will success justify the cost?
- Can I live with this decision?

### Final Advice
"The burden of command is choosing when to risk the irreplaceable for the indispensable. Make such choices with clear eyes, steady purpose, and full acceptance of responsibility. Ships can be rebuilt, but opportunities and lives cannot be recovered. Choose wisely, act decisively, and never waste the sacrifices of those who trust your judgment."

## Quick Decision Guide

### Risk the Asset When:
✓ Mission genuinely critical
✓ Success probability good
✓ No viable alternatives
✓ Time demands action
✓ Stakes justify cost

### Preserve the Asset When:
✓ Mission marginal value
✓ Success unlikely
✓ Alternatives exist
✓ Time permits patience
✓ Future need greater

## References
- 1.3.3 Risk Assessment Guidelines
- 1.3.4 Resource Allocation Decision Framework
- 1.3.6 Mission Abort Decision Matrix
- 1.3.7 Time-Critical Decision Making Advice''',
                'difficulty_level': 'Advanced',
                'is_required': False,
                'tags': ['command', 'risk', 'assets', 'preservation', 'advice']
            },
            {
                'document_number': '1.3.12',
                'title': 'Communication Under Fire Guidelines',
                'category': 'Guidelines',
                'summary': 'Guidelines for maintaining effective communication during combat operations.',
                'content': '''# Communication Under Fire Guidelines

## Purpose
These guidelines establish procedures and best practices for maintaining effective communication during combat operations when normal channels are degraded, jammed, or compromised.

## Communication Priorities

### Critical Information Hierarchy
1. **FLASH Priority**
   - Troops in contact
   - Emergency close air support
   - Imminent collision/danger
   - Nuclear/biological/chemical alert
   - Cease fire/abort mission

2. **IMMEDIATE Priority**
   - Medical evacuation request
   - Ammunition critical
   - Position compromised
   - System failures critical
   - Enemy breakthrough

3. **PRIORITY**
   - Operational updates
   - Resource requests
   - Intelligence reports
   - Status changes
   - Coordination requirements

4. **ROUTINE**
   - Administrative traffic
   - Logistics updates
   - Personnel matters
   - Training information
   - Non-urgent reports

## Combat Communication Principles

### Brevity
**Say More with Less**
- Eliminate filler words
- Use standard terminology
- Preset code words
- Number sequences
- Authentication minimal

**Example Transformation**
- Poor: "Uh, this is Alpha Six, we are currently taking fire from enemy positions"
- Better: "Alpha Six, contact, grid 247531"

### Clarity
**Ensure Understanding**
- Speak distinctly
- Moderate pace
- Standard pronunciation
- Repeat critical data
- Confirm receipt

**Phonetic Usage**
- Numbers: "TREE" (3), "FOWER" (4), "FIFE" (5), "NINER" (9)
- Letters: Alpha, Bravo, Charlie, Delta...
- Grids: Digit by digit
- Times: 24-hour format

### Security
**Minimize Intelligence Value**
- No unit sizes on net
- Code names only
- Grid references encrypted
- Frequencies changed
- Authentication current

## Degraded Communication Procedures

### Jamming Response
**Immediate Actions**
1. Recognize jamming (continuous noise/interference)
2. Attempt alternate frequency
3. Reduce power output
4. Switch to backup net
5. Use runners/signals

**Anti-Jamming Techniques**
- Frequency hopping
- Burst transmission
- Directional antennas
- Relay stations
- Physical messenger

### Equipment Failure
**Backup Methods**
- Secondary radios
- Laser communication
- Visual signals
- Sound signals
- Courier vessels

**Field Expedient Repairs**
- Antenna improvements
- Power conservation
- Component swapping
- Environmental protection
- Percussive maintenance

## Combat Net Discipline

### Net Priority Rules
**Who Talks When**
- Net control absolute authority
- Higher headquarters priority
- Combat units over support
- Emergency trumps all
- Brief transmissions only

**Breaking In Protocol**
For emergency traffic:
1. "BREAK, BREAK, BREAK"
2. Wait for "Go ahead"
3. Send traffic
4. Clear net immediately

### Authentication Procedures
**Challenge and Reply**
- Daily changing codes
- Number/letter combinations
- Time-based sequences
- Duress indicators
- Voice recognition backup

**Quick Authentication**
- Running password
- Number sequences
- Color codes
- Sports teams
- Personal facts

## Reporting Formats

### Contact Report (SALUTE)
- **S**ize: Squad/platoon/company
- **A**ctivity: Attacking/defending/moving
- **L**ocation: Grid reference
- **U**nit: Type of enemy
- **T**ime: When observed
- **E**quipment: Weapons/vehicles

### Situation Report (SITREP)
1. Enemy situation
2. Friendly situation
3. Status (Green/Amber/Red/Black)
4. Combat power percentage
5. Logistics status

### Medical Evacuation (MEDEVAC)
- Location of pickup
- Radio frequency/call sign
- Number of patients
- Equipment needed
- Number of litter/ambulatory
- Security at site
- Method of marking
- Patient nationality
- NBC contamination

## Technical Procedures

### Frequency Management
**Combat Frequency Plan**
- Primary tactical
- Alternate tactical
- Command net
- Fire support net
- Medical net
- Logistics net

**Frequency Changes**
- Time-based rotation
- Event-based triggers
- Compromise indicators
- Jamming response
- Emergency codes

### Power Management
**Emission Control**
- Minimum power use
- Directional transmission
- Scheduled windows
- Listen-only periods
- Emergency breaks

**Battery Conservation**
- Short transmissions
- Scheduled reports
- Sleep modes
- Solar charging
- Spare rotation

## Visual Communication

### Standard Signals
**Arm and Hand**
- Halt: Fist up
- Move out: Arm forward
- Down: Arm sweep down
- Enemy: Weapon pointed
- Rally: Arm circling

**Pyrotechnics**
- Red: Enemy contact
- Green: Friendly position
- White: Illumination
- Yellow: Mark location
- Combinations: Preset meanings

### Improvised Signals
- Mirror flashes
- Panel markers
- Smoke colors
- Ground symbols
- Laser pointers

## Special Situations

### Ambush Communication
**If Ambushed**
1. "CONTACT [direction]!" (immediate)
2. Return fire (suppress)
3. Detailed report (when able)
4. Request support
5. Update status

**Communication Discipline**
- Essential traffic only
- No position compromise
- Authentication critical
- Deception possible
- Monitor for orders

### Boarding Operations
**Team Coordination**
- Preset channels
- Code words ready
- Silent periods
- Progress reports
- Emergency extraction

**Jamming Expected**
- Physical touch signals
- Infrared markers
- Predetermined timing
- Written messages
- Runner system

### Electronic Warfare Environment
**High EW Threat**
- Minimal transmissions
- False traffic generation
- Decoy transmitters
- Message runners
- Dead drops

## Training Requirements

### Individual Skills
- Radio operation
- Phonetic alphabet
- Authentication procedures
- Report formats
- Emergency signals

### Unit Training
- Jamming response drills
- Degraded comm exercises
- Runner procedures
- Signal recognition
- Net discipline

## Common Errors

### During Combat
- Panic broadcasting
- Excessive detail
- Poor authentication
- Channel congestion
- Security violations

### Prevention Methods
- Regular drills
- Stress inoculation
- Checklist use
- Leader supervision
- After-action reviews

## Quick Reference Card

### Emergency Transmissions
**Format**: "[BREAK×3] [Call sign] [FLASH] [Message] [OUT]"

### Standard Responses
- "ROGER" = Understood
- "WILCO" = Will comply
- "OUT" = End transmission
- "WAIT" = Stand by
- "SAY AGAIN" = Repeat

### Prowords
- "BREAK" = Pause between messages
- "CORRECTION" = Error made
- "DISREGARD" = Cancel last
- "EXECUTE" = Do it now
- "INTERROGATIVE" = Question follows

## Technology Integration

### Digital Systems
- Text backup capability
- Automatic retransmission
- Error correction
- Encryption built-in
- Position reporting

### Hybrid Operations
- Voice primary
- Digital backup
- Visual confirmation
- Physical courier
- All methods ready

## After Action Requirements

### Communication Logs
- Time stamps
- Stations involved
- Message content
- Actions taken
- Problems encountered

### Lessons Learned
- What worked
- What failed
- Enemy tactics
- Equipment issues
- Training needs

## References
- 7.1.1 Radio Discipline & Brevity Codes
- 7.1.2 Frequency Management Procedure
- 7.1.3 Secure Communication Guidelines
- 8.1.1 Ejection & Survival Procedure''',
                'difficulty_level': 'Intermediate',
                'is_required': True,
                'tags': ['communication', 'combat', 'radio', 'procedures', 'guidelines']
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