#!/usr/bin/env python3
"""
Image Comparison Utilities for Visual Testing
"""

from enum import Enum

try:
    from PIL import Image, ImageChops, ImageStat

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class ComparisonMetric(Enum):
    """Image comparison metrics."""

    RMS = "rms"  # Root Mean Square
    MAE = "mae"  # Mean Absolute Error
    SSIM = "ssim"  # Structural Similarity Index
    HISTOGRAM = "histogram"  # Histogram comparison


class ImageComparator:
    """Advanced image comparison utilities."""

    def __init__(self):
        if not PIL_AVAILABLE:
            raise ImportError("PIL (Pillow) is required for image comparison")

    def compare_rms(self, img1: Image.Image, img2: Image.Image) -> float:
        """
        Compare images using Root Mean Square difference.

        Args:
            img1: First image
            img2: Second image

        Returns:
            Difference value (0.0 = identical, 1.0 = completely different)
        """
        if img1.size != img2.size:
            return 1.0

        # Calculate RMS difference
        diff = ImageChops.difference(img1, img2)
        stat = ImageStat.Stat(diff)
        rms = stat.rms

        # Normalize to 0-1 range
        max_rms = [255.0] * len(rms)
        normalized = sum(r / m for r, m in zip(rms, max_rms)) / len(rms)

        return normalized

    def compare_histogram(self, img1: Image.Image, img2: Image.Image) -> float:
        """
        Compare images using histogram correlation.

        Args:
            img1: First image
            img2: Second image

        Returns:
            Difference value (0.0 = identical, 1.0 = completely different)
        """
        # Convert to same mode if needed
        if img1.mode != img2.mode:
            img2 = img2.convert(img1.mode)

        # Get histograms
        hist1 = img1.histogram()
        hist2 = img2.histogram()

        # Calculate correlation coefficient
        sum1 = sum(hist1)
        sum2 = sum(hist2)

        if sum1 == 0 or sum2 == 0:
            return 1.0

        # Normalize histograms
        hist1_norm = [h / sum1 for h in hist1]
        hist2_norm = [h / sum2 for h in hist2]

        # Calculate chi-squared distance
        chi_squared = 0.0
        for h1, h2 in zip(hist1_norm, hist2_norm):
            if h1 + h2 > 0:
                chi_squared += ((h1 - h2) ** 2) / (h1 + h2)

        # Normalize to 0-1 range (approximate)
        return min(chi_squared / 2.0, 1.0)

    def compare_ssim_simple(self, img1: Image.Image, img2: Image.Image) -> float:
        """
        Simplified SSIM-like comparison.

        Args:
            img1: First image
            img2: Second image

        Returns:
            Difference value (0.0 = identical, 1.0 = completely different)
        """
        if img1.size != img2.size:
            return 1.0

        # Convert to grayscale for simplicity
        gray1 = img1.convert("L")
        gray2 = img2.convert("L")

        # Calculate means
        stat1 = ImageStat.Stat(gray1)
        stat2 = ImageStat.Stat(gray2)

        mean1 = stat1.mean[0]
        mean2 = stat2.mean[0]

        # Calculate variances
        var1 = stat1.var[0] if stat1.var else 0
        var2 = stat2.var[0] if stat2.var else 0

        # Calculate covariance (simplified)
        diff = ImageChops.difference(gray1, gray2)
        stat_diff = ImageStat.Stat(diff)
        covariance = stat_diff.var[0] if stat_diff.var else 0

        # SSIM-like calculation
        c1 = (0.01 * 255) ** 2
        c2 = (0.03 * 255) ** 2

        numerator = (2 * mean1 * mean2 + c1) * (2 * covariance + c2)
        denominator = (mean1**2 + mean2**2 + c1) * (var1 + var2 + c2)

        if denominator == 0:
            ssim = 1.0
        else:
            ssim = numerator / denominator

        # Convert SSIM to difference (1 - ssim for 0=identical, 1=different)
        return max(0.0, 1.0 - ssim)

    def compare_perceptual(self, img1: Image.Image, img2: Image.Image) -> float:
        """
        Perceptual image comparison considering human vision.

        Args:
            img1: First image
            img2: Second image

        Returns:
            Difference value (0.0 = identical, 1.0 = completely different)
        """
        if img1.size != img2.size:
            return 1.0

        # Convert to LAB color space for perceptual comparison
        try:
            lab1 = img1.convert("RGB")
            lab2 = img2.convert("RGB")

            # Simple perceptual weighting (rough approximation)
            # Weight red, green, blue channels differently based on human perception
            weights = [0.299, 0.587, 0.114]  # Luminance weights

            total_diff = 0.0
            pixel_count = 0

            data1 = lab1.getdata()
            data2 = lab2.getdata()

            for p1, p2 in zip(data1, data2):
                # Calculate weighted difference
                weighted_diff = sum(w * abs(c1 - c2) for w, c1, c2 in zip(weights, p1, p2))
                total_diff += weighted_diff
                pixel_count += 1

            if pixel_count == 0:
                return 0.0

            # Normalize to 0-1 range
            avg_diff = total_diff / pixel_count
            max_diff = sum(weights) * 255  # Maximum possible difference
            return min(avg_diff / max_diff, 1.0)

        except Exception:
            # Fallback to RMS if LAB conversion fails
            return self.compare_rms(img1, img2)

    def compare_images(
        self, img1: Image.Image, img2: Image.Image, metric: ComparisonMetric = ComparisonMetric.RMS
    ) -> float:
        """
        Compare two images using the specified metric.

        Args:
            img1: First image
            img2: Second image
            metric: Comparison metric to use

        Returns:
            Difference value (0.0 = identical, 1.0 = completely different)
        """
        if metric == ComparisonMetric.RMS:
            return self.compare_rms(img1, img2)
        elif metric == ComparisonMetric.HISTOGRAM:
            return self.compare_histogram(img1, img2)
        elif metric == ComparisonMetric.SSIM:
            return self.compare_ssim_simple(img1, img2)
        else:
            return self.compare_perceptual(img1, img2)

    def multi_metric_comparison(self, img1: Image.Image, img2: Image.Image) -> dict[str, float]:
        """
        Compare images using multiple metrics.

        Args:
            img1: First image
            img2: Second image

        Returns:
            Dictionary with results from all metrics
        """
        return {
            "rms": self.compare_rms(img1, img2),
            "histogram": self.compare_histogram(img1, img2),
            "ssim": self.compare_ssim_simple(img1, img2),
            "perceptual": self.compare_perceptual(img1, img2),
        }

    def is_similar(
        self,
        img1: Image.Image,
        img2: Image.Image,
        tolerance: float = 0.01,
        metric: ComparisonMetric = ComparisonMetric.RMS,
    ) -> bool:
        """
        Check if two images are similar within tolerance.

        Args:
            img1: First image
            img2: Second image
            tolerance: Similarity tolerance (0.0-1.0)
            metric: Comparison metric to use

        Returns:
            True if images are similar within tolerance
        """
        difference = self.compare_images(img1, img2, metric)
        return difference <= tolerance

    def get_best_metric(
        self, img1: Image.Image, img2: Image.Image
    ) -> tuple[ComparisonMetric, float]:
        """
        Find the best metric for comparing two specific images.

        Args:
            img1: First image
            img2: Second image

        Returns:
            Tuple of (best_metric, confidence_score)
        """
        results = self.multi_metric_comparison(img1, img2)

        # Simple heuristic: choose metric with most consistent results
        # This is a simplified implementation
        values = list(results.values())
        mean_val = sum(values) / len(values)
        variance = sum((v - mean_val) ** 2 for v in values) / len(values)

        # Lower variance indicates more consistent results
        confidence = 1.0 / (1.0 + variance)

        # Choose metric closest to mean (most representative)
        best_metric = min(results.keys(), key=lambda k: abs(results[k] - mean_val))

        return ComparisonMetric(best_metric), confidence
