"""
Comprehensive Project Management Methodology Knowledge Base
Covers ALL major PM methodologies with deep understanding of principles, practices, and deliverables
"""

from typing import Dict, List, Optional

class MethodologyKnowledge:
    """
    Complete knowledge base for all project management methodologies
    Enables AI to generate methodology-appropriate documents
    """
    
    def __init__(self):
        self.methodologies = {
            # TRADITIONAL METHODOLOGIES
            'waterfall': {
                'name': 'Waterfall',
                'type': 'Traditional',
                'description': 'Sequential design process with distinct phases',
                'phases': ['Requirements', 'Design', 'Implementation', 'Verification', 'Maintenance'],
                'key_principles': [
                    'Sequential progression through phases',
                    'Comprehensive documentation',
                    'Formal phase gate reviews',
                    'Detailed upfront planning'
                ],
                'key_deliverables': [
                    'Requirements Specification',
                    'Design Documents',
                    'Test Plans',
                    'User Manuals',
                    'Phase Gate Review Reports'
                ],
                'best_for': 'Projects with well-defined requirements and low uncertainty',
                'document_characteristics': {
                    'formality': 'High',
                    'detail_level': 'Comprehensive',
                    'change_control': 'Strict',
                    'documentation_volume': 'Extensive'
                }
            },
            
            'prince2': {
                'name': 'PRINCE2',
                'type': 'Traditional',
                'description': 'Process-based method for effective project management',
                'principles': [
                    'Continued Business Justification',
                    'Learn from Experience',
                    'Defined Roles and Responsibilities',
                    'Manage by Stages',
                    'Manage by Exception',
                    'Focus on Products',
                    'Tailor to Suit the Project Environment'
                ],
                'themes': [
                    'Business Case',
                    'Organization',
                    'Quality',
                    'Plans',
                    'Risk',
                    'Change',
                    'Progress'
                ],
                'processes': [
                    'Starting Up a Project (SU)',
                    'Directing a Project (DP)',
                    'Initiating a Project (IP)',
                    'Controlling a Stage (CS)',
                    'Managing Product Delivery (MP)',
                    'Managing a Stage Boundary (SB)',
                    'Closing a Project (CP)'
                ],
                'key_deliverables': [
                    'Project Brief',
                    'Project Initiation Documentation (PID)',
                    'Business Case',
                    'Product Descriptions',
                    'Highlight Reports',
                    'End Project Report'
                ],
                'best_for': 'Controlled environments requiring governance',
                'document_characteristics': {
                    'formality': 'Very High',
                    'detail_level': 'Comprehensive',
                    'change_control': 'Formal',
                    'documentation_volume': 'Extensive'
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
            
            # AGILE METHODOLOGIES
            'scrum': {
                'name': 'Scrum',
                'type': 'Agile',
                'description': 'Iterative and incremental agile framework',
                'roles': ['Product Owner', 'Scrum Master', 'Development Team'],
                'events': [
                    'Sprint',
                    'Sprint Planning',
                    'Daily Scrum',
                    'Sprint Review',
                    'Sprint Retrospective'
                ],
                'artifacts': [
                    'Product Backlog',
                    'Sprint Backlog',
                    'Increment',
                    'Definition of Done'
                ],
                'key_principles': [
                    'Empirical process control',
                    'Self-organizing teams',
                    'Time-boxed iterations',
                    'Continuous improvement'
                ],
                'key_deliverables': [
                    'Product Backlog',
                    'Sprint Backlog',
                    'Burndown Chart',
                    'Sprint Review Notes',
                    'Retrospective Action Items'
                ],
                'best_for': 'Complex products requiring flexibility and rapid delivery',
                'document_characteristics': {
                    'formality': 'Low',
                    'detail_level': 'Just Enough',
                    'change_control': 'Flexible',
                    'documentation_volume': 'Minimal'
                }
            },
            
            'kanban': {
                'name': 'Kanban',
                'type': 'Agile',
                'description': 'Visual workflow management method',
                'core_practices': [
                    'Visualize Workflow',
                    'Limit Work in Progress (WIP)',
                    'Manage Flow',
                    'Make Process Policies Explicit',
                    'Implement Feedback Loops',
                    'Improve Collaboratively'
                ],
                'key_metrics': [
                    'Cycle Time',
                    'Lead Time',
                    'Throughput',
                    'WIP Limits'
                ],
                'key_deliverables': [
                    'Kanban Board',
                    'Cumulative Flow Diagram',
                    'Cycle Time Report',
                    'WIP Limits Policy'
                ],
                'best_for': 'Continuous delivery and operational work',
                'document_characteristics': {
                    'formality': 'Very Low',
                    'detail_level': 'Visual',
                    'change_control': 'Continuous',
                    'documentation_volume': 'Minimal'
                }
            },
            
            'xp': {
                'name': 'Extreme Programming (XP)',
                'type': 'Agile',
                'description': 'Software development methodology emphasizing technical excellence',
                'values': ['Communication', 'Simplicity', 'Feedback', 'Courage', 'Respect'],
                'practices': [
                    'Pair Programming',
                    'Test-Driven Development (TDD)',
                    'Continuous Integration',
                    'Refactoring',
                    'Small Releases',
                    'Collective Code Ownership',
                    'Coding Standards',
                    'Sustainable Pace'
                ],
                'key_deliverables': [
                    'User Stories',
                    'Acceptance Tests',
                    'Iteration Plan',
                    'Code Standards Document'
                ],
                'best_for': 'Software development with changing requirements',
                'document_characteristics': {
                    'formality': 'Low',
                    'detail_level': 'Technical Focus',
                    'change_control': 'Continuous',
                    'documentation_volume': 'Code-Centric'
                }
            },
            
            'lean': {
                'name': 'Lean',
                'type': 'Agile',
                'description': 'Methodology focused on maximizing value and minimizing waste',
                'principles': [
                    'Eliminate Waste',
                    'Amplify Learning',
                    'Decide as Late as Possible',
                    'Deliver as Fast as Possible',
                    'Empower the Team',
                    'Build Integrity In',
                    'See the Whole'
                ],
                'waste_types': [
                    'Partially Done Work',
                    'Extra Features',
                    'Relearning',
                    'Handoffs',
                    'Delays',
                    'Task Switching',
                    'Defects'
                ],
                'key_deliverables': [
                    'Value Stream Map',
                    'Waste Analysis',
                    'A3 Problem Solving',
                    'Kaizen Events Log'
                ],
                'best_for': 'Process optimization and waste reduction',
                'document_characteristics': {
                    'formality': 'Low',
                    'detail_level': 'Value-Focused',
                    'change_control': 'Continuous',
                    'documentation_volume': 'Lean'
                }
            },
            
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
            
            # HYBRID METHODOLOGIES
            'scrumban': {
                'name': 'Scrumban',
                'type': 'Hybrid',
                'description': 'Combination of Scrum and Kanban',
                'key_elements': [
                    'Scrum roles and events',
                    'Kanban board and WIP limits',
                    'Pull-based workflow',
                    'Continuous improvement'
                ],
                'key_deliverables': [
                    'Scrumban Board',
                    'Backlog',
                    'Retrospective Notes',
                    'Flow Metrics'
                ],
                'best_for': 'Transitioning from Scrum to continuous flow',
                'document_characteristics': {
                    'formality': 'Low',
                    'detail_level': 'Balanced',
                    'change_control': 'Flexible',
                    'documentation_volume': 'Moderate'
                }
            },
            
            'water_scrum_fall': {
                'name': 'Water-Scrum-Fall',
                'type': 'Hybrid',
                'description': 'Waterfall planning and closure with Scrum execution',
                'phases': [
                    'Waterfall Requirements Phase',
                    'Scrum Development Sprints',
                    'Waterfall Testing and Deployment'
                ],
                'key_deliverables': [
                    'Requirements Document',
                    'Sprint Backlogs',
                    'Test Plans',
                    'Deployment Plan'
                ],
                'best_for': 'Organizations transitioning to agile',
                'document_characteristics': {
                    'formality': 'Mixed',
                    'detail_level': 'Variable by Phase',
                    'change_control': 'Phase-Dependent',
                    'documentation_volume': 'Moderate to High'
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
            
            # SPECIALIZED METHODOLOGIES
            'six_sigma': {
                'name': 'Six Sigma',
                'type': 'Specialized',
                'description': 'Data-driven methodology for process improvement',
                'phases': ['Define', 'Measure', 'Analyze', 'Improve', 'Control'],
                'key_principles': [
                    'Focus on customer requirements',
                    'Data-driven decision making',
                    'Process focus',
                    'Proactive management',
                    'Collaboration'
                ],
                'key_deliverables': [
                    'Project Charter',
                    'SIPOC Diagram',
                    'Process Map',
                    'Data Collection Plan',
                    'Statistical Analysis',
                    'Control Plan'
                ],
                'best_for': 'Quality improvement and defect reduction',
                'document_characteristics': {
                    'formality': 'High',
                    'detail_level': 'Statistical',
                    'change_control': 'Data-Driven',
                    'documentation_volume': 'Extensive'
                }
            },
            
            'critical_chain': {
                'name': 'Critical Chain Project Management (CCPM)',
                'type': 'Specialized',
                'description': 'Method based on Theory of Constraints',
                'key_concepts': [
                    'Resource dependencies',
                    'Buffer management',
                    'Eliminate multitasking',
                    'Focus on critical chain'
                ],
                'key_deliverables': [
                    'Critical Chain Schedule',
                    'Buffer Management Report',
                    'Resource Loading Chart',
                    'Fever Chart'
                ],
                'best_for': 'Resource-constrained environments',
                'document_characteristics': {
                    'formality': 'Moderate',
                    'detail_level': 'Resource-Focused',
                    'change_control': 'Buffer-Based',
                    'documentation_volume': 'Moderate'
                }
            },
            
            'devops': {
                'name': 'DevOps',
                'type': 'Specialized',
                'description': 'Culture and practices for software delivery',
                'key_practices': [
                    'Continuous Integration',
                    'Continuous Delivery',
                    'Infrastructure as Code',
                    'Monitoring and Logging',
                    'Collaboration and Communication'
                ],
                'key_deliverables': [
                    'CI/CD Pipeline Configuration',
                    'Infrastructure Code',
                    'Deployment Runbook',
                    'Monitoring Dashboard',
                    'Incident Response Plan'
                ],
                'best_for': 'Software delivery and operations',
                'document_characteristics': {
                    'formality': 'Low',
                    'detail_level': 'Technical',
                    'change_control': 'Automated',
                    'documentation_volume': 'Code-Based'
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
            
            # SCALED AGILE
            'safe': {
                'name': 'Scaled Agile Framework (SAFe)',
                'type': 'Scaled Agile',
                'description': 'Framework for scaling agile across enterprise',
                'levels': ['Team', 'Program', 'Large Solution', 'Portfolio'],
                'core_values': ['Alignment', 'Built-in Quality', 'Transparency', 'Program Execution'],
                'key_events': [
                    'PI Planning',
                    'System Demo',
                    'Inspect and Adapt',
                    'ART Sync'
                ],
                'key_deliverables': [
                    'Program Backlog',
                    'PI Objectives',
                    'Feature Cards',
                    'Solution Intent',
                    'Portfolio Canvas'
                ],
                'best_for': 'Large-scale agile transformation',
                'document_characteristics': {
                    'formality': 'Moderate',
                    'detail_level': 'Scaled',
                    'change_control': 'PI-Based',
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
            
            # INDUSTRY-SPECIFIC
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
            }
        }
    
    def get_methodology(self, methodology_name: str) -> Optional[Dict]:
        """Get methodology details by name (case-insensitive)"""
        method_lower = methodology_name.lower().replace(' ', '_').replace('-', '_')
        
        # Direct match
        if method_lower in self.methodologies:
            return self.methodologies[method_lower]
        
        # Partial match
        for key, method in self.methodologies.items():
            if method_lower in key or key in method_lower:
                return method
            if method_lower in method['name'].lower():
                return method
        
        return None
    
    def get_methodology_for_document(self, document_name: str, project_context: str = '') -> str:
        """Infer appropriate methodology from document name and context"""
        doc_lower = document_name.lower()
        context_lower = project_context.lower()
        
        # Agile indicators
        agile_keywords = ['sprint', 'backlog', 'scrum', 'kanban', 'user story', 'iteration']
        if any(keyword in doc_lower or keyword in context_lower for keyword in agile_keywords):
            if 'sprint' in doc_lower or 'scrum' in context_lower:
                return 'scrum'
            elif 'kanban' in doc_lower or 'board' in doc_lower:
                return 'kanban'
            return 'scrum'  # Default agile
        
        # Six Sigma indicators
        if any(word in doc_lower for word in ['dmaic', 'sigma', 'defect', 'statistical']):
            return 'six_sigma'
        
        # DevOps indicators
        if any(word in doc_lower for word in ['pipeline', 'deployment', 'ci/cd', 'infrastructure']):
            return 'devops'
        
        # SAFe indicators
        if any(word in doc_lower for word in ['pi ', 'art', 'program increment', 'portfolio']):
            return 'safe'
        
        # Default to waterfall for traditional PM documents
        return 'waterfall'
    
    def adapt_document_to_methodology(self, document_type: str, methodology: str) -> Dict:
        """Adapt document structure and content based on methodology"""
        # Handle methodology as either string or dict
        if isinstance(methodology, dict):
            methodology_name = methodology.get('name', 'waterfall')
        else:
            methodology_name = methodology if methodology else 'waterfall'
        
        method = self.get_methodology(methodology_name)
        if not method:
            method = self.methodologies['waterfall']  # Default
        
        return {
            'methodology': method['name'],
            'formality': method['document_characteristics']['formality'],
            'detail_level': method['document_characteristics']['detail_level'],
            'change_control': method['document_characteristics']['change_control'],
            'documentation_volume': method['document_characteristics']['documentation_volume'],
            'terminology': self._get_methodology_terminology(methodology_name),
            'structure_guidance': self._get_structure_guidance(document_type, methodology_name)
        }
    
    def _get_methodology_terminology(self, methodology: str) -> Dict[str, str]:
        """Get methodology-specific terminology"""
        # Handle methodology as either string or dict
        if isinstance(methodology, dict):
            methodology = methodology.get('name', 'waterfall').lower().replace(' ', '_').replace('-', '_')
        else:
            methodology = methodology.lower().replace(' ', '_').replace('-', '_') if methodology else 'waterfall'
        terminology_map = {
            'scrum': {
                'requirements': 'User Stories',
                'plan': 'Sprint Backlog',
                'meeting': 'Ceremony',
                'milestone': 'Sprint Goal',
                'team_lead': 'Scrum Master',
                'stakeholder': 'Product Owner'
            },
            'waterfall': {
                'requirements': 'Requirements Specification',
                'plan': 'Project Plan',
                'meeting': 'Review Meeting',
                'milestone': 'Phase Gate',
                'team_lead': 'Project Manager',
                'stakeholder': 'Stakeholder'
            },
            'kanban': {
                'requirements': 'Work Items',
                'plan': 'Kanban Board',
                'meeting': 'Standup',
                'milestone': 'Delivery',
                'team_lead': 'Flow Manager',
                'stakeholder': 'Customer'
            },
            'prince2': {
                'requirements': 'Product Descriptions',
                'plan': 'Stage Plan',
                'meeting': 'Checkpoint',
                'milestone': 'Stage Boundary',
                'team_lead': 'Project Manager',
                'stakeholder': 'Senior User'
            }
        }
        return terminology_map.get(methodology, terminology_map['waterfall'])
    
    def _get_structure_guidance(self, document_type: str, methodology: str) -> List[str]:
        """Get structure guidance for document type and methodology"""
        # Handle methodology as either string or dict
        if isinstance(methodology, dict):
            methodology = methodology.get('name', 'waterfall')
        methodology = methodology if methodology else 'waterfall'
        return [
            f"Use {methodology}-appropriate terminology",
            f"Follow {methodology} documentation standards",
            f"Include {methodology}-specific sections",
            "Align with methodology best practices"
        ]

# Global instance
methodology_knowledge = MethodologyKnowledge()

