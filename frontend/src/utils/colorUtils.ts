import React from 'react';

/**
 * Utility functions for adaptive text color based on background luminance
 */

export interface AdaptiveColors {
  text: string;
  textSecondary: string;
  border: string;
  background: string;
}

/**
 * Calculate the relative luminance of a color
 * @param r Red component (0-255)
 * @param g Green component (0-255)
 * @param b Blue component (0-255)
 * @returns Relative luminance (0-1)
 */
export const calculateLuminance = (r: number, g: number, b: number): number => {
  const [rs, gs, bs] = [r, g, b].map(c => {
    c = c / 255;
    return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
};

/**
 * Get the average color from a canvas context
 * @param canvas Canvas element
 * @returns RGB values as [r, g, b]
 */
export const getAverageColor = (canvas: HTMLCanvasElement): [number, number, number] => {
  const ctx = canvas.getContext('2d');
  if (!ctx) return [255, 255, 255]; // Default to white

  const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
  const data = imageData.data;
  let r = 0, g = 0, b = 0;
  const pixelCount = data.length / 4;

  for (let i = 0; i < data.length; i += 4) {
    r += data[i];
    g += data[i + 1];
    b += data[i + 2];
  }

  return [
    Math.round(r / pixelCount),
    Math.round(g / pixelCount),
    Math.round(b / pixelCount)
  ];
};

/**
 * Detect if the background is light or dark
 * @param element DOM element to analyze
 * @returns true if background is light, false if dark
 */
export const isBackgroundLight = (element: HTMLElement): boolean => {
  // Create a temporary canvas to sample the background
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  if (!ctx) return true; // Default to light

  const rect = element.getBoundingClientRect();
  canvas.width = Math.min(rect.width, 100);
  canvas.height = Math.min(rect.height, 100);

  // Draw the element's background onto the canvas
  const computedStyle = window.getComputedStyle(element);
  const bgColor = computedStyle.backgroundColor;
  
  // If background is transparent, sample from parent or body
  if (bgColor === 'rgba(0, 0, 0, 0)' || bgColor === 'transparent') {
    return isBackgroundLight(element.parentElement || document.body);
  }

  // Parse the background color
  const rgbMatch = bgColor.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
  if (rgbMatch) {
    const [, r, g, b] = rgbMatch.map(Number);
    const luminance = calculateLuminance(r, g, b);
    return luminance > 0.5;
  }

  return true; // Default to light
};

/**
 * Get adaptive colors based on background luminance
 * @param isLight Whether the background is light
 * @returns Adaptive color scheme
 */
export const getAdaptiveColors = (isLight: boolean): AdaptiveColors => {
  if (isLight) {
    return {
      text: 'rgba(0, 0, 0, 0.9)',
      textSecondary: 'rgba(0, 0, 0, 0.6)',
      border: 'rgba(0, 0, 0, 0.1)',
      background: 'rgba(255, 255, 255, 0.1)'
    };
  } else {
    return {
      text: 'rgba(255, 255, 255, 0.9)',
      textSecondary: 'rgba(255, 255, 255, 0.6)',
      border: 'rgba(255, 255, 255, 0.2)',
      background: 'rgba(0, 0, 0, 0.1)'
    };
  }
};

/**
 * React hook for adaptive colors
 */
export const useAdaptiveColors = (elementRef: React.RefObject<HTMLElement | null>) => {
  const [colors, setColors] = React.useState<AdaptiveColors>(getAdaptiveColors(true));

  React.useEffect(() => {
    const updateColors = () => {
      if (elementRef.current) {
        const isLight = isBackgroundLight(elementRef.current);
        setColors(getAdaptiveColors(isLight));
      }
    };

    updateColors();

    // Update colors when the page loads or resizes
    const handleResize = () => {
      setTimeout(updateColors, 100);
    };

    window.addEventListener('resize', handleResize);
    window.addEventListener('load', updateColors);

    // Observer for background changes
    const observer = new MutationObserver(updateColors);
    if (elementRef.current) {
      observer.observe(elementRef.current, {
        attributes: true,
        attributeFilter: ['style', 'class']
      });
    }

    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('load', updateColors);
      observer.disconnect();
    };
  }, [elementRef]);

  return colors;
};