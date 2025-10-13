"""
PMI 2025 PMBOK Knowledge Base
Complete implementation of PMI 2025 PMBOK standards for AI document generation
"""

from typing import Dict, List

class PMBOK2025Knowledge:
    """
    Comprehensive PMI 2025 PMBOK knowledge base
    Includes all process groups, knowledge areas, processes, inputs, tools & techniques, and outputs
    """
    
    def __init__(self):
        # PMI 2025 Process Groups
        self.process_groups = {
            'initiating': {
                'name': 'Initiating',
                'description': 'Processes performed to define a new project or phase by obtaining authorization',
                'key_outputs': ['Project Charter', 'Stakeholder Register']
            },
            'planning': {
                'name': 'Planning',
                'description': 'Processes required to establish scope, refine objectives, and define course of action',
                'key_outputs': ['Project Management Plan', 'Project Documents']
            },
            'executing': {
                'name': 'Executing',
                'description': 'Processes performed to complete work defined in project management plan',
                'key_outputs': ['Deliverables', 'Work Performance Data']
            },
            'monitoring_controlling': {
                'name': 'Monitoring and Controlling',
                'description': 'Processes required to track, review, and regulate progress and performance',
                'key_outputs': ['Work Performance Reports', 'Change Requests']
            },
            'closing': {
                'name': 'Closing',
                'description': 'Processes performed to formally complete or close project or phase',
                'key_outputs': ['Final Product/Service', 'Lessons Learned']
            }
        }
        
        # PMI 2025 Knowledge Areas
        self.knowledge_areas = {
            'integration': {
                'name': 'Project Integration Management',
                'description': 'Processes and activities to identify, define, combine, unify, and coordinate',
                'key_documents': ['Project Charter', 'Project Management Plan', 'Change Requests'],
                'processes': [
                    'Develop Project Charter',
                    'Develop Project Management Plan',
                    'Direct and Manage Project Work',
                    'Manage Project Knowledge',
                    'Monitor and Control Project Work',
                    'Perform Integrated Change Control',
                    'Close Project or Phase'
                ]
            },
            'scope': {
                'name': 'Project Scope Management',
                'description': 'Processes to ensure project includes all work required',
                'key_documents': ['Scope Management Plan', 'Requirements Documentation', 'WBS', 'Scope Baseline'],
                'processes': [
                    'Plan Scope Management',
                    'Collect Requirements',
                    'Define Scope',
                    'Create WBS',
                    'Validate Scope',
                    'Control Scope'
                ]
            },
            'schedule': {
                'name': 'Project Schedule Management',
                'description': 'Processes to manage timely completion of project',
                'key_documents': ['Schedule Management Plan', 'Activity List', 'Project Schedule', 'Schedule Baseline'],
                'processes': [
                    'Plan Schedule Management',
                    'Define Activities',
                    'Sequence Activities',
                    'Estimate Activity Durations',
                    'Develop Schedule',
                    'Control Schedule'
                ]
            },
            'cost': {
                'name': 'Project Cost Management',
                'description': 'Processes involved in planning, estimating, budgeting, and controlling costs',
                'key_documents': ['Cost Management Plan', 'Cost Estimates', 'Budget', 'Cost Baseline'],
                'processes': [
                    'Plan Cost Management',
                    'Estimate Costs',
                    'Determine Budget',
                    'Control Costs'
                ]
            },
            'quality': {
                'name': 'Project Quality Management',
                'description': 'Processes for incorporating organization quality policy',
                'key_documents': ['Quality Management Plan', 'Quality Metrics', 'Quality Reports'],
                'processes': [
                    'Plan Quality Management',
                    'Manage Quality',
                    'Control Quality'
                ]
            },
            'resource': {
                'name': 'Project Resource Management',
                'description': 'Processes to identify, acquire, and manage resources',
                'key_documents': ['Resource Management Plan', 'Resource Calendar', 'Resource Breakdown Structure'],
                'processes': [
                    'Plan Resource Management',
                    'Estimate Activity Resources',
                    'Acquire Resources',
                    'Develop Team',
                    'Manage Team',
                    'Control Resources'
                ]
            },
            'communications': {
                'name': 'Project Communications Management',
                'description': 'Processes to ensure timely and appropriate information',
                'key_documents': ['Communications Management Plan', 'Project Communications', 'Performance Reports'],
                'processes': [
                    'Plan Communications Management',
                    'Manage Communications',
                    'Monitor Communications'
                ]
            },
            'risk': {
                'name': 'Project Risk Management',
                'description': 'Processes for conducting risk management planning and activities',
                'key_documents': ['Risk Management Plan', 'Risk Register', 'Risk Report'],
                'processes': [
                    'Plan Risk Management',
                    'Identify Risks',
                    'Perform Qualitative Risk Analysis',
                    'Perform Quantitative Risk Analysis',
                    'Plan Risk Responses',
                    'Implement Risk Responses',
                    'Monitor Risks'
                ]
            },
            'procurement': {
                'name': 'Project Procurement Management',
                'description': 'Processes to purchase or acquire products, services, or results',
                'key_documents': ['Procurement Management Plan', 'Procurement Strategy', 'Agreements'],
                'processes': [
                    'Plan Procurement Management',
                    'Conduct Procurements',
                    'Control Procurements'
                ]
            },
            'stakeholder': {
                'name': 'Project Stakeholder Management',
                'description': 'Processes to identify and manage stakeholders',
                'key_documents': ['Stakeholder Register', 'Stakeholder Engagement Plan', 'Stakeholder Engagement Assessment'],
                'processes': [
                    'Identify Stakeholders',
                    'Plan Stakeholder Engagement',
                    'Manage Stakeholder Engagement',
                    'Monitor Stakeholder Engagement'
                ]
            }
        }
        
        # PMI 2025 Standard Terminology
        self.terminology = {
            'project': 'A temporary endeavor undertaken to create a unique product, service, or result',
            'project_management': 'The application of knowledge, skills, tools, and techniques to project activities',
            'program': 'A group of related projects managed in a coordinated manner',
            'portfolio': 'Projects, programs, subsidiary portfolios, and operations managed as a group',
            'deliverable': 'Any unique and verifiable product, result, or capability',
            'milestone': 'A significant point or event in a project',
            'baseline': 'The approved version of a work product that can be changed only through formal change control',
            'work_package': 'The work defined at the lowest level of the WBS',
            'critical_path': 'The sequence of activities that represents the longest path through a project',
            'earned_value': 'A measure of work performed expressed in terms of the budget authorized',
            'risk': 'An uncertain event or condition that, if it occurs, has a positive or negative effect',
            'issue': 'A current condition or situation that may impact project objectives',
            'assumption': 'A factor considered to be true, real, or certain without proof or demonstration',
            'constraint': 'A limiting factor that affects the execution of a project',
            'change_request': 'A formal proposal to modify any document, deliverable, or baseline'
        }
        
        # Document Templates by Knowledge Area
        self.document_templates = {
            'integration': [
                'Project Charter',
                'Project Management Plan',
                'Change Request Form',
                'Change Log',
                'Lessons Learned Register',
                'Project Closure Report'
            ],
            'scope': [
                'Scope Management Plan',
                'Requirements Documentation',
                'Requirements Traceability Matrix',
                'Work Breakdown Structure (WBS)',
                'WBS Dictionary',
                'Scope Statement'
            ],
            'schedule': [
                'Schedule Management Plan',
                'Activity List',
                'Network Diagram',
                'Gantt Chart',
                'Milestone List',
                'Schedule Baseline'
            ],
            'cost': [
                'Cost Management Plan',
                'Cost Estimates',
                'Budget',
                'Cost Baseline',
                'Earned Value Report'
            ],
            'quality': [
                'Quality Management Plan',
                'Quality Metrics',
                'Quality Checklist',
                'Quality Audit Report',
                'Test Plan'
            ],
            'resource': [
                'Resource Management Plan',
                'Resource Calendar',
                'Resource Breakdown Structure',
                'Team Charter',
                'Resource Histogram'
            ],
            'communications': [
                'Communications Management Plan',
                'Stakeholder Communication Matrix',
                'Status Report',
                'Meeting Minutes',
                'Communication Log'
            ],
            'risk': [
                'Risk Management Plan',
                'Risk Register',
                'Risk Breakdown Structure',
                'Probability and Impact Matrix',
                'Risk Report'
            ],
            'procurement': [
                'Procurement Management Plan',
                'Procurement Strategy',
                'Statement of Work (SOW)',
                'Vendor Selection Criteria',
                'Contract'
            ],
            'stakeholder': [
                'Stakeholder Register',
                'Stakeholder Engagement Plan',
                'Stakeholder Analysis Matrix',
                'Power/Interest Grid',
                'Stakeholder Engagement Assessment'
            ]
        }
    
    def get_knowledge_area_for_document(self, document_name: str) -> str:
        """Determine which knowledge area a document belongs to"""
        doc_lower = document_name.lower()
        
        # Check each knowledge area's documents
        for area, documents in self.document_templates.items():
            for doc in documents:
                if doc.lower() in doc_lower or doc_lower in doc.lower():
                    return self.knowledge_areas[area]['name']
        
        # Keyword-based fallback
        if 'risk' in doc_lower:
            return self.knowledge_areas['risk']['name']
        elif 'cost' in doc_lower or 'budget' in doc_lower or 'financial' in doc_lower:
            return self.knowledge_areas['cost']['name']
        elif 'schedule' in doc_lower or 'timeline' in doc_lower or 'gantt' in doc_lower:
            return self.knowledge_areas['schedule']['name']
        elif 'scope' in doc_lower or 'wbs' in doc_lower or 'requirement' in doc_lower:
            return self.knowledge_areas['scope']['name']
        elif 'stakeholder' in doc_lower:
            return self.knowledge_areas['stakeholder']['name']
        elif 'quality' in doc_lower:
            return self.knowledge_areas['quality']['name']
        elif 'resource' in doc_lower or 'team' in doc_lower:
            return self.knowledge_areas['resource']['name']
        elif 'communication' in doc_lower:
            return self.knowledge_areas['communications']['name']
        elif 'procurement' in doc_lower or 'vendor' in doc_lower or 'contract' in doc_lower:
            return self.knowledge_areas['procurement']['name']
        else:
            return self.knowledge_areas['integration']['name']
    
    def get_pmbok_guidance(self, document_name: str) -> Dict:
        """Get PMBOK-specific guidance for a document"""
        knowledge_area_name = self.get_knowledge_area_for_document(document_name)
        
        # Find the knowledge area key
        knowledge_area_key = None
        for key, area in self.knowledge_areas.items():
            if area['name'] == knowledge_area_name:
                knowledge_area_key = key
                break
        
        if not knowledge_area_key:
            knowledge_area_key = 'integration'
        
        area = self.knowledge_areas[knowledge_area_key]
        
        return {
            'knowledge_area': area['name'],
            'description': area['description'],
            'related_processes': area['processes'],
            'related_documents': area['key_documents'],
            'pmbok_standards': self._get_pmbok_standards(knowledge_area_key),
            'best_practices': self._get_pmbok_best_practices(knowledge_area_key)
        }
    
    def _get_pmbok_standards(self, knowledge_area: str) -> List[str]:
        """Get PMBOK standards for a knowledge area"""
        standards = {
            'integration': [
                'Ensure all project components are properly coordinated',
                'Maintain project management plan as single source of truth',
                'Use formal change control process for all changes',
                'Document lessons learned throughout project lifecycle'
            ],
            'scope': [
                'Define and control what is and is not included in project',
                'Use WBS to decompose work into manageable components',
                'Maintain requirements traceability throughout project',
                'Validate deliverables with stakeholders before acceptance'
            ],
            'schedule': [
                'Develop realistic schedule based on resource availability',
                'Identify and manage critical path',
                'Use network diagrams to show activity dependencies',
                'Monitor schedule performance using earned value'
            ],
            'cost': [
                'Establish cost baseline for performance measurement',
                'Use three-point estimating for accuracy',
                'Monitor cost performance using earned value management',
                'Control costs through formal change control'
            ],
            'quality': [
                'Plan quality into project from the beginning',
                'Focus on prevention over inspection',
                'Use quality metrics to measure performance',
                'Conduct regular quality audits'
            ],
            'resource': [
                'Plan for resource acquisition and allocation',
                'Develop team through training and team building',
                'Manage team performance and conflicts',
                'Release resources appropriately at project end'
            ],
            'communications': [
                'Plan communications based on stakeholder needs',
                'Use appropriate communication methods and technologies',
                'Monitor communication effectiveness',
                'Maintain communication records'
            ],
            'risk': [
                'Identify risks early and continuously',
                'Assess risks qualitatively and quantitatively',
                'Develop proactive risk response strategies',
                'Monitor risks and implement responses as needed'
            ],
            'procurement': [
                'Plan procurements based on make-or-buy analysis',
                'Use appropriate contract types',
                'Manage vendor relationships professionally',
                'Close procurements formally'
            ],
            'stakeholder': [
                'Identify all stakeholders early',
                'Analyze stakeholder power and interest',
                'Engage stakeholders appropriately',
                'Monitor stakeholder engagement continuously'
            ]
        }
        return standards.get(knowledge_area, standards['integration'])
    
    def _get_pmbok_best_practices(self, knowledge_area: str) -> List[str]:
        """Get PMBOK best practices for a knowledge area"""
        practices = {
            'integration': [
                'Develop comprehensive project charter with executive sponsorship',
                'Create integrated project management plan covering all knowledge areas',
                'Hold regular project review meetings',
                'Use project management information system (PMIS)'
            ],
            'scope': [
                'Involve stakeholders in requirements gathering',
                'Create detailed WBS with work packages',
                'Establish clear scope boundaries',
                'Use formal scope verification process'
            ],
            'schedule': [
                'Use critical path method for scheduling',
                'Build in appropriate schedule reserves',
                'Update schedule regularly based on actual progress',
                'Use schedule compression techniques when needed'
            ],
            'cost': [
                'Develop detailed cost estimates with supporting documentation',
                'Establish cost baseline with management reserve',
                'Track actual costs against budget regularly',
                'Use forecasting to predict final costs'
            ],
            'quality': [
                'Define quality standards and metrics upfront',
                'Implement quality assurance processes',
                'Conduct regular quality control inspections',
                'Use statistical sampling when appropriate'
            ],
            'resource': [
                'Create resource breakdown structure (RBS)',
                'Use resource leveling to optimize allocation',
                'Provide team development opportunities',
                'Recognize and reward team performance'
            ],
            'communications': [
                'Create stakeholder communication matrix',
                'Use multiple communication channels',
                'Establish regular reporting cadence',
                'Maintain project information repository'
            ],
            'risk': [
                'Create risk breakdown structure (RBS)',
                'Use probability and impact matrix',
                'Maintain risk register with regular updates',
                'Allocate contingency reserves for identified risks'
            ],
            'procurement': [
                'Conduct thorough make-or-buy analysis',
                'Develop clear statement of work (SOW)',
                'Use objective vendor selection criteria',
                'Manage contracts proactively'
            ],
            'stakeholder': [
                'Create power/interest grid for stakeholder analysis',
                'Develop tailored engagement strategies',
                'Monitor stakeholder sentiment regularly',
                'Address stakeholder concerns promptly'
            ]
        }
        return practices.get(knowledge_area, practices['integration'])

# Global instance
pmbok_knowledge = PMBOK2025Knowledge()

