import { useEffect, useRef } from "react";
import * as THREE from "three";
import { cn } from "../lib/cn";

interface DottedSurfaceProps {
  className?: string;
}

export function DottedSurface({ className }: DottedSurfaceProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const scene = new THREE.Scene();
    scene.fog = new THREE.Fog(0x111111, 1400, 6600);

    const camera = new THREE.PerspectiveCamera(60, 1, 1, 8000);
    camera.position.set(0, 330, 1180);

    const renderer = new THREE.WebGLRenderer({
      alpha: true,
      antialias: true,
      powerPreference: "high-performance",
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setClearColor(0x111111, 0);
    container.appendChild(renderer.domElement);

    const separation = 150;
    const amountX = 42;
    const amountY = 54;
    const positions: number[] = [];
    const colors: number[] = [];
    const geometry = new THREE.BufferGeometry();

    for (let ix = 0; ix < amountX; ix += 1) {
      for (let iy = 0; iy < amountY; iy += 1) {
        positions.push(
          ix * separation - (amountX * separation) / 2,
          0,
          iy * separation - (amountY * separation) / 2,
        );
        colors.push(0.58, 0.58, 0.58);
      }
    }

    geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
    geometry.setAttribute("color", new THREE.Float32BufferAttribute(colors, 3));

    const material = new THREE.PointsMaterial({
      size: 7,
      vertexColors: true,
      transparent: true,
      opacity: 0.06,
      sizeAttenuation: true,
    });

    const points = new THREE.Points(geometry, material);
    scene.add(points);

    let count = 0;
    let animationId = 0;
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    const resize = () => {
      const width = container.clientWidth || window.innerWidth;
      const height = container.clientHeight || window.innerHeight;
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height, false);
    };

    const animate = () => {
      animationId = requestAnimationFrame(animate);
      const positionAttribute = geometry.attributes.position;
      const positionArray = positionAttribute.array as Float32Array;

      let particle = 0;
      for (let ix = 0; ix < amountX; ix += 1) {
        for (let iy = 0; iy < amountY; iy += 1) {
          const index = particle * 3;
          positionArray[index + 1] =
            Math.sin((ix + count) * 0.28) * 38 +
            Math.sin((iy + count) * 0.44) * 34;
          particle += 1;
        }
      }

      positionAttribute.needsUpdate = true;
      points.rotation.x = -0.08;
      renderer.render(scene, camera);
      count += reducedMotion ? 0 : 0.045;
    };

    resize();
    animate();
    window.addEventListener("resize", resize);

    return () => {
      window.removeEventListener("resize", resize);
      cancelAnimationFrame(animationId);
      geometry.dispose();
      material.dispose();
      renderer.dispose();
      renderer.domElement.remove();
    };
  }, []);

  return <div ref={containerRef} className={cn("dotted-surface", className)} aria-hidden="true" />;
}
