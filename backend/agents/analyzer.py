"""
Analyzer Agent
Extracts numbers and computes financial metrics
"""
import re
from typing import Dict, List, Optional


class AnalyzerAgent:
    def __init__(self):
        """
        Initialize Analyzer Agent
        """
        pass
    
    def analyze(self, context: str, intent: str) -> Dict:
        """
        Analyze context and compute metrics
        Only activates for ratio_analysis or trend_analysis intents
        
        Args:
            context: Retrieved document context
            intent: Analysis intent from Planner
            
        Returns:
            Dictionary with computed metrics
        """
        if intent not in ["ratio_analysis", "trend_analysis"]:
            return {"computed_metrics": {}}
        
        # Extract numbers from context
        numbers = self._extract_numbers(context)
        
        # Compute metrics based on extracted data
        metrics = {}
        
        # Try to compute various financial ratios
        revenue = self._find_metric(context, ["revenue", "total revenue", "sales"])
        net_income = self._find_metric(context, ["net income", "net profit", "profit"])
        total_assets = self._find_metric(context, ["total assets", "assets"])
        total_liabilities = self._find_metric(context, ["total liabilities", "liabilities", "total debt"])
        total_equity = self._find_metric(context, ["total equity", "equity", "shareholders equity"])
        
        # Compute ratios
        if revenue and net_income:
            net_profit_margin = (net_income / revenue) * 100
            metrics["net_profit_margin_percent"] = round(net_profit_margin, 2)
        
        if total_liabilities and total_assets:
            debt_ratio = (total_liabilities / total_assets) * 100
            metrics["debt_ratio_percent"] = round(debt_ratio, 2)
        
        if total_equity and total_assets:
            equity_ratio = (total_equity / total_assets) * 100
            metrics["equity_ratio_percent"] = round(equity_ratio, 2)
        
        # Extract YoY growth if multiple years present
        yoy_growth = self._compute_yoy_growth(context)
        if yoy_growth:
            metrics["yoy_revenue_growth_percent"] = yoy_growth
        
        return {
            "computed_metrics": metrics,
            "extracted_values": {
                "revenue": revenue,
                "net_income": net_income,
                "total_assets": total_assets,
                "total_liabilities": total_liabilities,
                "total_equity": total_equity
            }
        }
    
    def _extract_numbers(self, text: str) -> List[float]:
        """
        Extract all numbers from text
        
        Args:
            text: Input text
            
        Returns:
            List of extracted numbers
        """
        # Pattern to match numbers with optional commas and decimals
        pattern = r'\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|billion|thousand|M|B|K)?'
        matches = re.findall(pattern, text, re.IGNORECASE)
        
        numbers = []
        for match in matches:
            try:
                # Remove commas
                num_str = match.replace(',', '')
                num = float(num_str)
                numbers.append(num)
            except:
                continue
        
        return numbers
    
    def _find_metric(self, text: str, keywords: List[str]) -> Optional[float]:
        """
        Find a specific metric value in text
        
        Args:
            text: Input text
            keywords: List of keyword variations to search for
            
        Returns:
            Extracted metric value or None
        """
        text_lower = text.lower()
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            # Find keyword position
            if keyword_lower in text_lower:
                idx = text_lower.find(keyword_lower)
                
                # Look for numbers near the keyword (within 100 chars)
                context_window = text[idx:idx+100]
                
                # Extract number with units
                pattern = r'\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(million|billion|thousand|M|B|K)?'
                match = re.search(pattern, context_window, re.IGNORECASE)
                
                if match:
                    num_str = match.group(1).replace(',', '')
                    num = float(num_str)
                    
                    # Apply multiplier if present
                    unit = match.group(2)
                    if unit:
                        unit_lower = unit.lower()
                        if unit_lower in ['million', 'm']:
                            num *= 1_000_000
                        elif unit_lower in ['billion', 'b']:
                            num *= 1_000_000_000
                        elif unit_lower in ['thousand', 'k']:
                            num *= 1_000
                    
                    return num
        
        return None
    
    def _compute_yoy_growth(self, text: str) -> Optional[float]:
        """
        Attempt to compute year-over-year growth
        
        Args:
            text: Input text
            
        Returns:
            YoY growth percentage or None
        """
        # Look for year patterns and associated revenue values
        year_pattern = r'(20\d{2})'
        years = re.findall(year_pattern, text)
        
        if len(years) >= 2:
            # This is simplified - would need more sophisticated logic
            # for production use
            pass
        
        return None


def analyze_context(context: str, intent: str) -> Dict:
    """
    Convenience function to analyze context
    
    Args:
        context: Retrieved document context
        intent: Analysis intent
        
    Returns:
        Analysis results with computed metrics
    """
    analyzer = AnalyzerAgent()
    return analyzer.analyze(context, intent)
