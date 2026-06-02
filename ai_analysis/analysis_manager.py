"""
AI Analysis Manager - Orchestrate AI-based interpretation
"""
from typing import Dict, Any, Optional, List
from loguru import logger
from datetime import datetime

from analysis.structured_extractor import StructuredExtractor
from analysis.narrative_interpreter import NarrativeInterpreter
from ai_analysis.base_ai_interpreter import BaseAIInterpreter
from ai_analysis.openai_interpreter import OpenAIInterpreter
from ai_analysis.claude_interpreter import ClaudeInterpreter
from ai_analysis.deepseek_interpreter import DeepSeekInterpreter
from ai_analysis.local_llm_interpreter import LocalLLMInterpreter


class AIAnalysisManager:
    """
    Manage AI-based analysis and interpretation
    """
    
    def __init__(self, ai_provider: str = "deepseek", **kwargs):
        """
        Initialize AI Analysis Manager
        
        Args:
            ai_provider: AI provider (openai, claude, deepseek, local)
            **kwargs: Provider-specific arguments
        """
        self.logger = logger.bind(name="AIAnalysisManager")
        self.ai_provider = ai_provider
        
        # Initialize interpreters
        self.structured_extractor = StructuredExtractor()
        self.narrative_interpreter = NarrativeInterpreter()
        self.ai_interpreter = self._initialize_ai_interpreter(ai_provider, kwargs)
        
        self.logger.info(f"AI Analysis Manager initialized with provider: {ai_provider}")
    
    def _initialize_ai_interpreter(self, provider: str, kwargs: Dict) -> Optional[BaseAIInterpreter]:
        """
        Initialize AI interpreter
        
        Args:
            provider: Provider name
            kwargs: Provider-specific arguments
            
        Returns:
            AI interpreter instance
        """
        try:
            if provider == "openai":
                return OpenAIInterpreter(
                    api_key=kwargs.get("api_key"),
                    model=kwargs.get("model", "gpt-4")
                )
            elif provider == "claude":
                return ClaudeInterpreter(api_key=kwargs.get("api_key"))
            elif provider == "deepseek":
                return DeepSeekInterpreter(
                    api_key=kwargs.get("api_key"),
                    base_url=kwargs.get("base_url", "https://api.deepseek.com")
                )
            elif provider == "local":
                return LocalLLMInterpreter(
                    base_url=kwargs.get("base_url", "http://localhost:11434"),
                    model=kwargs.get("model", "llama2-chinese")
                )
            else:
                self.logger.warning(f"Unknown AI provider: {provider}")
                return None
        except Exception as e:
            self.logger.error(f"Error initializing AI interpreter: {str(e)}")
            return None
    
    def analyze_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete analysis pipeline for an article
        他说 X → 说明 Y → 对应 Z（赛道 / 标的），AI 秒出产业解读
        
        Args:
            article: Article dictionary
            
        Returns:
            Complete analysis result
        """
        self.logger.info(f"Starting analysis for: {article.get('title', '')[:50]}")
        
        analysis_result = {
            "article": {
                "title": article.get("title"),
                "source": article.get("source"),
                "url": article.get("url"),
                "publish_date": article.get("publish_date"),
            },
            "analysis_timestamp": datetime.now().isoformat(),
            "ai_provider": self.ai_provider,
            "pipeline": {},
        }
        
        try:
            # Step 1: Structured Extraction
            self.logger.info("Step 1: Structured Extraction")
            extraction = self.structured_extractor.extract_all(article)
            analysis_result["pipeline"]["extraction"] = extraction
            
            # Step 2: Traditional Interpretation
            self.logger.info("Step 2: Traditional Interpretation")
            interpretation = self.narrative_interpreter.interpret(extraction)
            analysis_result["pipeline"]["traditional_interpretation"] = interpretation
            
            # Step 3: AI-based Three-part Interpretation
            if self.ai_interpreter:
                self.logger.info("Step 3: AI Three-part Interpretation")
                ai_interpretation = self.ai_interpreter.interpret_three_part(extraction)
                analysis_result["pipeline"]["ai_three_part"] = ai_interpretation
                
                # Step 4: AI Industry Insights
                self.logger.info("Step 4: AI Industry Insights")
                industries = [ind.get("industry") for ind in interpretation.get("three_part_framework", {}).get("part_3_mapping", {}).get("relevant_industries", [])]
                
                industry_insights = {}
                for industry in industries:
                    insight = self.ai_interpreter.generate_industry_insight(ai_interpretation, industry)
                    industry_insights[industry] = insight
                
                analysis_result["pipeline"]["ai_industry_insights"] = industry_insights
                
                # Step 5: AI Investment Thesis
                self.logger.info("Step 5: AI Investment Thesis")
                thesis = self.ai_interpreter.generate_investment_thesis(extraction, ai_interpretation)
                analysis_result["pipeline"]["ai_investment_thesis"] = thesis
                
                # Step 6: Deep Research (if DeepSeek)
                if self.ai_provider == "deepseek" and isinstance(self.ai_interpreter, DeepSeekInterpreter):
                    self.logger.info("Step 6: DeepSeek Deep Research")
                    topic = f"关于{article.get('title', '')}的深度研究分析"
                    deep_research = self.ai_interpreter.deep_research(topic, context=extraction)
                    analysis_result["pipeline"]["deep_research"] = deep_research
            else:
                self.logger.warning("AI interpreter not available, skipping AI-based steps")
            
            analysis_result["status"] = "success"
            self.logger.info("Analysis completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error during analysis: {str(e)}")
            analysis_result["status"] = "error"
            analysis_result["error"] = str(e)
        
        return analysis_result
    
    def batch_analyze(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze multiple articles
        
        Args:
            articles: List of articles
            
        Returns:
            List of analysis results
        """
        results = []
        for i, article in enumerate(articles, 1):
            self.logger.info(f"Processing article {i}/{len(articles)}")
            result = self.analyze_article(article)
            results.append(result)
        
        return results
    
    def generate_summary_report(self, analysis_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary report from multiple analyses
        
        Args:
            analysis_results: List of analysis results
            
        Returns:
            Summary report
        """
        report = {
            "total_articles": len(analysis_results),
            "successful": 0,
            "failed": 0,
            "ai_provider": self.ai_provider,
            "key_themes": [],
            "top_companies": [],
            "top_industries": [],
            "investment_signals": [],
        }
        
        company_mentions = {}
        industry_mentions = {}
        
        for result in analysis_results:
            if result.get("status") == "success":
                report["successful"] += 1
                
                # Collect company mentions
                companies = result.get("pipeline", {}).get("extraction", {}).get("companies", [])
                for company in companies:
                    ticker = company.get("ticker")
                    mentions = company.get("mentions", 1)
                    company_mentions[ticker] = company_mentions.get(ticker, 0) + mentions
                
                # Collect industry data
                industries = result.get("pipeline", {}).get("traditional_interpretation", {}).get("three_part_framework", {}).get("part_3_mapping", {}).get("relevant_industries", [])
                for industry in industries:
                    ind_name = industry.get("industry")
                    industry_mentions[ind_name] = industry_mentions.get(ind_name, 0) + 1
            else:
                report["failed"] += 1
        
        # Rank top companies and industries
        report["top_companies"] = sorted(
            [(k, v) for k, v in company_mentions.items()],
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        report["top_industries"] = sorted(
            [(k, v) for k, v in industry_mentions.items()],
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return report
    
    def switch_provider(self, new_provider: str, **kwargs):
        """
        Switch to a different AI provider
        
        Args:
            new_provider: New provider name (openai, claude, deepseek, local)
            **kwargs: Provider-specific arguments
        """
        self.logger.info(f"Switching AI provider from {self.ai_provider} to {new_provider}")
        self.ai_provider = new_provider
        self.ai_interpreter = self._initialize_ai_interpreter(new_provider, kwargs)
