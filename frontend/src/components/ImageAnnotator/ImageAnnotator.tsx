import React, { useEffect, useRef, useState } from "react";
import "./ImageAnnotator.css";

interface Coordinates {
  x: number;
  y: number;
}

interface Annotation {
  top_left: Coordinates;
  top_right: Coordinates;
  bottom_right: Coordinates;
  bottom_left: Coordinates;
  label?: string;
}

interface ImageAnnotatorProps {
  imageUrl: string;
  annotations: Annotation[];
  className?: string;
}

const ImageAnnotator: React.FC<ImageAnnotatorProps> = ({
  imageUrl,
  annotations,
  className = "",
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [scale, setScale] = useState(1);

  useEffect(() => {
    const updateScale = () => {
      if (containerRef.current) {
        const containerWidth = containerRef.current.clientWidth;
        const img = new Image();
        img.src = imageUrl;
        img.onload = () => {
          setScale(containerWidth / img.naturalWidth);
        };
      }
    };

    updateScale();
    window.addEventListener("resize", updateScale);
    return () => window.removeEventListener("resize", updateScale);
  }, [imageUrl]);

  return (
    <div className={`image-annotator-container ${className}`}>
      <img src={imageUrl} alt="Annotated content" className="annotated-image" />

      {annotations.map((annotation, index) => {
        const x = annotation.top_left.x * scale;
        const y = annotation.top_left.y * scale;
        const width = (annotation.top_right.x - annotation.top_left.x) * scale;
        const height =
          (annotation.bottom_left.y - annotation.top_left.y) * scale;

        return (
          <div
            key={index}
            className="annotation-box"
            style={{
              left: `${x}px`,
              top: `${y}px`,
              width: `${width}px`,
              height: `${height}px`,
            }}
          >
            {annotation.label && (
              <span className="annotation-label">{annotation.label}</span>
            )}
          </div>
        );
      })}
    </div>
  );
};

export default ImageAnnotator;
