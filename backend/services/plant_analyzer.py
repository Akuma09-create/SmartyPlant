"""
Plant analysis service.
Integrates image processing and disease detection for comprehensive plant analysis.
"""

import numpy as np
from typing import Optional, Dict, List
from models import PlantDiseaseDetector
from .image_processor import ImageProcessor


class PlantAnalyzer:
    """
    Service for comprehensive plant analysis.
    Combines image processing with disease detection.
    """
    
    def __init__(self):
        """Initialize plant analyzer with required services."""
        self.image_processor = ImageProcessor()
        self.disease_detector = PlantDiseaseDetector()
        self.analysis_cache = {}
    
    def analyze_plant_image(self, image_file, confidence_threshold: float = 0.7) -> Dict:
        """
        Perform comprehensive analysis of plant image.
        
        Args:
            image_file: File-like object or file path
            confidence_threshold: Minimum confidence for predictions
            
        Returns:
            Dictionary with complete analysis results
        """
        try:
            # Step 1: Validate image
            validation = self.image_processor.validate_image(image_file)
            if not validation['valid']:
                return {
                    'success': False,
                    'error': validation['error'],
                    'stage': 'validation'
                }
            
            # Step 2: Preprocess image
            image_array, original_image = self.image_processor.preprocess_image(image_file)
            
            # Step 3: Enhance image
            enhanced_image = self.image_processor.enhance_image(image_array)
            
            # Step 4: Extract regions of interest
            roi_list = self.image_processor.extract_roi(enhanced_image)
            
            # Step 5: Detect disease
            disease_detection = self.disease_detector.detect_disease(
                enhanced_image, 
                confidence_threshold=confidence_threshold
            )
            
            if not disease_detection['success']:
                return {
                    'success': False,
                    'error': disease_detection.get('error', 'Detection failed'),
                    'stage': 'detection'
                }
            
            # Step 6: Analyze severity
            primary_disease = disease_detection['primary_disease']
            severity_analysis = self._analyze_severity(
                primary_disease,
                disease_detection['feature_analysis'],
                roi_list
            )
            
            # Step 7: Compile results
            analysis_result = {
                'success': True,
                'image_info': {
                    'format': validation['format'],
                    'size': validation['size'],
                    'original_size': original_image.size
                },
                'disease_detection': {
                    'primary_disease': primary_disease['disease'],
                    'confidence': round(primary_disease['confidence'], 3),
                    'severity': severity_analysis['severity_level'],
                    'description': primary_disease['description'],
                    'common_causes': primary_disease['common_causes']
                },
                'predictions': disease_detection['predictions'],
                'feature_analysis': disease_detection['feature_analysis'],
                'roi_analysis': self._summarize_roi(roi_list),
                'severity_details': severity_analysis,
                'timestamp': self._get_timestamp()
            }
            
            return analysis_result
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Analysis failed: {str(e)}",
                'stage': 'analysis'
            }
    
    def _analyze_severity(self, disease_info: Dict, features: Dict, roi_list: List) -> Dict:
        """
        Analyze disease severity based on multiple factors.
        
        Args:
            disease_info: Disease detection information
            features: Extracted image features
            roi_list: List of regions of interest
            
        Returns:
            Dictionary with severity analysis
        """
        disease_name = disease_info['disease']
        base_severity = disease_info['severity']
        
        # Calculate severity multiplier based on features
        damage_ratio = features.get('damaged_pixels_ratio', 0)
        edge_density = features.get('edge_density', 0)
        
        # Determine affected area percentage
        affected_area = len([roi for roi in roi_list if self._is_roi_affected(roi)]) / max(len(roi_list), 1)
        
        # Calculate final severity level
        if damage_ratio > 0.6 or affected_area > 0.7:
            severity_level = 'severe'
            progression = 'advancing'
        elif damage_ratio > 0.3 or affected_area > 0.4:
            severity_level = 'moderate'
            progression = 'progressing'
        else:
            severity_level = 'mild'
            progression = 'early_stage'
        
        return {
            'base_severity': base_severity,
            'calculated_severity': severity_level,
            'severity_level': severity_level,
            'progression_stage': progression,
            'affected_area_percentage': round(affected_area * 100, 1),
            'damage_extent': round(damage_ratio * 100, 1),
            'confidence_in_severity': min(0.95, max(damage_ratio, affected_area))
        }
    
    def _is_roi_affected(self, roi: Dict) -> bool:
        """Check if region of interest shows signs of disease."""
        roi_data = roi['data']
        # Simple heuristic: if ROI has high edge density, likely affected
        edge_density = np.std(roi_data)
        return edge_density > 15
    
    def _summarize_roi(self, roi_list: List) -> Dict:
        """Summarize regions of interest analysis."""
        if not roi_list:
            return {'total_rois': 0, 'affected_rois': 0}
        
        affected = len([r for r in roi_list if self._is_roi_affected(r)])
        
        return {
            'total_rois': len(roi_list),
            'affected_rois': affected,
            'healthy_rois': len(roi_list) - affected,
            'affected_percentage': round((affected / len(roi_list)) * 100, 1)
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + 'Z'
    
    def batch_analyze(self, image_files: List) -> List[Dict]:
        """
        Analyze multiple plant images.
        
        Args:
            image_files: List of image files
            
        Returns:
            List of analysis results
        """
        results = []
        for image_file in image_files:
            result = self.analyze_plant_image(image_file)
            results.append(result)
        
        return results
