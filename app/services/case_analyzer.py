import json
import openai
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import hashlib
from dataclasses import dataclass, asdict
from enum import Enum
import concurrent.futures
from abc import ABC, abstractmethod
import threading
import time
import re

from app.utils.pii_remover import PIIRemover

class ConfidenceLevel(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class AgentRole(Enum):
    SPECIALIST = "specialist"
    COORDINATOR = "coordinator"

@dataclass
class LegalClassification:
    category: str
    subcategory: str
    confidence: ConfidenceLevel
    reasoning: str
    keywords_found: List[str]
    relevance_score: float
    urgency_score: float
    agent_id: str
    processing_time: float
    fallback_used: bool = False

@dataclass
class CaseAnalysisResult:
    primary_classification: LegalClassification
    secondary_classifications: List[LegalClassification]
    complexity_level: str
    requires_multiple_attorneys: bool
    total_processing_time: float
    agents_consulted: List[str]
    confidence_consensus: float

class InputGuardrails:
    @staticmethod
    def validate_case_input(case_text: str) -> Dict[str, Any]:
        validation_result = {
            "is_valid": True,
            "issues": [],
            "severity": "none"
        }
        
        if len(case_text.strip()) < 10:
            validation_result["is_valid"] = False
            validation_result["issues"].append("Case description too short")
            validation_result["severity"] = "error"
            return validation_result
        
        word_count = len(case_text.split())
        if word_count < 3:
            validation_result["is_valid"] = False
            validation_result["issues"].append("Insufficient detail provided")
            validation_result["severity"] = "error"
            return validation_result
        
        spam_indicators = [
            r'(.)\1{10,}',
            r'[!]{5,}',
            r'[?]{5,}',
            r'[A-Z]{20,}',
        ]
        
        for pattern in spam_indicators:
            if re.search(pattern, case_text):
                validation_result["issues"].append("Potential spam content detected")
                validation_result["severity"] = "warning"
                break
        
        legal_indicators = [
            'legal', 'law', 'attorney', 'lawyer', 'court', 'case', 'lawsuit',
            'contract', 'agreement', 'violation', 'injury', 'accident', 'dispute',
            'criminal', 'civil', 'rights', 'claim', 'damages', 'compensation',
            'arrest', 'charge', 'divorce', 'custody', 'property', 'business',
            'employment', 'discrimination', 'harassment', 'medical', 'malpractice',
            'insurance', 'bankruptcy', 'tax', 'estate', 'will', 'trust',
            'immigration', 'visa', 'deportation', 'patent', 'copyright', 'trademark',
            'landlord', 'tenant', 'eviction', 'lease', 'mortgage', 'foreclosure',
            'fired', 'employer', 'workplace', 'wages', 'overtime', 'benefits',
            'convicted', 'sentenced', 'probation', 'bail', 'felony', 'misdemeanor',
            'sue', 'sued', 'suing', 'liable', 'liability', 'negligence', 'fault',
            'settlement', 'judgment', 'verdict', 'trial', 'hearing', 'deposition'
        ]
        
        has_legal_context = any(indicator in case_text.lower() for indicator in legal_indicators)
        if not has_legal_context:
            validation_result["issues"].append("No clear legal context detected")
            validation_result["severity"] = "warning"
        
        return validation_result

class OutputGuardrails:
    @staticmethod
    def validate_classification(classification: Dict[str, Any], valid_categories: Dict[str, List[str]]) -> Dict[str, Any]:
        validation_result = {
            "is_valid": True,
            "issues": [],
            "severity": "none"
        }
        
        category = classification.get("category")
        if not category or category not in valid_categories:
            validation_result["is_valid"] = False
            validation_result["issues"].append(f"Invalid category: {category}")
            validation_result["severity"] = "error"
            return validation_result
        
        subcategory = classification.get("subcategory")
        if not subcategory or subcategory not in valid_categories[category]:
            validation_result["is_valid"] = False
            validation_result["issues"].append(f"Invalid subcategory: {subcategory}")
            validation_result["severity"] = "error"
            return validation_result
        
        confidence = classification.get("confidence")
        if confidence not in ["high", "medium", "low"]:
            validation_result["issues"].append(f"Invalid confidence level: {confidence}")
            validation_result["severity"] = "warning"
        
        reasoning = classification.get("reasoning", "")
        if len(reasoning.strip()) < 20:
            validation_result["issues"].append("Insufficient reasoning provided")
            validation_result["severity"] = "warning"
        
        return validation_result

class BaseAgent(ABC):
    def __init__(self, agent_id: str, client: openai.OpenAI):
        self.agent_id = agent_id
        self.client = client
        self.role = AgentRole.SPECIALIST
        
    @abstractmethod
    def process(self, case_text: str, context: Dict[str, Any] = None) -> Any:
        pass

class LegalSpecialistAgent(BaseAgent):
    def __init__(self, agent_id: str, client: openai.OpenAI, legal_area: str, 
                 keywords: List[str], subcategories: List[str], case_descriptions: List[str], 
                 legal_concepts: List[str], legal_categories: Dict[str, List[str]]):
        super().__init__(agent_id, client)
        self.legal_area = legal_area
        self.keywords = keywords
        self.subcategories = subcategories
        self.case_descriptions = case_descriptions
        self.legal_concepts = legal_concepts
        self.LEGAL_CATEGORIES = legal_categories
        self.role = AgentRole.SPECIALIST
        
    def process(self, case_text: str, context: Dict[str, Any] = None) -> Optional[LegalClassification]:
        start_time = time.time()
        
        try:
            validation = InputGuardrails.validate_case_input(case_text)
            if not validation["is_valid"]:
                return None
            
            case_lower = case_text.lower()
            keywords_found = [kw for kw in self.keywords if kw.lower() in case_lower]
            concepts_found = [concept for concept in self.legal_concepts if concept.lower() in case_lower]
            
            if keywords_found or concepts_found:
                return self._perform_specialist_analysis(case_text, keywords_found + concepts_found, start_time, fallback_used=False)
            else:
                return self._perform_fallback_analysis(case_text, start_time)
                
        except Exception as e:
            return None
    
    def _perform_specialist_analysis(self, case_text: str, indicators_found: List[str], start_time: float, fallback_used: bool = False) -> Optional[LegalClassification]:
        case_examples = "\n".join([f"• {desc}" for desc in self.case_descriptions])
        legal_concepts = "\n".join([f"• {concept}" for concept in self.legal_concepts])
        
        # Enhanced prompts for specific areas that commonly get misclassified
        if self.legal_area == "Business/Corporate Law":
            specific_guidance = """
CRITICAL BUSINESS LAW INDICATORS - CLASSIFY AS BUSINESS LAW IF ANY APPLY:
• Commercial contracts (modeling, entertainment, service agreements)
• Business partnerships or joint ventures
• Vendor/supplier agreements and disputes
• Professional service contracts (agencies, consultants, contractors)
• Commercial transactions between businesses and individuals
• Company formation, dissolution, or ownership disputes
• Breach of commercial agreements or contracts
• Business registration or licensing issues
• Commercial fraud or misrepresentation
• Entertainment industry contracts (modeling, talent, production)

EXAMPLES THAT ARE BUSINESS LAW:
• Modeling agency contract disputes
• Service provider non-performance
• Professional service agreements gone wrong
• Commercial licensing disputes
• Vendor payment disputes
• Business partnership breakdowns"""
            
        elif self.legal_area == "Government & Administrative Law":
            specific_guidance = """
GOVERNMENT LAW SCOPE - ONLY CLASSIFY IF DIRECTLY INVOLVES:
• Government agencies (Social Security, VA, unemployment offices)
• Government benefits (disability, social security, veterans benefits)
• Government regulatory violations or compliance
• Administrative proceedings with government entities
• Public sector employment issues
• Government licensing by regulatory bodies
• Constitutional rights violations by government

DO NOT CLASSIFY AS GOVERNMENT LAW:
• Private business disputes (even if business is unregistered)
• Commercial contracts between private parties
• Private company service agreements
• Entertainment/modeling agency disputes
• Private professional services
• Business-to-consumer issues
• Private company registration issues"""
            
        elif self.legal_area == "Employment Law":
            specific_guidance = """
EMPLOYMENT LAW SCOPE - ONLY CLASSIFY IF INVOLVES:
• Employer-employee relationship (W-2, payroll, benefits)
• Workplace discrimination or harassment
• Wrongful termination from employment
• Wage and hour violations by employers
• Workplace safety violations
• Employment contracts (not independent contractor agreements)

DO NOT CLASSIFY AS EMPLOYMENT LAW:
• Independent contractor disputes
• Modeling agency agreements (these are business contracts)
• Professional service agreements
• Talent agency contracts
• Freelance or gig work disputes"""
            
        elif self.legal_area == "Product & Services Liability Law":
            specific_guidance = """
PRODUCT/SERVICES LIABILITY SCOPE - CLASSIFY IF INVOLVES:
• Defective physical products causing injury
• Professional malpractice (attorney, medical, accounting)
• Service-related injuries or damages
• Product recalls or safety issues
• Consumer protection from defective goods

MAY ALSO CLASSIFY SERVICES LIABILITY FOR:
• Professional services that failed to deliver as promised
• Service contracts with inadequate performance
• Consumer fraud in service delivery"""
            
        else:
            specific_guidance = ""
        
        prompt = f"""You are an expert {self.legal_area} attorney with 25+ years of experience. Analyze this case to determine if it requires {self.legal_area} legal representation.

CASE DESCRIPTION:
"{case_text}"

{self.legal_area.upper()} LEGAL EXPERTISE COVERS:
{legal_concepts}

{specific_guidance}

TYPICAL {self.legal_area.upper()} SCENARIOS:
{case_examples}

AVAILABLE SUBCATEGORIES: {', '.join(self.subcategories)}

ANALYSIS REQUIREMENTS:
1. Determine if this case PRIMARILY involves {self.legal_area} legal issues
2. Consider if this is the MAIN legal problem requiring {self.legal_area} expertise
3. Identify the most appropriate subcategory if relevant
4. Assess complexity, urgency, and legal strength

CLASSIFICATION STANDARDS:
• HIGH confidence: Clear {self.legal_area} issue with strong legal basis
• MEDIUM confidence: Probable {self.legal_area} issue requiring investigation  
• LOW confidence: Possible {self.legal_area} implications, uncertain without more facts

CRITICAL: Focus on the PRIMARY legal issue. If this case is PRIMARILY a {self.legal_area} matter, classify it. If it's primarily another area of law, do NOT classify it as {self.legal_area}.

REQUIRED JSON RESPONSE:
{{
    "relevant": true/false,
    "subcategory": "exact subcategory name or null if not relevant",
    "confidence": "high/medium/low", 
    "reasoning": "detailed analysis focusing on why this is/isn't primarily a {self.legal_area} matter",
    "urgency_score": 0.0-1.0,
    "complexity_score": 0.0-1.0,
    "key_factors": ["3-5 specific {self.legal_area} factors identified"],
    "immediate_actions": ["2-4 recommended legal steps"],
    "strength_assessment": "assessment of legal position strength",
    "primary_legal_issue": "what is the main legal problem in this case"
}}

IMPORTANT: Only classify if this is PRIMARILY a {self.legal_area} matter requiring {self.legal_area} expertise."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": f"""You are an expert {self.legal_area} attorney. Provide precise professional legal analysis.

REQUIREMENTS:
- Always make your best professional judgment
- If any reasonable {self.legal_area} connection exists, classify it
- When uncertain, classify with LOW confidence rather than rejecting
- Focus on PRIMARY legal issue requiring attention
- Response must be valid JSON format

MAKE BEST POSSIBLE CLASSIFICATION - Do not refuse to classify reasonable cases."""
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=1000
            )
            
            result = json.loads(response.choices[0].message.content)
            
            if result.get("relevant", False):
                classification_dict = {
                    "category": self.legal_area,
                    "subcategory": result.get("subcategory"),
                    "confidence": result.get("confidence", "medium"),
                    "reasoning": result.get("reasoning", "")
                }
                
                validation = OutputGuardrails.validate_classification(
                    classification_dict, 
                    {self.legal_area: self.subcategories}
                )
                
                if not validation["is_valid"]:
                    return None
            
            if not result.get("relevant", False):
                return None
            
            urgency = result.get("urgency_score", 0.5)
            complexity = result.get("complexity_score", 0.5)
            indicator_density = len(indicators_found) / max(len(self.keywords + self.legal_concepts), 1)
            confidence_weight = {"high": 1.0, "medium": 0.7, "low": 0.4}.get(result.get("confidence", "medium"), 0.7)
            
            strength_keywords = ["strong", "clear", "definitive", "compelling"]
            strength_bonus = 0.1 if any(word in result.get("strength_assessment", "").lower() for word in strength_keywords) else 0
            
            relevance_score = (urgency * 0.3 + complexity * 0.25 + indicator_density * 0.15 + confidence_weight * 0.3 + strength_bonus)
            processing_time = time.time() - start_time
            
            confidence_map = {
                "high": ConfidenceLevel.HIGH, 
                "medium": ConfidenceLevel.MEDIUM, 
                "low": ConfidenceLevel.LOW
            }
            
            classification = LegalClassification(
                category=self.legal_area,
                subcategory=result.get("subcategory", self.subcategories[0]),
                confidence=confidence_map.get(result.get("confidence", "medium"), ConfidenceLevel.MEDIUM),
                reasoning=result.get("reasoning", ""),
                keywords_found=indicators_found,
                relevance_score=relevance_score,
                urgency_score=urgency,
                agent_id=self.agent_id,
                processing_time=processing_time,
                fallback_used=fallback_used
            )
            
            return classification
            
        except Exception as e:
            return None
    
    def _perform_fallback_analysis(self, case_text: str, start_time: float) -> Optional[LegalClassification]:
        legal_concepts = "\n".join([f"• {concept}" for concept in self.legal_concepts])
        
        prompt = f"""You are conducting comprehensive {self.legal_area} legal analysis. Even without obvious indicators, determine if this case has ANY connection to {self.legal_area}.

CASE DESCRIPTION: "{case_text}"

{self.legal_area.upper()} LEGAL DOMAIN: {legal_concepts}

SUBCATEGORIES: {', '.join(self.subcategories)}

FALLBACK ANALYSIS - MAKE BEST JUDGMENT:
1. Look for IMPLIED {self.legal_area} legal issues
2. Consider if situation could DEVELOP into {self.legal_area} matter
3. Analyze underlying {self.legal_area} rights/duties/obligations
4. Assess if person would BENEFIT from {self.legal_area} consultation
5. Consider {self.legal_area} legal relationships or processes

DECISION CRITERIA:
• Does this involve {self.legal_area} legal rights or obligations?
• Would a {self.legal_area} attorney be appropriate to consult?
• Are there {self.legal_area} statutes/regulations that apply?
• Is this governed by {self.legal_area} legal principles?

CRITICAL: Make your best professional judgment. If there's ANY reasonable {self.legal_area} connection, classify it with LOW confidence rather than rejecting.

REQUIRED JSON RESPONSE:
{{
    "relevant": true/false,
    "subcategory": "most appropriate subcategory or null",
    "confidence": "low/medium",
    "reasoning": "detailed analysis of {self.legal_area} connection",
    "urgency_score": 0.0-1.0,
    "complexity_score": 0.0-1.0,
    "key_factors": ["factors supporting classification"],
    "immediate_actions": ["recommended steps if relevant"],
    "connection_type": "describe type of {self.legal_area} connection"
}}

FALLBACK REQUIREMENT: Err on side of classification with LOW confidence rather than rejection."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": f"""You are performing fallback analysis for {self.legal_area}.

REQUIREMENTS:
- Make best professional judgment even with limited indicators
- If ANY reasonable {self.legal_area} connection exists, classify it
- Use LOW confidence for uncertain cases rather than rejecting
- Focus on PRIMARY legal issue
- Provide detailed reasoning for decision

MAKE BEST POSSIBLE CLASSIFICATION - Prefer classification over rejection."""
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=800
            )
            
            result = json.loads(response.choices[0].message.content)
            
            if result.get("relevant", False):
                confidence = result.get("confidence", "low")
                if confidence == "high":
                    confidence = "medium"
                result["confidence"] = confidence
                
                return self._perform_specialist_analysis(case_text, [], start_time, fallback_used=True)
            else:
                return None
                
        except Exception as e:
            return None

class FinalFallbackAgent(BaseAgent):
    def __init__(self, agent_id: str, client: openai.OpenAI, legal_categories: Dict[str, List[str]]):
        super().__init__(agent_id, client)
        self.legal_categories = legal_categories
        
    def _perform_edge_case_analysis(self, case_text: str, start_time: float) -> LegalClassification:
        """Dedicated edge case analysis that ALWAYS classifies within existing categories"""
        
        prompt = f"""You are a senior legal analyst with 30+ years experience across ALL areas of law. You must classify this case within the existing legal categories - NO EXCEPTIONS.

CASE DESCRIPTION: "{case_text}"

MANDATORY CLASSIFICATION WITHIN THESE CATEGORIES:
1. **Family Law**: Marriage, divorce, custody, adoption, family relationships
2. **Employment Law**: Employer-employee relationships, workplace issues, labor disputes  
3. **Criminal Law**: Arrests, charges, criminal violations, legal defense
4. **Real Estate Law**: Property transactions, mortgages, real estate disputes
5. **Business/Corporate Law**: Commercial contracts, business disputes, professional services, agencies, entertainment contracts, modeling agreements, service providers
6. **Immigration Law**: Visa, citizenship, deportation, immigration status
7. **Personal Injury Law**: Accidents, injuries, medical malpractice, negligence
8. **Wills, Trusts, & Estates Law**: Estate planning, inheritance, probate, trusts
9. **Bankruptcy, Finances, & Tax Law**: Debt, bankruptcy, tax issues, financial problems
10. **Government & Administrative Law**: Government agencies, benefits, administrative proceedings
11. **Product & Services Liability Law**: Defective products, service failures, consumer protection
12. **Intellectual Property Law**: Patents, copyrights, trademarks, IP disputes
13. **Landlord/Tenant Law**: Rental disputes, evictions, lease issues

EDGE CASE ANALYSIS METHODOLOGY:
1. **Identify core relationships**: Who are the main parties? (individual-business, individual-individual, business-business)
2. **Determine primary transaction type**: What kind of agreement, dispute, or issue is this?
3. **Assess legal remedy needed**: What type of legal help does this person need?
4. **Match to best category**: Which legal specialist would be most qualified to handle this?

ANALYSIS DECISION TREE:
- **Government agency involved?** → Government & Administrative Law
- **Criminal charges/arrests?** → Criminal Law  
- **Family/marriage relationships?** → Family Law
- **Property/real estate?** → Real Estate Law
- **Traditional employment (W-2, payroll)?** → Employment Law
- **Commercial contracts/business agreements?** → Business/Corporate Law
- **Physical injuries?** → Personal Injury Law
- **Intellectual property?** → Intellectual Property Law
- **Rental properties?** → Landlord/Tenant Law
- **Estate/inheritance?** → Wills, Trusts, & Estates Law
- **Debt/financial issues?** → Bankruptcy, Finances, & Tax Law
- **Immigration status?** → Immigration Law
- **Product/service problems?** → Product & Services Liability Law

CRITICAL INSTRUCTIONS:
- You MUST classify this case into one of the 13 categories above
- Make your BEST professional judgment based on the primary legal issue
- Even if unclear, choose the MOST APPROPRIATE category
- Focus on what type of attorney would be best qualified to help
- Consider the main legal relationship and transaction type
- NEVER refuse to classify - always make best guess

SUBCATEGORIES BY AREA:
- Family Law: Adoptions, Child Custody & Visitation, Child Support, Divorce, Guardianship, Paternity, Separations, Spousal Support or Alimony
- Employment Law: Disabilities, Employment Contracts, Employment Discrimination, Pensions and Benefits, Sexual Harassment, Wages and Overtime Pay, Workplace Disputes, Wrongful Termination
- Criminal Law: General Criminal Defense, Environmental Violations, Drug Crimes, Drunk Driving/DUI/DWI, Felonies, Misdemeanors, Speeding and Moving Violations, White Collar Crime, Tax Evasion
- Real Estate Law: Commercial Real Estate, Condominiums and Cooperatives, Construction Disputes, Foreclosures, Mortgages, Purchase and Sale of Residence, Title and Boundary Disputes
- Business/Corporate Law: Breach of Contract, Corporate Tax, Business Disputes, Buying and Selling a Business, Contract Drafting and Review, Corporations LLCs Partnerships etc, Entertainment Law
- Immigration Law: Citizenship, Deportation, Permanent Visas or Green Cards, Temporary Visas
- Personal Injury Law: Automobile Accidents, Dangerous Property or Buildings, Defective Products, Medical Malpractice, Personal Injury General
- Wills Trusts & Estates Law: Contested Wills or Probate, Drafting Wills and Trusts, Estate Administration, Estate Planning
- Bankruptcy Finances & Tax Law: Collections, Consumer Bankruptcy, Consumer Credit, Income Tax, Property Tax
- Government & Administrative Law: Education and Schools, Social Security Disability, Social Security Retirement, Social Security Dependent Benefits, Social Security Survivor Benefits, Veterans Benefits, General Administrative Law, Environmental Law, Liquor Licenses, Constitutional Law
- Product & Services Liability Law: Attorney Malpractice, Defective Products, Warranties, Consumer Protection and Fraud
- Intellectual Property Law: Copyright, Patents, Trademarks
- Landlord/Tenant Law: General Landlord and Tenant Issues

REQUIRED JSON RESPONSE:
{{
    "category": "exact category name from list above",
    "subcategory": "most appropriate subcategory from the category chosen",
    "confidence": "low/medium/high",
    "reasoning": "detailed explanation of why this category is the best fit based on the decision tree",
    "urgency_score": 0.0-1.0,
    "complexity_score": 0.0-1.0,
    "key_factors": ["3-5 factors that led to this classification"],
    "primary_legal_issue": "main legal problem identified",
    "attorney_type_needed": "what type of lawyer would be most qualified",
    "decision_tree_step": "which step in the decision tree led to this classification"
}}

MANDATORY: You must classify this case. Make your best professional judgment. Every case can be classified within these 13 categories. Choose the BEST FIT based on the primary legal issue."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": """You are a senior legal analyst conducting mandatory edge case classification. 

CORE PRINCIPLE: Every case can be classified within the 13 legal categories. Your job is to find the BEST FIT.

DECISION METHODOLOGY:
1. Identify the main parties and their relationship
2. Determine the primary legal issue or transaction
3. Consider what type of attorney is most qualified
4. Match to the most appropriate category
5. Choose the best subcategory within that area

CRITICAL: You CANNOT refuse to classify. Make your best professional judgment based on the primary legal issue. Focus on what type of legal specialist would be most qualified to handle this matter.

RESPONSE MUST BE VALID JSON."""
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=1000
            )
            
            result = json.loads(response.choices[0].message.content)
            
            category = result.get("category")
            subcategory = result.get("subcategory")
            
            # Validate and correct if necessary
            if category not in self.legal_categories:
                category = "Business/Corporate Law"
                subcategory = "Business Disputes"
            
            if subcategory not in self.legal_categories[category]:
                subcategory = self.legal_categories[category][0]
            
            processing_time = time.time() - start_time
            
            confidence_map = {
                "high": ConfidenceLevel.HIGH,
                "medium": ConfidenceLevel.MEDIUM, 
                "low": ConfidenceLevel.LOW
            }
            
            classification = LegalClassification(
                category=category,
                subcategory=subcategory,
                confidence=confidence_map.get(result.get("confidence", "medium"), ConfidenceLevel.MEDIUM),
                reasoning=result.get("reasoning", "Edge case analysis - best fit classification"),
                keywords_found=[],
                relevance_score=0.7,  # Good relevance for edge case analysis
                urgency_score=result.get("urgency_score", 0.5),
                agent_id=self.agent_id,
                processing_time=processing_time,
                fallback_used=True
            )
            
            return classification
            
        except Exception as e:
            # Ultimate safety net
            processing_time = time.time() - start_time
            return LegalClassification(
                category="Business/Corporate Law",
                subcategory="Business Disputes",
                confidence=ConfidenceLevel.MEDIUM,
                reasoning="Edge case analysis with system fallback - requires manual review",
                keywords_found=[],
                relevance_score=0.6,
                urgency_score=0.5,
                agent_id=self.agent_id,
                processing_time=processing_time,
                fallback_used=True
            )
    def process(self, case_text: str, context: Dict[str, Any] = None) -> LegalClassification:
        """Use edge case analysis to ensure EVERY case gets classified"""
        return self._perform_edge_case_analysis(case_text, time.time())

class CoordinatorAgent(BaseAgent):
    def __init__(self, agent_id: str, client: openai.OpenAI):
        super().__init__(agent_id, client)
        self.role = AgentRole.COORDINATOR
        
    def process(self, case_text: str, context: Dict[str, Any] = None) -> CaseAnalysisResult:
        classifications = context.get("classifications", [])
        
        if not classifications:
            raise Exception("No valid classifications from specialist agents")
        
        classifications.sort(key=lambda x: (
            not x.fallback_used,
            x.relevance_score * self._confidence_to_score(x.confidence),
            x.confidence.value == "high",
            x.urgency_score
        ), reverse=True)
        
        primary = classifications[0]
        secondaries = classifications[1:] if len(classifications) > 1 else []
        
        complexity_level = self._assess_complexity(classifications)
        requires_multiple_attorneys = len(classifications) > 1
        
        confidence_scores = [self._confidence_to_score(c.confidence) for c in classifications]
        confidence_consensus = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.7
        
        # Ensure minimum confidence to avoid rejection
        confidence_consensus = max(0.6, confidence_consensus)
        
        # Minimal penalty for fallback usage
        fallback_penalty = sum(0.02 for c in classifications if c.fallback_used)
        confidence_consensus = max(0.6, confidence_consensus - fallback_penalty)
        
        total_processing_time = sum(c.processing_time for c in classifications)
        agents_consulted = [c.agent_id for c in classifications]
        
        return CaseAnalysisResult(
            primary_classification=primary,
            secondary_classifications=secondaries,
            complexity_level=complexity_level,
            requires_multiple_attorneys=requires_multiple_attorneys,
            total_processing_time=total_processing_time,
            agents_consulted=agents_consulted,
            confidence_consensus=confidence_consensus
        )
    
    def _assess_complexity(self, classifications: List[LegalClassification]) -> str:
        num_areas = len(classifications)
        avg_complexity = sum(c.relevance_score for c in classifications) / num_areas
        high_urgency_count = sum(1 for c in classifications if c.urgency_score > 0.7)
        fallback_count = sum(1 for c in classifications if c.fallback_used)
        
        if fallback_count > 0:
            avg_complexity *= 0.9
        
        high_confidence_count = sum(1 for c in classifications if c.confidence == ConfidenceLevel.HIGH)
        
        if num_areas == 1 and avg_complexity < 0.6 and high_confidence_count > 0:
            return "simple"
        elif num_areas <= 2 and high_urgency_count <= 1 and fallback_count <= 1:
            return "moderate"
        else:
            return "complex"
    
    def _confidence_to_score(self, confidence: ConfidenceLevel) -> float:
        return {
            ConfidenceLevel.HIGH: 0.9,
            ConfidenceLevel.MEDIUM: 0.7,
            ConfidenceLevel.LOW: 0.5
        }.get(confidence, 0.5)

class SynchronousMultiAgentLegalAnalyzer:
    SYSTEM_VERSION = "4.2.0"
    PROMPT_VERSION = "2024-07-16-never-fail"
    
    LEGAL_CATEGORIES = {
        "Family Law": [
            "Adoptions", "Child Custody & Visitation", "Child Support", "Divorce",
            "Guardianship", "Paternity", "Separations", "Spousal Support or Alimony"
        ],
        "Employment Law": [
            "Disabilities", "Employment Contracts", "Employment Discrimination", 
            "Pensions and Benefits", "Sexual Harassment", "Wages and Overtime Pay", 
            "Workplace Disputes", "Wrongful Termination"
        ],
        "Criminal Law": [
            "General Criminal Defense", "Environmental Violations", "Drug Crimes",
            "Drunk Driving/DUI/DWI", "Felonies", "Misdemeanors", 
            "Speeding and Moving Violations", "White Collar Crime", "Tax Evasion"
        ],
        "Real Estate Law": [
            "Commercial Real Estate", "Condominiums and Cooperatives", "Construction Disputes",
            "Foreclosures", "Mortgages", "Purchase and Sale of Residence", "Title and Boundary Disputes"
        ],
        "Business/Corporate Law": [
            "Breach of Contract", "Corporate Tax", "Business Disputes", "Buying and Selling a Business",
            "Contract Drafting and Review", "Corporations, LLCs, Partnerships, etc.", "Entertainment Law"
        ],
        "Immigration Law": [
            "Citizenship", "Deportation", "Permanent Visas or Green Cards", "Temporary Visas"
        ],
        "Personal Injury Law": [
            "Automobile Accidents", "Dangerous Property or Buildings", "Defective Products",
            "Medical Malpractice", "Personal Injury (General)"
        ],
        "Wills, Trusts, & Estates Law": [
            "Contested Wills or Probate", "Drafting Wills and Trusts", "Estate Administration", "Estate Planning"
        ],
        "Bankruptcy, Finances, & Tax Law": [
            "Collections", "Consumer Bankruptcy", "Consumer Credit", "Income Tax", "Property Tax"
        ],
        "Government & Administrative Law": [
            "Education and Schools", "Social Security – Disability", "Social Security – Retirement",
            "Social Security – Dependent Benefits", "Social Security – Survivor Benefits", "Veterans Benefits",
            "General Administrative Law", "Environmental Law", "Liquor Licenses", "Constitutional Law"
        ],
        "Product & Services Liability Law": [
            "Attorney Malpractice", "Defective Products", "Warranties", "Consumer Protection and Fraud"
        ],
        "Intellectual Property Law": [
            "Copyright", "Patents", "Trademarks"
        ],
        "Landlord/Tenant Law": [
            "General Landlord and Tenant Issues"
        ]
    }

    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
        self.pii_remover = PIIRemover()
        
        self.specialist_agents = self._create_specialist_agents()
        self.coordinator = CoordinatorAgent("coordinator-001", self.client)
        self.final_fallback = FinalFallbackAgent("final-fallback-001", self.client, self.LEGAL_CATEGORIES)

    def _create_specialist_agents(self) -> List[LegalSpecialistAgent]:
        specialist_configs = [
            {
                "area": "Criminal Law",
                "keywords": ["arrest", "arrested", "charged", "criminal", "crime", "police", "felony", 
                           "misdemeanor", "drugs", "dui", "theft", "assault", "fraud", "jail", "prison",
                           "prosecutor", "defendant", "guilty", "plea", "sentence", "parole", "probation",
                           "convicted", "trial", "court", "judge", "jury", "warrant", "bail", "fine"],
                "legal_concepts": ["criminal liability", "criminal procedure", "constitutional rights", 
                                 "due process", "search and seizure", "Miranda rights", "plea bargaining",
                                 "criminal penalties", "criminal record", "legal defense", "prosecution"],
                "descriptions": [
                    "Person A was arrested for DUI after being stopped at a traffic checkpoint",
                    "Person B was charged with drug possession after a police search",
                    "Person C faces felony charges for white-collar fraud involving business accounts",
                    "Person D received a misdemeanor citation for public intoxication",
                    "Person E was charged with assault after a bar fight incident",
                    "Person F needs criminal defense for theft allegations at their workplace"
                ]
            },
            {
                "area": "Immigration Law", 
                "keywords": ["deport", "deportation", "immigration", "visa", "citizenship", "green card", 
                           "ice", "removal", "asylum", "refugee", "border", "undocumented", "daca",
                           "naturalization", "permanent resident", "work permit", "entry"],
                "legal_concepts": ["immigration status", "removal proceedings", "immigration benefits",
                                 "visa applications", "citizenship eligibility", "asylum claims",
                                 "deportation defense", "immigration court", "USCIS procedures"],
                "descriptions": [
                    "Person A received a deportation notice after overstaying their visa",
                    "Person B's green card application was denied due to criminal history",
                    "Person C seeks asylum after fleeing persecution in their home country",
                    "Person D faces removal proceedings despite having DACA status",
                    "Person E's citizenship application was rejected due to incomplete documentation"
                ]
            },
            {
                "area": "Family Law",
                "keywords": ["divorce", "custody", "child support", "marriage", "separation", "alimony", 
                           "adoption", "guardianship", "paternity", "visitation", "spousal support",
                           "family court", "parenting time", "domestic relations", "marital property"],
                "legal_concepts": ["marital dissolution", "child welfare", "parental rights", 
                                 "domestic relations", "family court procedures", "child advocacy",
                                 "spousal maintenance", "custody arrangements", "adoption law"],
                "descriptions": [
                    "Person A seeks divorce after 10 years of marriage with custody disputes",
                    "Person B wants to modify child support payments due to job loss",
                    "Person C is adopting their stepchild and needs legal documentation",
                    "Person D disputes paternity claims and requests DNA testing",
                    "Person E seeks emergency custody due to domestic violence concerns"
                ]
            },
            {
                "area": "Employment Law",
                "keywords": ["fired", "employer", "workplace", "discrimination", "harassment", "wages", 
                           "overtime", "wrongful termination", "sexual harassment", "disability", "job", "work",
                           "employment", "labor", "employee", "boss", "supervisor", "hr", "benefits"],
                "legal_concepts": ["employment discrimination", "wrongful termination", "workplace rights",
                                 "labor law", "employment contracts", "workplace harassment",
                                 "wage and hour law", "workers' compensation", "employment benefits"],
                "descriptions": [
                    "Person A was terminated after reporting workplace safety violations",
                    "Person B faces discrimination based on age and gender in promotion decisions",
                    "Person C experienced sexual harassment from their supervisor",
                    "Person D was denied reasonable accommodation for their disability",
                    "Person E wasn't paid overtime despite working 60-hour weeks"
                ]
            },
            {
                "area": "Personal Injury Law",
                "keywords": ["accident", "injury", "medical malpractice", "car accident", "slip and fall", 
                           "damages", "compensation", "negligence", "liability", "hospital", "doctor error",
                           "injured", "hurt", "pain", "suffering", "medical bills", "insurance claim"],
                "legal_concepts": ["personal injury claims", "negligence law", "medical malpractice",
                                 "premises liability", "product liability", "insurance coverage",
                                 "damages assessment", "liability determination", "injury compensation"],
                "descriptions": [
                    "Person A suffered serious injuries in a rear-end collision",
                    "Person B slipped and fell in a grocery store due to wet floors",
                    "Person C underwent wrong-site surgery due to medical error",
                    "Person D was injured by a defective product that malfunctioned",
                    "Person E developed complications from misdiagnosed medical condition"
                ]
            },
            {
                "area": "Business/Corporate Law",
                "keywords": ["business", "contract", "partnership", "corporation", "llc", "breach", 
                           "partnership dispute", "shareholder", "merger", "acquisition", "competitor",
                           "vendor", "client", "commercial", "enterprise", "company", "modeling agency",
                           "talent agency", "service agreement", "professional services", "consultant",
                           "contractor", "freelance", "agency", "modeling", "entertainment", "talent",
                           "management", "representation", "booking", "gigs", "exposure", "portfolio"],
                "legal_concepts": ["business law", "corporate governance", "commercial contracts",
                                 "business disputes", "corporate compliance", "business transactions",
                                 "partnership law", "contract law", "commercial litigation", "service contracts",
                                 "professional agreements", "agency agreements", "entertainment contracts",
                                 "modeling contracts", "talent representation", "commercial fraud",
                                 "contract performance", "breach of contract", "contract cancellation"],
                "descriptions": [
                    "Person A's business partner breached their partnership agreement",
                    "Person B's company faces breach of contract claims from a vendor", 
                    "Person C needs to dissolve their LLC due to partner disputes",
                    "Person D's corporation is involved in a merger negotiation",
                    "Person E discovered their competitor is using stolen trade secrets",
                    "Person F signed a modeling agency contract that promised work but delivered nothing",
                    "Person G's talent agency wants expensive cancellation fees for poor service",
                    "Person H's service provider failed to deliver promised professional services"
                ]
            },
            {
                "area": "Intellectual Property Law",
                "keywords": ["copyright", "trademark", "patent", "intellectual property", "logo", 
                           "brand", "content", "copied", "copying", "infringement", "stolen", "plagiarism",
                           "invention", "creative", "original", "ip", "licensing"],
                "legal_concepts": ["intellectual property rights", "copyright protection", "patent law",
                                 "trademark registration", "IP infringement", "licensing agreements",
                                 "trade secrets", "IP litigation", "creative works protection"],
                "descriptions": [
                    "Person A discovered their copyrighted content was stolen and republished",
                    "Person B's trademark application was rejected due to similarity conflicts",
                    "Person C believes their patent is being infringed by a competitor",
                    "Person D's company logo was copied by another business",
                    "Person E wants to protect their invention with a patent application"
                ]
            },
            {
                "area": "Real Estate Law",
                "keywords": ["real estate", "property", "house", "home", "mortgage", "foreclosure",
                           "deed", "title", "closing", "inspection", "appraisal", "zoning",
                           "real property", "land", "residential", "commercial property"],
                "legal_concepts": ["real estate transactions", "property law", "real estate contracts",
                                 "property disputes", "real estate closings", "property rights",
                                 "foreclosure proceedings", "title issues", "property development"],
                "descriptions": [
                    "Person A faces foreclosure proceedings on their family home",
                    "Person B discovered title defects when trying to sell their property",
                    "Person C's real estate closing was delayed due to inspection issues",
                    "Person D disputes their property boundary with their neighbor",
                    "Person E was denied a mortgage despite meeting all requirements"
                ]
            },
            {
                "area": "Product & Services Liability Law",
                "keywords": ["defective", "product", "recall", "contamination", "malfunction", "warranty",
                           "consumer protection", "false advertising", "attorney malpractice",
                           "service failure", "product safety", "consumer rights"],
                "legal_concepts": ["product liability", "consumer protection law", "warranty law",
                                 "product safety", "professional malpractice", "consumer fraud",
                                 "defective products", "service liability", "consumer rights"],
                "descriptions": [
                    "Person A was injured by a defective product that malfunctioned",
                    "Person B's car was recalled due to safety defects after purchase",
                    "Person C suffered damages due to contaminated food products",
                    "Person D's attorney committed malpractice by missing filing deadlines",
                    "Person E was deceived by false advertising claims about a product"
                ]
            },
            {
                "area": "Bankruptcy, Finances, & Tax Law",
                "keywords": ["bankruptcy", "debt", "creditor", "collection", "tax", "irs", "audit",
                           "property tax", "income tax", "consumer credit", "chapter 7", "chapter 13",
                           "financial", "money", "payment", "owe", "owing", "bill", "bills"],
                "legal_concepts": ["bankruptcy law", "debt relief", "tax law", "financial restructuring",
                                 "creditor rights", "tax compliance", "debt collection", "financial planning",
                                 "tax disputes", "bankruptcy proceedings"],
                "descriptions": [
                    "Person A considers filing Chapter 7 bankruptcy due to overwhelming debt",
                    "Person B faces aggressive debt collection actions from creditors",
                    "Person C was audited by the IRS for three consecutive years",
                    "Person D disputes their property tax assessment increase",
                    "Person E needs help with tax planning for their small business"
                ]
            },
            {
                "area": "Government & Administrative Law",
                "keywords": ["social security", "disability", "benefits", "government", "administrative", 
                           "veterans", "unemployment", "medicaid", "medicare", "denied", "claim", "appeal",
                           "agency", "federal", "state", "public", "governmental", "va", "irs", "uscis",
                           "department", "bureau", "commission", "regulatory", "compliance", "license suspension"],
                "legal_concepts": ["administrative law", "government benefits", "administrative procedures",
                                 "regulatory compliance", "government agencies", "administrative appeals",
                                 "public law", "government services", "administrative hearings", "federal agencies",
                                 "state agencies", "regulatory enforcement", "government licensing",
                                 "public benefits", "administrative review"],
                "descriptions": [
                    "Person A's social security disability claim was denied after two years",
                    "Person B's veterans benefits were reduced without proper notice", 
                    "Person C was denied unemployment benefits despite qualifying",
                    "Person D appeals their Medicare coverage denial decision",
                    "Person E faces administrative hearing for professional license suspension",
                    "Person F's business license was suspended by regulatory agency",
                    "Person G appeals denial of government benefit application"
                ]
            },
            {
                "area": "Wills, Trusts, & Estates Law",
                "keywords": ["will", "trust", "estate", "probate", "inheritance", "beneficiary", "executor",
                           "power of attorney", "living will", "advance directive", "heir", "inherit",
                           "estate planning", "testament", "legacy"],
                "legal_concepts": ["estate planning", "probate law", "trust administration", "estate law",
                                 "inheritance law", "will contests", "estate administration", "fiduciary duties",
                                 "estate taxation", "trust law"],
                "descriptions": [
                    "Person A contests their father's will due to suspicious circumstances",
                    "Person B needs to establish a trust for their minor children",
                    "Person C faces probate complications as executor of an estate",
                    "Person D requires estate planning for their growing business",
                    "Person E needs power of attorney for their aging parent"
                ]
            },
            {
                "area": "Landlord/Tenant Law",
                "keywords": ["landlord", "tenant", "lease", "rent", "eviction", "deposit", "repairs",
                           "rental", "apartment", "housing", "mold", "habitability", "security deposit",
                           "renter", "renting", "tenancy", "rental property"],
                "legal_concepts": ["landlord-tenant law", "rental agreements", "housing law", "tenant rights",
                                 "habitability standards", "eviction procedures", "rental disputes",
                                 "housing regulations", "lease agreements", "property management"],
                "descriptions": [
                    "Person A faces eviction due to non-payment of rent during COVID-19",
                    "Person B's landlord refuses to return their security deposit",
                    "Person C's apartment has mold issues that landlord won't address",
                    "Person D's lease was terminated without proper notice",
                    "Person E disputes rent increase that violates rent control laws"
                ]
            }
        ]
        
        agents = []
        for i, config in enumerate(specialist_configs):
            agent_id = f"specialist-{config['area'].lower().replace(' ', '-').replace('/', '-')}-{i+1:03d}"
            subcategories = self.LEGAL_CATEGORIES.get(config["area"], ["General"])
            
            agent = LegalSpecialistAgent(
                agent_id=agent_id,
                client=self.client,
                legal_area=config["area"],
                keywords=config["keywords"],
                subcategories=subcategories,
                case_descriptions=config["descriptions"],
                legal_concepts=config["legal_concepts"],
                legal_categories=self.LEGAL_CATEGORIES
            )
            agents.append(agent)
            
        return agents

    def initial_analysis(self, case_text: str, max_retries: int = 2) -> Dict[str, Any]:
        try:
            start_time = time.time()
            
            input_validation = InputGuardrails.validate_case_input(case_text)
            if not input_validation["is_valid"]:
                return {
                    "status": "error",
                    "error": f"Input validation failed: {'; '.join(input_validation['issues'])}",
                    "timestamp": datetime.utcnow().isoformat(),
                    "system_version": self.SYSTEM_VERSION
                }
            
            cleaned_text = self.pii_remover.clean_text(case_text)
            quality_assessment = self._assess_text_quality(case_text, cleaned_text)
            
            valid_classifications = []
            agent_performance = {}
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                future_to_agent = {
                    executor.submit(agent.process, cleaned_text): agent 
                    for agent in self.specialist_agents
                }
                
                for future in concurrent.futures.as_completed(future_to_agent):
                    agent = future_to_agent[future]
                    
                    try:
                        result = future.result()
                        
                        if isinstance(result, LegalClassification):
                            valid_classifications.append(result)
                            agent_performance[agent.agent_id] = {
                                "status": "success",
                                "classification": f"{result.category} - {result.subcategory}",
                                "relevance_score": result.relevance_score,
                                "processing_time": result.processing_time,
                                "fallback_used": result.fallback_used,
                                "confidence": result.confidence.value
                            }
                        else:
                            agent_performance[agent.agent_id] = {
                                "status": "not_relevant"
                            }
                    except Exception as e:
                        agent_performance[agent.agent_id] = {
                            "status": "error", 
                            "error": str(e)
                        }
            
            if not valid_classifications:
                fallback_classification = self.final_fallback.process(cleaned_text)
                valid_classifications.append(fallback_classification)
                agent_performance[self.final_fallback.agent_id] = {
                    "status": "final_fallback",
                    "classification": f"{fallback_classification.category} - {fallback_classification.subcategory}",
                    "relevance_score": fallback_classification.relevance_score,
                    "processing_time": fallback_classification.processing_time,
                    "fallback_used": True,
                    "confidence": fallback_classification.confidence.value
                }
            
            coordination_context = {"classifications": valid_classifications}
            analysis_result = self.coordinator.process(cleaned_text, coordination_context)
            
            total_time = time.time() - start_time
            
            enhanced_result = {
                "category": analysis_result.primary_classification.category,
                "subcategory": analysis_result.primary_classification.subcategory,
                "confidence": analysis_result.primary_classification.confidence.value,
                "reasoning": analysis_result.primary_classification.reasoning,
                "case_title": f"{analysis_result.primary_classification.subcategory} Case",
                "method": "never_fail_classification",
                "gibberish_detected": quality_assessment["gibberish_detected"],
                "fallback_used": analysis_result.primary_classification.fallback_used,
                
                "secondary_issues": [
                    {
                        "category": sec.category,
                        "subcategory": sec.subcategory,
                        "confidence": sec.confidence.value,
                        "relevance_score": sec.relevance_score,
                        "urgency_score": sec.urgency_score,
                        "reasoning": sec.reasoning,
                        "fallback_used": sec.fallback_used
                    }
                    for sec in analysis_result.secondary_classifications
                ],
                "case_complexity": analysis_result.complexity_level,
                "requires_multiple_attorneys": analysis_result.requires_multiple_attorneys,
                "confidence_consensus": analysis_result.confidence_consensus,
                "total_legal_areas": 1 + len(analysis_result.secondary_classifications),
                
                "agents_consulted": analysis_result.agents_consulted,
                "total_processing_time": total_time,
                "agent_performance": agent_performance,
                "text_quality": quality_assessment,
                "input_validation": input_validation,
                
                "key_details": [
                    f"Primary: {analysis_result.primary_classification.subcategory}",
                    f"Additional areas: {len(analysis_result.secondary_classifications)}",
                    f"Complexity: {analysis_result.complexity_level}",
                    f"Consensus confidence: {analysis_result.confidence_consensus:.1f}",
                    f"Agents consulted: {len(analysis_result.agents_consulted)}",
                    f"Fallback used: {analysis_result.primary_classification.fallback_used}"
                ]
            }
            
            self._log_multi_agent_analysis(case_text, enhanced_result, True, agent_performance)
            
            return {
                "status": "success",
                "method": "never_fail_classification",
                "timestamp": datetime.utcnow().isoformat(),
                "original_text": case_text,
                "cleaned_text": cleaned_text,
                "analysis": json.dumps(enhanced_result, ensure_ascii=False),
                "system_version": self.SYSTEM_VERSION,
                "prompt_version": self.PROMPT_VERSION,
                "processing_stats": {
                    "total_time": total_time,
                    "agents_deployed": len(self.specialist_agents),
                    "agents_responded": len(valid_classifications),
                    "coordination_time": analysis_result.total_processing_time,
                    "fallback_used": analysis_result.primary_classification.fallback_used,
                    "confidence_consensus": analysis_result.confidence_consensus
                }
            }
            
        except Exception as e:
            try:
                emergency_classification = self.final_fallback.process(case_text)
                return {
                    "status": "success",
                    "method": "emergency_fallback",
                    "timestamp": datetime.utcnow().isoformat(),
                    "original_text": case_text,
                    "analysis": json.dumps({
                        "category": emergency_classification.category,
                        "subcategory": emergency_classification.subcategory,
                        "confidence": emergency_classification.confidence.value,
                        "reasoning": "Emergency fallback classification",
                        "case_title": f"{emergency_classification.subcategory} Case",
                        "fallback_used": True,
                        "method": "emergency_fallback",
                        "gibberish_detected": False,
                        "secondary_issues": [],
                        "case_complexity": "unknown",
                        "requires_multiple_attorneys": False,
                        "confidence_consensus": 0.5,
                        "total_legal_areas": 1,
                        "agents_consulted": [emergency_classification.agent_id],
                        "total_processing_time": emergency_classification.processing_time,
                        "agent_performance": {},
                        "text_quality": {"quality_acceptable": False},
                        "input_validation": {"is_valid": True},
                        "key_details": ["Emergency classification"]
                    }),
                    "system_version": self.SYSTEM_VERSION,
                    "prompt_version": self.PROMPT_VERSION
                }
            except Exception as fallback_error:
                return {
                    "status": "success",
                    "method": "ultimate_fallback",
                    "timestamp": datetime.utcnow().isoformat(),
                    "original_text": case_text,
                    "analysis": json.dumps({
                        "category": "Business/Corporate Law",
                        "subcategory": "Business Disputes",
                        "confidence": "medium",
                        "reasoning": "Ultimate fallback classification - manual review recommended",
                        "case_title": "Business Disputes Case",
                        "fallback_used": True,
                        "method": "ultimate_fallback",
                        "gibberish_detected": False,
                        "secondary_issues": [],
                        "case_complexity": "unknown",
                        "requires_multiple_attorneys": False,
                        "confidence_consensus": 0.5,
                        "total_legal_areas": 1,
                        "agents_consulted": ["ultimate-fallback"],
                        "total_processing_time": 0.1,
                        "agent_performance": {},
                        "text_quality": {"quality_acceptable": False},
                        "input_validation": {"is_valid": True},
                        "key_details": ["Ultimate fallback"]
                    }),
                    "system_version": self.SYSTEM_VERSION,
                    "prompt_version": self.PROMPT_VERSION
                }

    def _assess_text_quality(self, original: str, cleaned: str) -> Dict[str, Any]:
        try:
            original_words = len(original.split())
            cleaned_words = len(cleaned.split())
            
            if original_words == 0:
                reduction_pct = 100
            else:
                reduction_pct = ((original_words - cleaned_words) / original_words) * 100
            
            legal_indicators = [
                'medical', 'surgery', 'device', 'business', 'partner', 'customer', 
                'company', 'contract', 'employer', 'fired', 'accident', 'injury',
                'property', 'defective', 'product', 'divorce', 'custody', 'arrested',
                'lawyer', 'attorney', 'court', 'lawsuit', 'doctor', 'hospital',
                'legal', 'law', 'rights', 'claim', 'damages', 'violation'
            ]
            
            has_legal_context = any(word in cleaned.lower() for word in legal_indicators)
            
            sentence_count = len([s for s in cleaned.split('.') if s.strip()])
            avg_sentence_length = cleaned_words / max(sentence_count, 1)
            
            quality_acceptable = (
                reduction_pct < 60 and
                cleaned_words >= 5 and
                has_legal_context and
                len(cleaned.strip()) > 15 and
                sentence_count > 0
            )
            
            return {
                "original_words": original_words,
                "cleaned_words": cleaned_words,
                "reduction_percentage": reduction_pct,
                "has_legal_context": has_legal_context,
                "sentence_count": sentence_count,
                "avg_sentence_length": avg_sentence_length,
                "quality_acceptable": quality_acceptable,
                "gibberish_detected": not quality_acceptable
            }
        except Exception as e:
            return {
                "original_words": 0,
                "cleaned_words": 0,
                "reduction_percentage": 100,
                "has_legal_context": False,
                "sentence_count": 0,
                "avg_sentence_length": 0,
                "quality_acceptable": False,
                "gibberish_detected": True
            }

    def _log_multi_agent_analysis(self, case_text: str, response: Dict[str, Any], 
                                 success: bool, agent_performance: Dict[str, Any]) -> None:
        try:
            case_hash = "unknown"
            try:
                case_hash = hashlib.sha256(case_text.encode('utf-8', errors='replace')).hexdigest()
            except Exception:
                case_hash = "hash_failed"
            
            fallback_count = sum(1 for p in agent_performance.values() 
                               if p.get("fallback_used", False))
            
            high_confidence_count = sum(1 for p in agent_performance.values()
                                      if p.get("confidence") == "high")
            
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "system_version": self.SYSTEM_VERSION,
                "prompt_version": self.PROMPT_VERSION,
                "case_text_hash": case_hash,
                "case_length": len(case_text),
                "analysis_type": "never_fail_classification",
                "success": success,
                "total_agents": len(self.specialist_agents) + 2,
                "responding_agents": len([p for p in agent_performance.values() if p.get("status") == "success"]),
                "fallback_agents_used": fallback_count,
                "high_confidence_classifications": high_confidence_count,
                "guardrails_applied": True,
                "never_fail_enabled": True
            }
                
        except Exception as e:
            pass

    def generate_final_summary(self, initial_analysis: Dict[str, Any], form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a final case summary using PII-cleaned case text and user-provided form data"""
        try:
            if initial_analysis.get("status") == "error":
                return {
                    "status": "error",
                    "error": "Cannot generate summary - multi-agent analysis failed",
                    "timestamp": datetime.utcnow().isoformat(),
                    "system_version": self.SYSTEM_VERSION
                }
            
            if isinstance(initial_analysis.get("analysis"), str):
                analysis_data = json.loads(initial_analysis.get("analysis", "{}"))
            else:
                analysis_data = initial_analysis.get("analysis", {})
            
            category = analysis_data.get("category", "Unknown")
            subcategory = analysis_data.get("subcategory", "Unknown")
            
            cleaned_case_text = initial_analysis.get("cleaned_text", "No case details available.")
            
            case_title = analysis_data.get("case_title")
            if not case_title:
                title_prompt = f"""Generate a specific, descriptive title (MAXIMUM 70 characters) for this {category} - {subcategory} case based on these details:
                
                Case details: {cleaned_case_text}
                Form data: {form_data}
                
                The title MUST NOT contain any personally identifiable information (PII) such as names, addresses, specific dates, or unique identifiers.
                
                Focus on the legal situation, not the individuals involved.
                Examples of good titles:
                - "Interstate Adoption with Biological Parent Consent"
                - "Workplace Discrimination Based on Religious Practices"
                - "Contested Foreclosure with Improper Notice Claims"
                
                YOUR RESPONSE MUST BE ONLY THE TITLE TEXT, MAXIMUM 70 CHARACTERS.
                """
                
                title_response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You generate concise, specific legal case titles without any PII, maximum 70 characters."},
                        {"role": "user", "content": title_prompt}
                    ]
                )
                
                case_title = title_response.choices[0].message.content.strip('"').strip()
                
                if len(case_title) > 70:
                    case_title = case_title[:67] + "..."
            else:
                if len(case_title) > 70:
                    case_title = case_title[:67] + "..."
            
            prompt = f"""You are a professional legal summarizer assisting a {category} attorney specializing in {subcategory} cases in reviewing potential client leads.

Follow these guidelines:
1. STRICTLY FORBIDDEN: Do not include or reference the original case description.
2. STRICTLY FORBIDDEN: Remove ALL Personally Identifiable Information (PII).
3. Each bullet point should be a complete, professional statement.
4. Use formal legal terminology relevant to {category} cases.
5. Focus only on legal aspects, requirements, and considerations.
6. Ensure descriptions are abstract and applicable to similar cases.

### **PII-Cleaned Case Details:**
{cleaned_case_text}

### **User-Provided Form Responses:**
{form_data}

Now, create a structured case summary:
{{
  "title": "{case_title}",
  "summary": "summary with sections:
              General Case Summary
                concise paragraph (3-4 sentences) summarizing core legal situation
              Key aspects of the case
                [4-5 bullet points listing key legal components]
              Potential Merits of the Case
                [4-5 bullet points analyzing legal strategies and potential outcomes]
              Critical factors
                [4-5 bullet points listing and analyzing critical factors of the case]
            
              "
}}"""

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a legal document summarizer."},
                    {"role": "user", "content": prompt}
                ]
            )

            summary = response.choices[0].message.content

            return {
                "status": "success",
                "timestamp": datetime.utcnow().isoformat(),
                "summary": summary
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

def create_subcategory_to_form_mapping():
    return {
        "Adoptions": "Form for Adoptions",
        "Child Custody & Visitation": "Form for Child Custody & Visitation", 
        "Child Support": "Form for Child Support",
        "Divorce": "Form for Divorce",
        "Guardianship": "Form for Guardianship",
        "Paternity": "Form for Paternity",
        "Separations": "Form for Separations",
        "Spousal Support or Alimony": "Form for Spousal Support or Alimony",
        "Disabilities": "Form for Disabilities",
        "Employment Contracts": "Form for Employment Contracts",
        "Employment Discrimination": "Form for Employment Discrimination",
        "Pensions and Benefits": "Form for Pensions and Benefits", 
        "Sexual Harassment": "Form for Sexual Harassment",
        "Wages and Overtime Pay": "Form for Wages and Overtime Pay",
        "Workplace Disputes": "Form for Workplace Disputes",
        "Wrongful Termination": "Form for Wrongful Termination",
        "General Criminal Defense": "Form for General Criminal Defense",
        "Environmental Violations": "Form for Environmental Violations",
        "Drug Crimes": "Form for Drug Crimes",
        "Drunk Driving/DUI/DWI": "Form for Drunk Driving/DUI/DWI",
        "Felonies": "Form for Felonies", 
        "Misdemeanors": "Form for Misdemeanors",
        "Speeding and Moving Violations": "Form for Speeding and Moving Violations",
        "White Collar Crime": "Form for White Collar Crime",
        "Tax Evasion": "Form for Tax Evasion",
        "Commercial Real Estate": "Form for Commercial Real Estate",
        "Condominiums and Cooperatives": "Form for Condominiums and Cooperatives",
        "Construction Disputes": "Form for Construction Disputes",
        "Foreclosures": "Form for Foreclosures",
        "Mortgages": "Form for Mortgages",
        "Purchase and Sale of Residence": "Form for Purchase and Sale of Residence",
        "Title and Boundary Disputes": "Form for Title and Boundary Disputes",
        "Breach of Contract": "Form for Breach of Contract",
        "Corporate Tax": "Form for Corporate Tax",
        "Business Disputes": "Form for Business Disputes",
        "Buying and Selling a Business": "Form for Buying and Selling a Business",
        "Contract Drafting and Review": "Form for Contract Drafting and Review",
        "Corporations, LLCs, Partnerships, etc.": "Form for Corporations, LLCs, Partnerships, etc.",
        "Entertainment Law": "Form for Entertainment Law",
        "Citizenship": "Form for Citizenship",
        "Deportation": "Form for Deportation", 
        "Permanent Visas or Green Cards": "Form for Permanent Visas or Green Cards",
        "Temporary Visas": "Form for Temporary Visas",
        "Automobile Accidents": "Form for Automobile Accidents",
        "Dangerous Property or Buildings": "Form for Dangerous Property or Buildings",
        "Defective Products": "Form for Defective Products",
        "Medical Malpractice": "Form for Medical Malpractice", 
        "Personal Injury (General)": "Form for Personal Injury (General)",
        "Contested Wills or Probate": "Form for Contested Wills or Probate",
        "Drafting Wills and Trusts": "Form for Drafting Wills and Trusts",
        "Estate Administration": "Form for Estate Administration",
        "Estate Planning": "Form for Estate Planning",
        "Collections": "Form for Collections",
        "Consumer Bankruptcy": "Form for Consumer Bankruptcy",
        "Consumer Credit": "Form for Consumer Credit", 
        "Income Tax": "Form for Income Tax",
        "Property Tax": "Form for Property Tax",
        "Education and Schools": "Form for Education and Schools",
        "Social Security – Disability": "Form for Social Security – Disability",
        "Social Security – Retirement": "Form for Social Security – Retirement",
        "Social Security – Dependent Benefits": "Form for Social Security – Dependent Benefits",
        "Social Security – Survivor Benefits": "Form for Social Security – Survivor Benefits", 
        "Veterans Benefits": "Form for Veterans Benefits",
        "General Administrative Law": "Form for General Administrative Law",
        "Environmental Law": "Form for Environmental Law",
        "Liquor Licenses": "Form for Liquor Licenses",
        "Constitutional Law": "Form for Constitutional Law",
        "Attorney Malpractice": "Form for Attorney Malpractice",
        "Defective Products": "Form for Defective Products", 
        "Warranties": "Form for Warranties",
        "Consumer Protection and Fraud": "Form for Consumer Protection and Fraud",
        "Copyright": "Form for Copyright",
        "Patents": "Form for Patents",
        "Trademarks": "Form for Trademarks",
        "General Landlord and Tenant Issues": "Form for General Landlord and Tenant Issues"
    }

def find_form_by_subcategory(subcategory, forms_data):
    mapping = create_subcategory_to_form_mapping()
    target_title = mapping.get(subcategory)
    
    if target_title:
        for form_id, form_data in forms_data.items():
            if form_data.get("title") == target_title:
                return form_id, form_data
    
    return None, None

class MultiAgentLegalAnalyzer(SynchronousMultiAgentLegalAnalyzer):
    pass

CaseAnalyzer = MultiAgentLegalAnalyzer
BulletproofCaseAnalyzer = MultiAgentLegalAnalyzer