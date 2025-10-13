"""
PM Document Intelligence Module
Built-in intelligence for generating ANY project management document
Understands ALL high-value PM documents beyond the template library
"""

import re
from typing import Dict, List, Tuple, Optional

class PMDocumentIntelligence:
    """
    Intelligent system that understands PM document patterns, structures, and formats
    Can generate ANY PM document - roadmaps, Visio diagrams, business cases, and more
    """
    
    def __init__(self):
        # Comprehensive PM document type patterns
        self.document_patterns = {
            'register': ['risk', 'issue', 'stakeholder', 'assumption', 'dependency', 'change', 'vendor', 'contract', 'asset'],
            'log': ['decision', 'change', 'action', 'defect', 'incident', 'meeting', 'lessons', 'contact', 'communication'],
            'plan': ['project', 'communication', 'resource', 'quality', 'procurement', 'risk', 'scope', 'schedule', 'cost', 'transition', 'deployment', 'training', 'test', 'integration', 'contingency'],
            'charter': ['project', 'team'],
            'matrix': ['raci', 'responsibility', 'traceability', 'escalation', 'evaluation', 'allocation', 'capacity', 'skills', 'competency'],
            'analysis': ['stakeholder', 'swot', 'cost-benefit', 'gap', 'root cause', 'feasibility', 'impact', 'variance', 'trend'],
            'report': ['status', 'progress', 'performance', 'lessons learned', 'closure', 'executive', 'weekly', 'monthly', 'quarterly'],
            'schedule': ['project', 'milestone', 'gantt', 'timeline', 'critical path'],
            'budget': ['project', 'cost', 'financial', 'forecast', 'estimate'],
            'statement': ['work', 'scope', 'vision', 'problem', 'requirement', 'objective'],
            'breakdown': ['work', 'wbs', 'resource', 'cost', 'organizational', 'product'],
            'baseline': ['scope', 'schedule', 'cost', 'performance', 'quality'],
            'dashboard': ['project', 'kpi', 'metrics', 'executive', 'portfolio', 'program'],
            'roadmap': ['product', 'technology', 'strategic', 'release', 'project', 'portfolio', 'capability'],
            'diagram': ['process', 'flow', 'network', 'swimlane', 'organizational', 'data flow', 'architecture', 'sequence'],
            'case': ['business', 'use', 'test'],
            'scorecard': ['vendor', 'supplier', 'balanced', 'performance', 'project'],
            'form': ['change request', 'issue', 'timesheet', 'expense', 'approval', 'requisition'],
            'framework': ['governance', 'risk', 'quality', 'architecture', 'compliance'],
            'model': ['financial', 'risk', 'resource', 'capacity', 'maturity', 'cost'],
            'assessment': ['readiness', 'maturity', 'capability', 'risk', 'impact', 'vendor'],
            'inventory': ['asset', 'resource', 'skill', 'tool', 'software', 'hardware'],
            'procedure': ['standard operating', 'work instruction', 'process', 'guideline'],
            'policy': ['project', 'governance', 'security', 'quality', 'change', 'procurement'],
            'specification': ['requirement', 'technical', 'functional', 'design', 'interface'],
            'database': ['lessons learned', 'knowledge', 'best practices'],
            'template': ['meeting agenda', 'meeting minutes', 'email', 'memo'],
            'checklist': ['quality', 'review', 'audit', 'handoff', 'closure'],
            'guide': ['user', 'implementation', 'training', 'reference'],
            'manual': ['user', 'operations', 'maintenance', 'training']
        }
        
        # Format determination rules - including Visio
        self.format_rules = {
            'excel': ['register', 'log', 'matrix', 'budget', 'schedule', 'tracker', 'list', 'breakdown', 'dashboard', 'scorecard', 'model', 'inventory', 'forecast', 'allocation', 'database', 'checklist'],
            'word': ['plan', 'charter', 'statement', 'analysis', 'report', 'procedure', 'policy', 'specification', 'case', 'framework', 'assessment', 'lessons', 'guide', 'manual', 'template'],
            'powerpoint': ['presentation', 'dashboard', 'executive', 'summary', 'review', 'kickoff', 'roadmap', 'overview'],
            'visio': ['diagram', 'flow', 'process', 'network', 'swimlane', 'organizational chart', 'architecture', 'workflow', 'sequence']
        }
        
        # PM knowledge areas (PMI PMBOK)
        self.knowledge_areas = [
            'Integration Management',
            'Scope Management',
            'Schedule Management',
            'Cost Management',
            'Quality Management',
            'Resource Management',
            'Communications Management',
            'Risk Management',
            'Procurement Management',
            'Stakeholder Management'
        ]
        
        # Common PM deliverable structures
        self.excel_structures = {
            'register': ['ID', 'Title', 'Description', 'Owner', 'Status', 'Priority', 'Date Created', 'Last Updated'],
            'log': ['ID', 'Date', 'Description', 'Action', 'Owner', 'Due Date', 'Status', 'Notes'],
            'matrix': ['ID', 'Item', 'Category', 'Responsible', 'Accountable', 'Consulted', 'Informed'],
            'budget': ['Category', 'Description', 'Planned Cost', 'Actual Cost', 'Variance', 'Status', 'Notes'],
            'schedule': ['Task ID', 'Task Name', 'Start Date', 'End Date', 'Duration', 'Dependencies', 'Owner', 'Status'],
            'tracker': ['ID', 'Item', 'Status', 'Owner', 'Due Date', 'Priority', 'Progress %', 'Notes'],
            'scorecard': ['Vendor/Item', 'Criteria', 'Weight', 'Score', 'Weighted Score', 'Comments', 'Rank'],
            'dashboard': ['Metric', 'Target', 'Actual', 'Variance', 'Status', 'Trend', 'Owner'],
            'inventory': ['ID', 'Item Name', 'Category', 'Quantity', 'Location', 'Owner', 'Status', 'Notes'],
            'checklist': ['Item', 'Description', 'Responsible', 'Due Date', 'Status', 'Completed Date', 'Notes']
        }
        
        self.word_structures = {
            'plan': ['Executive Summary', 'Purpose', 'Scope', 'Objectives', 'Approach', 'Roles & Responsibilities', 'Timeline', 'Resources', 'Risks', 'Success Criteria'],
            'charter': ['Project Title', 'Purpose', 'Objectives', 'Scope', 'Deliverables', 'Stakeholders', 'Assumptions', 'Constraints', 'Budget', 'Timeline', 'Authorization'],
            'analysis': ['Executive Summary', 'Background', 'Methodology', 'Findings', 'Analysis', 'Recommendations', 'Conclusion'],
            'report': ['Executive Summary', 'Project Overview', 'Accomplishments', 'Issues & Risks', 'Upcoming Activities', 'Budget Status', 'Schedule Status', 'Next Steps'],
            'statement': ['Introduction', 'Background', 'Objectives', 'Scope', 'Deliverables', 'Assumptions', 'Constraints', 'Acceptance Criteria'],
            'case': ['Executive Summary', 'Business Need', 'Problem Statement', 'Proposed Solution', 'Benefits', 'Costs', 'ROI Analysis', 'Risks', 'Recommendations'],
            'specification': ['Introduction', 'Scope', 'Requirements', 'Functional Specifications', 'Technical Specifications', 'Constraints', 'Acceptance Criteria', 'Appendices'],
            'procedure': ['Purpose', 'Scope', 'Responsibilities', 'Procedure Steps', 'References', 'Definitions', 'Forms/Templates'],
            'assessment': ['Executive Summary', 'Assessment Scope', 'Methodology', 'Current State', 'Gap Analysis', 'Recommendations', 'Action Plan']
        }
        
        self.visio_structures = {
            'diagram': ['Process Flow', 'Decision Points', 'Inputs/Outputs', 'Roles/Swimlanes', 'Start/End Points'],
            'flow': ['Start', 'Process Steps', 'Decision Points', 'End', 'Connectors'],
            'network': ['Nodes', 'Connections', 'Labels', 'Legend'],
            'organizational': ['Hierarchy Levels', 'Reporting Lines', 'Roles/Titles', 'Names']
        }
    
    def analyze_document_request(self, document_name: str, description: str = "") -> Dict:
        """
        Analyze what type of PM document is being requested
        Returns document intelligence including format, structure, and content guidance
        Works for ANY PM document, not just pre-defined ones
        """
        doc_lower = document_name.lower()
        desc_lower = description.lower()
        combined = f"{doc_lower} {desc_lower}"
        
        # Determine document category
        category = self._determine_category(doc_lower)
        
        # Determine optimal format
        format_type = self._determine_format(doc_lower, category)
        
        # Get structure template
        structure = self._get_structure(category, format_type)
        
        # Determine knowledge area
        knowledge_area = self._determine_knowledge_area(combined)
        
        # Generate content guidance
        content_guidance = self._generate_content_guidance(category, document_name, description)
        
        return {
            'document_name': document_name,
            'category': category,
            'format': format_type,
            'structure': structure,
            'knowledge_area': knowledge_area,
            'content_guidance': content_guidance,
            'pm_principles': self._get_pm_principles(category),
            'is_high_value': True  # All PM documents are high value
        }
    
    def _determine_category(self, doc_name: str) -> str:
        """Determine document category from name - works for ANY PM document"""
        for category, keywords in self.document_patterns.items():
            if any(keyword in doc_name for keyword in keywords):
                return category
        
        # Intelligent fallback categorization
        if 'track' in doc_name or 'monitor' in doc_name:
            return 'tracker'
        elif 'assess' in doc_name or 'evaluat' in doc_name:
            return 'analysis'
        elif 'summar' in doc_name or 'overview' in doc_name:
            return 'report'
        elif 'map' in doc_name or 'visual' in doc_name:
            return 'diagram'
        elif 'business' in doc_name and 'case' in doc_name:
            return 'case'
        else:
            return 'document'
    
    def _determine_format(self, doc_name: str, category: str) -> str:
        """Determine optimal document format - Excel, Word, PowerPoint, or Visio"""
        # Check explicit format rules
        for format_type, keywords in self.format_rules.items():
            if any(keyword in doc_name for keyword in keywords):
                return format_type
            if category in keywords:
                return format_type
        
        # Intelligent format determination
        if 'diagram' in doc_name or 'flow' in doc_name or 'chart' in doc_name and 'org' in doc_name:
            return 'visio'
        elif category in ['register', 'log', 'matrix', 'tracker', 'scorecard', 'dashboard']:
            return 'excel'
        elif 'present' in doc_name or 'slide' in doc_name or 'deck' in doc_name or 'roadmap' in doc_name:
            return 'powerpoint'
        else:
            return 'word'
    
    def _get_structure(self, category: str, format_type: str) -> List[str]:
        """Get appropriate structure based on category and format"""
        if format_type == 'excel':
            return self.excel_structures.get(category, self.excel_structures.get('tracker', ['ID', 'Item', 'Description', 'Owner', 'Status', 'Date', 'Notes']))
        elif format_type == 'word':
            return self.word_structures.get(category, self.word_structures.get('statement', ['Introduction', 'Purpose', 'Content', 'Conclusion']))
        elif format_type == 'visio':
            return self.visio_structures.get(category, self.visio_structures['diagram'])
        else:  # PowerPoint
            return ['Title Slide', 'Agenda', 'Overview', 'Key Points', 'Analysis', 'Recommendations', 'Next Steps', 'Q&A']
    
    def _determine_knowledge_area(self, text: str) -> str:
        """Determine which PMI knowledge area this document relates to"""
        for area in self.knowledge_areas:
            area_keywords = area.lower().split()[0]  # e.g., 'risk' from 'Risk Management'
            if area_keywords in text:
                return area
        return 'Integration Management'  # Default
    
    def _generate_content_guidance(self, category: str, doc_name: str, description: str) -> Dict:
        """Generate intelligent content guidance for AI generation"""
        guidance = {
            'purpose': self._get_document_purpose(category, doc_name),
            'key_elements': self._get_key_elements(category),
            'best_practices': self._get_best_practices(category),
            'sample_content_hints': self._get_content_hints(category, description)
        }
        return guidance
    
    def _get_document_purpose(self, category: str, doc_name: str) -> str:
        """Get the purpose of this document type"""
        purposes = {
            'register': f'Track and manage {doc_name} throughout the project lifecycle',
            'log': f'Record and document {doc_name} with dates, actions, and ownership',
            'plan': f'Define approach, processes, and procedures for {doc_name}',
            'charter': f'Formally authorize and define {doc_name} with objectives and scope',
            'matrix': f'Map relationships and responsibilities for {doc_name}',
            'analysis': f'Analyze and evaluate {doc_name} to support decision-making',
            'report': f'Communicate status, progress, and performance of {doc_name}',
            'statement': f'Define and document {doc_name} clearly and comprehensively',
            'roadmap': f'Visualize strategic direction and timeline for {doc_name}',
            'diagram': f'Illustrate processes, flows, and relationships for {doc_name}',
            'case': f'Justify and document business rationale for {doc_name}',
            'scorecard': f'Evaluate and compare options for {doc_name}',
            'framework': f'Establish governance structure and guidelines for {doc_name}'
        }
        return purposes.get(category, f'Document and manage {doc_name} effectively for project success')
    
    def _get_key_elements(self, category: str) -> List[str]:
        """Get key elements that should be in this document"""
        elements = {
            'register': ['Unique ID', 'Clear description', 'Owner assignment', 'Status tracking', 'Priority/severity', 'Dates'],
            'log': ['Chronological entries', 'Action items', 'Ownership', 'Due dates', 'Status updates'],
            'plan': ['Objectives', 'Scope', 'Approach', 'Roles', 'Timeline', 'Resources', 'Risks'],
            'charter': ['Authorization', 'Objectives', 'Scope', 'Stakeholders', 'Budget', 'Success criteria'],
            'matrix': ['Clear mapping', 'Defined relationships', 'Accountability', 'Traceability'],
            'analysis': ['Data/findings', 'Methodology', 'Insights', 'Recommendations', 'Supporting evidence'],
            'roadmap': ['Timeline', 'Milestones', 'Dependencies', 'Strategic themes', 'Visual clarity'],
            'diagram': ['Clear flow', 'Proper symbols', 'Labels', 'Legend', 'Start/end points'],
            'case': ['Problem statement', 'Solution', 'Benefits', 'Costs', 'ROI', 'Risks'],
            'scorecard': ['Evaluation criteria', 'Weights', 'Scores', 'Rankings', 'Justification']
        }
        return elements.get(category, ['Clear structure', 'Relevant content', 'Professional format', 'Actionable information'])
    
    def _get_best_practices(self, category: str) -> List[str]:
        """Get PM best practices for this document type"""
        practices = {
            'register': ['Use unique IDs', 'Assign clear ownership', 'Update regularly', 'Track status changes', 'Include dates'],
            'log': ['Maintain chronological order', 'Be specific and concise', 'Assign action owners', 'Set due dates', 'Follow up on actions'],
            'plan': ['Align with project objectives', 'Define clear roles', 'Include success metrics', 'Address risks', 'Get stakeholder approval'],
            'charter': ['Get executive sponsor signature', 'Define clear scope boundaries', 'Identify key stakeholders', 'Set realistic objectives'],
            'matrix': ['Ensure complete coverage', 'Avoid overlaps', 'Define clear roles', 'Get stakeholder agreement'],
            'analysis': ['Use data-driven approach', 'Document assumptions', 'Provide actionable recommendations', 'Include executive summary'],
            'roadmap': ['Align with strategy', 'Show dependencies', 'Update regularly', 'Make it visual', 'Include milestones'],
            'diagram': ['Use standard notation', 'Keep it simple', 'Label clearly', 'Show flow direction', 'Include legend'],
            'case': ['Quantify benefits', 'Be realistic on costs', 'Address risks', 'Show ROI', 'Get stakeholder buy-in'],
            'scorecard': ['Use objective criteria', 'Weight appropriately', 'Document scoring logic', 'Be consistent', 'Show calculations']
        }
        return practices.get(category, ['Follow PMI standards', 'Use clear language', 'Maintain professional format', 'Update regularly', 'Ensure stakeholder alignment'])
    
    def _get_content_hints(self, category: str, description: str) -> List[str]:
        """Generate content hints based on category and user description"""
        hints = []
        
        # Extract project context from description
        if description:
            desc_lower = description.lower()
            if 'software' in desc_lower or 'it' in desc_lower or 'tech' in desc_lower:
                hints.append('Include IT/software-specific considerations and terminology')
            if 'agile' in desc_lower or 'scrum' in desc_lower:
                hints.append('Adapt for Agile/Scrum methodology')
            if 'construction' in desc_lower:
                hints.append('Include construction industry standards and safety considerations')
            if 'healthcare' in desc_lower:
                hints.append('Consider healthcare compliance and regulatory requirements')
            if 'finance' in desc_lower or 'banking' in desc_lower:
                hints.append('Include financial industry regulations and compliance')
        
        # Category-specific hints
        if category == 'register':
            hints.append('Include columns for tracking, monitoring, and reporting')
        elif category == 'plan':
            hints.append('Structure with clear sections, subsections, and appendices')
        elif category == 'charter':
            hints.append('Include authorization and sign-off section with stakeholder approval')
        elif category == 'roadmap':
            hints.append('Use visual timeline with clear milestones and dependencies')
        elif category == 'diagram':
            hints.append('Use standard notation (BPMN, UML, etc.) and include legend')
        elif category == 'case':
            hints.append('Quantify benefits and costs with supporting data and ROI calculation')
        
        return hints if hints else ['Apply PM best practices and PMI standards']
    
    def _get_pm_principles(self, category: str) -> List[str]:
        """Get relevant PM principles to apply"""
        return [
            'Use PMI-compliant terminology and standards',
            'Follow industry best practices',
            'Ensure traceability and accountability',
            'Include version control and change history',
            'Make it actionable and practical',
            'Focus on value delivery',
            'Align with project objectives',
            'Consider stakeholder needs'
        ]

# Global instance
pm_intelligence = PMDocumentIntelligence()

