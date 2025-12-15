// src/components/ShotLibrary.jsx
import { motion } from 'framer-motion';
import { Grid, RefreshCw, Image as ImageIcon, Clock } from 'lucide-react';

export default function ShotLibrary({ shots, onShotSelect, onRefresh }) {
  if (shots.length === 0) {
    return (
      <div className="text-center py-20">
        <ImageIcon className="w-16 h-16 mx-auto mb-4 text-cinema-accent opacity-50" />
        <h2 className="text-2xl font-bold mb-2">No shots yet</h2>
        <p className="text-cinema-lightgray mb-6">Create your first cinematic shot to see it here</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-3">
            <Grid className="w-7 h-7 text-cinema-accent" />
            Shot Library
          </h2>
          <p className="text-cinema-lightgray mt-1">{shots.length} shots total</p>
        </div>
        
        <button
          onClick={onRefresh}
          className="px-4 py-2 bg-cinema-gray hover:bg-cinema-lightgray rounded-lg transition-colors flex items-center gap-2"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {shots.map((shot, index) => (
          <motion.div
            key={shot.shot_id}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.05 }}
            onClick={() => onShotSelect(shot)}
            className="bg-cinema-dark rounded-xl border border-cinema-gray overflow-hidden hover:border-cinema-accent transition-all cursor-pointer group"
          >
            {/* Thumbnail */}
            <div className="aspect-video bg-cinema-darker relative overflow-hidden">
              {shot.image_url ? (
                <img 
                  src={shot.image_url}
                  alt={shot.scene_description}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <ImageIcon className="w-12 h-12 text-cinema-gray" />
                </div>
              )}
              
              {/* Overlay */}
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
                <div className="absolute bottom-0 left-0 right-0 p-3">
                  <p className="text-xs text-white/80 capitalize">{shot.shot_type}</p>
                </div>
              </div>
            </div>

            {/* Info */}
            <div className="p-4 space-y-2">
              <p className="text-sm font-semibold line-clamp-2 group-hover:text-cinema-accent transition-colors">
                {shot.scene_description}
              </p>
              
              <div className="flex items-center gap-2 text-xs text-cinema-lightgray">
                <Clock className="w-3 h-3" />
                {new Date(shot.created_at).toLocaleString()}
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}