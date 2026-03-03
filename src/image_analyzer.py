import cv2
import numpy as np
from pathlib import Path
from PIL import Image
import imagehash
from typing import Dict, List, Tuple


class ImageAnalyzer:
    """Analyze images for quality, duplicates, and issues"""

    def __init__(self, blur_threshold: float = 100.0, similarity_threshold: int = 5):
        """
        Initialize ImageAnalyzer

        Args:
            blur_threshold: Threshold for blur detection (lower = more blurry)
            similarity_threshold: Hash difference threshold for similar images
        """
        self.blur_threshold = blur_threshold
        self.similarity_threshold = similarity_threshold

        # Supported image formats
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}

    def is_image(self, file_path: Path) -> bool:
        """Check if file is an image"""
        return file_path.suffix.lower() in self.image_extensions

    def detect_blur(self, image_path: Path) -> Tuple[bool, float]:
        """
        Detect if image is blurry using Laplacian variance

        Returns:
            (is_blurry, blur_score)
        """
        try:
            # Read image
            image = cv2.imread(str(image_path))
            if image is None:
                return False, 0.0

            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Calculate Laplacian variance
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

            is_blurry = laplacian_var < self.blur_threshold

            return is_blurry, laplacian_var

        except Exception as e:
            print(f"Error analyzing {image_path}: {e}")
            return False, 0.0

    def detect_face_crop(self, image_path: Path) -> Tuple[bool, int]:
        """
        Detect if faces are cropped/cut off

        Returns:
            (has_cropped_face, number_of_faces)
        """
        try:
            # Load the cascade classifier for face detection
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )

            # Read image
            image = cv2.imread(str(image_path))
            if image is None:
                return False, 0

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Detect faces
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )

            # Check if any face is near the edge (potentially cropped)
            img_height, img_width = image.shape[:2]
            edge_threshold = 10  # pixels from edge

            has_cropped = False
            for (x, y, w, h) in faces:
                # Check if face touches edges
                if (x < edge_threshold or
                        y < edge_threshold or
                        x + w > img_width - edge_threshold or
                        y + h > img_height - edge_threshold):
                    has_cropped = True
                    break

            return has_cropped, len(faces)

        except Exception as e:
            print(f"Error detecting faces in {image_path}: {e}")
            return False, 0

    def get_image_hash(self, image_path: Path) -> str:
        """Get perceptual hash of image"""
        try:
            image = Image.open(image_path)
            return str(imagehash.average_hash(image))
        except Exception as e:
            print(f"Error hashing {image_path}: {e}")
            return ""

    def find_similar_images(self, directory: Path) -> Dict[str, List[Path]]:
        """
        Find similar/duplicate images using perceptual hashing

        Returns:
            Dictionary with hash as key and list of similar images
        """
        hash_map = {}

        for file_path in directory.rglob('*'):
            if file_path.is_file() and self.is_image(file_path):
                img_hash = self.get_image_hash(file_path)

                if img_hash:
                    if img_hash not in hash_map:
                        hash_map[img_hash] = []
                    hash_map[img_hash].append(file_path)

        # Return only groups with multiple images
        similar = {k: v for k, v in hash_map.items() if len(v) > 1}
        return similar

    def analyze_image_quality(self, image_path: Path) -> Dict:
        """
        Comprehensive image quality analysis

        Returns:
            Dictionary with analysis results
        """
        result = {
            'path': str(image_path),
            'is_blurry': False,
            'blur_score': 0.0,
            'has_cropped_face': False,
            'face_count': 0,
            'is_low_resolution': False,
            'resolution': (0, 0),
            'file_size_mb': 0.0,
            'quality_issues': []
        }

        try:
            # Check blur
            is_blurry, blur_score = self.detect_blur(image_path)
            result['is_blurry'] = is_blurry
            result['blur_score'] = blur_score

            if is_blurry:
                result['quality_issues'].append('Blurry image')

            # Check face cropping
            has_cropped, face_count = self.detect_face_crop(image_path)
            result['has_cropped_face'] = has_cropped
            result['face_count'] = face_count

            if has_cropped:
                result['quality_issues'].append('Face partially cropped')

            # Check resolution
            image = Image.open(image_path)
            width, height = image.size
            result['resolution'] = (width, height)

            # Consider low resolution if smaller than 800x600
            if width < 800 or height < 600:
                result['is_low_resolution'] = True
                result['quality_issues'].append(f'Low resolution ({width}x{height})')

            # File size
            file_size = image_path.stat().st_size
            result['file_size_mb'] = file_size / (1024 * 1024)

        except Exception as e:
            result['quality_issues'].append(f'Error analyzing: {str(e)}')

        return result

    def organize_by_quality(self, source_dir: Path) -> Dict:
        """
        Organize images into quality categories

        Returns:
            Statistics about organized images
        """
        source_dir = Path(source_dir)

        # Create output directories
        good_dir = source_dir / "Good_Images"
        bad_dir = source_dir / "Bad_Images"
        blurry_dir = bad_dir / "Blurry"
        cropped_dir = bad_dir / "Cropped_Faces"
        low_res_dir = bad_dir / "Low_Resolution"

        good_dir.mkdir(exist_ok=True)
        bad_dir.mkdir(exist_ok=True)
        blurry_dir.mkdir(exist_ok=True)
        cropped_dir.mkdir(exist_ok=True)
        low_res_dir.mkdir(exist_ok=True)

        stats = {
            'total_analyzed': 0,
            'good_images': 0,
            'blurry_images': 0,
            'cropped_faces': 0,
            'low_resolution': 0,
            'errors': 0
        }

        for file_path in source_dir.iterdir():
            if file_path.is_file() and self.is_image(file_path):
                stats['total_analyzed'] += 1

                analysis = self.analyze_image_quality(file_path)

                # Determine destination
                if not analysis['quality_issues']:
                    # Good image
                    dest = good_dir / file_path.name
                    stats['good_images'] += 1
                else:
                    # Bad image - categorize by primary issue
                    if analysis['is_blurry']:
                        dest = blurry_dir / file_path.name
                        stats['blurry_images'] += 1
                    elif analysis['has_cropped_face']:
                        dest = cropped_dir / file_path.name
                        stats['cropped_faces'] += 1
                    elif analysis['is_low_resolution']:
                        dest = low_res_dir / file_path.name
                        stats['low_resolution'] += 1
                    else:
                        dest = bad_dir / file_path.name

                # Move file
                try:
                    import shutil
                    shutil.move(str(file_path), str(dest))
                    print(f"Moved {file_path.name} to {dest.parent.name}/")
                except Exception as e:
                    print(f"Error moving {file_path}: {e}")
                    stats['errors'] += 1

        return stats