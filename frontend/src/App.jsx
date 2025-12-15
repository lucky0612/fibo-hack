// src/App.jsx
import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Film, Camera, Sparkles, Settings, Download, 
  Play, Layers, Grid, List, Plus, Loader2,
  Zap, Eye, Image as ImageIcon, ChevronRight
} from 'lucide-react';
import toast, { Toaster } from 'react-hot-toast';
import './App.css';

import { createShot, modifyParameter, listShots } from './lib/api';
import ShotCreator from './components/ShotCreator';
import ShotLibrary from './components/ShotLibrary';
import CameraControl from './components/CameraControl';
import ShotComparison from './components/ShotComparison';

function App() {
  const [activeTab, setActiveTab] = useState('create');
  const [currentShot, setCurrentShot] = useState(null);
  const [shots, setShots] = useState([]);
  const [loading, setLoading] = useState(false);

  // Load shots on mount
  useEffect(() => {
    loadShots();
  }, []);

  const loadShots = async () => {
    try {
      const data = await listShots();
      setShots(data.shots || []);
    } catch (error) {
      console.error('Failed to load shots:', error);
    }
  };

  const handleShotCreated = (newShot) => {
    setCurrentShot(newShot);
    loadShots();
    toast.success('Shot created successfully!');
  };

  const handleParameterChange = async (parameter, value) => {
    if (!currentShot) return;

    setLoading(true);
    try {
      const result = await modifyParameter(currentShot.shot_id, {
        shot_id: currentShot.shot_id,
        parameter,
        value
      });

      setCurrentShot(result.shot);
      toast.success(`${parameter} modified!`);
      loadShots();
    } catch (error) {
      toast.error('Failed to modify parameter');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-cinema-black text-white">
      <Toaster 
        position="top-right"
        toastOptions={{
          style: {
            background: '#1a1a1a',
            color: '#fff',
            border: '1px solid #3a3a3a',
          },
          success: {
            iconTheme: {
              primary: '#d4af37',
              secondary: '#1a1a1a',
            },
          },
        }}
      />

      {/* Header */}
      <header className="border-b border-cinema-gray bg-cinema-darker/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-[1920px] mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <motion.div 
              className="flex items-center gap-3"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
            >
              <div className="bg-gradient-to-br from-cinema-accent to-cinema-blue p-2 rounded-lg">
                <Film className="w-8 h-8 text-cinema-black" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-cinema-accent to-white bg-clip-text text-transparent">
                  FIBO CINEMATICS
                </h1>
                <p className="text-xs text-cinema-lightgray">Professional AI Cinematography Studio</p>
              </div>
            </motion.div>

            {/* Navigation */}
            <nav className="flex items-center gap-2">
              {[
                { id: 'create', label: 'Create Shot', icon: Camera },
                { id: 'library', label: 'Shot Library', icon: Grid },
                { id: 'storyboard', label: 'Storyboard', icon: Layers },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    px-4 py-2 rounded-lg flex items-center gap-2 transition-all
                    ${activeTab === tab.id 
                      ? 'bg-cinema-accent text-cinema-black font-semibold' 
                      : 'bg-cinema-gray text-cinema-lightgray hover:bg-cinema-lightgray'
                    }
                  `}
                >
                  <tab.icon className="w-4 h-4" />
                  <span className="hidden md:inline">{tab.label}</span>
                </button>
              ))}
            </nav>

            {/* Stats */}
            <div className="flex items-center gap-4 text-sm">
              <div className="flex items-center gap-2">
                <ImageIcon className="w-4 h-4 text-cinema-accent" />
                <span className="text-cinema-lightgray">{shots.length} shots</span>
              </div>
              <div className="flex items-center gap-2">
                <Zap className="w-4 h-4 text-cinema-blue" />
                <span className="text-cinema-lightgray">Connected</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-[1920px] mx-auto p-6">
        <AnimatePresence mode="wait">
          {activeTab === 'create' && (
            <motion.div
              key="create"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-6"
            >
              {/* Shot Creator */}
              <ShotCreator onShotCreated={handleShotCreated} />

              {/* Current Shot Display */}
              {currentShot && (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  {/* Image Display */}
                  <div className="lg:col-span-2 space-y-4">
                    <div className="bg-cinema-dark rounded-xl overflow-hidden border border-cinema-gray film-strip">
                      <div className="p-4 bg-cinema-darker border-b border-cinema-gray flex items-center justify-between">
                        <h2 className="text-lg font-semibold flex items-center gap-2">
                          <Eye className="w-5 h-5 text-cinema-accent" />
                          Generated Shot
                        </h2>
                        <div className="flex items-center gap-2 text-sm text-cinema-lightgray">
                          <span>ID: {currentShot.shot_id?.substring(0, 12)}...</span>
                        </div>
                      </div>
                      
                      <div className="p-6 bg-black">
                        {loading ? (
                          <div className="aspect-video flex items-center justify-center">
                            <Loader2 className="w-12 h-12 animate-spin text-cinema-accent" />
                          </div>
                        ) : (
                          <img 
                            src={currentShot.image_url} 
                            alt="Generated shot"
                            className="w-full rounded-lg shadow-2xl"
                          />
                        )}
                      </div>

                      {/* Shot Info */}
                      <div className="p-4 bg-cinema-darker border-t border-cinema-gray">
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <p className="text-cinema-lightgray">Shot Type</p>
                            <p className="font-semibold text-cinema-accent capitalize">
                              {currentShot.shot_type}
                            </p>
                          </div>
                          <div>
                            <p className="text-cinema-lightgray">Aspect Ratio</p>
                            <p className="font-semibold">{currentShot.aspect_ratio}</p>
                          </div>
                          <div>
                            <p className="text-cinema-lightgray">Seed</p>
                            <p className="font-semibold font-mono">{currentShot.seed}</p>
                          </div>
                          <div>
                            <p className="text-cinema-lightgray">Created</p>
                            <p className="font-semibold">
                              {new Date(currentShot.created_at).toLocaleTimeString()}
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Comparison View */}
                    {currentShot.hdr_comparison_path && (
                      <ShotComparison shot={currentShot} />
                    )}
                  </div>

                  {/* Camera Controls */}
                  <div className="space-y-4">
                    <CameraControl 
                      currentShot={currentShot}
                      onParameterChange={handleParameterChange}
                      loading={loading}
                    />
                  </div>
                </div>
              )}
            </motion.div>
          )}

          {activeTab === 'library' && (
            <motion.div
              key="library"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <ShotLibrary 
                shots={shots} 
                onShotSelect={setCurrentShot}
                onRefresh={loadShots}
              />
            </motion.div>
          )}

          {activeTab === 'storyboard' && (
            <motion.div
              key="storyboard"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="text-center py-20"
            >
              <Layers className="w-16 h-16 mx-auto mb-4 text-cinema-accent opacity-50" />
              <h2 className="text-2xl font-bold mb-2">Storyboard Creator</h2>
              <p className="text-cinema-lightgray mb-6">Coming in next iteration!</p>
              <button className="px-6 py-3 bg-cinema-accent text-cinema-black rounded-lg font-semibold hover:bg-opacity-90 transition">
                Create Storyboard
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Footer */}
      <footer className="border-t border-cinema-gray bg-cinema-darker mt-20">
        <div className="max-w-[1920px] mx-auto px-6 py-8">
          <div className="flex items-center justify-between text-sm text-cinema-lightgray">
            <p>FIBO Cinematics Studio • Built for FIBO Hackathon 2025</p>
            <p>Powered by Bria.ai FIBO • CrewAI • React</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;