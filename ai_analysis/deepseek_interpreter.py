"""
DeepSeek API interpreter
"""
import os
from typing import Dict, Any, Optional
import json
from loguru import logger

from .base_ai_interpreter import BaseAIInterpreter


class DeepSeekInterpreter(BaseAIInterpreter):
    """
    DeepSeek API interpreter (Deep Research)
    """
    
    # Core prompts templates
    THREE_PART_PROMPT = """
你是一位资深投资分析师。请根据以下信息，使用"三段式"分析框架进行产业解读：

【信息】
- 新闻标题: {title}
- 核心论点: {core_arguments}
- 提及公司: {companies}
- 提及产品: {products}
- 市场情感: {sentiment}

【分析框架 - 必须三段式】

【第一段】他说 X - 梳理核心观点
- 这条信息的核心主张是什么？
- 涉及哪些关键技术或市场趋势？
- 信息的强度和可信度如何？

【第二段】说明 Y - 解释市场意义
- 为什么这条信息重要？
- 它对产业链的哪些环节有影响？
- 这反映了什么样的市场动态？

【第三段】对应 Z - 映射投资标的
- 这条信息指向哪个赛道？
- 哪些公司会直接受益？
- 哪些公司可能面临风险？
- 产业链上下游的机会在哪里？

请用JSON格式返回，包含以下字段：
{{
  "part_1_what_said": {{
    "core_claim": "核心主张",
    "key_technologies": ["技术1", "技术2"],
    "trend": "市场趋势",
    "intensity": "信息强度(高/中/低)"
  }},
  "part_2_explanation": {{
    "significance": "为什么重要",
    "affected_segments": ["产业链环节1", "环节2"],
    "market_dynamics": "市场动态解析"
  }},
  "part_3_mapping": {{
    "track": "赛道名称",
    "direct_beneficiaries": [
      {{
        "company": "公司名",
        "ticker": "股票代码",
        "reason": "受益原因",
        "confidence": "确定度(高/中/低)",
        "upside": "潜在上升空间%"
      }}
    ],
    "at_risk": [
      {{
        "company": "公司名",
        "ticker": "股票代码",
        "reason": "风险原因",
        "confidence": "确定度",
        "downside": "潜在下降空间%"
      }}
    ],
    "supply_chain_opportunities": [
      {{
        "segment": "产业链环节",
        "opportunity": "具体机会",
        "key_players": ["公司1", "公司2"]
      }}
    ]
  }},
  "confidence_score": 0.85,
  "key_risks": ["风险1", "风险2"],
  "next_catalysts": ["下一步触发因素1", "因素2"]
}}
"""
    
    INDUSTRY_INSIGHT_PROMPT = """
你是行业分析专家。为{industry}赛道生成深度产业解读：

【解读要求】
1. 行业现状与趋势 - 当前阶段、发展方向
2. 竞争格局分析 - 主要玩家、市场份额、竞争优势
3. 技术迭代方向 - 关键技术突破、研发投入
4. 政策影响评估 - 相关政策、监管风险
5. 投资机会评估 - 具体投资标的、估值机会

返回JSON格式，包含详细分析结果。
"""
    
    INVESTMENT_THESIS_PROMPT = """
你是投资策略师。基于以下分析结果，生成投资论文(Investment Thesis)：

【信息摘要】
{summary}

【分析结果】
{analysis}

【投资论文要求】
1. 投资假设（What）- 要表述清楚地我们认为会发生什么
2. 为什么（Why）- 3个关键理由，每个理由必须有证据支持
3. 如何验证（How）- 关键指标、验证路径
4. 时间框架（When）- 预期实现周期
5. 风险因素（Risk）- 关键风险及应对方案

返回JSON格式的完整投资论文。
"""
    
    DEEP_RESEARCH_PROMPT = """
进行深度研究分析（Deep Research）：

【研究主题】
{topic}

【深度研究要求】
1. 详尽的背景分析
2. 多个维度的问题拆解
3. 历史数据和趋势分析
4. 竞争对手对标分析
5. 未来预测和建议

请提供深度、多角度的分析报告。
"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.deepseek.com"):
        """
        Initialize DeepSeek interpreter
        
        Args:
            api_key: DeepSeek API key
            base_url: DeepSeek API base URL
        """
        super().__init__("DeepSeek", api_key)
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.base_url = base_url
        
        if not self.api_key:
            self.logger.warning("DeepSeek API key not provided")
            return
        
        try:
            from openai import OpenAI
            # DeepSeek API is OpenAI-compatible
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=base_url
            )
            self.logger.info("DeepSeek client initialized")
        except ImportError:
            self.logger.error("openai package not installed. Install with: pip install openai")
            self.client = None
    
    def interpret_three_part(self, extraction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate three-part interpretation using DeepSeek
        
        Args:
            extraction: Structured extraction result
            
        Returns:
            Three-part interpretation
        """
        if not self.client:
            self.logger.error("DeepSeek client not initialized")
            return {"error": "Client not initialized"}
        
        try:
            # Prepare prompt
            prompt = self.THREE_PART_PROMPT.format(
                title=extraction.get("title", ""),
                core_arguments=json.dumps(extraction.get("core_arguments", []), ensure_ascii=False),
                companies=json.dumps(extraction.get("companies", []), ensure_ascii=False),
                products=json.dumps(extraction.get("products", []), ensure_ascii=False),
                sentiment=json.dumps(extraction.get("sentiment", {}), ensure_ascii=False),
            )
            
            # Call DeepSeek API
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "system",
                        "content": "你是一位资深投资分析师，擅长产业链分析和投资解读。请用中文回答。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000,
            )
            
            # Parse response
            response_text = response.choices[0].message.content
            
            # Extract JSON from response
            result = self._extract_json(response_text)
            
            self.logger.info(f"Three-part interpretation completed")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in three-part interpretation: {str(e)}")
            return {"error": str(e)}
    
    def generate_industry_insight(self, interpretation: Dict[str, Any], industry: str) -> Dict[str, Any]:
        """
        Generate industry insights using DeepSeek
        
        Args:
            interpretation: Interpretation result
            industry: Industry name
            
        Returns:
            Industry insight
        """
        if not self.client:
            return {"error": "Client not initialized"}
        
        try:
            prompt = self.INDUSTRY_INSIGHT_PROMPT.format(industry=industry)
            
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "system",
                        "content": "你是行业分析专家，提供深度产业解读。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000,
            )
            
            response_text = response.choices[0].message.content
            result = self._extract_json(response_text)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in industry insight: {str(e)}")
            return {"error": str(e)}
    
    def generate_investment_thesis(self, extraction: Dict[str, Any], interpretation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate investment thesis using DeepSeek
        
        Args:
            extraction: Extraction result
            interpretation: Interpretation result
            
        Returns:
            Investment thesis
        """
        if not self.client:
            return {"error": "Client not initialized"}
        
        try:
            summary = f"{extraction.get('title', '')} - {extraction.get('summary', '')}"
            analysis = json.dumps(interpretation, ensure_ascii=False)
            
            prompt = self.INVESTMENT_THESIS_PROMPT.format(
                summary=summary,
                analysis=analysis
            )
            
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "system",
                        "content": "你是投资策略师，擅长撰写投资论文。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000,
            )
            
            response_text = response.choices[0].message.content
            result = self._extract_json(response_text)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in investment thesis: {str(e)}")
            return {"error": str(e)}
    
    def deep_research(
        self,
        topic: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform deep research on a topic using DeepSeek
        DeepSeek 特有的深度研究功能
        
        Args:
            topic: Research topic
            context: Additional context
            
        Returns:
            Deep research result
        """
        if not self.client:
            return {"error": "Client not initialized"}
        
        try:
            prompt = self.DEEP_RESEARCH_PROMPT.format(topic=topic)
            
            if context:
                prompt += f"\n\n【背景信息】\n{json.dumps(context, ensure_ascii=False)}"
            
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "system",
                        "content": "你是深度研究专家，提供全面、深入的分析报告。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=3000,
            )
            
            response_text = response.choices[0].message.content
            
            return {
                "topic": topic,
                "research": response_text,
                "model": "deepseek-chat"
            }
            
        except Exception as e:
            self.logger.error(f"Error in deep research: {str(e)}")
            return {"error": str(e)}
    
    def _extract_json(self, text: str) -> Dict[str, Any]:
        """
        Extract JSON from response text
        
        Args:
            text: Response text
            
        Returns:
            Extracted JSON
        """
        try:
            # Try to find JSON in response
            start = text.find('{')
            end = text.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_str = text[start:end]
                return json.loads(json_str)
            else:
                # If no JSON found, return text as-is
                return {"raw_response": text}
        except json.JSONDecodeError:
            return {"raw_response": text}
