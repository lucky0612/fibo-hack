// src/components/CameraControl.jsx
import { useState } from 'react';
import { motion } from 'framer-motion';
import { Settings, Loader2, Zap } from 'lucide-react';

export default function CameraControl({ currentShot, onParameterChange, loading }) {
  const [activeParam, setActiveParam] = useState(null);

  const cameraAngles = [
    'eye-level',
    'low-angle',
    'high-angle',
    'overhead',
    'dutch angle',
    'point of view'
  ];

  const focalLengths = [
    '14mm wide angle',
    '24mm',
    '35mm',
    '50mm',
    '85mm portrait',
    '135mm',
    '200mm telephoto'
  ];

  const depthOfFields = [
    'shallow, f/1.4',
    'shallow, f/2.8',
    'medium, f/5.6',
    'medium, f/8',
    'deep, f/11',
    'deep, f/16'
  ];

  const lightingDirections = [
    'front',
    '45-degree key light',
    'side',
    'back',
    'overhead',
    'low angle'
  ];

  const colorSchemes = [
    'warm golden tones',
    'cool blue tones',
    'monochromatic',
    'high contrast',
    'desaturated',
    'vibrant'
  ];

  const handleChange = (param, value) => {
    setActiveParam(param);
    onParameterChange(param, value);
  };

  const ControlSection = ({ title, parameter, options, icon: Icon }) => (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold flex items-center gap-2">
          {Icon && <Icon className="w-4 h-4 text-cinema-accent" />}
          {title}
        </h3>
        {activeParam === parameter && loading && (
          <Loader2 className="w-4 h-4 animate-spin text-cinema-accent" />
        )}
      </div>
      
      <div className="grid grid-cols-1 gap-2">
        {options.map((option) => (
          <button
            key={option}
            onClick={() => handleChange(parameter, option)}
            disabled={loading}
            className={`
              px-3 py-2 rounded-lg text-left text-sm transition-all
              ${loading 
                ? 'bg-cinema-gray text-cinema-lightgray cursor-not-allowed' 
                : 'bg-cinema-darker hover:bg-cinema-gray border border-cinema-gray hover:border-cinema-accent'
              }
            `}
          >
            {option}
          </button>
        ))}
      </div>
    </div>
  );

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className="bg-cinema-dark rounded-xl border border-cinema-gray overflow-hidden"
    >
      {/* Header */}
      <div className="p-4 bg-cinema-darker border-b border-cinema-gray">
        <h2 className="text-lg font-bold flex items-center gap-2">
          <Settings className="w-5 h-5 text-cinema-accent" />
          Virtual Camera Controls
        </h2>
        <p className="text-xs text-cinema-lightgray mt-1">
          Modify parameters independently - see FIBO's disentanglement!
        </p>
      </div>

      {/* Controls */}
      <div className="p-4 space-y-6 max-h-[calc(100vh-200px)] overflow-y-auto">
        {!currentShot ? (
          <div className="text-center py-12 text-cinema-lightgray">
            <Zap className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>Create a shot to access camera controls</p>
          </div>
        ) : (
          <>
            <ControlSection
              title="Camera Angle"
              parameter="camera_angle"
              options={cameraAngles}
            />

            <ControlSection
              title="Lens Focal Length"
              parameter="lens_focal_length"
              options={focalLengths}
            />

            <ControlSection
              title="Depth of Field"
              parameter="depth_of_field"
              options={depthOfFields}
            />

            <ControlSection
              title="Lighting Direction"
              parameter="lighting_direction"
              options={lightingDirections}
            />

            <ControlSection
              title="Color Scheme"
              parameter="color_scheme"
              options={colorSchemes}
            />
          </>
        )}
      </div>

      {/* Note */}
      {currentShot && (
        <div className="p-4 bg-cinema-darker border-t border-cinema-gray">
          <p className="text-xs text-cinema-lightgray">
            💡 <span className="text-cinema-accent font-semibold">Pro Tip:</span> Each control modifies ONLY that parameter. Composition stays identical - that's FIBO's superpower!
          </p>
        </div>
      )}
    </motion.div>
  );
}