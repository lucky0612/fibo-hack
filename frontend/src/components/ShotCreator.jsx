// src/components/ShotCreator.jsx
import { useState } from 'react';
import { motion } from 'framer-motion';
import { Camera, Loader2, Sparkles, Wand2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { createShot } from '../lib/api';

export default function ShotCreator({ onShotCreated }) {
  const [sceneDescription, setSceneDescription] = useState('');
  const [shotType, setShotType] = useState('medium shot');
  const [aspectRatio, setAspectRatio] = useState('16:9');
  const [hdrPreset, setHdrPreset] = useState('neutral');
  const [loading, setLoading] = useState(false);

  const shotTypes = [
    'extreme wide shot',
    'wide shot',
    'medium shot',
    'medium close-up',
    'close-up',
    'extreme close-up'
  ];

  const aspectRatios = ['16:9', '1:1', '4:3', '2:3', '9:16'];
  
  const hdrPresets = [
    { value: 'neutral', label: 'Neutral', desc: 'Clean, balanced' },
    { value: 'warm', label: 'Warm', desc: 'Golden hour' },
    { value: 'cool', label: 'Cool', desc: 'Sci-fi/clinical' },
    { value: 'dramatic', label: 'Dramatic', desc: 'High contrast' },
    { value: 'vintage', label: 'Vintage', desc: 'Desaturated' },
  ];

  const exampleScenes = [
    "Astronaut discovering ancient alien artifact on Mars at sunset",
    "Detective in noir film standing in rain-soaked alley at night",
    "Hero character at edge of cliff overlooking vast fantasy landscape",
    "Close-up of hands typing on vintage typewriter in dim library",
    "Futuristic city skyline with flying cars at golden hour"
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!sceneDescription.trim()) {
      toast.error('Please describe your scene');
      return;
    }

    setLoading(true);
    
    try {
      const result = await createShot({
        scene_description: sceneDescription,
        shot_type: shotType,
        aspect_ratio: aspectRatio,
        apply_hdr: true,
        hdr_preset: hdrPreset,
        hdr_settings: {
          exposure: 0.0,
          contrast: 1.0,
          saturation: 1.0,
          temperature: 0.0
        }
      });

      toast.success('Shot created! Processing HDR...');
      onShotCreated(result.shot);
      
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create shot');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-cinema-dark rounded-xl border border-cinema-gray overflow-hidden"
    >
      {/* Header */}
      <div className="p-6 bg-cinema-darker border-b border-cinema-gray">
        <h2 className="text-2xl font-bold flex items-center gap-3">
          <Camera className="w-7 h-7 text-cinema-accent" />
          Create Cinematic Shot
        </h2>
        <p className="text-cinema-lightgray mt-2">
          Describe your scene and let the AI cinema crew bring it to life
        </p>
      </div>

      <form onSubmit={handleSubmit} className="p-6 space-y-6">
        {/* Scene Description */}
        <div>
          <label className="block text-sm font-semibold mb-3 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-cinema-accent" />
            Scene Description
          </label>
          
          <textarea
            value={sceneDescription}
            onChange={(e) => setSceneDescription(e.target.value)}
            placeholder="Describe your scene in detail..."
            className="w-full h-32 px-4 py-3 bg-cinema-darker border border-cinema-gray rounded-lg text-white placeholder-cinema-lightgray focus:border-cinema-accent focus:ring-2 focus:ring-cinema-accent/20 outline-none transition-all resize-none"
            disabled={loading}
          />

          {/* Example Prompts */}
          <div className="mt-3">
            <p className="text-xs text-cinema-lightgray mb-2">Quick examples:</p>
            <div className="flex flex-wrap gap-2">
              {exampleScenes.map((example, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => setSceneDescription(example)}
                  className="text-xs px-3 py-1 bg-cinema-gray hover:bg-cinema-lightgray rounded-full transition-colors"
                  disabled={loading}
                >
                  {example.substring(0, 40)}...
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Settings Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Shot Type */}
          <div>
            <label className="block text-sm font-semibold mb-2">Shot Type</label>
            <select
              value={shotType}
              onChange={(e) => setShotType(e.target.value)}
              className="w-full px-4 py-3 bg-cinema-darker border border-cinema-gray rounded-lg text-white focus:border-cinema-accent outline-none transition-all"
              disabled={loading}
            >
              {shotTypes.map((type) => (
                <option key={type} value={type} className="capitalize">
                  {type}
                </option>
              ))}
            </select>
          </div>

          {/* Aspect Ratio */}
          <div>
            <label className="block text-sm font-semibold mb-2">Aspect Ratio</label>
            <select
              value={aspectRatio}
              onChange={(e) => setAspectRatio(e.target.value)}
              className="w-full px-4 py-3 bg-cinema-darker border border-cinema-gray rounded-lg text-white focus:border-cinema-accent outline-none transition-all"
              disabled={loading}
            >
              {aspectRatios.map((ratio) => (
                <option key={ratio} value={ratio}>
                  {ratio}
                </option>
              ))}
            </select>
          </div>

          {/* HDR Preset */}
          <div>
            <label className="block text-sm font-semibold mb-2">Color Grade</label>
            <select
              value={hdrPreset}
              onChange={(e) => setHdrPreset(e.target.value)}
              className="w-full px-4 py-3 bg-cinema-darker border border-cinema-gray rounded-lg text-white focus:border-cinema-accent outline-none transition-all"
              disabled={loading}
            >
              {hdrPresets.map((preset) => (
                <option key={preset.value} value={preset.value}>
                  {preset.label} - {preset.desc}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading || !sceneDescription.trim()}
          className="w-full py-4 bg-gradient-to-r from-cinema-accent to-cinema-blue hover:from-cinema-accent/90 hover:to-cinema-blue/90 disabled:from-cinema-gray disabled:to-cinema-gray text-cinema-black font-bold rounded-lg transition-all shadow-lg hover:shadow-xl disabled:cursor-not-allowed flex items-center justify-center gap-3"
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Creating Shot... (60-120s)
            </>
          ) : (
            <>
              <Wand2 className="w-5 h-5" />
              Generate Cinematic Shot
            </>
          )}
        </button>

        {loading && (
          <div className="text-center text-sm text-cinema-lightgray space-y-2">
            <p className="animate-pulse">🎬 Cinema Crew is working...</p>
            <p className="text-xs">Director → DP → Gaffer → Editor → FIBO</p>
          </div>
        )}
      </form>
    </motion.div>
  );
}