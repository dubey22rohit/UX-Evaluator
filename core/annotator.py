from PIL import Image, ImageDraw, ImageFont
import io

class ScreenshotAnnotator:
    def __init__(self):
        self.font = ImageFont.load_default()
    
    def annotate_screenshot(self, screenshot_bytes, issues):
        """Add visual annotations to highlight UX issues on the screenshot
        
        Args:
            screenshot_bytes: Original screenshot as bytes
            issues: List of detected UX issues with coordinates
        
        Returns:
            Bytes of annotated screenshot
        """
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(screenshot_bytes))
        draw = ImageDraw.Draw(image)
        
        # Add annotations for each issue
        for i, issue in enumerate(issues):
            # Extract coordinates
            if all(k in issue for k in ['top_left_coordinates', 'top_right_coordinates', 
                                      'bottom_right_coordinates', 'bottom_left_coordinates']):
                
                # Create points list for polygon
                points = [
                    (issue['top_left_coordinates']['x'], issue['top_left_coordinates']['y']),
                    (issue['top_right_coordinates']['x'], issue['top_right_coordinates']['y']),
                    (issue['bottom_right_coordinates']['x'], issue['bottom_right_coordinates']['y']),
                    (issue['bottom_left_coordinates']['x'], issue['bottom_left_coordinates']['y'])
                ]
                
                # Draw rectangle outline
                draw.polygon(points, outline='red', width=2)
                
                # Add issue number at top-left corner
                x, y = points[0]
                draw.text((x + 5, y - 20), str(i + 1), fill='red', font=self.font)
        
        # Convert back to bytes
        output = io.BytesIO()
        image.save(output, format='PNG')
        return output.getvalue()