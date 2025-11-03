import React, { useEffect, useRef } from 'react';
import { useAppStore } from '../store/useAppStore';
import { colors, personalityModes } from '../styles/designTokens';
import { AppPhase } from '../types';
import { Clock } from 'lucide-react';

interface Particle {
  x: number;
  y: number;
  size: number;
  speedX: number;
  speedY: number;
  opacity: number;
}

interface ShootingStar {
  x: number;
  y: number;
  length: number;
  speed: number;
  angle: number;
  isActive: boolean;
  spawnTime: number; // ADD: The timestamp when it was created
  duration: number;  // ADD: How long it should live, in milliseconds
}

/**
 * AnimatedBackground Component
 * Renders a celestial background with particles and shooting stars that adapt to personality modes
 */
export const AnimatedBackground: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const { phase, personalityMode } = useAppStore();
  const particlesRef = useRef<Particle[]>([]);
  const shootingStarRef = useRef<ShootingStar | null>(null);
  const lastStarTimeRef = useRef<number>(0);
  const animationFrameRef = useRef<number>();

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Initialize particles based on phase
    const initParticles = () => {
      const particleCount = phase === AppPhase.READY || phase === AppPhase.QUERYING ? 50 : 30;
      particlesRef.current = [];

      for (let i = 0; i < particleCount; i++) {
        particlesRef.current.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          size: Math.random() * 2 + 1,
          speedX: (Math.random() - 0.5) * 0.3,
          speedY: (Math.random() - 0.5) * 0.3,
          opacity: Math.random() * 0.5 + 0.3,
        });
      }
    };
    initParticles();

    // Get personality config
    const modeConfig = personalityModes[personalityMode];
    const tempo = modeConfig.tempo;
    // You can control the rate by adding 'shootingStarRate' (stars per minute) to your personalityModes object
    const shootingStarRate = modeConfig.shootingStarRate || 0.1 ; // Default to 2 per minute
    const shootingStarInterval = 60000 / shootingStarRate; // Time in ms between stars

    // Spawn a new shooting star
    const spawnShootingStar = () => {
      const angle = Math.PI * 0.2 + Math.random() * Math.PI * 0.1; // Diagonal angle
      shootingStarRef.current = {
        x: Math.random() * canvas.width,
        y: -50,
        length: Math.random() * 150 + 100,
        speed: Math.random() * 5 + 5,
        angle,
        isActive: true,
        spawnTime: Date.now(), // ADD: Set the spawn time
        duration: Math.random() * 2000 + 500, // ADD: Set duration (2000-4000 ms)
      };
      lastStarTimeRef.current = Date.now();
    };
    
    // Main animation loop
    const animate = () => {
      const currentTime = Date.now();

      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // --- Draw and update particles ---
      particlesRef.current.forEach((p, index) => {
        let particleColor = colors.silver.warm;
        if (personalityMode === 'apollo' && index % 3 === 0) {
          particleColor = colors.apollo.primary;
        } else if (personalityMode === 'hermes') {
          particleColor = index % 2 === 0 ? colors.hermes.cyan : colors.hermes.violet;
        } else if (phase === AppPhase.INSIGHT) {
          particleColor = colors.insight.bloom;
        }
        const rgb = hexToRgb(particleColor);
        
        // Draw particle
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, ${p.opacity})`;
        ctx.fill();

        // Update position
        const speedMultiplier = tempo / 80;
        p.x += p.speedX * speedMultiplier;
        p.y += p.speedY * speedMultiplier;

        // Wrap around screen edges
        if (p.x < 0) p.x = canvas.width;
        if (p.x > canvas.width) p.x = 0;
        if (p.y < 0) p.y = canvas.height;
        if (p.y > canvas.height) p.y = 0;
      });

      // --- Spawn, draw, and update shooting star ---
      if (!shootingStarRef.current?.isActive && currentTime - lastStarTimeRef.current > shootingStarInterval) {
        spawnShootingStar();
      }

      const star = shootingStarRef.current;
      if (star && star.isActive) {
        // Calculate how far along the star is in its life (0 to 1)
        const lifeProgress = Math.min((currentTime - star.spawnTime) / star.duration, 1);
        // The opacity will fade from 0.8 down to 0
        const currentOpacity = 0.8 * (1 - lifeProgress);

        const endX = star.x - Math.cos(star.angle) * star.length;
        const endY = star.y - Math.sin(star.angle) * star.length;

        // Create gradient for the tail using the new dynamic opacity
        const gradient = ctx.createLinearGradient(star.x, star.y, endX, endY);
        gradient.addColorStop(0, `rgba(255, 255, 255, ${currentOpacity})`); // USE currentOpacity
        gradient.addColorStop(1, `rgba(255, 255, 255, 0)`);

        ctx.strokeStyle = gradient;
        ctx.lineWidth = 2;
        ctx.lineCap = 'round';
        
        ctx.beginPath();
        ctx.moveTo(star.x, star.y);
        ctx.lineTo(endX, endY);
        ctx.stroke();

        // Update position
        star.x += Math.cos(star.angle) * star.speed;
        star.y += Math.sin(star.angle) * star.speed;

        // Deactivate when its lifetime expires OR it goes off-screen
        if (currentTime - star.spawnTime > star.duration || star.x > canvas.width + star.length) {
          star.isActive = false;
        }
      }

      // Special effect for insight bloom phase
      // if (phase === AppPhase.INSIGHT) {
      //   const bloomProgress = Math.min(( % 4000) / 4000, 1);
      //   const bloomSize = bloomProgress * 100;
      //   const bloomOpacity = Math.sin(bloomProgress * Math.PI) * 0.3;

      //   const rgb = hexToRgb(colors.insight.bloom);
      //   const gradient = ctx.createRadialGradient(
      //     canvas.width / 2,
      //     canvas.height / 2,
      //     0,
      //     canvas.width / 2,
      //     canvas.height / 2,
      //     bloomSize
      //   );
      //   gradient.addColorStop(0, `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, ${bloomOpacity})`);
      //   gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');

      //   ctx.fillStyle = gradient;
      //   ctx.fillRect(0, 0, canvas.width, canvas.height);
      // }

      animationFrameRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener('resize', resizeCanvas);
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [phase, personalityMode]);

  return (
    <canvas
      ref={canvasRef}
      className="fixed top-0 left-0 w-full h-full pointer-events-none z-0"
      style={{ backgroundColor: colors.midnight.deep }}
    />
  );
};

// Helper function to convert hex to RGB
function hexToRgb(hex: string): { r: number; g: number; b: number } {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16),
      }
    : { r: 232, g: 238, b: 242 }; // Default to silver
}