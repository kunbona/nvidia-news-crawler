"""
File export functionality for multiple formats
"""
import json
import csv
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger

try:
    import pandas as pd
except ImportError:
    pd = None


class FileExporter:
    """Export crawled data to various file formats"""
    
    def __init__(self, output_dir: str = "./output"):
        """
        Initialize file exporter
        
        Args:
            output_dir: Output directory path
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logger.bind(name="FileExporter")
    
    def _get_timestamp_filename(self, prefix: str, extension: str) -> str:
        """
        Generate timestamped filename
        
        Args:
            prefix: File prefix
            extension: File extension
            
        Returns:
            Timestamped filename
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}.{extension}"
    
    def export_json(self, data: List[Dict[str, Any]], filename: Optional[str] = None) -> bool:
        """
        Export data to JSON format
        
        Args:
            data: List of data dictionaries
            filename: Output filename (auto-generated if None)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if filename is None:
                filename = self._get_timestamp_filename("articles", "json")
            
            filepath = self.output_dir / filename
            
            serializable_data = []
            for item in data:
                serializable_item = {}
                for key, value in item.items():
                    if isinstance(value, datetime):
                        serializable_item[key] = value.isoformat()
                    else:
                        serializable_item[key] = value
                serializable_data.append(serializable_item)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(serializable_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Exported {len(data)} items to JSON: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting to JSON: {str(e)}")
            return False
    
    def export_csv(self, data: List[Dict[str, Any]], filename: Optional[str] = None) -> bool:
        """
        Export data to CSV format
        
        Args:
            data: List of data dictionaries
            filename: Output filename (auto-generated if None)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not data:
                self.logger.warning("No data to export")
                return False
            
            if filename is None:
                filename = self._get_timestamp_filename("articles", "csv")
            
            filepath = self.output_dir / filename
            
            fieldnames = set()
            for item in data:
                fieldnames.update(item.keys())
            fieldnames = sorted(list(fieldnames))
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for item in data:
                    row = {}
                    for key, value in item.items():
                        if isinstance(value, (list, dict)):
                            row[key] = json.dumps(value, ensure_ascii=False)
                        elif isinstance(value, datetime):
                            row[key] = value.isoformat()
                        else:
                            row[key] = value
                    writer.writerow(row)
            
            self.logger.info(f"Exported {len(data)} items to CSV: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting to CSV: {str(e)}")
            return False
    
    def export_excel(self, data: List[Dict[str, Any]], filename: Optional[str] = None) -> bool:
        """
        Export data to Excel format
        
        Args:
            data: List of data dictionaries
            filename: Output filename (auto-generated if None)
            
        Returns:
            True if successful, False otherwise
        """
        if pd is None:
            self.logger.error("pandas not installed. Install with: pip install pandas openpyxl")
            return False
        
        try:
            if not data:
                self.logger.warning("No data to export")
                return False
            
            if filename is None:
                filename = self._get_timestamp_filename("articles", "xlsx")
            
            filepath = self.output_dir / filename
            
            df_data = []
            for item in data:
                row = {}
                for key, value in item.items():
                    if isinstance(value, (list, dict)):
                        row[key] = json.dumps(value, ensure_ascii=False)
                    elif isinstance(value, datetime):
                        row[key] = value.isoformat()
                    else:
                        row[key] = value
                df_data.append(row)
            
            df = pd.DataFrame(df_data)
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Articles')
                
                worksheet = writer.sheets['Articles']
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            self.logger.info(f"Exported {len(data)} items to Excel: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting to Excel: {str(e)}")
            return False
    
    def export_markdown(self, data: List[Dict[str, Any]], filename: Optional[str] = None) -> bool:
        """
        Export data to Markdown format
        
        Args:
            data: List of data dictionaries
            filename: Output filename (auto-generated if None)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not data:
                self.logger.warning("No data to export")
                return False
            
            if filename is None:
                filename = self._get_timestamp_filename("articles", "md")
            
            filepath = self.output_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("# NVIDIA News and Information\n\n")
                f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"Total Items: {len(data)}\n\n")
                f.write("---\n\n")
                
                for idx, item in enumerate(data, 1):
                    f.write(f"## {idx}. {item.get('title', 'Untitled')}\n\n")
                    
                    if 'source' in item:
                        f.write(f"**Source:** {item['source']}\n\n")
                    
                    if 'url' in item:
                        f.write(f"**URL:** [{item['url']}]({item['url']})\n\n")
                    
                    if 'author' in item and item['author']:
                        f.write(f"**Author:** {item['author']}\n\n")
                    
                    if 'publish_date' in item:
                        pub_date = item['publish_date']
                        if isinstance(pub_date, datetime):
                            pub_date = pub_date.strftime('%Y-%m-%d %H:%M:%S')
                        f.write(f"**Published:** {pub_date}\n\n")
                    
                    if 'tags' in item and item['tags']:
                        tags_str = ', '.join([f"`{tag}`" for tag in item['tags']])
                        f.write(f"**Tags:** {tags_str}\n\n")
                    
                    if 'summary' in item and item['summary']:
                        f.write(f"**Summary:**\n\n{item['summary']}\n\n")
                    
                    if 'content' in item and item['content']:
                        content = item['content']
                        if len(content) > 500:
                            content = content[:500] + "...\n\n[Content truncated]"
                        f.write(f"**Content:**\n\n{content}\n\n")
                    
                    if 'metrics' in item and item['metrics']:
                        metrics = item['metrics']
                        f.write(f"**Metrics:** ")
                        metrics_list = [f"{k}: {v}" for k, v in metrics.items()]
                        f.write(', '.join(metrics_list) + "\n\n")
                    
                    f.write("---\n\n")
            
            self.logger.info(f"Exported {len(data)} items to Markdown: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting to Markdown: {str(e)}")
            return False
    
    def export_by_source(self, data: List[Dict[str, Any]], format: str = "json") -> bool:
        """
        Export data grouped by source
        
        Args:
            data: List of data dictionaries
            format: Export format (json, csv, excel, markdown)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            by_source = {}
            for item in data:
                source = item.get('source', 'unknown')
                if source not in by_source:
                    by_source[source] = []
                by_source[source].append(item)
            
            for source, items in by_source.items():
                filename = f"{source}_{self._get_timestamp_filename('data', format)}"
                
                if format == "json":
                    self.export_json(items, filename)
                elif format == "csv":
                    self.export_csv(items, filename)
                elif format == "excel":
                    self.export_excel(items, filename)
                elif format == "markdown":
                    self.export_markdown(items, filename)
                else:
                    self.logger.error(f"Unsupported format: {format}")
                    return False
            
            self.logger.info(f"Exported data by source in {format} format")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting by source: {str(e)}")
            return False
    
    def export_all_formats(self, data: List[Dict[str, Any]]) -> bool:
        """
        Export data to all supported formats
        
        Args:
            data: List of data dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            formats = [
                ("json", f"articles_{timestamp}.json"),
                ("csv", f"articles_{timestamp}.csv"),
                ("markdown", f"articles_{timestamp}.md"),
            ]
            
            for format_type, filename in formats:
                if format_type == "json":
                    self.export_json(data, filename)
                elif format_type == "csv":
                    self.export_csv(data, filename)
                elif format_type == "markdown":
                    self.export_markdown(data, filename)
            
            if pd is not None:
                self.export_excel(data, f"articles_{timestamp}.xlsx")
            
            self.logger.info("Exported data to all available formats")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting to all formats: {str(e)}")
            return False
    
    def list_exports(self) -> List[str]:
        """
        List all exported files
        
        Returns:
            List of file paths
        """
        files = list(self.output_dir.glob("*"))
        return [str(f) for f in sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)]
