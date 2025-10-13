# Additional methodologies to insert before the closing brace of self.methodologies

            'crystal': {
                'name': 'Crystal',
                'type': 'Agile',
                'description': 'Family of agile methodologies tailored by project size and criticality',
                'variants': ['Crystal Clear', 'Crystal Yellow', 'Crystal Orange', 'Crystal Red'],
                'key_principles': [
                    'Frequent Delivery',
                    'Reflective Improvement',
                    'Osmotic Communication',
                    'Personal Safety',
                    'Focus',
                    'Easy Access to Expert Users',
                    'Technical Environment with Automated Tests'
                ],
                'key_deliverables': [
                    'Iteration Plan',
                    'Reflection Workshop Notes',
                    'User Stories',
                    'Working Software'
                ],
                'best_for': 'Projects requiring methodology tailored to team size',
                'document_characteristics': {
                    'formality': 'Low',
                    'detail_level': 'Adaptive',
                    'change_control': 'Flexible',
                    'documentation_volume': 'Minimal'
                }
            },
            
            'fdd': {
                'name': 'Feature-Driven Development (FDD)',
                'type': 'Agile',
                'description': 'Model-driven short iteration process',
                'processes': [
                    'Develop Overall Model',
                    'Build Feature List',
                    'Plan by Feature',
                    'Design by Feature',
                    'Build by Feature'
                ],
                'key_roles': ['Chief Architect', 'Development Manager', 'Chief Programmer', 'Class Owner'],
                'key_deliverables': [
                    'Domain Object Model',
                    'Feature List',
                    'Feature Sets',
                    'Design Package',
                    'Build Package'
                ],
                'best_for': 'Larger teams requiring model-driven approach',
                'document_characteristics': {
                    'formality': 'Moderate',
                    'detail_level': 'Model-Focused',
                    'change_control': 'Feature-Based',
                    'documentation_volume': 'Moderate'
                }
            },
            
            'dsdm': {
                'name': 'Dynamic Systems Development Method (DSDM)',
                'type': 'Agile',
                'description': 'Agile project delivery framework',
                'principles': [
                    'Focus on Business Need',
                    'Deliver on Time',
                    'Collaborate',
                    'Never Compromise Quality',
                    'Build Incrementally from Firm Foundations',
                    'Develop Iteratively',
                    'Communicate Continuously and Clearly',
                    'Demonstrate Control'
                ],
                'phases': ['Pre-Project', 'Feasibility', 'Foundations', 'Evolutionary Development', 'Deployment', 'Post-Project'],
                'key_deliverables': [
                    'Business Case',
                    'Prioritized Requirements List',
                    'Solution Architecture',
                    'Evolutionary Prototypes',
                    'Deployed Solution'
                ],
                'best_for': 'Business-focused agile projects',
                'document_characteristics': {
                    'formality': 'Moderate',
                    'detail_level': 'Business-Focused',
                    'change_control': 'Timeboxed',
                    'documentation_volume': 'Moderate'
                }
            },
            
            'dad': {
                'name': 'Disciplined Agile Delivery (DAD)',
                'type': 'Hybrid',
                'description': 'People-first, learning-oriented hybrid approach',
                'lifecycle_phases': ['Inception', 'Construction', 'Transition'],
                'key_principles': [
                    'Delight Customers',
                    'Be Awesome',
                    'Context Counts',
                    'Choice is Good',
                    'Optimize Flow',
                    'Enterprise Awareness'
                ],
                'key_deliverables': [
                    'Vision Document',
                    'Architecture Roadmap',
                    'Iteration Plan',
                    'Working Solution',
                    'Release Plan'
                ],
                'best_for': 'Enterprise agile with governance needs',
                'document_characteristics': {
                    'formality': 'Moderate',
                    'detail_level': 'Contextual',
                    'change_control': 'Governed',
                    'documentation_volume': 'Moderate'
                }
            },
            
            'less': {
                'name': 'Large-Scale Scrum (LeSS)',
                'type': 'Scaled Agile',
                'description': 'Scrum applied to many teams working together',
                'principles': [
                    'Large-Scale Scrum is Scrum',
                    'Empirical Process Control',
                    'Transparency',
                    'More with Less',
                    'Whole Product Focus',
                    'Customer-Centric',
                    'Continuous Improvement',
                    'Lean Thinking',
                    'Systems Thinking'
                ],
                'key_events': [
                    'Sprint Planning One',
                    'Sprint Planning Two',
                    'Daily Scrum',
                    'Product Backlog Refinement',
                    'Sprint Review',
                    'Overall Retrospective'
                ],
                'key_deliverables': [
                    'Product Backlog',
                    'Sprint Backlogs',
                    'Definition of Done',
                    'Potentially Shippable Product Increment'
                ],
                'best_for': 'Scaling Scrum to 2-8 teams',
                'document_characteristics': {
                    'formality': 'Low',
                    'detail_level': 'Scrum-Based',
                    'change_control': 'Sprint-Based',
                    'documentation_volume': 'Minimal'
                }
            },
            
            'nexus': {
                'name': 'Nexus',
                'type': 'Scaled Agile',
                'description': 'Framework for scaling Scrum',
                'roles': ['Nexus Integration Team', 'Product Owner', 'Scrum Masters', 'Development Teams'],
                'artifacts': ['Nexus Sprint Backlog', 'Integrated Increment'],
                'events': [
                    'Nexus Sprint Planning',
                    'Nexus Daily Scrum',
                    'Nexus Sprint Review',
                    'Nexus Sprint Retrospective'
                ],
                'key_deliverables': [
                    'Nexus Sprint Backlog',
                    'Integrated Increment',
                    'Integration Issues Log',
                    'Nexus Sprint Goal'
                ],
                'best_for': 'Scaling Scrum to 3-9 teams',
                'document_characteristics': {
                    'formality': 'Low',
                    'detail_level': 'Integration-Focused',
                    'change_control': 'Sprint-Based',
                    'documentation_volume': 'Minimal'
                }
            },
            
            'spotify_model': {
                'name': 'Spotify Model',
                'type': 'Scaled Agile',
                'description': 'Agile scaling model based on autonomous squads',
                'organizational_units': ['Squads', 'Tribes', 'Chapters', 'Guilds'],
                'key_principles': [
                    'Autonomy',
                    'Alignment',
                    'Minimum Viable Bureaucracy',
                    'Community over Structure',
                    'Trust over Control'
                ],
                'key_deliverables': [
                    'Squad Mission',
                    'Tribe Objectives',
                    'Chapter Guidelines',
                    'Guild Knowledge Sharing'
                ],
                'best_for': 'Large organizations seeking autonomous teams',
                'document_characteristics': {
                    'formality': 'Very Low',
                    'detail_level': 'Minimal',
                    'change_control': 'Autonomous',
                    'documentation_volume': 'Minimal'
                }
            },
            
            'cpm': {
                'name': 'Critical Path Method (CPM)',
                'type': 'Traditional',
                'description': 'Algorithm for scheduling project activities',
                'key_concepts': [
                    'Activity Network Diagram',
                    'Critical Path',
                    'Float/Slack',
                    'Forward Pass',
                    'Backward Pass',
                    'Early Start/Finish',
                    'Late Start/Finish'
                ],
                'key_deliverables': [
                    'Network Diagram',
                    'Critical Path Analysis',
                    'Schedule with Float',
                    'Activity List with Dependencies'
                ],
                'best_for': 'Complex projects with many interdependencies',
                'document_characteristics': {
                    'formality': 'High',
                    'detail_level': 'Detailed',
                    'change_control': 'Formal',
                    'documentation_volume': 'Extensive'
                }
            },
            
            'itil': {
                'name': 'ITIL (IT Infrastructure Library)',
                'type': 'IT Service Management',
                'description': 'Framework for IT service management',
                'service_lifecycle': [
                    'Service Strategy',
                    'Service Design',
                    'Service Transition',
                    'Service Operation',
                    'Continual Service Improvement'
                ],
                'key_processes': [
                    'Incident Management',
                    'Problem Management',
                    'Change Management',
                    'Service Level Management',
                    'Configuration Management'
                ],
                'key_deliverables': [
                    'Service Catalog',
                    'Service Level Agreement (SLA)',
                    'Change Request',
                    'Incident Report',
                    'Configuration Management Database (CMDB)'
                ],
                'best_for': 'IT service delivery and support',
                'document_characteristics': {
                    'formality': 'High',
                    'detail_level': 'Process-Oriented',
                    'change_control': 'Formal',
                    'documentation_volume': 'Extensive'
                }
            },
            
            'design_thinking': {
                'name': 'Design Thinking',
                'type': 'Specialized',
                'description': 'Human-centered approach to innovation',
                'phases': ['Empathize', 'Define', 'Ideate', 'Prototype', 'Test'],
                'key_principles': [
                    'Human-Centered',
                    'Collaborative',
                    'Iterative',
                    'Experimental',
                    'Bias Toward Action'
                ],
                'key_deliverables': [
                    'Empathy Map',
                    'Problem Statement',
                    'Ideation Session Notes',
                    'Prototypes',
                    'User Testing Results'
                ],
                'best_for': 'Innovation and user experience projects',
                'document_characteristics': {
                    'formality': 'Low',
                    'detail_level': 'Visual',
                    'change_control': 'Iterative',
                    'documentation_volume': 'Visual-Heavy'
                }
            },
            
            'construction_management': {
                'name': 'Construction Project Management',
                'type': 'Industry-Specific',
                'description': 'Methodology for construction projects',
                'phases': [
                    'Pre-Construction',
                    'Procurement',
                    'Construction',
                    'Commissioning',
                    'Close-Out'
                ],
                'key_principles': [
                    'Safety First',
                    'Quality Control',
                    'Cost Management',
                    'Schedule Adherence',
                    'Stakeholder Coordination'
                ],
                'key_deliverables': [
                    'Site Plan',
                    'Construction Schedule',
                    'Safety Plan',
                    'Quality Control Plan',
                    'As-Built Drawings',
                    'Punch List',
                    'Certificate of Occupancy'
                ],
                'best_for': 'Construction and infrastructure projects',
                'document_characteristics': {
                    'formality': 'High',
                    'detail_level': 'Technical',
                    'change_control': 'Change Orders',
                    'documentation_volume': 'Extensive'
                }
            },
            
            'manufacturing_pm': {
                'name': 'Manufacturing Project Management',
                'type': 'Industry-Specific',
                'description': 'Methodology for manufacturing projects',
                'key_concepts': [
                    'Production Planning',
                    'Capacity Planning',
                    'Quality Assurance',
                    'Supply Chain Management',
                    'Lean Manufacturing'
                ],
                'key_deliverables': [
                    'Production Schedule',
                    'Bill of Materials (BOM)',
                    'Quality Control Plan',
                    'Manufacturing Process Flow',
                    'Capacity Analysis',
                    'Inventory Management Plan'
                ],
                'best_for': 'Manufacturing and production projects',
                'document_characteristics': {
                    'formality': 'High',
                    'detail_level': 'Process-Detailed',
                    'change_control': 'Engineering Change Orders',
                    'documentation_volume': 'Extensive'
                }
            },

