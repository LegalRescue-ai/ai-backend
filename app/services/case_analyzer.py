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
            
            return self._perform_comprehensive_analysis(case_text, keywords_found + concepts_found, start_time)
                
        except Exception as e:
            return None
    
    def _perform_comprehensive_analysis(self, case_text: str, indicators_found: List[str], start_time: float) -> Optional[LegalClassification]:
        legal_definitions = self._get_legal_area_definitions()
        case_examples = "\n".join([f"• {desc}" for desc in self.case_descriptions])
        
        system_prompt = f"""You are a senior {self.legal_area} attorney with 25+ years of experience. Your expertise includes all aspects of {self.legal_area} legal practice, statutes, regulations, and case law.

Your role is to conduct comprehensive legal analysis to determine if a case requires {self.legal_area} legal representation. You must analyze the legal substance of the case, not just look for keywords.

ANALYSIS FRAMEWORK:
1. Legal Relationship Analysis: What legal relationships exist between the parties?
2. Rights and Obligations: What legal rights, duties, or obligations are at stake?
3. Governing Law: What statutes, regulations, or legal principles apply?
4. Legal Remedy: What type of legal remedy or resolution is needed?
5. Jurisdiction: Which legal specialist would be most qualified to handle this matter?

CRITICAL INSTRUCTION: Make your determination based on legal analysis, not keyword matching. Focus on the underlying legal issues and relationships."""

        analysis_prompt = f"""CASE FOR ANALYSIS:
"{case_text}"

{self.legal_area.upper()} LEGAL DOMAIN ANALYSIS:

AREA OF LAW DEFINITION:
{legal_definitions}

SUBCATEGORIES WITHIN {self.legal_area.upper()}:
{', '.join(self.subcategories)}

TYPICAL CASE SCENARIOS:
{case_examples}

COMPREHENSIVE LEGAL ANALYSIS REQUIRED:

1. LEGAL RELATIONSHIP ANALYSIS:
   - What is the primary legal relationship between parties?
   - Are there contractual, statutory, or common law obligations involved?
   - What type of legal dispute or matter is this?

2. SUBSTANTIVE LAW ANALYSIS:
   - Which area of law governs this situation?
   - What legal principles, statutes, or regulations apply?
   - What legal rights or duties are at issue?

3. PROCEDURAL CONSIDERATIONS:
   - What type of legal proceeding or action is needed?
   - Which court or administrative body has jurisdiction?
   - What legal remedies are available?

4. PROFESSIONAL COMPETENCY ASSESSMENT:
   - Would a {self.legal_area} attorney be the primary specialist needed?
   - Is this matter within the core competency of {self.legal_area} practice?
   - Are there any secondary legal areas involved?

DECISION CRITERIA:
- PRIMARY TEST: Does this case primarily involve {self.legal_area} legal issues?
- COMPETENCY TEST: Would a {self.legal_area} attorney be the most qualified specialist?
- SUBSTANCE TEST: Do the legal rights, obligations, or remedies fall within {self.legal_area}?

CONFIDENCE LEVELS:
- HIGH: Clear {self.legal_area} matter requiring {self.legal_area} expertise with strong legal basis
- MEDIUM: Likely {self.legal_area} matter but requires further investigation or has mixed legal issues
- LOW: Possible {self.legal_area} connection but uncertain or weak legal basis

REQUIRED JSON RESPONSE FORMAT:
{{
    "is_relevant": true/false,
    "primary_legal_area": "{self.legal_area} or other area name",
    "subcategory": "specific subcategory name or null",
    "confidence_level": "high/medium/low",
    "legal_reasoning": "detailed legal analysis explaining the determination",
    "legal_relationships": ["key legal relationships identified"],
    "applicable_law": ["relevant statutes, regulations, or legal principles"],
    "legal_remedies": ["available legal remedies or actions"],
    "urgency_assessment": 0.0-1.0,
    "complexity_assessment": 0.0-1.0,
    "competency_match": "assessment of whether {self.legal_area} attorney is most qualified",
    "secondary_areas": ["other legal areas that may be involved"]
}}

CRITICAL: Base your analysis on legal substance and relationships, not keyword presence. Every case involves legal issues that can be analyzed and classified."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": analysis_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=1500
            )
            
            result = json.loads(response.choices[0].message.content)
            
            if not result.get("is_relevant", False) or result.get("primary_legal_area") != self.legal_area:
                return None
            
            subcategory = result.get("subcategory")
            if not subcategory or subcategory not in self.subcategories:
                subcategory = self._determine_best_subcategory(case_text, result)
            
            classification_dict = {
                "category": self.legal_area,
                "subcategory": subcategory,
                "confidence": result.get("confidence_level", "medium"),
                "reasoning": result.get("legal_reasoning", "")
            }
            
            validation = OutputGuardrails.validate_classification(
                classification_dict, 
                {self.legal_area: self.subcategories}
            )
            
            if not validation["is_valid"]:
                return None
            
            urgency = result.get("urgency_assessment", 0.5)
            complexity = result.get("complexity_assessment", 0.5)
            confidence_weight = {"high": 1.0, "medium": 0.7, "low": 0.5}.get(result.get("confidence_level", "medium"), 0.7)
            
            relevance_score = (urgency * 0.3 + complexity * 0.3 + confidence_weight * 0.4)
            processing_time = time.time() - start_time
            
            confidence_map = {
                "high": ConfidenceLevel.HIGH, 
                "medium": ConfidenceLevel.MEDIUM, 
                "low": ConfidenceLevel.LOW
            }
            
            classification = LegalClassification(
                category=self.legal_area,
                subcategory=subcategory,
                confidence=confidence_map.get(result.get("confidence_level", "medium"), ConfidenceLevel.MEDIUM),
                reasoning=result.get("legal_reasoning", ""),
                keywords_found=indicators_found,
                relevance_score=relevance_score,
                urgency_score=urgency,
                agent_id=self.agent_id,
                processing_time=processing_time,
                fallback_used=False
            )
            
            return classification
            
        except Exception as e:
            return self._perform_fallback_analysis(case_text, start_time)
    
    def _get_legal_area_definitions(self) -> str:
        definitions = {
            "Family Law": "Legal matters involving family relationships, including marriage, divorce, child custody, adoption, domestic relations, and family-related disputes. Governs legal rights and obligations between family members.",
            
            "Employment Law": "Legal matters involving the employer-employee relationship, including workplace rights, employment contracts, discrimination, harassment, wrongful termination, wages, and workplace conditions. Covers both statutory employment protections and contractual employment relationships.",
            
            "Criminal Law": "Legal matters involving violations of criminal statutes, including arrests, charges, criminal proceedings, and defense against criminal allegations. Covers felonies, misdemeanors, and criminal violations prosecuted by the state.",
            
            "Real Estate Law": "Legal matters involving real property transactions, ownership rights, property disputes, real estate contracts, mortgages, foreclosures, and property development. Governs rights and obligations related to real property.",
            
            "Business/Corporate Law": "Legal matters involving business operations, commercial transactions, corporate governance, business contracts, partnerships, business disputes, and commercial relationships. Includes entertainment industry contracts and professional service agreements.",
            
            "Immigration Law": "Legal matters involving immigration status, visa applications, deportation proceedings, citizenship, asylum, and immigration-related proceedings before immigration courts and agencies.",
            
            "Personal Injury Law": "Legal matters involving physical injuries, medical malpractice, accidents, negligence claims, and compensation for personal injuries or damages caused by others' actions or negligence.",
            
            "Wills, Trusts, & Estates Law": "Legal matters involving estate planning, probate proceedings, will contests, trust administration, inheritance, and posthumous asset distribution. Governs transfer of assets upon death or incapacity.",
            
            "Bankruptcy, Finances, & Tax Law": "Legal matters involving debt relief, bankruptcy proceedings, tax disputes, financial restructuring, creditor-debtor relationships, and tax compliance or disputes with tax authorities.",
            
            "Government & Administrative Law": "Legal matters involving government agencies, administrative proceedings, government benefits, regulatory compliance, administrative appeals, and disputes with government entities or administrative bodies.",
            
            "Product & Services Liability Law": "Legal matters involving defective products, service failures, consumer protection, professional malpractice, warranties, and liability for products or services that cause harm or fail to perform as expected.",
            
            "Intellectual Property Law": "Legal matters involving patents, copyrights, trademarks, trade secrets, and other intellectual property rights, including infringement claims and IP protection.",
            
            "Landlord/Tenant Law": "Legal matters involving rental relationships, lease agreements, eviction proceedings, habitability issues, rent disputes, and rights and obligations between landlords and tenants."
        }
        
        return definitions.get(self.legal_area, f"Legal matters primarily governed by {self.legal_area} statutes, regulations, and legal principles.")
    
    def _determine_best_subcategory(self, case_text: str, analysis_result: Dict[str, Any]) -> str:
        if not self.subcategories:
            return "General"
        
        subcategory_prompt = f"""Based on your analysis of this {self.legal_area} case, determine the most appropriate subcategory.

CASE: {case_text}

ANALYSIS RESULTS: {analysis_result}

AVAILABLE SUBCATEGORIES:
{chr(10).join([f"• {sub}" for sub in self.subcategories])}

Select the single most appropriate subcategory that best matches the primary legal issue. Respond with only the exact subcategory name."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": f"You select the most appropriate {self.legal_area} subcategory based on legal analysis."},
                    {"role": "user", "content": subcategory_prompt}
                ],
                temperature=0.1,
                max_tokens=100
            )
            
            selected = response.choices[0].message.content.strip().strip('"').strip("'")
            
            if selected in self.subcategories:
                return selected
            
            for subcategory in self.subcategories:
                if subcategory.lower() in selected.lower() or selected.lower() in subcategory.lower():
                    return subcategory
            
            return self.subcategories[0]
            
        except Exception:
            return self.subcategories[0]
    
    def _perform_fallback_analysis(self, case_text: str, start_time: float) -> Optional[LegalClassification]:
        fallback_prompt = f"""As a {self.legal_area} attorney, conduct fallback analysis for potential {self.legal_area} legal issues that may not be immediately apparent.

CASE: "{case_text}"

FALLBACK ANALYSIS CRITERIA:
1. Could this situation evolve into a {self.legal_area} matter?
2. Are there underlying {self.legal_area} legal relationships?
3. Would consulting a {self.legal_area} attorney be beneficial?
4. Are there {self.legal_area} legal principles that apply?

DECISION: Even if not clearly a {self.legal_area} matter, if there is ANY reasonable connection to {self.legal_area}, classify with LOW confidence rather than rejecting.

SUBCATEGORIES: {', '.join(self.subcategories)}

JSON RESPONSE:
{{
    "is_relevant": true/false,
    "subcategory": "most appropriate subcategory or null",
    "confidence_level": "low/medium",
    "legal_reasoning": "detailed reasoning for classification or rejection",
    "urgency_assessment": 0.0-1.0,
    "complexity_assessment": 0.0-1.0
}}"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": f"You are conducting fallback analysis for {self.legal_area}. Prefer classification with low confidence over rejection when any connection exists."},
                    {"role": "user", "content": fallback_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=800
            )
            
            result = json.loads(response.choices[0].message.content)
            
            if not result.get("is_relevant", False):
                return None
            
            subcategory = result.get("subcategory") or self.subcategories[0]
            if subcategory not in self.subcategories:
                subcategory = self.subcategories[0]
            
            processing_time = time.time() - start_time
            confidence_level = result.get("confidence_level", "low")
            
            confidence_map = {
                "high": ConfidenceLevel.MEDIUM,  # Cap fallback at medium
                "medium": ConfidenceLevel.MEDIUM,
                "low": ConfidenceLevel.LOW
            }
            
            classification = LegalClassification(
                category=self.legal_area,
                subcategory=subcategory,
                confidence=confidence_map.get(confidence_level, ConfidenceLevel.LOW),
                reasoning=result.get("legal_reasoning", "Fallback analysis classification"),
                keywords_found=[],
                relevance_score=0.4,  # Lower relevance for fallback
                urgency_score=result.get("urgency_assessment", 0.5),
                agent_id=self.agent_id,
                processing_time=processing_time,
                fallback_used=True
            )
            
            return classification
                
        except Exception as e:
            return None

class FinalFallbackAgent(BaseAgent):
    def __init__(self, agent_id: str, client: openai.OpenAI, legal_categories: Dict[str, List[str]]):
        super().__init__(agent_id, client)
        self.legal_categories = legal_categories
        
    def process(self, case_text: str, context: Dict[str, Any] = None) -> LegalClassification:
        start_time = time.time()
        
        comprehensive_prompt = f"""You are a senior legal analyst with expertise across all areas of law. You must classify this case into one of the established legal categories based on comprehensive legal analysis.

CASE FOR CLASSIFICATION: "{case_text}"

LEGAL CATEGORIES AND THEIR CORE DOMAINS:

1. **Family Law**: Marriage, divorce, child custody, adoption, family relationships, domestic relations
2. **Employment Law**: Employer-employee relationships, workplace rights, employment discrimination, labor disputes
3. **Criminal Law**: Criminal charges, arrests, criminal violations, criminal defense, criminal proceedings
4. **Real Estate Law**: Property transactions, mortgages, real estate disputes, property rights, foreclosures
5. **Business/Corporate Law**: Business contracts, commercial disputes, corporate matters, professional services, entertainment contracts
6. **Immigration Law**: Immigration status, deportation, visas, citizenship, immigration proceedings
7. **Personal Injury Law**: Physical injuries, accidents, medical malpractice, negligence claims, injury compensation
8. **Wills, Trusts, & Estates Law**: Estate planning, probate, inheritance, trusts, posthumous asset distribution
9. **Bankruptcy, Finances, & Tax Law**: Debt relief, bankruptcy, tax disputes, financial problems, creditor issues
10. **Government & Administrative Law**: Government agencies, administrative proceedings, government benefits, regulatory matters
11. **Product & Services Liability Law**: Defective products, service failures, consumer protection, professional malpractice
12. **Intellectual Property Law**: Patents, copyrights, trademarks, IP protection, IP infringement
13. **Landlord/Tenant Law**: Rental relationships, lease disputes, eviction proceedings, landlord-tenant rights

ANALYSIS METHODOLOGY:
1. Identify the primary parties and their relationship
2. Determine the core legal issue or dispute
3. Assess which area of law governs the situation
4. Consider which legal specialist would be most qualified
5. Match to the most appropriate category and subcategory

SUBCATEGORIES BY CATEGORY:
{self._format_subcategories()}

MANDATORY CLASSIFICATION: You must classify this case. Choose the category that best fits the primary legal issue, even if the fit is not perfect.

JSON RESPONSE REQUIRED:
{{
    "category": "exact category name from the 13 categories above",
    "subcategory": "most appropriate subcategory from the chosen category",
    "confidence_level": "low/medium/high",
    "legal_reasoning": "detailed explanation of classification based on legal analysis",
    "primary_legal_issue": "the main legal problem identified",
    "urgency_assessment": 0.0-1.0,
    "complexity_assessment": 0.0-1.0,
    "alternative_categories": ["other categories that could potentially apply"]
}}"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a senior legal analyst who must classify every case into one of the 13 established legal categories. Use comprehensive legal analysis to determine the best fit. Every case can be classified."},
                    {"role": "user", "content": comprehensive_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=1200
            )
            
            result = json.loads(response.choices[0].message.content)
            
            category = result.get("category", "Business/Corporate Law")
            subcategory = result.get("subcategory")
            
            # Validate and correct if necessary
            if category not in self.legal_categories:
                category = "Business/Corporate Law"
            
            if not subcategory or subcategory not in self.legal_categories[category]:
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
                confidence=confidence_map.get(result.get("confidence_level", "medium"), ConfidenceLevel.MEDIUM),
                reasoning=result.get("legal_reasoning", "Comprehensive legal analysis classification"),
                keywords_found=[],
                relevance_score=0.7,
                urgency_score=result.get("urgency_assessment", 0.5),
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
                reasoning="System fallback classification - requires manual review",
                keywords_found=[],
                relevance_score=0.6,
                urgency_score=0.5,
                agent_id=self.agent_id,
                processing_time=processing_time,
                fallback_used=True
            )
    
    def _format_subcategories(self) -> str:
        formatted = []
        for category, subcategories in self.legal_categories.items():
            subcats = ", ".join(subcategories)
            formatted.append(f"**{category}**: {subcats}")
        return "\n".join(formatted)

class CoordinatorAgent(BaseAgent):
    def __init__(self, agent_id: str, client: openai.OpenAI):
        super().__init__(agent_id, client)
        self.role = AgentRole.COORDINATOR
        
    def process(self, case_text: str, context: Dict[str, Any] = None) -> CaseAnalysisResult:
        classifications = context.get("classifications", [])
        
        if not classifications:
            raise Exception("No valid classifications from specialist agents")
        
        # Sort by relevance and confidence
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
        
        # Ensure minimum confidence
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
    SYSTEM_VERSION = "5.0.0"
    PROMPT_VERSION = "2024-07-18-comprehensive"
    
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
                    "Defendant charged with felony drug possession requiring criminal defense strategy",
                    "Individual arrested for DUI seeking representation for criminal proceedings",
                    "Person facing white-collar fraud charges in federal criminal court",
                    "Defendant requiring legal representation for assault charges and plea negotiations",
                    "Individual needing criminal defense for theft allegations and trial preparation"
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
                    "Individual facing removal proceedings requiring deportation defense",
                    "Foreign national seeking asylum protection from persecution",
                    "Person applying for permanent residence through family sponsorship",
                    "Individual appealing denial of citizenship application",
                    "Worker requiring legal assistance with employment-based visa application"
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
                    "Couple seeking legal divorce with contested child custody arrangements",
                    "Parent requesting modification of child support due to changed circumstances",
                    "Individual pursuing stepchild adoption requiring legal documentation",
                    "Party disputing paternity and seeking court-ordered DNA testing",
                    "Parent seeking emergency custody modification due to safety concerns"
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
                    "Employee terminated in retaliation for reporting workplace safety violations",
                    "Worker experiencing age and gender discrimination in promotion decisions",
                    "Employee subjected to sexual harassment by supervisor requiring legal action",
                    "Worker denied reasonable disability accommodation in workplace",
                    "Employee denied overtime compensation despite working excessive hours"
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
                    "Individual injured in motor vehicle collision seeking compensation for damages",
                    "Person injured in slip and fall accident due to negligent premises maintenance",
                    "Patient harmed by medical malpractice requiring professional liability claim",
                    "Consumer injured by defective product seeking product liability compensation",
                    "Individual suffering complications from misdiagnosed medical condition"
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
                    "Business partners disputing partnership agreement terms and profit distribution",
                    "Company facing breach of contract claims from commercial vendor",
                    "Corporation requiring legal assistance with merger and acquisition transaction",
                    "Business owner discovering competitor using proprietary trade secrets",
                    "Individual with modeling agency contract dispute regarding service delivery",
                    "Professional service provider facing contract performance disputes",
                    "Entertainment industry professional requiring contract review and negotiation"
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
                    "Creator discovering unauthorized use of copyrighted material requiring enforcement action",
                    "Business owner facing trademark infringement claims from competitor",
                    "Inventor seeking patent protection for new technological innovation",
                    "Company pursuing trade secret misappropriation claim against former employee",
                    "Artist requiring copyright registration and licensing agreement assistance"
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
                    "Homeowner facing foreclosure proceedings requiring legal defense",
                    "Property buyer discovering title defects requiring legal resolution",
                    "Real estate transaction delayed due to contract disputes and inspection issues",
                    "Property owners disputing boundary lines with neighboring landowners",
                    "Commercial property developer facing zoning and land use restrictions"
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
                    "Consumer injured by defective product requiring product liability claim",
                    "Individual harmed by contaminated food product seeking compensation",
                    "Client pursuing attorney malpractice claim for missed legal deadlines",
                    "Consumer deceived by false advertising requiring consumer protection action",
                    "Person harmed by recalled product that was not properly warned about defects"
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
                    "Individual filing Chapter 7 bankruptcy for overwhelming debt relief",
                    "Debtor facing aggressive creditor collection actions requiring legal protection",
                    "Taxpayer undergoing IRS audit requiring professional tax representation",
                    "Property owner disputing tax assessment and seeking property tax reduction",
                    "Small business owner requiring tax planning and compliance assistance"
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
                    "Individual appealing denial of Social Security disability benefits determination",
                    "Veteran challenging reduction of VA benefits requiring administrative appeal", 
                    "Person denied unemployment benefits seeking administrative review",
                    "Individual appealing Medicare coverage denial through administrative process",
                    "Professional facing license suspension by regulatory agency requiring defense",
                    "Business owner appealing regulatory agency enforcement action",
                    "Individual challenging government agency benefit determination"
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
                    "Family member contesting will due to suspicious circumstances and undue influence",
                    "Individual establishing trust for minor children and estate planning purposes",
                    "Executor facing complex probate administration with contested inheritance claims",
                    "Business owner requiring comprehensive estate planning for asset protection",
                    "Family member seeking power of attorney for incapacitated relative"
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
                    "Tenant facing eviction proceedings requiring legal defense",
                    "Renter pursuing security deposit return from non-responsive landlord",
                    "Tenant dealing with habitability issues and landlord negligence",
                    "Landlord pursuing eviction for lease violations and non-payment",
                    "Renter challenging improper rent increase under rent control regulations"
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
                "method": "comprehensive_legal_analysis",
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
                "method": "comprehensive_legal_analysis",
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
                "analysis_type": "comprehensive_legal_analysis",
                "success": success,
                "total_agents": len(self.specialist_agents) + 2,
                "responding_agents": len([p for p in agent_performance.values() if p.get("status") == "success"]),
                "fallback_agents_used": fallback_count,
                "high_confidence_classifications": high_confidence_count,
                "guardrails_applied": True,
                "comprehensive_analysis_enabled": True
            }
                
        except Exception as e:
            pass

    def generate_final_summary(self, initial_analysis: Dict[str, Any], form_data: Dict[str, Any]) -> Dict[str, Any]:
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
                    model="gpt-4o-mini",
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
                model="gpt-4o-mini",
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