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

from app.utils.pii_remover import PIIRemover

class ConfidenceLevel(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class AgentRole(Enum):
    SPECIALIST = "specialist"
    COORDINATOR = "coordinator"
    VALIDATOR = "validator"
    SUMMARIZER = "summarizer"

@dataclass
class LegalClassification:
    """Individual classification result from a specialist agent"""
    category: str
    subcategory: str
    confidence: ConfidenceLevel
    reasoning: str
    keywords_found: List[str]
    relevance_score: float
    urgency_score: float
    agent_id: str
    processing_time: float

@dataclass
class CaseAnalysisResult:
    """Final coordinated result from all agents"""
    primary_classification: LegalClassification
    secondary_classifications: List[LegalClassification]
    complexity_level: str
    requires_multiple_attorneys: bool
    case_summary: str
    total_processing_time: float
    agents_consulted: List[str]
    confidence_consensus: float

class BaseAgent(ABC):
    """Abstract base class for all agents in the system"""
    
    def __init__(self, agent_id: str, client: openai.OpenAI):
        self.agent_id = agent_id
        self.client = client
        self.role = AgentRole.SPECIALIST
        
    @abstractmethod
    def process(self, case_text: str, context: Dict[str, Any] = None) -> Any:
        """Process the case text and return results"""
        pass

class LegalSpecialistAgent(BaseAgent):
    """Specialist agent focused on one area of law - ENCODING FIXED"""
    
    def __init__(self, agent_id: str, client: openai.OpenAI, legal_area: str, 
                 keywords: List[str], subcategories: List[str]):
        super().__init__(agent_id, client)
        self.legal_area = legal_area
        self.keywords = keywords
        self.subcategories = subcategories
        self.role = AgentRole.SPECIALIST
        
    def process(self, case_text: str, context: Dict[str, Any] = None) -> Optional[LegalClassification]:
        """Analyze case for relevance to this legal area - ENCODING SAFE"""
        start_time = time.time()
        
        try:
            # Simple validation - no complex encoding handling
            if not case_text or len(case_text.strip()) < 10:
                print(f"[{self.legal_area}] Case text too short")
                return None
            
            # Simple keyword screening
            case_lower = case_text.lower()
            keywords_found = [kw for kw in self.keywords if kw.lower() in case_lower]
            
            # SIMPLIFIED DEBUG OUTPUT - no emojis, simple text
            print(f"[{self.legal_area}] Agent Analysis:")
            print(f"   Case preview: {case_text[:100]}...")
            print(f"   Keywords found: {keywords_found}")
            
            if not keywords_found:
                print(f"   Result: Not relevant - no keywords matched")
                return None
                
            print(f"   Result: Relevant - proceeding with LLM analysis")
                
            # LLM analysis - same approach as your working simple version
            prompt = f"""You are a {self.legal_area} specialist attorney with 20+ years experience.

ANALYZE THIS CASE ONLY FROM A {self.legal_area.upper()} PERSPECTIVE:
"{case_text}"

Available subcategories for {self.legal_area}:
{', '.join(self.subcategories)}

STRICT INSTRUCTIONS:
- If this case has {self.legal_area} issues, classify it precisely
- If this case has NO {self.legal_area} issues, return "NOT_RELEVANT"
- Focus ONLY on {self.legal_area} - ignore other legal areas
- Rate urgency: how quickly does the {self.legal_area} issue need attention?
- Rate complexity: how complex is the {self.legal_area} portion?

Return JSON in this exact format:
{{
    "relevant": true/false,
    "subcategory": "exact subcategory name or null",
    "confidence": "high/medium/low",
    "reasoning": "specific {self.legal_area} analysis",
    "urgency_score": 0.0-1.0,
    "complexity_score": 0.0-1.0,
    "key_factors": ["3-4 key {self.legal_area} factors"],
    "immediate_actions": ["2-3 immediate {self.legal_area} actions needed"]
}}"""

            # Use same approach as your working simple version
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system", 
                        "content": f"You are an expert {self.legal_area} attorney. ONLY analyze {self.legal_area} issues. Be precise and specific."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=600
            )
            
            # SIMPLE JSON PARSING - same as working version
            result = json.loads(response.choices[0].message.content)
            
            print(f"   LLM Response: {result}")
            
            if not result.get("relevant", False):
                print(f"   Final Result: LLM determined not relevant")
                return None
                
            # Calculate relevance score
            urgency = result.get("urgency_score", 0.5)
            complexity = result.get("complexity_score", 0.5)
            keyword_density = len(keywords_found) / max(len(self.keywords), 1)
            confidence_weight = {"high": 1.0, "medium": 0.7, "low": 0.4}.get(result.get("confidence", "medium"), 0.7)
            
            relevance_score = (urgency * 0.3 + complexity * 0.2 + keyword_density * 0.2 + confidence_weight * 0.3)
            processing_time = time.time() - start_time
            
            confidence_map = {
                "high": ConfidenceLevel.HIGH, 
                "medium": ConfidenceLevel.MEDIUM, 
                "low": ConfidenceLevel.LOW
            }
            
            classification = LegalClassification(
                category=self.legal_area,
                subcategory=result.get("subcategory", "General"),
                confidence=confidence_map.get(result.get("confidence", "medium"), ConfidenceLevel.MEDIUM),
                reasoning=result.get("reasoning", ""),
                keywords_found=keywords_found,
                relevance_score=relevance_score,
                urgency_score=urgency,
                agent_id=self.agent_id,
                processing_time=processing_time
            )
            
            print(f"   SUCCESS: Created classification: {classification.category} - {classification.subcategory}")
            return classification
            
        except json.JSONDecodeError as e:
            print(f"[{self.legal_area}] JSON parse error: {e}")
            return None
        except Exception as e:
            print(f"[{self.legal_area}] Agent error: {e}")
            return None

class CoordinatorAgent(BaseAgent):
    """Coordinates multiple specialist agents and makes final decisions"""
    
    def __init__(self, agent_id: str, client: openai.OpenAI):
        super().__init__(agent_id, client)
        self.role = AgentRole.COORDINATOR
        
    def process(self, case_text: str, context: Dict[str, Any] = None) -> CaseAnalysisResult:
        """Coordinate analysis across all specialist agents"""
        classifications = context.get("classifications", [])
        
        if not classifications:
            raise Exception("No valid classifications from specialist agents")
            
        # Sort by combined relevance and urgency
        classifications.sort(key=lambda x: (x.relevance_score + x.urgency_score) / 2, reverse=True)
        
        primary = classifications[0]
        secondaries = classifications[1:] if len(classifications) > 1 else []
        
        # Determine complexity
        complexity_level = self._assess_complexity(classifications)
        requires_multiple_attorneys = len(classifications) > 1
        
        # Calculate consensus confidence
        confidence_scores = [self._confidence_to_score(c.confidence) for c in classifications]
        confidence_consensus = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5
        
        # Get processing stats
        total_processing_time = sum(c.processing_time for c in classifications)
        agents_consulted = [c.agent_id for c in classifications]
        
        return CaseAnalysisResult(
            primary_classification=primary,
            secondary_classifications=secondaries,
            complexity_level=complexity_level,
            requires_multiple_attorneys=requires_multiple_attorneys,
            case_summary="",  # Will be filled by SummarizerAgent
            total_processing_time=total_processing_time,
            agents_consulted=agents_consulted,
            confidence_consensus=confidence_consensus
        )
    
    def _assess_complexity(self, classifications: List[LegalClassification]) -> str:
        """Assess case complexity based on multiple factors"""
        num_areas = len(classifications)
        avg_complexity = sum(c.relevance_score for c in classifications) / num_areas
        high_urgency_count = sum(1 for c in classifications if c.urgency_score > 0.7)
        
        if num_areas == 1 and avg_complexity < 0.6:
            return "simple"
        elif num_areas <= 2 and high_urgency_count <= 1:
            return "moderate"
        else:
            return "complex"
    
    def _confidence_to_score(self, confidence: ConfidenceLevel) -> float:
        """Convert confidence enum to numeric score"""
        return {
            ConfidenceLevel.HIGH: 0.9,
            ConfidenceLevel.MEDIUM: 0.7,
            ConfidenceLevel.LOW: 0.4
        }.get(confidence, 0.5)

class SummarizerAgent(BaseAgent):
    """Creates comprehensive case summaries considering all legal areas"""
    
    def __init__(self, agent_id: str, client: openai.OpenAI):
        super().__init__(agent_id, client)
        self.role = AgentRole.SUMMARIZER
        
    def process(self, case_text: str, context: Dict[str, Any] = None) -> str:
        """Generate comprehensive summary of multi-faceted case"""
        result = context.get("analysis_result")
        
        if not result:
            return "Summary unavailable - no analysis result provided"
            
        primary = result.primary_classification
        secondaries = result.secondary_classifications
        
        areas_involved = [primary.category] + [s.category for s in secondaries]
        
        prompt = f"""Create a professional legal case summary for a multi-faceted case.

CASE TEXT: "{case_text}"

LEGAL ANALYSIS:
Primary Issue: {primary.category} - {primary.subcategory}
- Confidence: {primary.confidence.value}
- Urgency: {primary.urgency_score:.1f}/1.0
- Reasoning: {primary.reasoning}

Additional Legal Areas: {len(secondaries)}
{chr(10).join([f"- {s.category} - {s.subcategory} (urgency: {s.urgency_score:.1f})" for s in secondaries])}

Case Complexity: {result.complexity_level}
Multiple Attorneys Needed: {result.requires_multiple_attorneys}

REQUIREMENTS:
- Professional but accessible language
- Acknowledge ALL legal areas involved
- Prioritize issues by urgency and complexity
- Suggest coordination strategy if multiple attorneys needed
- Include immediate next steps
- 3-4 sentences maximum

Focus on providing actionable insights for legal professionals."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a senior legal coordinator who specializes in complex multi-faceted cases. Create clear, actionable case summaries."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=400
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Summary generation error: {e}")
            return f"Multi-area case involving {', '.join(areas_involved)}. Primary focus: {primary.category} - {primary.subcategory}."

class SynchronousMultiAgentLegalAnalyzer:
    """
    ENCODING-SAFE Multi-Agent Legal Analyzer
    Uses the same simple approach as your working single-agent version
    """
    
    # Version tracking
    SYSTEM_VERSION = "3.1.0-ENCODING-FIXED"
    PROMPT_VERSION = "2024-07-06-encoding-safe"
    
    # Same categories as your working simple version
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
        
        # Initialize specialist agents
        self.specialist_agents = self._create_specialist_agents()
        
        # Initialize coordination agents
        self.coordinator = CoordinatorAgent("coordinator-001", self.client)
        self.summarizer = SummarizerAgent("summarizer-001", self.client)
        
        print(f"Multi-Agent System Initialized:")
        print(f"   - {len(self.specialist_agents)} Specialist Agents")
        print(f"   - 1 Coordinator Agent")
        print(f"   - 1 Summarizer Agent")
        print(f"   - Total: {len(self.specialist_agents) + 2} Agents")

    def _create_specialist_agents(self) -> List[LegalSpecialistAgent]:
        """Create specialist agents for each legal area"""
        
        # Enhanced keywords for better detection
        specialist_configs = [
            {
                "area": "Criminal Law",
                "keywords": ["arrest", "arrested", "charged", "criminal", "crime", "police", "felony", 
                           "misdemeanor", "drugs", "dui", "theft", "assault", "fraud", "jail", "prison",
                           "prosecutor", "defendant", "guilty", "plea", "sentence", "parole", "probation"]
            },
            {
                "area": "Immigration Law", 
                "keywords": ["deport", "deportation", "immigration", "visa", "citizenship", "green card", 
                           "ice", "removal", "asylum", "refugee", "border", "undocumented", "daca"]
            },
            {
                "area": "Family Law",
                "keywords": ["divorce", "custody", "child support", "marriage", "separation", "alimony", 
                           "adoption", "guardianship", "paternity", "visitation", "spousal support"]
            },
            {
                "area": "Employment Law",
                "keywords": ["fired", "employer", "workplace", "discrimination", "harassment", "wages", 
                           "overtime", "wrongful termination", "sexual harassment", "disability", "job", "work"]
            },
            {
                "area": "Personal Injury Law",
                "keywords": ["accident", "injury", "medical malpractice", "car accident", "slip and fall", 
                           "damages", "compensation", "negligence", "liability", "hospital", "doctor error"]
            },
            {
                "area": "Business/Corporate Law",
                "keywords": ["business", "contract", "partnership", "corporation", "llc", "breach", 
                           "partnership dispute", "shareholder", "merger", "acquisition", "competitor"]
            },
            {
                "area": "Intellectual Property Law",
                "keywords": ["copyright", "trademark", "patent", "intellectual property", "logo", 
                           "brand", "content", "copied", "copying", "infringement", "stolen", "plagiarism"]
            },
            {
                "area": "Real Estate Law",
                "keywords": ["real estate", "property", "house", "home", "mortgage", "foreclosure",
                           "deed", "title", "closing", "inspection", "appraisal", "zoning"]
            },
            {
                "area": "Product & Services Liability Law",
                "keywords": ["defective", "product", "recall", "contamination", "malfunction", "warranty",
                           "consumer protection", "false advertising", "attorney malpractice"]
            },
            {
                "area": "Bankruptcy, Finances, & Tax Law",
                "keywords": ["bankruptcy", "debt", "creditor", "collection", "tax", "irs", "audit",
                           "property tax", "income tax", "consumer credit", "chapter 7", "chapter 13"]
            },
            {
                "area": "Government & Administrative Law",
                "keywords": ["social security", "disability", "benefits", "government", "administrative", 
                           "veterans", "unemployment", "medicaid", "medicare", "denied", "claim", "appeal"]
            },
            {
                "area": "Wills, Trusts, & Estates Law",
                "keywords": ["will", "trust", "estate", "probate", "inheritance", "beneficiary", "executor",
                           "power of attorney", "living will", "advance directive"]
            },
            {
                "area": "Landlord/Tenant Law",
                "keywords": ["landlord", "tenant", "lease", "rent", "eviction", "deposit", "repairs",
                           "rental", "apartment", "housing", "mold", "habitability", "security deposit"]
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
                subcategories=subcategories
            )
            agents.append(agent)
            print(f"   Created {config['area']} specialist with {len(config['keywords'])} keywords")
            
        return agents

    def initial_analysis(self, case_text: str, max_retries: int = 2) -> Dict[str, Any]:
        """
        ENCODING-SAFE Multi-Agent Analysis Process
        Uses same simple approach as your working single-agent version
        """
        try:
            start_time = time.time()
            
            print(f"MULTI-AGENT ANALYSIS STARTING")
            print(f"Case preview: {case_text[:100]}...")
            print(f"Deploying {len(self.specialist_agents)} specialist agents...")
            
            # Step 1: Deploy all specialist agents in parallel
            valid_classifications = []
            agent_performance = {}
            
            print(f"Running {len(self.specialist_agents)} agents in parallel...")
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                # Submit all specialist tasks
                future_to_agent = {
                    executor.submit(agent.process, case_text): agent 
                    for agent in self.specialist_agents
                }
                
                # Collect results as they complete
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
                                "processing_time": result.processing_time
                            }
                            print(f"SUCCESS: {agent.legal_area}: {result.subcategory} (relevance: {result.relevance_score:.2f})")
                            
                        else:
                            agent_performance[agent.agent_id] = {
                                "status": "not_relevant"
                            }
                            print(f"SKIP: {agent.legal_area}: Not relevant")
                            
                    except Exception as e:
                        agent_performance[agent.agent_id] = {
                            "status": "error", 
                            "error": str(e)
                        }
                        print(f"ERROR: {agent.legal_area}: Failed - {e}")
            
            if not valid_classifications:
                raise Exception("No specialist agents found relevant legal issues")
            
            print(f"RESULTS: {len(valid_classifications)} legal areas identified")
            
            # Step 2: Coordinate results
            print(f"Coordinator processing results...")
            coordination_context = {"classifications": valid_classifications}
            analysis_result = self.coordinator.process(case_text, coordination_context)
            
            print(f"Coordination complete:")
            print(f"   Primary: {analysis_result.primary_classification.category} - {analysis_result.primary_classification.subcategory}")
            print(f"   Secondary areas: {len(analysis_result.secondary_classifications)}")
            print(f"   Complexity: {analysis_result.complexity_level}")
            
            # Step 3: Generate summary
            print(f"Generating case summary...")
            summary_context = {"analysis_result": analysis_result}
            case_summary = self.summarizer.process(case_text, summary_context)
            analysis_result.case_summary = case_summary
            
            print(f"Summary generated: {len(case_summary)} characters")
            
            # Step 4: PII removal and quality assessment
            cleaned_text = self.pii_remover.clean_text(case_text)
            quality_assessment = self._assess_text_quality(case_text, cleaned_text)
            
            total_time = time.time() - start_time
            
            print(f"MULTI-AGENT ANALYSIS COMPLETE in {total_time:.2f}s")
            
            # Create result compatible with existing system
            enhanced_result = {
                "category": analysis_result.primary_classification.category,
                "subcategory": analysis_result.primary_classification.subcategory,
                "confidence": analysis_result.primary_classification.confidence.value,
                "reasoning": analysis_result.primary_classification.reasoning,
                "case_title": f"{analysis_result.primary_classification.subcategory} Case",
                "method": "multi_agent_cooperative_sync",
                "gibberish_detected": quality_assessment["gibberish_detected"],
                
                # Multi-agent specific data
                "secondary_issues": [
                    {
                        "category": sec.category,
                        "subcategory": sec.subcategory,
                        "confidence": sec.confidence.value,
                        "relevance_score": sec.relevance_score,
                        "urgency_score": sec.urgency_score,
                        "reasoning": sec.reasoning
                    }
                    for sec in analysis_result.secondary_classifications
                ],
                "case_complexity": analysis_result.complexity_level,
                "requires_multiple_attorneys": analysis_result.requires_multiple_attorneys,
                "confidence_consensus": analysis_result.confidence_consensus,
                "total_legal_areas": 1 + len(analysis_result.secondary_classifications),
                "case_summary": analysis_result.case_summary,
                
                # Agent performance data
                "agents_consulted": analysis_result.agents_consulted,
                "total_processing_time": total_time,
                "agent_performance": agent_performance,
                "text_quality": quality_assessment,
                
                "key_details": [
                    f"Primary: {analysis_result.primary_classification.subcategory}",
                    f"Additional areas: {len(analysis_result.secondary_classifications)}",
                    f"Complexity: {analysis_result.complexity_level}",
                    f"Consensus confidence: {analysis_result.confidence_consensus:.1f}",
                    f"Agents consulted: {len(analysis_result.agents_consulted)}"
                ]
            }
            
            # SAFE LOGGING - avoid encoding issues in logs
            self._log_multi_agent_analysis(case_text, enhanced_result, True, agent_performance)
            
            return {
                "status": "success",
                "method": "multi_agent_cooperative_sync",
                "timestamp": datetime.utcnow().isoformat(),
                "original_text": case_text,
                "cleaned_text": cleaned_text,
                "analysis": json.dumps(enhanced_result, ensure_ascii=False),  # Keep UTF-8 support but be safe
                "system_version": self.SYSTEM_VERSION,
                "prompt_version": self.PROMPT_VERSION,
                "processing_stats": {
                    "total_time": total_time,
                    "agents_deployed": len(self.specialist_agents),
                    "agents_responded": len(valid_classifications),
                    "coordination_time": analysis_result.total_processing_time
                }
            }
            
        except Exception as e:
            print(f"MULTI-AGENT SYSTEM ERROR: {str(e)}")
            
            error_response = {
                "status": "error",
                "method": "multi_agent_cooperative_sync",
                "timestamp": datetime.utcnow().isoformat(),
                "original_text": case_text,
                "error": str(e),
                "system_version": self.SYSTEM_VERSION,
                "prompt_version": self.PROMPT_VERSION
            }
            
            self._log_multi_agent_analysis(case_text, error_response, False, {})
            return error_response

    def _assess_text_quality(self, original: str, cleaned: str) -> Dict[str, Any]:
        """Assess text quality - same as working version"""
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
                'lawyer', 'attorney', 'court', 'lawsuit', 'doctor', 'hospital'
            ]
            
            has_legal_context = any(word in cleaned.lower() for word in legal_indicators)
            
            quality_acceptable = (
                reduction_pct < 50 and
                cleaned_words >= 5 and
                has_legal_context and
                len(cleaned.strip()) > 20
            )
            
            return {
                "original_words": original_words,
                "cleaned_words": cleaned_words,
                "reduction_percentage": reduction_pct,
                "has_legal_context": has_legal_context,
                "quality_acceptable": quality_acceptable,
                "gibberish_detected": not quality_acceptable
            }
        except Exception as e:
            print(f"Text quality assessment error: {e}")
            return {
                "original_words": 0,
                "cleaned_words": 0,
                "reduction_percentage": 100,
                "has_legal_context": False,
                "quality_acceptable": False,
                "gibberish_detected": True
            }

    def _log_multi_agent_analysis(self, case_text: str, response: Dict[str, Any], 
                                 success: bool, agent_performance: Dict[str, Any]) -> None:
        """ENCODING-SAFE logging"""
        try:
            # SAFE hash generation
            case_hash = "unknown"
            try:
                case_hash = hashlib.sha256(case_text.encode('utf-8', errors='replace')).hexdigest()
            except Exception:
                case_hash = "hash_failed"
            
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "system_version": self.SYSTEM_VERSION,
                "prompt_version": self.PROMPT_VERSION,
                "case_text_hash": case_hash,
                "case_length": len(case_text),
                "analysis_type": "multi_agent_cooperative_sync",
                "success": success,
                "total_agents": len(self.specialist_agents) + 2,
                "responding_agents": len([p for p in agent_performance.values() if p.get("status") == "success"])
            }
            
            # SAFE JSON logging - avoid encoding issues
            try:
                log_json = json.dumps(log_entry, ensure_ascii=False, indent=2)
                print(f"MULTI-AGENT LOG: {log_json}")
            except Exception as log_error:
                print(f"MULTI-AGENT LOG: Basic log only - JSON error: {log_error}")
                print(f"   Success: {success}")
                print(f"   Total agents: {log_entry['total_agents']}")
                print(f"   Responding agents: {log_entry['responding_agents']}")
                
        except Exception as e:
            print(f"Logging error (non-critical): {e}")

    # Legacy compatibility method - same as your working simple version
    def generate_final_summary(self, initial_analysis: Dict[str, Any], form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Legacy compatibility wrapper - same approach as working simple version"""
        try:
            if initial_analysis.get("status") == "error":
                return {
                    "status": "error",
                    "error": "Cannot generate summary - multi-agent analysis failed",
                    "timestamp": datetime.utcnow().isoformat(),
                    "system_version": self.SYSTEM_VERSION
                }
            
            # Parse analysis data
            analysis_data = json.loads(initial_analysis.get("analysis", "{}"))
            existing_summary = analysis_data.get("case_summary", "")
            
            if existing_summary:
                return {
                    "status": "success",
                    "timestamp": datetime.utcnow().isoformat(),
                    "summary": json.dumps({
                        "title": analysis_data.get("case_title", "Legal Case"),
                        "summary": {
                            "general_case_summary": existing_summary,
                            "key_aspects": analysis_data.get("key_details", []),
                            "potential_merits": [f"Strong {analysis_data.get('category')} case"],
                            "critical_factors": [f"Requires {analysis_data.get('case_complexity')} legal strategy"]
                        }
                    }, ensure_ascii=False),
                    "system_version": self.SYSTEM_VERSION
                }
            
            # Fallback summary
            return {
                "status": "success",
                "timestamp": datetime.utcnow().isoformat(),
                "summary": json.dumps({
                    "title": "Multi-Area Legal Case",
                    "summary": {
                        "general_case_summary": f"Complex case involving {analysis_data.get('category')} and potentially other legal areas.",
                        "key_aspects": analysis_data.get("key_details", []),
                        "potential_merits": ["Multi-faceted legal strategy required"],
                        "critical_factors": ["Coordination between multiple legal specialties"]
                    }
                }, ensure_ascii=False),
                "system_version": self.SYSTEM_VERSION
            }
            
        except Exception as e:
            print(f"Summary generation error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "system_version": self.SYSTEM_VERSION
            }

# FORM MATCHING HELPER FUNCTIONS (unchanged)
def create_subcategory_to_form_mapping():
    """Create mapping from subcategory names to form titles"""
    return {
        # Family Law
        "Adoptions": "Form for Adoptions",
        "Child Custody & Visitation": "Form for Child Custody & Visitation", 
        "Child Support": "Form for Child Support",
        "Divorce": "Form for Divorce",
        "Guardianship": "Form for Guardianship",
        "Paternity": "Form for Paternity",
        "Separations": "Form for Separations",
        "Spousal Support or Alimony": "Form for Spousal Support or Alimony",
        
        # Employment Law
        "Disabilities": "Form for Disabilities",
        "Employment Contracts": "Form for Employment Contracts",
        "Employment Discrimination": "Form for Employment Discrimination",
        "Pensions and Benefits": "Form for Pensions and Benefits", 
        "Sexual Harassment": "Form for Sexual Harassment",
        "Wages and Overtime Pay": "Form for Wages and Overtime Pay",
        "Workplace Disputes": "Form for Workplace Disputes",
        "Wrongful Termination": "Form for Wrongful Termination",
        
        # Criminal Law
        "General Criminal Defense": "Form for General Criminal Defense",
        "Environmental Violations": "Form for Environmental Violations",
        "Drug Crimes": "Form for Drug Crimes",
        "Drunk Driving/DUI/DWI": "Form for Drunk Driving/DUI/DWI",
        "Felonies": "Form for Felonies", 
        "Misdemeanors": "Form for Misdemeanors",
        "Speeding and Moving Violations": "Form for Speeding and Moving Violations",
        "White Collar Crime": "Form for White Collar Crime",
        "Tax Evasion": "Form for Tax Evasion",
        
        # Real Estate Law
        "Commercial Real Estate": "Form for Commercial Real Estate",
        "Condominiums and Cooperatives": "Form for Condominiums and Cooperatives",
        "Construction Disputes": "Form for Construction Disputes",
        "Foreclosures": "Form for Foreclosures",
        "Mortgages": "Form for Mortgages",
        "Purchase and Sale of Residence": "Form for Purchase and Sale of Residence",
        "Title and Boundary Disputes": "Form for Title and Boundary Disputes",
        
        # Business/Corporate Law  
        "Breach of Contract": "Form for Breach of Contract",
        "Corporate Tax": "Form for Corporate Tax",
        "Business Disputes": "Form for Business Disputes",
        "Buying and Selling a Business": "Form for Buying and Selling a Business",
        "Contract Drafting and Review": "Form for Contract Drafting and Review",
        "Corporations, LLCs, Partnerships, etc.": "Form for Corporations, LLCs, Partnerships, etc.",
        "Entertainment Law": "Form for Entertainment Law",
        
        # Immigration Law
        "Citizenship": "Form for Citizenship",
        "Deportation": "Form for Deportation", 
        "Permanent Visas or Green Cards": "Form for Permanent Visas or Green Cards",
        "Temporary Visas": "Form for Temporary Visas",
        
        # Personal Injury Law
        "Automobile Accidents": "Form for Automobile Accidents",
        "Dangerous Property or Buildings": "Form for Dangerous Property or Buildings",
        "Defective Products": "Form for Defective Products",
        "Medical Malpractice": "Form for Medical Malpractice", 
        "Personal Injury (General)": "Form for Personal Injury (General)",
        
        # Wills, Trusts, & Estates Law
        "Contested Wills or Probate": "Form for Contested Wills or Probate",
        "Drafting Wills and Trusts": "Form for Drafting Wills and Trusts",
        "Estate Administration": "Form for Estate Administration",
        "Estate Planning": "Form for Estate Planning",
        
        # Bankruptcy, Finances, & Tax Law
        "Collections": "Form for Collections",
        "Consumer Bankruptcy": "Form for Consumer Bankruptcy",
        "Consumer Credit": "Form for Consumer Credit", 
        "Income Tax": "Form for Income Tax",
        "Property Tax": "Form for Property Tax",
        
        # Government & Administrative Law
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
        
        # Product & Services Liability Law
        "Attorney Malpractice": "Form for Attorney Malpractice",
        "Defective Products": "Form for Defective Products", 
        "Warranties": "Form for Warranties",
        "Consumer Protection and Fraud": "Form for Consumer Protection and Fraud",
        
        # Intellectual Property Law
        "Copyright": "Form for Copyright",
        "Patents": "Form for Patents",
        "Trademarks": "Form for Trademarks",
        
        # Landlord/Tenant Law
        "General Landlord and Tenant Issues": "Form for General Landlord and Tenant Issues"
    }

def find_form_by_subcategory(subcategory, forms_data):
    """Find form using subcategory name"""
    mapping = create_subcategory_to_form_mapping()
    target_title = mapping.get(subcategory)
    
    if target_title:
        # Search for form with matching title
        for form_id, form_data in forms_data.items():
            if form_data.get("title") == target_title:
                return form_id, form_data
    
    return None, None

# FLASK INTEGRATION - Drop-in replacement for your existing analyzer
class MultiAgentLegalAnalyzer(SynchronousMultiAgentLegalAnalyzer):
    """Main class - encoding-safe multi-agent system for Flask integration"""
    pass

# Backward compatibility aliases
CaseAnalyzer = MultiAgentLegalAnalyzer
BulletproofCaseAnalyzer = MultiAgentLegalAnalyzer