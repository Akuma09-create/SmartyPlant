"""
Report generation service for plant analysis reports.
Generates PDF and image reports with analysis results.
"""

import io
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image as RLImage,
    Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from PIL import Image, ImageDraw, ImageFont

from services.translation_service import t, get_text


# ============================================================================
# Report Configuration
# ============================================================================

SEVERITY_COLORS = {
    'mild': (76, 175, 80),      # Green
    'moderate': (255, 152, 0),   # Orange
    'severe': (244, 67, 54),     # Red
    'healthy': (76, 175, 80)     # Green
}

HEALTH_SCORE_COLORS = {
    'excellent': (76, 175, 80),  # >= 80
    'good': (139, 195, 74),      # >= 60
    'fair': (255, 193, 7),       # >= 40
    'poor': (255, 152, 0),       # >= 20
    'critical': (244, 67, 54)    # < 20
}


def get_health_color(score: float) -> Tuple[int, int, int]:
    """Get color based on health score."""
    if score >= 80:
        return HEALTH_SCORE_COLORS['excellent']
    elif score >= 60:
        return HEALTH_SCORE_COLORS['good']
    elif score >= 40:
        return HEALTH_SCORE_COLORS['fair']
    elif score >= 20:
        return HEALTH_SCORE_COLORS['poor']
    else:
        return HEALTH_SCORE_COLORS['critical']


# ============================================================================
# PDF Report Generation
# ============================================================================

class PlantAnalysisPDFReport:
    """Generate PDF reports for plant analysis."""
    
    def __init__(self, analysis_data: Dict, language: str = 'en'):
        self.analysis = analysis_data
        self.lang = language
        self.styles = getSampleStyleSheet()
        self._setup_styles()
    
    def _setup_styles(self):
        """Setup custom styles for the report."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2E7D32')
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceBefore=15,
            spaceAfter=10,
            textColor=colors.HexColor('#1565C0'),
            borderPadding=5
        ))
        
        # Normal text style
        self.styles.add(ParagraphStyle(
            name='ReportBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            leading=14
        ))
        
        # Highlight style for important info
        self.styles.add(ParagraphStyle(
            name='Highlight',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#D32F2F'),
            fontName='Helvetica-Bold'
        ))
    
    def _t(self, key: str) -> str:
        """Get translated text."""
        return get_text(key, self.lang)
    
    def generate(self, output_path: str = None) -> bytes:
        """
        Generate PDF report.
        
        Args:
            output_path: Optional file path to save PDF
        
        Returns:
            PDF content as bytes
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50
        )
        
        story = []
        
        # Title
        story.append(Paragraph(
            self._t('plant_analysis'),
            self.styles['ReportTitle']
        ))
        story.append(Spacer(1, 10))
        
        # Date
        date_str = datetime.now().strftime('%Y-%m-%d %H:%M')
        story.append(Paragraph(
            f"<i>{date_str}</i>",
            ParagraphStyle('DateStyle', parent=self.styles['Normal'], alignment=TA_CENTER)
        ))
        story.append(Spacer(1, 20))
        
        # Horizontal line
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#E0E0E0')))
        story.append(Spacer(1, 15))
        
        # Health Score Section
        health_score = self.analysis.get('health_score', 
                                         self.analysis.get('confidence_score', 50))
        story.append(Paragraph(
            f"<b>{self._t('health_score')}:</b> {health_score:.0f}%",
            self.styles['SectionHeader']
        ))
        
        # Disease Info Table
        disease_data = [
            [self._t('plant_type'), self.analysis.get('plant_type', 'Unknown')],
            [self._t('disease_detected'), self.analysis.get('disease_detected', self._t('no_disease'))],
            [self._t('severity'), self._t(self.analysis.get('severity_level', 'mild'))],
            [self._t('confidence'), f"{self.analysis.get('confidence_score', 0):.1f}%"]
        ]
        
        disease_table = Table(disease_data, colWidths=[2*inch, 4*inch])
        disease_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F5F5F5')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E0E0E0'))
        ]))
        story.append(disease_table)
        story.append(Spacer(1, 20))
        
        # Analysis Details
        details = self.analysis.get('analysis_details', {})
        if isinstance(details, str):
            try:
                details = json.loads(details)
            except:
                details = {'description': details}
        
        if details:
            story.append(Paragraph(
                f"<b>{self._t('recommendations')}:</b>",
                self.styles['SectionHeader']
            ))
            
            if isinstance(details, dict):
                for key, value in details.items():
                    if value and key not in ['id', 'created_at', 'updated_at']:
                        if isinstance(value, list):
                            value = ', '.join(str(v) for v in value)
                        story.append(Paragraph(
                            f"<b>{key.replace('_', ' ').title()}:</b> {value}",
                            self.styles['ReportBody']
                        ))
            else:
                story.append(Paragraph(str(details), self.styles['ReportBody']))
            
            story.append(Spacer(1, 15))
        
        # Care Plan / Recommended Actions
        actions = self.analysis.get('recommended_actions', [])
        if isinstance(actions, str):
            try:
                actions = json.loads(actions)
            except:
                actions = [actions] if actions else []
        
        if actions:
            story.append(Paragraph(
                f"<b>{self._t('care_plan')}:</b>",
                self.styles['SectionHeader']
            ))
            
            if isinstance(actions, list):
                for i, action in enumerate(actions, 1):
                    story.append(Paragraph(
                        f"{i}. {action}",
                        self.styles['ReportBody']
                    ))
            elif isinstance(actions, dict):
                for key, value in actions.items():
                    if value:
                        story.append(Paragraph(
                            f"<b>{key.replace('_', ' ').title()}:</b> {value}",
                            self.styles['ReportBody']
                        ))
        
        story.append(Spacer(1, 30))
        
        # Footer
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#E0E0E0')))
        story.append(Spacer(1, 10))
        story.append(Paragraph(
            f"<i>{self._t('app_name')} - {date_str}</i>",
            ParagraphStyle('FooterStyle', parent=self.styles['Normal'], 
                          alignment=TA_CENTER, fontSize=9, textColor=colors.grey)
        ))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF content
        pdf_content = buffer.getvalue()
        buffer.close()
        
        # Save to file if path provided
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(pdf_content)
        
        return pdf_content


# ============================================================================
# Image Report Generation
# ============================================================================

class PlantAnalysisImageReport:
    """Generate image reports for plant analysis."""
    
    def __init__(self, analysis_data: Dict, language: str = 'en'):
        self.analysis = analysis_data
        self.lang = language
        self.width = 800
        self.height = 1000
        self.padding = 40
        self.bg_color = (255, 255, 255)
        self.text_color = (33, 33, 33)
        self.accent_color = (46, 125, 50)
    
    def _t(self, key: str) -> str:
        """Get translated text."""
        return get_text(key, self.lang)
    
    def _get_font(self, size: int = 16, bold: bool = False) -> ImageFont:
        """Get font for text rendering."""
        try:
            # Try to use a system font
            if bold:
                return ImageFont.truetype("arialbd.ttf", size)
            return ImageFont.truetype("arial.ttf", size)
        except:
            try:
                # Fallback to default
                return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
            except:
                return ImageFont.load_default()
    
    def _draw_health_gauge(self, draw: ImageDraw, x: int, y: int, score: float, size: int = 120):
        """Draw a circular health gauge."""
        color = get_health_color(score)
        
        # Background circle
        draw.ellipse(
            [x, y, x + size, y + size],
            outline=(220, 220, 220),
            width=8
        )
        
        # Score arc (simplified as a filled portion)
        # For simplicity, we just draw the score text in the center
        
        # Score text
        font = self._get_font(28, bold=True)
        score_text = f"{score:.0f}%"
        bbox = draw.textbbox((0, 0), score_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        draw.text(
            (x + size // 2 - text_width // 2, y + size // 2 - text_height // 2 - 5),
            score_text,
            fill=color,
            font=font
        )
        
        # Label
        label_font = self._get_font(12)
        label = self._t('health_score')
        bbox = draw.textbbox((0, 0), label, font=label_font)
        label_width = bbox[2] - bbox[0]
        
        draw.text(
            (x + size // 2 - label_width // 2, y + size + 10),
            label,
            fill=self.text_color,
            font=label_font
        )
    
    def generate(self, output_path: str = None) -> bytes:
        """
        Generate image report.
        
        Args:
            output_path: Optional file path to save image
        
        Returns:
            PNG image content as bytes
        """
        # Create image
        img = Image.new('RGB', (self.width, self.height), self.bg_color)
        draw = ImageDraw.Draw(img)
        
        y_pos = self.padding
        
        # Title
        title_font = self._get_font(28, bold=True)
        title = self._t('plant_analysis')
        draw.text((self.padding, y_pos), title, fill=self.accent_color, font=title_font)
        y_pos += 50
        
        # Date
        date_font = self._get_font(12)
        date_str = datetime.now().strftime('%Y-%m-%d %H:%M')
        draw.text((self.padding, y_pos), date_str, fill=(128, 128, 128), font=date_font)
        y_pos += 30
        
        # Horizontal line
        draw.line([(self.padding, y_pos), (self.width - self.padding, y_pos)], 
                  fill=(220, 220, 220), width=2)
        y_pos += 30
        
        # Health Score Gauge
        health_score = self.analysis.get('health_score', 
                                         self.analysis.get('confidence_score', 50))
        self._draw_health_gauge(draw, self.width // 2 - 60, y_pos, health_score)
        y_pos += 180
        
        # Disease Information
        section_font = self._get_font(16, bold=True)
        label_font = self._get_font(14, bold=True)
        value_font = self._get_font(14)
        
        info_items = [
            (self._t('plant_type'), self.analysis.get('plant_type', 'Unknown')),
            (self._t('disease_detected'), self.analysis.get('disease_detected', self._t('no_disease'))),
            (self._t('severity'), self._t(self.analysis.get('severity_level', 'mild'))),
            (self._t('confidence'), f"{self.analysis.get('confidence_score', 0):.1f}%")
        ]
        
        for label, value in info_items:
            draw.text((self.padding, y_pos), f"{label}:", fill=self.text_color, font=label_font)
            draw.text((self.padding + 200, y_pos), str(value), fill=(66, 66, 66), font=value_font)
            y_pos += 35
        
        y_pos += 20
        
        # Recommendations
        draw.line([(self.padding, y_pos), (self.width - self.padding, y_pos)], 
                  fill=(220, 220, 220), width=1)
        y_pos += 20
        
        draw.text((self.padding, y_pos), self._t('recommendations') + ":", 
                  fill=self.accent_color, font=section_font)
        y_pos += 35
        
        actions = self.analysis.get('recommended_actions', [])
        if isinstance(actions, str):
            try:
                actions = json.loads(actions)
            except:
                actions = [actions] if actions else []
        
        if isinstance(actions, list):
            for i, action in enumerate(actions[:5], 1):  # Limit to 5 items
                action_text = f"{i}. {action}"
                # Word wrap for long text
                if len(action_text) > 60:
                    action_text = action_text[:57] + "..."
                draw.text((self.padding + 10, y_pos), action_text, 
                          fill=self.text_color, font=value_font)
                y_pos += 30
        
        # Footer
        y_pos = self.height - 60
        draw.line([(self.padding, y_pos), (self.width - self.padding, y_pos)], 
                  fill=(220, 220, 220), width=1)
        y_pos += 15
        
        footer_font = self._get_font(10)
        footer_text = f"{self._t('app_name')} - {date_str}"
        draw.text((self.padding, y_pos), footer_text, fill=(128, 128, 128), font=footer_font)
        
        # Convert to bytes
        buffer = io.BytesIO()
        img.save(buffer, format='PNG', quality=95)
        img_content = buffer.getvalue()
        buffer.close()
        
        # Save to file if path provided
        if output_path:
            img.save(output_path, 'PNG', quality=95)
        
        return img_content


# ============================================================================
# Report Service
# ============================================================================

class ReportService:
    """Main service for generating reports."""
    
    def __init__(self, reports_folder: str = None):
        self.reports_folder = reports_folder or str(Path(__file__).parent.parent.parent / 'reports')
        Path(self.reports_folder).mkdir(parents=True, exist_ok=True)
    
    def generate_pdf_report(self, analysis_data: Dict, language: str = 'en', 
                           save_to_file: bool = False) -> Tuple[bytes, Optional[str]]:
        """
        Generate PDF report.
        
        Args:
            analysis_data: Analysis data dictionary
            language: Language code
            save_to_file: Whether to save to file
        
        Returns:
            Tuple of (PDF bytes, file path if saved)
        """
        report = PlantAnalysisPDFReport(analysis_data, language)
        
        file_path = None
        if save_to_file:
            filename = f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            file_path = os.path.join(self.reports_folder, filename)
        
        pdf_bytes = report.generate(file_path)
        return pdf_bytes, file_path
    
    def generate_image_report(self, analysis_data: Dict, language: str = 'en',
                             save_to_file: bool = False) -> Tuple[bytes, Optional[str]]:
        """
        Generate image report.
        
        Args:
            analysis_data: Analysis data dictionary
            language: Language code
            save_to_file: Whether to save to file
        
        Returns:
            Tuple of (PNG bytes, file path if saved)
        """
        report = PlantAnalysisImageReport(analysis_data, language)
        
        file_path = None
        if save_to_file:
            filename = f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            file_path = os.path.join(self.reports_folder, filename)
        
        img_bytes = report.generate(file_path)
        return img_bytes, file_path


# Global report service instance
report_service = ReportService()
